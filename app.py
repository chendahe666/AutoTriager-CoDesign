from __future__ import annotations
import json,time
from pathlib import Path
import pandas as pd
import streamlit as st
from autotriager.config import ROOT, DATA, MODEL, api_key
from autotriager.data import cases,fingerprint
from autotriager.analysis import query_meta,date_list,prepare,run
from autotriager.i18n import tr
from autotriager.state import record_review,visible_result

st.set_page_config(page_title='AutoTriager | Incident review',page_icon='◈',layout='wide')
st.markdown('''<style>
.stApp{background:#f7f7f4;color:#1b252a}
.block-container{max-width:1240px;padding-top:2.2rem}
h1,h2,h3{font-family:Georgia,"Noto Serif SC",serif;letter-spacing:-.02em}
[data-testid="stSidebar"]{background:#eaece7;border-right:1px solid #d3d8ce}
[data-testid="stMetric"]{background:#fff;border-top:2px solid #285649;padding:12px 16px}
.stButton button[kind="primary"]{background:#245345;border:0}
</style>''',unsafe_allow_html=True)
st.session_state.setdefault('results',{})
st.session_state.setdefault('reviews',{})
with st.sidebar:
    st.caption('CS 5588  /  CHALLENGE 2')
    language=st.selectbox('Language / 语言',['en','zh'],format_func=lambda x:'English' if x=='en' else '中文',key='language')
    t=lambda k:tr(k,language)
    st.title('AutoTriager')
    st.caption(t('read_only'))
    catalog=cases()
    if not catalog:
        st.warning(t('no_data'));st.stop()
    selected=st.selectbox(t('case'),[c['id'] for c in catalog],key='case_id')
    case=next(c for c in catalog if c['id']==selected)
    case_changed=st.session_state.get('rendered_case')!=selected
    st.session_state['rendered_case']=selected
    st.divider()
    st.caption('OpenRCA · Bank')
    st.caption(MODEL)
    st.caption(t('api') if api_key() else t('no_api'))
    st.caption(t('free'))
    st.caption(t('version'))

@st.cache_resource(show_spinner=False,max_entries=3)
def cached_prepare(case_json,file_fingerprint):
    # The fingerprint includes missing files and mtimes; no result reuse on changed data.
    return prepare(json.loads(case_json))

st.title(t('title'))
st.write(t('subtitle'))
st.caption(t('intro'))
qm=query_meta(case)
st.subheader('01  '+t('scope'))
with st.expander(t('question'),expanded=True):
    st.write(case['instruction'])
    st.caption(t('timezone'))
    st.caption(t('baseline'))
if st.button(t('run'),type='primary',disabled=not bool(api_key()),key='run_button'):
    # Remove previous run immediately, including when this run fails during preparation.
    st.session_state['results'].pop(selected,None)
    started=time.monotonic()
    with st.status(t('stages'),expanded=True) as status:
        try:
            st.write(t('metrics')+' / '+t('logs')+' / '+t('traces'))
            fp=fingerprint(DATA/'telemetry',date_list(qm))
            prepared=cached_prepare(json.dumps(case,sort_keys=True),fp)
            result=run(case,prepared,language,progress=lambda s:st.write(t(s)))
            result['total_seconds']=round(time.monotonic()-started,2)
            st.session_state['results'][selected]=result
            (ROOT/'runs').mkdir(exist_ok=True)
            (ROOT/'runs'/f'{selected}-{result["run_id"]}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            status.update(label=t(result['status']),state='error' if result['status'] in ('api_error','incomplete') else 'complete',expanded=False)
        except Exception as exc:
            status.update(label=t('error'),state='error')
            # Print no raw exception payload: third-party errors can contain request details.
            st.error(t('error')+' ('+type(exc).__name__+')')

result=visible_result(st.session_state['results'],selected)
st.subheader('02  '+t('result'))
if result is None:
    st.info(t('no_result'));st.stop()
st.caption(f"{result['run_id']} · {t('generation_locale')}: {result['language']} · {result['model']}")
cols=st.columns(3)
cols[0].metric(t('elapsed'),f"{result['total_seconds']:.1f} s")
cols[1].metric(t('requests'),result['calls'])
cols[2].metric(t('citations'),len(result['evidence']))
if result['status']=='complete': st.success(t('complete'))
else: st.warning(t(result['status']))
if result.get('error'): st.code(result['error'])
for candidate in result['candidates']:
    with st.container(border=True):
        st.markdown(f"**{t('candidate')}: {candidate['component']}**")
        st.write(t('reason')+': '+(candidate.get('reason') or t('unknown')))
        st.write(candidate['explanation'])
        st.caption(' · '.join(candidate['evidence_ids']))
if not result['candidates']: st.info(t('empty'))
with st.expander(t('limitations'),expanded=result['status']!='complete'):
    st.write(t('claims_note'))
    for item in result['limitations']: st.write('• '+item)
    st.caption(t('baseline'))

st.subheader('03  '+t('evidence'))
if result['evidence']:
    order=sorted(result['evidence'],key=lambda e: result['evidence'][e]['tool']!='get_kpi_series')
    eid=st.selectbox(t('choose_evidence'),order,
        format_func=lambda e:f"{e} · {result['evidence'][e]['tool']} · {result['evidence'][e]['arguments'].get('component','all')}",
        key='evidence_'+result['run_id'])
    ev=result['evidence'][eid]
    with st.expander(t('observation'),expanded=True):
        try:
            observation=json.loads(ev['content'])
            if isinstance(observation,dict): observation.pop('hint',None)
            st.json(observation,expanded=1)
        except ValueError: st.text(ev['content'])
    st.caption(t('raw_note'))
    if ev['sources']:
        candidate_components={c['component'] for c in result['candidates']}
        source_order=sorted(range(len(ev['sources'])),key=lambda i:ev['sources'][i]['component'] not in candidate_components)
        si=st.selectbox(t('source'),source_order,
            format_func=lambda i:f"{ev['sources'][i]['component']} / {ev['sources'][i]['series']}",key='source_'+result['run_id']+'_'+eid)
        source=ev['sources'][si]
        st.caption(f"{t('scope_count')}: {source['record_count']} | "+', '.join(source['files']))
        raw=pd.DataFrame(source['samples'])
        first=[c for c in ('_source','_record','timestamp','cmdb_id','kpi_name','value') if c in raw]
        st.dataframe(raw[first+[c for c in raw.columns if c not in first]],hide_index=True,width='stretch')
    st.caption(t('claims_note'))

st.subheader('04  '+t('review'))
rid=result['run_id']
saved_review=st.session_state['reviews'].get(rid)
if saved_review:
    if case_changed or 'decision_'+rid not in st.session_state:
        st.session_state['decision_'+rid]=saved_review['decision']
    if case_changed or 'reason_'+rid not in st.session_state:
        st.session_state['reason_'+rid]=saved_review['reason']
with st.form('review_'+rid):
    decision=st.radio(t('judgment'),['unresolved','accept','reject'],format_func=lambda x:t(x),horizontal=True,key='decision_'+rid)
    reason=st.text_area(t('feedback'),key='reason_'+rid)
    submitted=st.form_submit_button(t('save'))
    if submitted:
        if not reason.strip(): st.warning(t('need_reason'))
        else:
            st.session_state['reviews'][rid]=record_review(result,decision,reason)
if rid in st.session_state['reviews']:
    st.success(t('saved'))
    review=st.session_state['reviews'][rid]
    st.write(t(review['decision'])+' — '+review['reason'])
st.caption(t('session'))
export={**result,'human_review':st.session_state['reviews'].get(rid)}
st.download_button(t('export'),json.dumps(export,ensure_ascii=False,indent=2),file_name=f'autotriager-{rid}.json',mime='application/json')

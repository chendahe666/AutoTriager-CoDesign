import copy,json,sys
from pathlib import Path
from types import SimpleNamespace
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from autotriager.analysis import query_meta,date_list,validate_submission,run
from autotriager.config import DATA,MODEL
from autotriager.data import cases,fingerprint,verify_record
from autotriager.state import visible_result,record_review
from autotriager.i18n import TEXT

@pytest.fixture
def actual():
    paths=sorted((ROOT/'runs').glob('bank-001-*.json'),key=lambda p:p.stat().st_mtime)
    if not paths: pytest.skip('Run an actual case first; this test does not fabricate results.')
    successful=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
    successful=[r for r in successful if r['status'] in ('complete','partial')]
    if not successful: pytest.skip('No completed real run; see failure log and official evaluation for all attempts.')
    value=successful[-1]
    return value

def test_T1_real_case_has_traceable_diagnosis(actual):
    assert actual['status'] in ('complete','partial')
    assert actual['calls']>0 and actual['model']==MODEL
    assert actual['evidence']
    assert actual['candidates']
    for c in actual['candidates']:
        assert all(e in actual['evidence'] for e in c['evidence_ids'])

def test_T2_case_switch_never_shows_stale_output(actual):
    results={actual['case_id']:actual}
    assert visible_result(results,'bank-004') is None
    results['bank-004']=actual
    assert visible_result(results,'bank-004') is None

def test_T3_query_and_timestamp_units(actual):
    from datetime import datetime,timezone,timedelta
    qm=query_meta(cases()[0])
    assert datetime.fromtimestamp(qm.window_start_seconds,timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')=='2021-03-04 18:00'
    assert qm.window_end_seconds-qm.window_start_seconds==1800
    metric=next(s['samples'][0] for ev in actual['evidence'].values() for s in ev['sources'] if '/metric/' in s['files'][0])
    assert float(metric['timestamp'])==metric['_seconds']
    import pandas as pd
    row=pd.read_csv(DATA/'telemetry/2021_03_04/trace/trace_span.csv',nrows=1).iloc[0]
    assert 1_600_000_000<float(row['timestamp'])*.001<1_700_000_000

def test_T4_raw_evidence_record_resolves(actual):
    samples=[]
    for candidate in actual['candidates']:
        for eid in candidate['evidence_ids']:
            ev=actual['evidence'][eid]
            matches=[s for s in ev['sources'] if s['component']==candidate['component']]
            if ev['tool']=='get_golden_signal':
                assert ev['sources']
                matches=ev['sources']
            else: assert matches
            samples.append(matches[0]['samples'][0])
    assert samples and all(verify_record(DATA/'telemetry',r) for r in samples)

def test_T5_human_feedback_bound_to_run(actual):
    review=record_review(actual,'unresolved','Automated test input, not a real human judgment.')
    assert review['run_id']==actual['run_id'] and review['case_id']==actual['case_id']
    with pytest.raises(ValueError): record_review(actual,'accept',' ')

def test_T6_removed_metrics_are_not_cached(tmp_path):
    from autotriager.analysis import prepare
    qm=query_meta(cases()[0]); dates=date_list(qm)
    folder=tmp_path/dates[0]/'metric';folder.mkdir(parents=True)
    file=folder/'metric_container.csv'
    file.write_text('timestamp,cmdb_id,kpi_name,value\n',encoding='utf-8')
    before=fingerprint(tmp_path,dates)
    file.unlink()
    assert fingerprint(tmp_path,dates)!=before
    with pytest.raises(ValueError,match='Required metrics missing'):
        prepare(cases()[0],root=tmp_path)

def test_T7_invalid_citation_is_rejected(actual):
    from evirca.adapters.bank.adapter import BankAdapter
    payload={'candidates':copy.deepcopy(actual['candidates']),'limitations':[]}
    payload['candidates'][0]['evidence_ids']=['E999']
    errors=validate_submission(payload,actual['evidence'],BankAdapter(),query_meta(cases()[0]))
    assert any('Unknown evidence' in e for e in errors)
    payload['candidates'][0]['component']=[]
    assert 'Component must be a string' in validate_submission(payload,actual['evidence'],BankAdapter(),query_meta(cases()[0]))

def test_T8_timeout_never_fabricates_diagnosis():
    from evirca.adapters.bank.adapter import BankAdapter
    class Failing:
        def create(self,**kwargs): raise TimeoutError('TEST ONLY')
    client=SimpleNamespace(chat=SimpleNamespace(completions=Failing()))
    prep=SimpleNamespace(ctx=SimpleNamespace(adapter=BankAdapter()),fingerprint='test',missing=[],
        qm=query_meta(cases()[0]),index={('metric','Redis02','test_kpi'):{'count':1,'sources':{'test.csv'},'samples':[]}})
    result=run(cases()[0],prep,client=client)
    assert result['status']=='api_error' and result['calls']==1 and result['candidates']==[]
    assert result['evidence']['E001']['tool']=='prepared_records'

def test_T9_locale_dictionary_complete():
    assert all(len(v)==2 and all(isinstance(s,str) and s for s in v) for v in TEXT.values())
    # Stateful no-extra-call check is performed separately in the real browser.

import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from autotriager.data import cases
from autotriager.analysis import prepare,run

p=argparse.ArgumentParser()
p.add_argument('--case',default='all')
p.add_argument('--language',default='en',choices=['en','zh'])
p.add_argument('--prepare-only',action='store_true')
args=p.parse_args()
(ROOT/'runs').mkdir(exist_ok=True)
for case in cases():
    if args.case!='all' and args.case!=case['id']: continue
    started=time.monotonic()
    print(case['id'],'preparing',flush=True)
    prepared=prepare(case,progress=lambda s:print(s,flush=True))
    print('Prepared',round(time.monotonic()-started,2),'seconds; entries',len(prepared.ctx.package.entries),'index',len(prepared.index),flush=True)
    if args.prepare_only: continue
    result=run(case,prepared,args.language,progress=lambda s:print(s,flush=True))
    result['total_seconds']=round(time.monotonic()-started,2)
    (ROOT/'runs'/f'{case["id"]}-{result["run_id"]}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('evidence','steps')},ensure_ascii=True,indent=2),flush=True)

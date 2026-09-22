"""Score saved outputs offline; labels never enter the application pipeline."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('openrca_evaluate',ROOT/'vendor/OpenRCA/main/evaluate.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
labels=json.loads((ROOT/'data/evaluation_only/labels.json').read_text(encoding='utf-8'))
report=[]
for file in sorted((ROOT/'runs').glob('bank-*.json')):
    result=json.loads(file.read_text(encoding='utf-8'))
    predictions=[]
    for c in result['candidates']:
        pred={}
        if c.get('datetime'): pred['root cause occurrence datetime']=c['datetime']
        if c.get('component'): pred['root cause component']=c['component']
        if c.get('reason'): pred['root cause reason']=c['reason']
        predictions.append(pred)
    passed,failed,score=module.evaluate(json.dumps(predictions),labels[result['case_id']])
    report.append({k:result.get(k) for k in ('run_id','case_id','status','calls','elapsed_seconds','total_seconds')}
                  |{'official_partial_score':score,'all_required_fields_correct':score==1.0,'passed':passed,'failed':failed})
(ROOT/'test-results').mkdir(exist_ok=True)
(ROOT/'test-results/official_scores.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

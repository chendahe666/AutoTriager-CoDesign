"""Separate public instructions from scoring labels before the app reads anything."""
import csv
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'data/Bank/query.csv').open(encoding='utf-8',newline='') as f:
    rows=list(csv.DictReader(f))
cases=[]
labels={}
for row_id in (1,4):
    row=rows[row_id]
    cid=f'bank-{row_id:03d}'
    cases.append({'id':cid,'system':'Bank','instruction':row['instruction'],
                  'task_index':row['task_index'],'query_row_zero_based':row_id,
                  'split':'development; not held out'})
    labels[cid]=row['scoring_points']
(ROOT/'data/cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data/evaluation_only').mkdir(exist_ok=True)
(ROOT/'data/evaluation_only/labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared two real case instructions; scoring labels saved separately.')

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import pandas as pd
from .config import ROOT, DATA

def cases():
    path=ROOT/'data/cases.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else []

def fingerprint(root: Path, dates: list[str]):
    """Every missing or changed input produces a different cache key."""
    values=[]
    for date in dates:
        for rel in ('metric/metric_container.csv','metric/metric_app.csv','trace/trace_span.csv','log/log_service.csv'):
            path=root/date/rel
            stat=path.stat() if path.exists() else None
            values.append((date+'/'+rel,stat.st_size if stat else None,stat.st_mtime_ns if stat else None))
    return hashlib.sha256(json.dumps(values).encode()).hexdigest()

def scan_window(root, dates, start, end, progress=lambda s:None):
    """Retain source record ordinals and bounded raw examples, not model-generated evidence.

    CSV record numbers are 1-based data records excluding the header, not text lines.
    Metric examples include min/max, so excursions are inspectable. Full computations
    remain in EviRCA; this index independently links to original observations.
    """
    index={}
    specs=[('metric','metric_container.csv',1.0,'kpi_name'),
           ('metric','metric_app.csv',1.0,'__all__'),
           ('log','log_service.csv',1.0,'log_name'),
           ('trace','trace_span.csv',.001,'__all__')]
    missing=[]
    for date in dates:
        for kind,name,factor,groupcol in specs:
            path=root/date/kind/name
            if not path.exists():
                missing.append(f'{date}/{kind}/{name}')
                continue
            progress(f'Indexing {date}/{kind}/{name}')
            offset=0
            for chunk in pd.read_csv(path,chunksize=150_000,dtype=str,keep_default_na=False):
                idcol='tc' if name=='metric_app.csv' else 'cmdb_id'
                if not {'timestamp',idcol}.issubset(chunk.columns):
                    raise ValueError(f'Missing timestamp/{idcol}: {name}')
                seconds=pd.to_numeric(chunk['timestamp'],errors='coerce')*factor
                mask=seconds.between(start,end)
                sub=chunk.loc[mask].copy()
                sub['_record']=[offset+int(i-chunk.index[0])+1 for i in sub.index]
                offset+=len(chunk)
                if sub.empty: continue
                sub['_seconds']=seconds.loc[mask]
                if groupcol=='__all__': sub['_group']='all'
                else:
                    if groupcol not in sub: raise ValueError(f'Missing {groupcol}: {name}')
                    sub['_group']=sub[groupcol]
                for (comp,group),g in sub.groupby([idcol,'_group'],sort=False):
                    key=(kind,comp,group)
                    bucket=index.setdefault(key,{'count':0,'samples':[],'sources':set()})
                    bucket['count']+=len(g)
                    rel=path.relative_to(root).as_posix()
                    bucket['sources'].add(rel)
                    take=g.head(2)
                    if kind=='metric' and 'value' in g:
                        numbers=pd.to_numeric(g['value'],errors='coerce').dropna()
                        if not numbers.empty:
                            take=pd.concat([take,g.loc[[numbers.idxmin(),numbers.idxmax()]]]).drop_duplicates('_record')
                    for row in take.to_dict('records'):
                        row.pop('_group',None)
                        row['_source']=rel
                        bucket['samples'].append(row)
                    # Bound per-series examples while retaining extrema for metric values.
                    if len(bucket['samples'])>10:
                        samples=bucket['samples']
                        if kind=='metric' and 'value' in samples[0]:
                            numeric=[r for r in samples if _number(r.get('value')) is not None]
                            extremes=sorted(numeric,key=lambda r:float(r['value']))
                            bucket['samples']=samples[:2]+extremes[:2]+extremes[-2:]
                        else: bucket['samples']=samples[:6]
    return index,missing

def _number(x):
    try: return float(x)
    except (ValueError,TypeError): return None

def sources_for(index, tool, args):
    comp=args.get('component')
    kpi=args.get('kpi')
    kind='trace' if tool=='get_call_graph' else 'log' if 'log' in tool else 'metric'
    selected=[]
    for (kd,component,group),bucket in index.items():
        if kd!=kind or (comp and comp!=component) or (kpi and group!=kpi): continue
        if tool=='get_golden_signal' and group!='all': continue
        selected.append({'component':component,'series':group,'record_count':bucket['count'],
                         'files':sorted(bucket['sources']),'samples':bucket['samples']})
    return selected

def verify_record(root, record):
    path=(Path(root)/record['_source']).resolve()
    if not path.is_relative_to(Path(root).resolve()): return False
    wanted=int(record['_record'])
    offset=0
    for ch in pd.read_csv(path,chunksize=150_000,dtype=str,keep_default_na=False):
        if offset<wanted<=offset+len(ch):
            actual=ch.iloc[wanted-offset-1].to_dict()
            return all(str(actual.get(k,''))==str(v) for k,v in record.items() if not k.startswith('_'))
        offset+=len(ch)
    return False

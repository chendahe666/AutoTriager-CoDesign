"""Download selected full days from the official Bank ZIP using HTTP ranges.

Raw telemetry stays local. Does not manufacture samples or crop daily baselines.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
URL = ('https://drive.usercontent.google.com/download?'
       'id=1enBrdPT3wLG94ITGbSOwUFg9fkLR-16R&export=download&confirm=t')

class RangeReader(io.RawIOBase):
    def __init__(self, url):
        self.url, self.pos = url, 0
        self.session = requests.Session()
        r = self.session.get(url, headers={'Range': 'bytes=-65536'}, timeout=60)
        r.raise_for_status()
        if r.status_code != 206:
            raise RuntimeError('Server does not support partial download; no full download attempted.')
        self.size = int(r.headers['Content-Range'].split('/')[-1])
        self.tail = r.content
        self.transferred = len(self.tail)
        self.cache_start, self.cache = 0, b''

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos
    def read(self, n=-1):
        if n < 0: n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0: return b''
        start = self.pos
        if start >= self.size - len(self.tail):
            result = self.tail[start-(self.size-len(self.tail)):start-(self.size-len(self.tail))+n]
        elif self.cache_start <= start and start+n <= self.cache_start+len(self.cache):
            result = self.cache[start-self.cache_start:start-self.cache_start+n]
        else:
            fetch_n = min(max(n, 8*1024*1024), self.size-start)
            r = self.session.get(self.url, headers={'Range':f'bytes={start}-{start+fetch_n-1}'}, timeout=120)
            r.raise_for_status()
            if r.status_code != 206 or not r.headers.get('Content-Range','').startswith(f'bytes {start}-'):
                raise RuntimeError('Unexpected range response')
            self.cache_start, self.cache = start, r.content
            if len(self.cache) != fetch_n: raise RuntimeError('Incomplete range')
            result = self.cache[:n]
            self.transferred += fetch_n
        self.pos += len(result)
        return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--list',action='store_true')
    parser.add_argument('--dates',nargs='+',default=['2021_03_04','2021_03_06'])
    args=parser.parse_args()
    reader=RangeReader(URL)
    with zipfile.ZipFile(reader) as z:
        selected=[i for i in z.infolist() if not i.is_dir() and i.filename.endswith('.csv') and (
            any(d in i.filename for d in args.dates) or i.filename.endswith(('query.csv','record.csv')))]
        print(json.dumps([{'name':i.filename,'bytes':i.file_size,'compressed':i.compress_size} for i in selected],indent=2))
        if args.list: return
        target=ROOT/'data'
        target.mkdir(exist_ok=True)
        manifest=[]
        for info in selected:
            path=(target/info.filename).resolve()
            if not path.is_relative_to(target.resolve()): raise ValueError('Unsafe ZIP path')
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists() or path.stat().st_size != info.file_size:
                # A bounded member download; ZipExtFile verifies CRC at EOF.
                with z.open(info) as src, path.with_suffix(path.suffix+'.part').open('wb') as dst:
                    shutil.copyfileobj(src,dst,1024*1024)
                path.with_suffix(path.suffix+'.part').replace(path)
            digest=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
            manifest.append({'path':path.relative_to(target).as_posix(),'bytes':path.stat().st_size,'sha256':digest,'zip_crc':info.CRC})
            print('Ready:',path.relative_to(target),flush=True)
        (target/'download_manifest.json').write_text(json.dumps({'source':URL,'archive_bytes':reader.size,'downloaded_bytes':reader.transferred,'files':manifest},indent=2),encoding='utf-8')
        print('Transferred bytes:',reader.transferred)

if __name__=='__main__': main()

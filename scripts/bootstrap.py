"""Fetch original dependencies at reviewed commits; do not redistribute EviRCA."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPOS={
 'evirca':('https://github.com/yuhao541/EviRCA.git','bc11c06932717751f68b8ed7da6d31f5c23c952c'),
 'OpenRCA':('https://github.com/microsoft/OpenRCA.git','c1bd4af7f635171a1c31cdd567c07d698dff6abc'),
}
for name,(url,revision) in REPOS.items():
    target=ROOT/'vendor'/name
    target.parent.mkdir(exist_ok=True)
    if not target.exists(): subprocess.run(['git','clone',url,str(target)],check=True)
    subprocess.run(['git','-C',str(target),'checkout','--detach',revision],check=True)
    print(name,revision)

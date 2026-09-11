#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys, uuid
ROOT=Path(__file__).resolve().parents[1]; CONTROL=ROOT/'training_control'; sys.path.insert(0,str(CONTROL))
from no_trainable_surface_v1 import audit  # noqa: E402
OUT=ROOT/'artifacts'/'training_control'/'no_trainable_surface_v1.json'
def main()->int:
 p=audit(); p['status']='PASS' if p['no_trainable_surface'] else 'FAIL'; OUT.parent.mkdir(parents=True,exist_ok=True); t=OUT.with_name(f'.{OUT.name}.tmp-{uuid.uuid4().hex}'); t.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n',encoding='utf-8'); t.replace(OUT); print(json.dumps(p,indent=2,sort_keys=True)); return 0 if p['no_trainable_surface'] else 2
if __name__=='__main__': raise SystemExit(main())

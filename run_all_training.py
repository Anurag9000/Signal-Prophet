#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent; R='Anurag9000/Signal-Prophet'; C='fd34a95d18892df7fb14d1efbb99076a7810fb91'; S='05ef472b29933f18e956c69dfb7e543921ddaff5'; U=f'https://raw.githubusercontent.com/Anurag9000/RigorousRAG/{C}/tools/universal_training_controller_entry.py'
P={"repository":R,"scientific_authority":"training_control/no_trainable_surface_v1.py","jobs":[{"id":"audit-no-trainable-surface","command":[sys.executable,"scripts/audit_no_trainable_surface_v1.py"],"phase":"audit","family":"scientific-authority","device_capable":False,"is_training_job":False,"depends_on":[],"resume_strategy":"restart_exact","checkpoint_contract":{"exact_resume":True,"deterministic":True,"idempotent":True,"atomic_outputs":True},"deterministic":True,"idempotent":True,"atomic_outputs":True,"early_stopping_applicable":False,"early_stopping_exception_reason":"source classification audit","completion_artifacts":["artifacts/training_control/no_trainable_surface_v1.json"]}],"preferred_training_entrypoints":[],"preferred_dataset_entrypoints":[],"dynamic_registry_covers":["api/core/**/*.py","api/main.py","training_control/no_trainable_surface_v1.py"],"ignore_entrypoints":["run_all_training.py","scripts/audit_no_trainable_surface_v1.py","training_control/no_trainable_surface_v1.py"],"strict_coverage":True,"require_native_resume":True,"require_exact_resume":True,"require_training_exact_resume":True,"require_training_early_stopping":True,"require_dag_enforcement":True,"require_model_surface_accounting":True,"require_workload_surface_accounting":True,"require_literal_opf_mechanism_parity":True,"require_registry_member_accounting":True,"require_dynamic_registry_accounting":True,"require_declared_combination_accounting":True,"require_scientific_ontology_accounting":True,"require_declarative_scientific_source_accounting":True,"require_extended_scientific_component_accounting":True,"require_full_scientific_choice_accounting":True,"require_role_paradigm_protocol_accounting":True,"require_all_retained_trainable_source_reachability":True,"auto_console_training_jobs":False,"auto_console_subcommand_jobs":False}
def h(x):return hashlib.sha1(f'blob {len(x)}\0'.encode()+x).hexdigest()
def main():
 q=ROOT/'.training_control'/'universal_training_controller_entry.py'
 if not q.is_file() or h(q.read_bytes())!=S:
  q.parent.mkdir(parents=True,exist_ok=True);x=urllib.request.urlopen(U,timeout=60).read()
  if h(x)!=S:raise RuntimeError('Pinned controller checksum mismatch')
  t=q.with_suffix('.tmp');t.write_bytes(x);os.replace(t,q)
 e=os.environ.copy();e['TRAINING_CONTROL_PROFILE']=json.dumps(P,separators=(',',':'));e['TRAINING_CONTROL_REPO_ROOT']=str(ROOT);e.setdefault('TRAINING_CONTROL_TERMINATION_GRACE_SEC','30');return subprocess.call([sys.executable,str(q),*sys.argv[1:]],cwd=ROOT,env=e)
if __name__=='__main__':raise SystemExit(main())

import copy, json
from pathlib import Path
import security_prioritization_validate as v

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / 'reports/fase-7-etapa-4-priorizacion-seguridad.json').read_text(encoding='utf-8'))

def test_committed_prioritization_valid(): assert v.validate(copy.deepcopy(BASE))
def test_duplicate_ids_fail():
    d=copy.deepcopy(BASE); d['hallazgos'][1]['id']=d['hallazgos'][0]['id']
    try: v.validate(d); assert False
    except AssertionError: pass
def test_missing_contract_mapping_fails():
    d=copy.deepcopy(BASE); d['hallazgos'][0]['contratos'].remove('SEC-CON-026')
    try: v.validate(d); assert False
    except AssertionError: pass
def test_correction_must_remain_unauthorized():
    d=copy.deepcopy(BASE); d['correcciones_autorizadas']=1
    try: v.validate(d); assert False
    except AssertionError: pass

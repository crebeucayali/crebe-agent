import json
from pathlib import Path
import pytest

from security_permission_tests_validate import validate


def load_report():
    return json.loads(Path('reports/fase-7-etapa-5-pruebas-permisos.json').read_text(encoding='utf-8'))


def test_committed_report_valid():
    assert validate()


def test_detects_failed_contract(tmp_path):
    data = load_report()
    data['pruebas'][0]['resultado'] = 'FAIL'
    p = tmp_path / 'bad.json'
    p.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(AssertionError):
        validate(p)


def test_detects_residue(tmp_path):
    data = load_report()
    data['resultado']['residuos'] = 1
    p = tmp_path / 'bad.json'
    p.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(AssertionError):
        validate(p)


def test_detects_stage6_started(tmp_path):
    data = load_report()
    data['etapa_6_iniciada'] = True
    p = tmp_path / 'bad.json'
    p.write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(AssertionError):
        validate(p)

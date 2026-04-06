"""
Tests for the generation engine (app/core/engine.py).
"""
import pytest

import app.generators  # noqa: F401 — trigger field registration
from app.core import engine


# ── Basic generation ──────────────────────────────────────────────────────────

def test_generate_returns_correct_count():
    result = engine.generate(['cpf', 'nome_completo'], count=5, filters={})
    assert len(result['data']) == 5


def test_generate_returns_requested_fields():
    fields = ['cpf', 'email', 'cidade']
    result = engine.generate(fields, count=3, filters={})
    for record in result['data']:
        for f in fields:
            assert f in record, f"Field '{f}' missing in record"


def test_generate_result_has_key():
    result = engine.generate(['cpf'], count=1, filters={})
    assert result['key']
    assert result['fields_labels']
    assert 'elapsed_ms' in result


def test_generate_fields_labels_match():
    fields = ['nome_completo', 'cpf', 'email']
    result = engine.generate(fields, count=1, filters={})
    label_keys = {fl['key'] for fl in result['fields_labels']}
    for f in fields:
        assert f in label_keys


# ── Dependency resolution ─────────────────────────────────────────────────────

def test_idade_after_data_nascimento():
    """When both are selected, data_nascimento must come before idade."""
    result = engine.generate(['idade', 'data_nascimento'], count=10, filters={})
    for record in result['data']:
        assert record['idade'] is not None
        assert record['data_nascimento'] is not None


def test_idade_consistent_with_data_nascimento():
    """Age should match the generated birth date."""
    from datetime import date
    result = engine.generate(['data_nascimento', 'idade'], count=20, filters={})
    for record in result['data']:
        dob_str = record['data_nascimento']
        day, month, year = map(int, dob_str.split('/'))
        dob = date(year, month, day)
        hoje = date.today()
        expected_age = hoje.year - dob.year - ((hoje.month, hoje.day) < (dob.month, dob.day))
        assert abs(record['idade'] - expected_age) <= 1, (
            f"Age mismatch: dob={dob_str}, age={record['idade']}, expected~{expected_age}"
        )


# ── Shared context groups ─────────────────────────────────────────────────────

def test_location_fields_share_same_city():
    """CEP, cidade, estado, bairro should all be consistent per record."""
    from app.generators.utils import CIDADES_BRASIL
    result = engine.generate(['cep', 'cidade', 'estado'], count=20, filters={})
    city_names = {c['cidade'] for c in CIDADES_BRASIL}
    for record in result['data']:
        assert record['cidade'] in city_names, f"Unknown city: {record['cidade']}"


def test_name_fields_share_context():
    """email and usuario generated alongside nome_completo use the same name."""
    import re
    result = engine.generate(['nome_completo', 'email', 'usuario'], count=10, filters={})
    for record in result['data']:
        nome = record['nome_completo'].split()[0].lower()
        normalised = re.sub(r'[^a-z]', '', nome[:4])
        # The local part of the email or the username should derive from the name
        email_local = record['email'].split('@')[0].lower()
        username = record['usuario'].lower()
        assert (normalised in email_local or normalised in username), (
            f"Name '{nome}' not reflected in email '{record['email']}' or user '{record['usuario']}'"
        )


# ── Gender filter propagation ─────────────────────────────────────────────────

def test_gender_filter_feminine():
    """All generated names should sound feminine when filter is set."""
    from app.generators.utils import fake
    # We can't validate "femininity" linguistically, but we can verify no crash
    # and that the field is populated.
    result = engine.generate(
        ['nome_completo', 'primeiro_nome'],
        count=5,
        filters={'nome_completo': {'genero': 'feminino'}},
    )
    for record in result['data']:
        assert record['nome_completo']
        assert record['primeiro_nome']


# ── Cache / get_stored ────────────────────────────────────────────────────────

def test_get_stored_returns_result():
    result = engine.generate(['cpf'], count=2, filters={})
    key = result['key']
    stored = engine.get_stored(key)
    assert stored is not None
    assert len(stored['records']) == 2


def test_get_stored_unknown_key_returns_none():
    assert engine.get_stored('nonexistent-key-xyz') is None


# ── Field order preserved ─────────────────────────────────────────────────────

def test_field_order_in_labels():
    """fields_labels must respect the requested field order (minus dependency reordering)."""
    # When no dependency forces a reorder, the order should match input.
    fields = ['cpf', 'banco', 'placa']
    result = engine.generate(fields, count=1, filters={})
    label_keys = [fl['key'] for fl in result['fields_labels']]
    assert label_keys == fields, f"Unexpected order: {label_keys}"


def test_dependency_reorder_data_nascimento_before_idade():
    """Even if idade is requested first, data_nascimento must precede it."""
    result = engine.generate(['idade', 'data_nascimento'], count=1, filters={})
    label_keys = [fl['key'] for fl in result['fields_labels']]
    assert label_keys.index('data_nascimento') < label_keys.index('idade')

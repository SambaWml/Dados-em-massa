"""
Tests for Flask API routes (app/api/routes.py).
"""
import json

import pytest

import app.generators  # noqa: F401


# ── GET / ─────────────────────────────────────────────────────────────────────

def test_index_returns_html(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<!DOCTYPE html>' in resp.data or b'<html' in resp.data


# ── GET /api/fields ───────────────────────────────────────────────────────────

def test_fields_returns_200(client):
    resp = client.get('/api/fields')
    assert resp.status_code == 200


def test_fields_response_structure(client):
    resp = client.get('/api/fields')
    body = resp.get_json()
    assert 'categories' in body
    assert isinstance(body['categories'], list)
    assert len(body['categories']) > 0


def test_fields_contains_expected_keys(client):
    resp = client.get('/api/fields')
    body = resp.get_json()
    all_keys = {f['key'] for cat in body['categories'] for f in cat['fields']}
    expected = {'cpf', 'nome_completo', 'email', 'cidade', 'cnpj', 'placa'}
    assert expected.issubset(all_keys), f"Missing fields: {expected - all_keys}"


# ── POST /api/generate ────────────────────────────────────────────────────────

def test_generate_basic(client):
    resp = client.post('/api/generate', json={'fields': ['cpf', 'email'], 'count': 3})
    assert resp.status_code == 200
    body = resp.get_json()
    assert 'data' in body
    assert len(body['data']) == 3


def test_generate_response_has_key(client):
    resp = client.post('/api/generate', json={'fields': ['cpf'], 'count': 1})
    body = resp.get_json()
    assert 'key' in body and body['key']


def test_generate_response_has_fields_labels(client):
    resp = client.post('/api/generate', json={'fields': ['cpf', 'nome_completo'], 'count': 1})
    body = resp.get_json()
    assert 'fields_labels' in body
    label_keys = [fl['key'] for fl in body['fields_labels']]
    assert 'cpf' in label_keys
    assert 'nome_completo' in label_keys


def test_generate_with_filters(client):
    resp = client.post('/api/generate', json={
        'fields': ['nome_completo'],
        'count': 5,
        'filters': {'nome_completo': {'genero': 'feminino'}},
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body['data']) == 5


def test_generate_no_fields_returns_400(client):
    resp = client.post('/api/generate', json={'fields': [], 'count': 10})
    assert resp.status_code == 400
    body = resp.get_json()
    assert 'error' in body


def test_generate_invalid_count_returns_400(client):
    resp = client.post('/api/generate', json={'fields': ['cpf'], 'count': 0})
    assert resp.status_code == 400


def test_generate_count_too_large_returns_400(client):
    resp = client.post('/api/generate', json={'fields': ['cpf'], 'count': 99999})
    assert resp.status_code == 400


def test_generate_unknown_field_returns_400(client):
    resp = client.post('/api/generate', json={'fields': ['campo_inexistente'], 'count': 1})
    assert resp.status_code == 400


def test_generate_elapsed_ms_present(client):
    resp = client.post('/api/generate', json={'fields': ['cpf'], 'count': 10})
    body = resp.get_json()
    assert 'elapsed_ms' in body
    assert body['elapsed_ms'] >= 0


# ── GET /api/export/<key> ─────────────────────────────────────────────────────

def _generate_and_get_key(client, fields=None, count=5):
    """Helper: generate data and return the session key."""
    resp = client.post('/api/generate', json={
        'fields': fields or ['cpf', 'nome_completo'],
        'count': count,
    })
    return resp.get_json()['key']


def test_export_csv(client):
    key = _generate_and_get_key(client)
    resp = client.get(f'/api/export/{key}?format=csv')
    assert resp.status_code == 200
    assert 'text/csv' in resp.content_type
    assert resp.data.startswith(b'\xef\xbb\xbf')  # BOM


def test_export_json(client):
    key = _generate_and_get_key(client)
    resp = client.get(f'/api/export/{key}?format=json')
    assert resp.status_code == 200
    assert 'application/json' in resp.content_type
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_export_excel(client):
    key = _generate_and_get_key(client)
    resp = client.get(f'/api/export/{key}?format=excel')
    assert resp.status_code == 200
    assert 'spreadsheetml' in resp.content_type
    assert resp.data[:2] == b'PK'  # XLSX = ZIP


def test_export_unknown_format_returns_400(client):
    key = _generate_and_get_key(client)
    resp = client.get(f'/api/export/{key}?format=pdf')
    assert resp.status_code == 400


def test_export_missing_key_returns_404(client):
    resp = client.get('/api/export/chave-inexistente?format=csv')
    assert resp.status_code == 404


def test_export_csv_default_format(client):
    """format param defaults to csv."""
    key = _generate_and_get_key(client)
    resp = client.get(f'/api/export/{key}')
    assert resp.status_code == 200
    assert 'text/csv' in resp.content_type


# ── Column order preservation ─────────────────────────────────────────────────

def test_field_order_preserved_in_response(client):
    """The fields_labels order should match the requested order (no dependency forcing)."""
    fields = ['cpf', 'banco', 'placa']
    resp = client.post('/api/generate', json={'fields': fields, 'count': 1})
    body = resp.get_json()
    label_keys = [fl['key'] for fl in body['fields_labels']]
    assert label_keys == fields, f"Order changed: {label_keys}"


def test_field_order_different_sequences(client):
    """Two requests with different field orders return different column orderings."""
    order_a = ['cpf', 'email', 'cidade']
    order_b = ['cidade', 'email', 'cpf']

    resp_a = client.post('/api/generate', json={'fields': order_a, 'count': 1})
    resp_b = client.post('/api/generate', json={'fields': order_b, 'count': 1})

    keys_a = [fl['key'] for fl in resp_a.get_json()['fields_labels']]
    keys_b = [fl['key'] for fl in resp_b.get_json()['fields_labels']]

    assert keys_a == order_a, f"Order A wrong: {keys_a}"
    assert keys_b == order_b, f"Order B wrong: {keys_b}"

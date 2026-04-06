import io
import time

from flask import Blueprint, jsonify, render_template, request, send_file

from app.core import engine, exporters
from app.generators import FIELD_REGISTRY, get_fields_by_category

api_bp = Blueprint('api', __name__)


# ── Pages ─────────────────────────────────────────────────────────────────────

@api_bp.route('/')
def index():
    return render_template('index.html')


# ── API: field catalog ────────────────────────────────────────────────────────

@api_bp.route('/api/fields')
def get_fields():
    return jsonify({'categories': get_fields_by_category()})


# ── API: generate ─────────────────────────────────────────────────────────────

@api_bp.route('/api/generate', methods=['POST'])
def generate():
    body = request.get_json(silent=True) or {}

    fields  = body.get('fields', [])
    count   = body.get('count', 100)
    filters = body.get('filters', {})

    # ── Validation ────────────────────────────────────────────────────────────
    if not fields:
        return jsonify({'error': 'Selecione pelo menos um campo.'}), 400

    try:
        count = int(count)
    except (TypeError, ValueError):
        return jsonify({'error': 'Quantidade inválida.'}), 400

    if not (1 <= count <= 50_000):
        return jsonify({'error': 'Quantidade deve ser entre 1 e 50.000.'}), 400

    invalid = [f for f in fields if f not in FIELD_REGISTRY]
    if invalid:
        return jsonify({'error': f'Campos desconhecidos: {invalid}'}), 400

    # ── Generate ──────────────────────────────────────────────────────────────
    result = engine.generate(fields, count, filters)
    return jsonify(result)


# ── API: export ───────────────────────────────────────────────────────────────

@api_bp.route('/api/export/<key>')
def export_data(key: str):
    stored = engine.get_stored(key)
    if not stored:
        return jsonify({
            'error': 'Sessão expirada ou não encontrada. Gere os dados novamente.'
        }), 404

    fmt     = request.args.get('format', 'csv').lower()
    records = stored['records']
    fields  = stored['fields']
    f_labels = stored['fields_labels']

    ts = time.strftime('%Y%m%d_%H%M%S')

    if fmt == 'csv':
        content = exporters.export_csv(records, fields)
        return send_file(
            io.BytesIO(content),
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=f'dados_{ts}.csv',
        )

    if fmt == 'json':
        content = exporters.export_json(records)
        return send_file(
            io.BytesIO(content),
            mimetype='application/json',
            as_attachment=True,
            download_name=f'dados_{ts}.json',
        )

    if fmt == 'excel':
        content = exporters.export_excel(records, fields, f_labels)
        return send_file(
            io.BytesIO(content),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'dados_{ts}.xlsx',
        )

    return jsonify({'error': f'Formato desconhecido: {fmt}'}), 400

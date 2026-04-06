"""
Data generation engine.

Flow per record:
  1. Pre-populate shared contexts (_name, _location) if any of the
     corresponding fields were requested.
  2. Generate each field in dependency-resolved order, accumulating
     values in the context dict so dependent generators can read them.
"""
import logging
import time
import uuid
from collections import OrderedDict
from typing import Any, Dict, List

from app.generators.registry import FIELD_REGISTRY
from app.generators.utils import get_name_context, get_location_context

logger = logging.getLogger(__name__)

# ── In-memory result cache ────────────────────────────────────────────────────
_store: OrderedDict = OrderedDict()
_MAX_STORE = 50

# Fields that belong to each shared-context group
_NAME_FIELDS     = {'nome_completo', 'primeiro_nome', 'sobrenome', 'email', 'usuario'}
_LOCATION_FIELDS = {'cep', 'cidade', 'estado', 'bairro', 'endereco', 'pais'}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gender_from_filters(fields: List[str], filters: Dict) -> str:
    """Pick the gender filter from the first name-type field that has one."""
    for key in ('nome_completo', 'primeiro_nome', 'email', 'usuario'):
        if key in fields and 'genero' in filters.get(key, {}):
            return filters[key]['genero']
    return 'aleatorio'


def _resolve_order(fields: List[str]) -> List[str]:
    """Topological sort: dependencies first."""
    ordered: List[str] = []
    visited: set = set()

    def visit(key: str) -> None:
        if key in visited:
            return
        visited.add(key)
        fd = FIELD_REGISTRY.get(key)
        if fd:
            for dep in fd.dependencies:
                if dep in fields:
                    visit(dep)
        if key in fields:
            ordered.append(key)

    for f in fields:
        visit(f)
    return ordered


def _generate_record(ordered_fields: List[str], filters: Dict,
                     needs_name: bool, genero: str, needs_location: bool) -> Dict:
    ctx: Dict[str, Any] = {}

    if needs_name:
        get_name_context(ctx, genero)
    if needs_location:
        get_location_context(ctx)

    record: Dict[str, Any] = {}
    for key in ordered_fields:
        fd = FIELD_REGISTRY.get(key)
        if not fd:
            continue
        try:
            value = fd.generator(ctx, filters.get(key, {}))
        except Exception as exc:
            logger.error("Error generating field '%s': %s", key, exc)
            value = None
        record[key] = value
        ctx[key] = value

    return record


# ── Public API ────────────────────────────────────────────────────────────────

def generate(fields: List[str], count: int, filters: Dict[str, Any]) -> Dict:
    """
    Generate *count* records with the requested *fields*.

    Returns a dict with:
      - key           : cache key for subsequent export
      - data          : list of generated records (dicts)
      - fields_labels : [{'key': ..., 'label': ...}, ...]
      - elapsed_ms    : generation time in milliseconds
    """
    t0 = time.time()

    ordered = _resolve_order(fields)
    needs_name     = bool(_NAME_FIELDS & set(fields))
    needs_location = bool(_LOCATION_FIELDS & set(fields))
    genero         = _gender_from_filters(fields, filters)

    records = [
        _generate_record(ordered, filters, needs_name, genero, needs_location)
        for _ in range(count)
    ]

    elapsed_ms = int((time.time() - t0) * 1000)

    fields_labels = [
        {'key': k, 'label': FIELD_REGISTRY[k].label}
        for k in ordered
        if k in FIELD_REGISTRY
    ]

    key = str(uuid.uuid4())
    if len(_store) >= _MAX_STORE:
        _store.popitem(last=False)
    _store[key] = {
        'records': records,
        'fields': ordered,
        'fields_labels': fields_labels,
    }

    logger.info(
        "Generated %d records × %d fields in %d ms (key=%s)",
        count, len(fields), elapsed_ms, key,
    )

    return {
        'key': key,
        'data': records,
        'fields_labels': fields_labels,
        'elapsed_ms': elapsed_ms,
    }


def get_stored(key: str) -> Dict | None:
    return _store.get(key)

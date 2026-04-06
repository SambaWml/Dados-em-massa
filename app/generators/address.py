import random
from typing import Dict

from app.generators.registry import FieldDefinition, FilterOption, register_field
from app.generators.utils import get_location_context

# ---------------------------------------------------------------------------
# Generator functions — all share the same _location context per record
# ---------------------------------------------------------------------------

def gen_cep(context: Dict, filters: Dict) -> str:
    return get_location_context(context)['cep']


def gen_endereco(context: Dict, filters: Dict) -> str:
    return get_location_context(context)['logradouro']


def gen_numero(context: Dict, filters: Dict) -> str:
    return str(random.randint(1, 9999))


def gen_bairro(context: Dict, filters: Dict) -> str:
    return get_location_context(context)['bairro']


def gen_cidade(context: Dict, filters: Dict) -> str:
    return get_location_context(context)['cidade']


def gen_estado(context: Dict, filters: Dict) -> str:
    fmt = filters.get('formato', 'nome')
    loc = get_location_context(context)
    return loc['uf'] if fmt == 'sigla' else loc['estado']


def gen_pais(context: Dict, filters: Dict) -> str:
    return 'Brasil'


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

register_field(FieldDefinition(
    key='cep', label='CEP',
    category='endereco', category_label='Endereço',
    generator=gen_cep,
    description='CEP consistente com cidade/estado',
    icon='fas fa-map-pin',
))

register_field(FieldDefinition(
    key='endereco', label='Endereço',
    category='endereco', category_label='Endereço',
    generator=gen_endereco,
    description='Tipo e nome do logradouro',
    icon='fas fa-road',
))

register_field(FieldDefinition(
    key='numero', label='Número',
    category='endereco', category_label='Endereço',
    generator=gen_numero,
    description='Número do imóvel',
    icon='fas fa-hashtag',
))

register_field(FieldDefinition(
    key='bairro', label='Bairro',
    category='endereco', category_label='Endereço',
    generator=gen_bairro,
    description='Nome do bairro',
    icon='fas fa-map',
))

register_field(FieldDefinition(
    key='cidade', label='Cidade',
    category='endereco', category_label='Endereço',
    generator=gen_cidade,
    description='Cidade brasileira (consistente com CEP/estado)',
    icon='fas fa-city',
))

register_field(FieldDefinition(
    key='estado', label='Estado',
    category='endereco', category_label='Endereço',
    generator=gen_estado,
    filter_options=[
        FilterOption(
            key='formato', label='Formato', type='select',
            options=[
                {'value': 'nome',  'label': 'Nome completo'},
                {'value': 'sigla', 'label': 'Sigla (UF)'},
            ],
            default='nome',
        ),
    ],
    description='Estado (nome ou sigla)',
    icon='fas fa-map-marked-alt',
))

register_field(FieldDefinition(
    key='pais', label='País',
    category='endereco', category_label='Endereço',
    generator=gen_pais,
    description='País (Brasil)',
    icon='fas fa-globe-americas',
))

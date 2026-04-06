import random
import string
from typing import Dict

from app.generators.registry import FieldDefinition, FilterOption, register_field
from app.generators.utils import fake, normalize, get_name_context

# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------

_DOMINIOS_PESSOAIS = [
    'gmail.com', 'hotmail.com', 'yahoo.com.br', 'outlook.com',
    'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br',
    'live.com', 'icloud.com',
]

_DOMINIOS_CORPORATIVOS = [
    'empresa.com.br', 'corp.com.br', 'companhia.com.br',
    'negocios.com.br', 'grupo.com.br', 'holding.com.br',
    'tech.com.br', 'digital.com.br', 'sistemas.com.br',
]

_DDD_BRASIL = [
    '11', '12', '13', '14', '15', '16', '17', '18', '19',
    '21', '22', '24', '27', '28',
    '31', '32', '33', '34', '35', '37', '38',
    '41', '42', '43', '44', '45', '46',
    '47', '48', '49',
    '51', '53', '54', '55',
    '61', '62', '63', '64', '65', '66', '67', '68', '69',
    '71', '73', '74', '75', '77', '79',
    '81', '82', '83', '84', '85', '86', '87', '88', '89',
    '91', '92', '93', '94', '95', '96', '97', '98', '99',
]


def _build_email(primeiro: str, sobrenome: str, dominio: str) -> str:
    p = normalize(primeiro).lower().replace(' ', '')
    s = normalize(sobrenome).lower().replace(' ', '')
    s_curto = s[:6] if len(s) > 6 else s
    num = random.randint(1, 999)
    patterns = [
        f"{p}.{s_curto}",
        f"{p}{s_curto[:3]}",
        f"{p[0]}{s_curto}",
        f"{p}.{s_curto}{num}",
        f"{p}{num}",
    ]
    local = random.choice(patterns)
    return f"{local}@{dominio}"


def gen_email(context: Dict, filters: Dict) -> str:
    tipo = filters.get('tipo', 'aleatorio')
    dominio_custom = filters.get('dominio', '').strip()

    if dominio_custom:
        dominio = dominio_custom
    elif tipo == 'corporativo':
        dominio = random.choice(_DOMINIOS_CORPORATIVOS)
    elif tipo == 'pessoal':
        dominio = random.choice(_DOMINIOS_PESSOAIS)
    else:
        dominio = random.choice(_DOMINIOS_PESSOAIS + _DOMINIOS_CORPORATIVOS)

    nc = get_name_context(context)
    return _build_email(nc['primeiro'], nc['sobrenome'], dominio)


def gen_telefone(context: Dict, filters: Dict) -> str:
    ddd = random.choice(_DDD_BRASIL)
    numero = f"{random.randint(2000, 5999)}-{random.randint(1000, 9999)}"
    return f"({ddd}) {numero}"


def gen_celular(context: Dict, filters: Dict) -> str:
    ddd = random.choice(_DDD_BRASIL)
    numero = f"9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    return f"({ddd}) {numero}"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

register_field(FieldDefinition(
    key='email', label='E-mail',
    category='contato', category_label='Contato',
    generator=gen_email,
    filter_options=[
        FilterOption(
            key='tipo', label='Tipo', type='select',
            options=[
                {'value': 'aleatorio',   'label': 'Aleatório'},
                {'value': 'pessoal',     'label': 'Pessoal'},
                {'value': 'corporativo', 'label': 'Corporativo'},
            ],
            default='aleatorio',
        ),
        FilterOption(key='dominio', label='Domínio personalizado', type='text', default=''),
    ],
    description='Consistente com o nome gerado',
    icon='fas fa-envelope',
))

register_field(FieldDefinition(
    key='telefone', label='Telefone',
    category='contato', category_label='Contato',
    generator=gen_telefone,
    description='Telefone fixo com DDD brasileiro',
    icon='fas fa-phone',
))

register_field(FieldDefinition(
    key='celular', label='Celular',
    category='contato', category_label='Contato',
    generator=gen_celular,
    description='Celular com DDD brasileiro (9 dígitos)',
    icon='fas fa-mobile-alt',
))

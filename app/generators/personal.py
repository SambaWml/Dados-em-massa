import random
from datetime import date, timedelta
from typing import Dict

from app.generators.registry import FieldDefinition, FilterOption, register_field
from app.generators.utils import fake, get_name_context

# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------

def gen_nome_completo(context: Dict, filters: Dict) -> str:
    genero = filters.get('genero', 'aleatorio')
    nc = get_name_context(context, genero)
    return f"{nc['primeiro']} {nc['sobrenome']}"


def gen_primeiro_nome(context: Dict, filters: Dict) -> str:
    genero = filters.get('genero', 'aleatorio')
    nc = get_name_context(context, genero)
    return nc['primeiro']


def gen_sobrenome(context: Dict, filters: Dict) -> str:
    nc = get_name_context(context)
    return nc['sobrenome']


def _gerar_cpf() -> str:
    def digito(parcial):
        n = len(parcial) + 1
        soma = sum(d * (n - i) for i, d in enumerate(parcial))
        r = soma % 11
        return 0 if r < 2 else 11 - r

    nums = [random.randint(0, 9) for _ in range(9)]
    nums.append(digito(nums))
    nums.append(digito(nums))
    s = ''.join(map(str, nums))
    return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"


def gen_cpf(context: Dict, filters: Dict) -> str:
    return _gerar_cpf()


def gen_rg(context: Dict, filters: Dict) -> str:
    nums = [random.randint(0, 9) for _ in range(8)]
    digito = random.choice('0123456789X')
    s = ''.join(map(str, nums))
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}-{digito}"


def gen_data_nascimento(context: Dict, filters: Dict) -> str:
    idade_min = max(0, int(filters.get('idade_min', 18)))
    idade_max = min(120, int(filters.get('idade_max', 70)))
    if idade_min > idade_max:
        idade_min, idade_max = idade_max, idade_min

    hoje = date.today()
    data_max = hoje - timedelta(days=idade_min * 365)
    data_min = hoje - timedelta(days=idade_max * 365)

    delta = (data_max - data_min).days
    if delta < 0:
        delta = 0
    data = data_min + timedelta(days=random.randint(0, delta))

    context['_data_nascimento'] = data
    return data.strftime('%d/%m/%Y')


def gen_idade(context: Dict, filters: Dict) -> int:
    if '_data_nascimento' in context:
        data = context['_data_nascimento']
        hoje = date.today()
        return hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))

    idade_min = int(filters.get('idade_min', 18))
    idade_max = int(filters.get('idade_max', 70))
    return random.randint(idade_min, idade_max)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_GENERO_FILTER = FilterOption(
    key='genero', label='Gênero', type='select',
    options=[
        {'value': 'aleatorio', 'label': 'Aleatório'},
        {'value': 'masculino', 'label': 'Masculino'},
        {'value': 'feminino',  'label': 'Feminino'},
    ],
    default='aleatorio',
)

_IDADE_FILTERS = [
    FilterOption(key='idade_min', label='Idade mínima', type='number', min_value=0, max_value=120, default=18),
    FilterOption(key='idade_max', label='Idade máxima', type='number', min_value=0, max_value=120, default=70),
]

register_field(FieldDefinition(
    key='nome_completo', label='Nome Completo',
    category='pessoal', category_label='Pessoal',
    generator=gen_nome_completo,
    filter_options=[_GENERO_FILTER],
    description='Nome e sobrenome completo',
    icon='fas fa-user',
))

register_field(FieldDefinition(
    key='primeiro_nome', label='Primeiro Nome',
    category='pessoal', category_label='Pessoal',
    generator=gen_primeiro_nome,
    filter_options=[_GENERO_FILTER],
    description='Apenas o primeiro nome',
    icon='fas fa-user',
))

register_field(FieldDefinition(
    key='sobrenome', label='Sobrenome',
    category='pessoal', category_label='Pessoal',
    generator=gen_sobrenome,
    description='Apenas o sobrenome',
    icon='fas fa-user',
))

register_field(FieldDefinition(
    key='cpf', label='CPF',
    category='pessoal', category_label='Pessoal',
    generator=gen_cpf,
    description='CPF válido (XXX.XXX.XXX-XX)',
    icon='fas fa-id-card',
))

register_field(FieldDefinition(
    key='rg', label='RG',
    category='pessoal', category_label='Pessoal',
    generator=gen_rg,
    description='RG com dígito verificador',
    icon='fas fa-id-card',
))

register_field(FieldDefinition(
    key='data_nascimento', label='Data de Nascimento',
    category='pessoal', category_label='Pessoal',
    generator=gen_data_nascimento,
    filter_options=_IDADE_FILTERS,
    description='Data no formato DD/MM/AAAA',
    icon='fas fa-birthday-cake',
))

register_field(FieldDefinition(
    key='idade', label='Idade',
    category='pessoal', category_label='Pessoal',
    generator=gen_idade,
    dependencies=['data_nascimento'],
    filter_options=_IDADE_FILTERS,
    description='Consistente com data de nascimento se selecionada',
    icon='fas fa-birthday-cake',
))

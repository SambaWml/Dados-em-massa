import random
import string
from typing import Dict

from app.generators.registry import FieldDefinition, FilterOption, register_field
from app.generators.utils import normalize, get_name_context


def gen_usuario(context: Dict, filters: Dict) -> str:
    nc = get_name_context(context)
    p = normalize(nc['primeiro']).lower().replace(' ', '')
    s = normalize(nc['sobrenome']).lower().replace(' ', '')
    s_curto = s[:6] if len(s) > 6 else s
    num = random.randint(1, 9999)

    patterns = [
        f"{p}.{s_curto}",
        f"{p}{s_curto[:3]}",
        f"{p[0]}{s_curto}",
        f"{p}_{num}",
        f"{p}.{s_curto[0]}{num}",
    ]
    return random.choice(patterns)


def gen_senha(context: Dict, filters: Dict) -> str:
    forca = filters.get('forca', 'medio')
    comp = int(filters.get('comprimento', 0))

    if forca == 'fraco':
        length = comp if comp >= 4 else random.randint(6, 8)
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    if forca == 'forte':
        length = comp if comp >= 8 else random.randint(12, 16)
        especiais = '!@#$%&*'
        partes = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice(especiais),
        ]
        resto = random.choices(
            string.ascii_letters + string.digits + especiais,
            k=length - 4,
        )
        senha = partes + resto
        random.shuffle(senha)
        return ''.join(senha)

    # medio
    length = comp if comp >= 6 else random.randint(8, 12)
    chars = string.ascii_letters + string.digits + '@#$!'
    return ''.join(random.choice(chars) for _ in range(length))


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

register_field(FieldDefinition(
    key='usuario', label='Usuário',
    category='acesso', category_label='Acesso',
    generator=gen_usuario,
    description='Username baseado no nome gerado',
    icon='fas fa-at',
))

register_field(FieldDefinition(
    key='senha', label='Senha',
    category='acesso', category_label='Acesso',
    generator=gen_senha,
    filter_options=[
        FilterOption(
            key='forca', label='Força', type='select',
            options=[
                {'value': 'fraco',  'label': 'Fraca (6–8 chars, sem especiais)'},
                {'value': 'medio',  'label': 'Média (8–12 chars, poucos especiais)'},
                {'value': 'forte',  'label': 'Forte (12–16 chars, todos os tipos)'},
            ],
            default='medio',
        ),
        FilterOption(key='comprimento', label='Comprimento fixo (0 = automático)',
                     type='number', min_value=0, max_value=64, default=0),
    ],
    description='Senha com força configurável',
    icon='fas fa-lock',
))

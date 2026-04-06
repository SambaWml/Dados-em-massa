import random
import string
from typing import Dict

from app.generators.registry import FieldDefinition, FilterOption, register_field

_LETRAS = string.ascii_uppercase


def gen_placa(context: Dict, filters: Dict) -> str:
    fmt = filters.get('formato', 'aleatorio')

    if fmt == 'antigo':
        # ABC-1234
        letras = ''.join(random.choice(_LETRAS) for _ in range(3))
        nums = ''.join(str(random.randint(0, 9)) for _ in range(4))
        return f"{letras}-{nums}"

    if fmt == 'mercosul':
        # ABC1D23
        letras1 = ''.join(random.choice(_LETRAS) for _ in range(3))
        n1 = random.randint(0, 9)
        letra_mid = random.choice(_LETRAS)
        n23 = ''.join(str(random.randint(0, 9)) for _ in range(2))
        return f"{letras1}{n1}{letra_mid}{n23}"

    # aleatorio: 50/50
    if random.random() > 0.5:
        letras = ''.join(random.choice(_LETRAS) for _ in range(3))
        nums = ''.join(str(random.randint(0, 9)) for _ in range(4))
        return f"{letras}-{nums}"
    else:
        letras1 = ''.join(random.choice(_LETRAS) for _ in range(3))
        n1 = random.randint(0, 9)
        letra_mid = random.choice(_LETRAS)
        n23 = ''.join(str(random.randint(0, 9)) for _ in range(2))
        return f"{letras1}{n1}{letra_mid}{n23}"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

register_field(FieldDefinition(
    key='placa', label='Placa de Veículo',
    category='veiculo', category_label='Veículo',
    generator=gen_placa,
    filter_options=[
        FilterOption(
            key='formato', label='Formato', type='select',
            options=[
                {'value': 'aleatorio', 'label': 'Aleatório'},
                {'value': 'antigo',    'label': 'Antigo (ABC-1234)'},
                {'value': 'mercosul',  'label': 'Mercosul (ABC1D23)'},
            ],
            default='aleatorio',
        ),
    ],
    description='Placa no formato antigo ou Mercosul',
    icon='fas fa-car',
))

import random
from typing import Dict

from app.generators.registry import FieldDefinition, register_field

_BANCOS = [
    "Banco do Brasil",
    "Caixa Econômica Federal",
    "Bradesco",
    "Itaú Unibanco",
    "Santander",
    "BTG Pactual",
    "Banco Inter",
    "Nubank",
    "C6 Bank",
    "XP Investimentos",
    "Banrisul",
    "Sicredi",
    "Sicoob",
    "Banco Safra",
    "Banco Original",
    "Mercado Pago",
    "PicPay",
    "Banco Neon",
    "Banco Votorantim",
    "Banco Pan",
]


def _gerar_cnpj() -> str:
    def digito(parcial, pesos):
        soma = sum(d * p for d, p in zip(parcial, pesos))
        r = soma % 11
        return 0 if r < 2 else 11 - r

    base = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    base.append(digito(base, p1))
    base.append(digito(base, p2))
    s = ''.join(map(str, base))
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"


def gen_cnpj(context: Dict, filters: Dict) -> str:
    return _gerar_cnpj()


def gen_banco(context: Dict, filters: Dict) -> str:
    return random.choice(_BANCOS)


def gen_agencia(context: Dict, filters: Dict) -> str:
    num = random.randint(1, 9999)
    digito = random.randint(0, 9)
    return f"{num:04d}-{digito}"


def gen_conta(context: Dict, filters: Dict) -> str:
    num = random.randint(10000, 999999)
    digito = random.randint(0, 9)
    return f"{num}-{digito}"


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

register_field(FieldDefinition(
    key='cnpj', label='CNPJ',
    category='financeiro', category_label='Financeiro',
    generator=gen_cnpj,
    description='CNPJ válido com dígitos verificadores',
    icon='fas fa-file-invoice',
))

register_field(FieldDefinition(
    key='banco', label='Banco',
    category='financeiro', category_label='Financeiro',
    generator=gen_banco,
    description='Nome de banco brasileiro',
    icon='fas fa-university',
))

register_field(FieldDefinition(
    key='agencia', label='Agência',
    category='financeiro', category_label='Financeiro',
    generator=gen_agencia,
    description='Número de agência com dígito',
    icon='fas fa-landmark',
))

register_field(FieldDefinition(
    key='conta', label='Conta',
    category='financeiro', category_label='Financeiro',
    generator=gen_conta,
    description='Número de conta corrente com dígito',
    icon='fas fa-piggy-bank',
))

"""
Tests for individual field generator functions.
"""
import re
from datetime import date

import pytest

# Trigger registration before importing generators
import app.generators  # noqa: F401

from app.generators.personal import (
    gen_cpf, gen_rg, gen_nome_completo, gen_primeiro_nome, gen_sobrenome,
    gen_data_nascimento, gen_idade, _gerar_cpf,
)
from app.generators.contact import gen_email, gen_telefone, gen_celular
from app.generators.address import (
    gen_cep, gen_cidade, gen_estado, gen_bairro, gen_endereco, gen_pais,
)
from app.generators.professional import gen_empresa, gen_cargo, gen_salario
from app.generators.account import gen_usuario, gen_senha
from app.generators.financial import gen_cnpj, gen_banco, gen_agencia, gen_conta
from app.generators.vehicle import gen_placa


# ── CPF validation ────────────────────────────────────────────────────────────

def _cpf_digits_valid(cpf: str) -> bool:
    """Re-verify both check digits."""
    nums = [int(c) for c in cpf.replace(".", "").replace("-", "")]
    assert len(nums) == 11

    def check(partial, digit_pos):
        n = digit_pos + 1
        soma = sum(d * (n - i) for i, d in enumerate(partial))
        r = soma % 11
        expected = 0 if r < 2 else 11 - r
        return nums[digit_pos] == expected

    return check(nums[:9], 9) and check(nums[:10], 10)


def test_cpf_format(empty_context):
    cpf = gen_cpf(empty_context, {})
    assert re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf), f"Bad format: {cpf}"


def test_cpf_check_digits(empty_context):
    for _ in range(20):
        cpf = _gerar_cpf()
        assert _cpf_digits_valid(cpf), f"Invalid CPF check digits: {cpf}"


# ── CNPJ validation ───────────────────────────────────────────────────────────

def _cnpj_valid(cnpj: str) -> bool:
    nums = [int(c) for c in re.sub(r"\D", "", cnpj)]
    assert len(nums) == 14

    def calc(base, weights):
        soma = sum(d * w for d, w in zip(base, weights))
        r = soma % 11
        return 0 if r < 2 else 11 - r

    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    return nums[12] == calc(nums[:12], w1) and nums[13] == calc(nums[:13], w2)


def test_cnpj_format(empty_context):
    cnpj = gen_cnpj(empty_context, {})
    assert re.fullmatch(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", cnpj), f"Bad format: {cnpj}"


def test_cnpj_check_digits(empty_context):
    for _ in range(20):
        cnpj = gen_cnpj(empty_context, {})
        assert _cnpj_valid(cnpj), f"Invalid CNPJ check digits: {cnpj}"


# ── RG ────────────────────────────────────────────────────────────────────────

def test_rg_format(empty_context):
    rg = gen_rg(empty_context, {})
    assert re.fullmatch(r"\d{2}\.\d{3}\.\d{3}-[\dX]", rg), f"Bad RG: {rg}"


# ── Name fields ───────────────────────────────────────────────────────────────

def test_nome_completo_has_two_parts(empty_context):
    nome = gen_nome_completo(empty_context, {})
    assert len(nome.split()) >= 2, f"Expected full name: {nome}"


def test_primeiro_nome_single_word(empty_context):
    nome = gen_primeiro_nome({}, {})
    assert nome and ' ' not in nome.strip(), f"Expected single word: {nome}"


def test_sobrenome_non_empty(empty_context):
    sob = gen_sobrenome({}, {})
    assert sob and isinstance(sob, str)


def test_name_context_consistency():
    """nome_completo and email generated in same context share the same name."""
    from app.generators.contact import gen_email
    ctx = {}
    nome = gen_nome_completo(ctx, {})
    email = gen_email(ctx, {'tipo': 'pessoal'})
    # The email should derive from the same name stored in _name
    primeiro = ctx['_name']['primeiro'].lower()
    # Normalised first name should appear somewhere in the email local part
    normalised = re.sub(r'[^a-z]', '', primeiro[:6])
    assert normalised in email.split('@')[0].lower() or len(normalised) == 0


# ── Date / Age consistency ─────────────────────────────────────────────────────

def test_data_nascimento_format(empty_context):
    d = gen_data_nascimento(empty_context, {})
    assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", d), f"Bad date: {d}"


def test_data_nascimento_stores_in_context():
    ctx = {}
    gen_data_nascimento(ctx, {'idade_min': 20, 'idade_max': 30})
    assert '_data_nascimento' in ctx
    assert isinstance(ctx['_data_nascimento'], date)


def test_idade_reads_from_context():
    ctx = {}
    gen_data_nascimento(ctx, {'idade_min': 25, 'idade_max': 25})
    idade = gen_idade(ctx, {})
    # Age should be 24 or 25 depending on exact birthday vs today
    assert 24 <= idade <= 26, f"Unexpected age: {idade}"


def test_idade_range_without_context(empty_context):
    idade = gen_idade({}, {'idade_min': 30, 'idade_max': 40})
    assert 30 <= idade <= 40


def test_data_nascimento_age_range():
    for _ in range(10):
        ctx = {}
        gen_data_nascimento(ctx, {'idade_min': 18, 'idade_max': 65})
        dob: date = ctx['_data_nascimento']
        hoje = date.today()
        age = hoje.year - dob.year - ((hoje.month, hoje.day) < (dob.month, dob.day))
        assert 17 <= age <= 66, f"Age out of range: {age}"


# ── Contact fields ────────────────────────────────────────────────────────────

def test_email_format(empty_context):
    email = gen_email({}, {})
    assert re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email), f"Bad email: {email}"


def test_email_corporate_domain(empty_context):
    email = gen_email({}, {'tipo': 'corporativo'})
    # Corporate emails don't use the personal domains
    personal_domains = {'gmail.com', 'hotmail.com', 'yahoo.com.br', 'outlook.com'}
    domain = email.split('@')[1]
    assert domain not in personal_domains, f"Got personal domain in corporate email: {email}"


def test_email_custom_domain():
    email = gen_email({}, {'dominio': 'minha-empresa.com'})
    assert email.endswith('@minha-empresa.com'), f"Expected custom domain: {email}"


def test_telefone_format(empty_context):
    tel = gen_telefone({}, {})
    assert re.fullmatch(r"\(\d{2}\) \d{4}-\d{4}", tel), f"Bad phone: {tel}"


def test_celular_format(empty_context):
    cel = gen_celular({}, {})
    assert re.fullmatch(r"\(\d{2}\) 9\d{4}-\d{4}", cel), f"Bad cell: {cel}"


# ── Address fields ────────────────────────────────────────────────────────────

def test_cep_format(empty_context):
    cep = gen_cep({}, {})
    assert re.fullmatch(r"\d{5}-\d{3}", cep), f"Bad CEP: {cep}"


def test_location_context_shared():
    """CEP, cidade, estado from same context must belong to the same city."""
    ctx = {}
    gen_cep(ctx, {})
    cidade = gen_cidade(ctx, {})
    estado = gen_estado(ctx, {})
    loc = ctx['_location']
    assert loc['cidade'] == cidade
    assert loc['uf'] == estado or loc['estado'] == estado


def test_estado_formato_sigla():
    ctx = {}
    uf = gen_estado(ctx, {'formato': 'sigla'})
    assert len(uf) == 2 and uf.isupper(), f"Expected 2-letter UF: {uf}"


def test_estado_formato_nome():
    ctx = {}
    nome = gen_estado(ctx, {'formato': 'nome'})
    assert len(nome) > 2, f"Expected full state name: {nome}"


def test_pais_is_brasil(empty_context):
    assert gen_pais({}, {}) == "Brasil"


# ── Professional fields ───────────────────────────────────────────────────────

def test_salario_format(empty_context):
    s = gen_salario({}, {})
    assert s.startswith("R$"), f"Expected R$ prefix: {s}"


def test_salario_range():
    for _ in range(20):
        s = gen_salario({}, {'salario_min': 3000, 'salario_max': 5000})
        value = float(s.replace('R$', '').replace('.', '').replace(',', '.').strip())
        assert 3000 <= value <= 5000, f"Salary out of range: {value}"


def test_empresa_non_empty(empty_context):
    assert gen_empresa({}, {})


def test_cargo_non_empty(empty_context):
    assert gen_cargo({}, {})


# ── Account fields ────────────────────────────────────────────────────────────

def test_usuario_no_spaces(empty_context):
    u = gen_usuario({}, {})
    assert ' ' not in u, f"Username has space: {u}"


def test_usuario_ascii_only():
    for _ in range(10):
        u = gen_usuario({}, {})
        assert re.fullmatch(r"[a-z0-9._]+", u), f"Non-ASCII username: {u}"


def test_senha_fraca_length():
    s = gen_senha({}, {'forca': 'fraca'})
    assert 6 <= len(s) <= 8, f"Weak password length wrong: {len(s)}"


def test_senha_forte_complexity():
    for _ in range(10):
        s = gen_senha({}, {'forca': 'forte'})
        assert len(s) >= 12
        assert any(c.isupper() for c in s), f"No uppercase in strong password: {s}"
        assert any(c.isdigit() for c in s), f"No digit in strong password: {s}"


def test_senha_comprimento_fixo():
    for _ in range(10):
        s = gen_senha({}, {'comprimento': 16})
        assert len(s) == 16, f"Expected length 16, got {len(s)}"


# ── Financial fields ──────────────────────────────────────────────────────────

def test_banco_non_empty(empty_context):
    assert gen_banco({}, {})


def test_agencia_format(empty_context):
    a = gen_agencia({}, {})
    assert re.fullmatch(r"\d{4}-\d", a), f"Bad agencia: {a}"


def test_conta_format(empty_context):
    c = gen_conta({}, {})
    assert re.fullmatch(r"\d{5,6}-\d", c), f"Bad conta: {c}"


# ── Vehicle ───────────────────────────────────────────────────────────────────

def test_placa_antigo():
    for _ in range(10):
        p = gen_placa({}, {'formato': 'antigo'})
        assert re.fullmatch(r"[A-Z]{3}-\d{4}", p), f"Bad antigo plate: {p}"


def test_placa_mercosul():
    for _ in range(10):
        p = gen_placa({}, {'formato': 'mercosul'})
        assert re.fullmatch(r"[A-Z]{3}\d[A-Z]\d{2}", p), f"Bad mercosul plate: {p}"


def test_placa_aleatorio():
    results = {gen_placa({}, {'formato': 'aleatorio'}) for _ in range(30)}
    # With 30 samples, we expect at least one of each format (probabilistically safe)
    antigo   = any(re.fullmatch(r"[A-Z]{3}-\d{4}", p) for p in results)
    mercosul = any(re.fullmatch(r"[A-Z]{3}\d[A-Z]\d{2}", p) for p in results)
    assert antigo or mercosul  # at least one valid plate

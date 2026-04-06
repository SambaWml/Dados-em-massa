import random
from typing import Dict

from app.generators.registry import FieldDefinition, FilterOption, register_field
from app.generators.utils import fake

_CARGOS = [
    "Analista de Sistemas", "Desenvolvedor Full Stack", "Desenvolvedor Front-end",
    "Desenvolvedor Back-end", "Gerente de Projetos", "Coordenador de TI",
    "Analista de RH", "Assistente Administrativo", "Analista Financeiro",
    "Supervisor de Vendas", "Analista de Marketing", "Engenheiro de Software",
    "Designer UX/UI", "Product Manager", "Scrum Master", "DevOps Engineer",
    "Data Scientist", "Analista de Dados", "Arquiteto de Software", "Tech Lead",
    "Gerente Comercial", "Analista de Negócios", "Consultor SAP",
    "Analista de Suporte", "Técnico de TI", "Programador Java",
    "Desenvolvedor Python", "Analista de Qualidade (QA)", "QA Engineer",
    "Agile Coach", "Gerente de Infraestrutura", "Administrador de Redes",
    "DBA Oracle", "DBA SQL Server", "Analista de Segurança", "CISO",
    "Gerente de Operações", "Diretor de TI", "VP de Engenharia",
    "Assistente Financeiro", "Contador", "Advogado", "Médico",
    "Enfermeiro(a)", "Professor(a)", "Engenheiro Civil", "Arquiteto",
    "Designer Gráfico", "Redator", "Analista de Conteúdo", "Atendente",
    "Vendedor(a)", "Gerente de Loja", "Coordenador Pedagógico",
    "Analista de Logística", "Motorista", "Técnico em Informática",
]

_EMPRESAS_SUFIXOS = [
    "Ltda", "S.A.", "ME", "EPP", "Eireli", "S/A", "& Associados",
]

_EMPRESAS_TIPOS = [
    "Tecnologias", "Soluções", "Sistemas", "Consultoria", "Serviços",
    "Comércio", "Indústria", "Distribuidora", "Holding", "Grupo",
    "Digital", "Inovação", "Negócios", "Empreendimentos",
]

_EMPRESAS_NOMES = [
    "Alpha", "Beta", "Omega", "Delta", "Sigma", "Nova", "Prime",
    "Brasil", "Nacional", "Global", "Sul", "Norte", "Central",
    "Link", "Tech", "Net", "Info", "Data", "Cloud", "Smart",
    "Master", "Pro", "Max", "Fast", "Gold", "Plus", "Top",
    "Flex", "Connect", "Hub", "Vision", "Nexus",
]


def gen_empresa(context: Dict, filters: Dict) -> str:
    nome = random.choice(_EMPRESAS_NOMES)
    tipo = random.choice(_EMPRESAS_TIPOS)
    suf = random.choice(_EMPRESAS_SUFIXOS)
    return f"{nome} {tipo} {suf}"


def gen_cargo(context: Dict, filters: Dict) -> str:
    return random.choice(_CARGOS)


def gen_salario(context: Dict, filters: Dict) -> str:
    sal_min = float(filters.get('salario_min', 1412.0))
    sal_max = float(filters.get('salario_max', 25000.0))
    if sal_min > sal_max:
        sal_min, sal_max = sal_max, sal_min

    valor = random.uniform(sal_min, sal_max)
    # Round to nearest 50
    valor = round(valor / 50) * 50
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

register_field(FieldDefinition(
    key='empresa', label='Empresa',
    category='profissional', category_label='Profissional',
    generator=gen_empresa,
    description='Nome fictício de empresa',
    icon='fas fa-building',
))

register_field(FieldDefinition(
    key='cargo', label='Cargo',
    category='profissional', category_label='Profissional',
    generator=gen_cargo,
    description='Cargo/função profissional',
    icon='fas fa-briefcase',
))

register_field(FieldDefinition(
    key='salario', label='Salário',
    category='profissional', category_label='Profissional',
    generator=gen_salario,
    filter_options=[
        FilterOption(key='salario_min', label='Salário mínimo (R$)', type='number',
                     min_value=0, max_value=500000, default=1412),
        FilterOption(key='salario_max', label='Salário máximo (R$)', type='number',
                     min_value=0, max_value=500000, default=25000),
    ],
    description='Salário em reais dentro da faixa configurada',
    icon='fas fa-dollar-sign',
))

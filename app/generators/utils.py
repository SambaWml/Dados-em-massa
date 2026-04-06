import random
import unicodedata
from typing import Dict

from faker import Faker

fake = Faker('pt_BR')

# ---------------------------------------------------------------------------
# Brazilian cities with state info and CEP numeric ranges
# ---------------------------------------------------------------------------
CIDADES_BRASIL = [
    {"cidade": "São Paulo",          "estado": "São Paulo",           "uf": "SP", "cep_i": 1000,  "cep_f": 9999},
    {"cidade": "Rio de Janeiro",     "estado": "Rio de Janeiro",      "uf": "RJ", "cep_i": 20000, "cep_f": 23799},
    {"cidade": "Belo Horizonte",     "estado": "Minas Gerais",        "uf": "MG", "cep_i": 30000, "cep_f": 31999},
    {"cidade": "Salvador",           "estado": "Bahia",               "uf": "BA", "cep_i": 40000, "cep_f": 41999},
    {"cidade": "Fortaleza",          "estado": "Ceará",               "uf": "CE", "cep_i": 60000, "cep_f": 60999},
    {"cidade": "Curitiba",           "estado": "Paraná",              "uf": "PR", "cep_i": 80000, "cep_f": 82999},
    {"cidade": "Manaus",             "estado": "Amazonas",            "uf": "AM", "cep_i": 69000, "cep_f": 69099},
    {"cidade": "Recife",             "estado": "Pernambuco",          "uf": "PE", "cep_i": 50000, "cep_f": 51999},
    {"cidade": "Porto Alegre",       "estado": "Rio Grande do Sul",   "uf": "RS", "cep_i": 90000, "cep_f": 91999},
    {"cidade": "Belém",              "estado": "Pará",                "uf": "PA", "cep_i": 66000, "cep_f": 66999},
    {"cidade": "Goiânia",            "estado": "Goiás",               "uf": "GO", "cep_i": 74000, "cep_f": 74999},
    {"cidade": "Guarulhos",          "estado": "São Paulo",           "uf": "SP", "cep_i": 7000,  "cep_f": 7399},
    {"cidade": "Campinas",           "estado": "São Paulo",           "uf": "SP", "cep_i": 13000, "cep_f": 13199},
    {"cidade": "Maceió",             "estado": "Alagoas",             "uf": "AL", "cep_i": 57000, "cep_f": 57099},
    {"cidade": "Natal",              "estado": "Rio Grande do Norte", "uf": "RN", "cep_i": 59000, "cep_f": 59099},
    {"cidade": "Teresina",           "estado": "Piauí",               "uf": "PI", "cep_i": 64000, "cep_f": 64099},
    {"cidade": "Campo Grande",       "estado": "Mato Grosso do Sul",  "uf": "MS", "cep_i": 79000, "cep_f": 79099},
    {"cidade": "João Pessoa",        "estado": "Paraíba",             "uf": "PB", "cep_i": 58000, "cep_f": 58099},
    {"cidade": "Aracaju",            "estado": "Sergipe",             "uf": "SE", "cep_i": 49000, "cep_f": 49099},
    {"cidade": "Cuiabá",             "estado": "Mato Grosso",         "uf": "MT", "cep_i": 78000, "cep_f": 78099},
    {"cidade": "Macapá",             "estado": "Amapá",               "uf": "AP", "cep_i": 68900, "cep_f": 68999},
    {"cidade": "Porto Velho",        "estado": "Rondônia",            "uf": "RO", "cep_i": 76800, "cep_f": 76899},
    {"cidade": "Palmas",             "estado": "Tocantins",           "uf": "TO", "cep_i": 77000, "cep_f": 77099},
    {"cidade": "Boa Vista",          "estado": "Roraima",             "uf": "RR", "cep_i": 69300, "cep_f": 69399},
    {"cidade": "Rio Branco",         "estado": "Acre",                "uf": "AC", "cep_i": 69900, "cep_f": 69999},
    {"cidade": "Florianópolis",      "estado": "Santa Catarina",      "uf": "SC", "cep_i": 88000, "cep_f": 88099},
    {"cidade": "Vitória",            "estado": "Espírito Santo",      "uf": "ES", "cep_i": 29000, "cep_f": 29099},
    {"cidade": "Brasília",           "estado": "Distrito Federal",    "uf": "DF", "cep_i": 70000, "cep_f": 72899},
    {"cidade": "São Luís",           "estado": "Maranhão",            "uf": "MA", "cep_i": 65000, "cep_f": 65099},
    {"cidade": "Santos",             "estado": "São Paulo",           "uf": "SP", "cep_i": 11000, "cep_f": 11099},
    {"cidade": "Ribeirão Preto",     "estado": "São Paulo",           "uf": "SP", "cep_i": 14000, "cep_f": 14099},
    {"cidade": "Uberlândia",         "estado": "Minas Gerais",        "uf": "MG", "cep_i": 38400, "cep_f": 38499},
    {"cidade": "Feira de Santana",   "estado": "Bahia",               "uf": "BA", "cep_i": 44000, "cep_f": 44099},
    {"cidade": "Contagem",           "estado": "Minas Gerais",        "uf": "MG", "cep_i": 32000, "cep_f": 32099},
    {"cidade": "Joinville",          "estado": "Santa Catarina",      "uf": "SC", "cep_i": 89200, "cep_f": 89299},
    {"cidade": "Londrina",           "estado": "Paraná",              "uf": "PR", "cep_i": 86000, "cep_f": 86099},
    {"cidade": "Sorocaba",           "estado": "São Paulo",           "uf": "SP", "cep_i": 18000, "cep_f": 18099},
    {"cidade": "Niterói",            "estado": "Rio de Janeiro",      "uf": "RJ", "cep_i": 24000, "cep_f": 24499},
]

BAIRROS = [
    "Centro", "Jardim América", "Vila Nova", "Jardim Paulista", "Bela Vista",
    "São Lucas", "Jardim Primavera", "Nova Era", "Cidade Nova", "Parque Industrial",
    "Vila Esperança", "Jardim Europa", "Residencial das Flores", "Alto da Serra",
    "Parque das Nações", "Vila Santa Cruz", "Jardim Atlântico", "São Francisco",
    "Vila Rica", "Jardim Imperial", "Distrito Industrial", "Jardim Tropical",
    "Vila São José", "Parque Verde", "Jardim das Acácias", "Jardim Leblon",
    "Vila Madalena", "Pinheiros", "Consolação", "Liberdade", "Mooca",
    "Lapa", "Santana", "Vila Mariana", "Campo Belo", "Morumbi",
    "Ipiranga", "Jardim Anália Franco", "Tatuapé", "Saúde",
]

TIPOS_LOGRADOURO = ["Rua", "Avenida", "Alameda", "Travessa", "Estrada", "Via"]

NOMES_LOGRADOURO = [
    "das Flores", "dos Lírios", "das Acácias", "São Paulo", "Brasil",
    "das Palmeiras", "dos Pinheiros", "da Paz", "Central", "João Pessoa",
    "Getúlio Vargas", "Tiradentes", "Dom Pedro II", "XV de Novembro",
    "Sete de Setembro", "das Nações", "do Comércio", "Industrial",
    "das Orquídeas", "Santa Maria", "São José", "do Trabalho",
    "Carlos Gomes", "Marechal Deodoro", "República Argentina",
    "das Aroeiras", "dos Coqueiros", "do Sol", "da Lua", "das Estrelas",
    "Presidente Vargas", "Independência", "da Liberdade", "dos Ipês",
]


# ---------------------------------------------------------------------------
# Shared context helpers
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Strip accents from text."""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )


def get_name_context(context: Dict, genero: str = 'aleatorio') -> Dict:
    """Return (or lazily create) the shared name context for one record."""
    if '_name' not in context:
        if genero == 'masculino':
            primeiro = fake.first_name_male()
            gen = 'masculino'
        elif genero == 'feminino':
            primeiro = fake.first_name_female()
            gen = 'feminino'
        else:
            if random.random() > 0.5:
                primeiro = fake.first_name_male()
                gen = 'masculino'
            else:
                primeiro = fake.first_name_female()
                gen = 'feminino'

        context['_name'] = {
            'primeiro': primeiro,
            'sobrenome': fake.last_name(),
            'genero': gen,
        }
    return context['_name']


def get_location_context(context: Dict) -> Dict:
    """Return (or lazily create) the shared address context for one record."""
    if '_location' not in context:
        cd = random.choice(CIDADES_BRASIL)
        cep_num = random.randint(cd['cep_i'], cd['cep_f'])
        sufixo = random.randint(0, 999)
        cep = f"{cep_num:05d}-{sufixo:03d}"

        tipo = random.choice(TIPOS_LOGRADOURO)
        nome = random.choice(NOMES_LOGRADOURO)

        context['_location'] = {
            'cidade': cd['cidade'],
            'estado': cd['estado'],
            'uf': cd['uf'],
            'cep': cep,
            'bairro': random.choice(BAIRROS),
            'logradouro': f"{tipo} {nome}",
            'pais': 'Brasil',
        }
    return context['_location']

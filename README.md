# Gerador de Dados em Massa

Aplicação web para geração de dados fictícios brasileiros em massa, com seleção dinâmica de campos, filtros por campo e exportação em CSV, JSON e Excel.

---

## Instalação

### Pré-requisitos
- Python 3.10+

### 1. Instalar dependências

```bash
py -m pip install -r requirements.txt
```

### 2. Executar

```bash
py main.py
```

Acesse no navegador: **http://localhost:5000**

---

## Uso

1. **Selecione os campos** que deseja gerar (clique nos cards por categoria)
2. **Configure filtros** por campo clicando no ícone de filtro ao lado de cada campo selecionado
3. **Informe a quantidade** de registros (1 a 50.000)
4. **Clique em "Gerar Dados"**
5. **Visualize o preview** dos primeiros 50 registros
6. **Exporte** em CSV, JSON ou Excel

---

## Campos disponíveis

| Categoria     | Campos                                                              |
|---------------|---------------------------------------------------------------------|
| Pessoal       | Nome Completo, Primeiro Nome, Sobrenome, CPF, RG, Data de Nascimento, Idade |
| Contato       | E-mail, Telefone, Celular                                           |
| Endereço      | CEP, Endereço, Número, Bairro, Cidade, Estado, País                |
| Profissional  | Empresa, Cargo, Salário                                             |
| Acesso        | Usuário, Senha                                                      |
| Financeiro    | CNPJ, Banco, Agência, Conta                                         |
| Veículo       | Placa de Veículo                                                    |

---

## Filtros disponíveis por campo

| Campo            | Filtros                                      |
|------------------|----------------------------------------------|
| Nome / Primeiro nome | Gênero (Masculino / Feminino / Aleatório) |
| Data de nascimento   | Idade mínima e máxima                    |
| Idade                | Idade mínima e máxima                    |
| E-mail               | Tipo (Pessoal / Corporativo), Domínio personalizado |
| Salário              | Faixa mínima e máxima (R$)               |
| Senha                | Força (Fraca / Média / Forte), Comprimento fixo |
| Estado               | Formato (Nome completo / Sigla UF)        |
| Placa                | Formato (Antigo / Mercosul / Aleatório)   |

---

## Consistência entre campos

O sistema mantém coerência automática entre campos relacionados:

- **Nome + E-mail + Usuário**: o e-mail e o usuário são gerados a partir do nome
- **CEP + Cidade + Estado + Bairro + Endereço**: todos compartilham a mesma localização brasileira
- **Data de nascimento + Idade**: a idade é calculada da data de nascimento quando ambos são selecionados
- **Gênero**: aplicado a todos os campos de nome simultaneamente

---

## Estrutura do projeto

```
Dados em massa/
├── main.py                         # Ponto de entrada
├── requirements.txt
├── app/
│   ├── __init__.py                 # Fábrica da aplicação Flask
│   ├── generators/
│   │   ├── registry.py             # Definição de campos (FieldDefinition, FilterOption)
│   │   ├── utils.py                # Dados de cidades, contextos compartilhados
│   │   ├── personal.py             # Campos: nome, cpf, rg, data_nascimento, idade
│   │   ├── contact.py              # Campos: email, telefone, celular
│   │   ├── address.py              # Campos: cep, endereco, numero, bairro, cidade, estado, pais
│   │   ├── professional.py         # Campos: empresa, cargo, salario
│   │   ├── account.py              # Campos: usuario, senha
│   │   ├── financial.py            # Campos: cnpj, banco, agencia, conta
│   │   └── vehicle.py              # Campos: placa
│   ├── core/
│   │   ├── engine.py               # Motor de geração (ordenação por dependências, contextos)
│   │   └── exporters.py            # Exportadores: CSV, JSON, Excel
│   ├── api/
│   │   └── routes.py               # Endpoints Flask
│   └── templates/
│       └── index.html              # Interface web
```

---

## Como adicionar um novo campo

1. **Crie ou edite um módulo em `app/generators/`**

```python
# app/generators/meu_modulo.py
from app.generators.registry import FieldDefinition, FilterOption, register_field

def gen_meu_campo(context: dict, filters: dict) -> str:
    return "valor gerado"

register_field(FieldDefinition(
    key='meu_campo',
    label='Meu Campo',
    category='pessoal',          # categoria existente ou nova
    category_label='Pessoal',
    generator=gen_meu_campo,
    filter_options=[             # opcional
        FilterOption(key='opcao', label='Opção', type='select',
                     options=[{'value': 'a', 'label': 'A'}], default='a'),
    ],
    description='Descrição do campo',
    icon='fas fa-tag',           # ícone Font Awesome
))
```

2. **Registre o módulo em `app/generators/__init__.py`**

```python
import app.generators.meu_modulo  # noqa: F401
```

3. O campo aparece automaticamente na interface e nos exportadores.

---

## Exemplos de uso via API

### Gerar dados
```http
POST /api/generate
Content-Type: application/json

{
  "fields": ["nome_completo", "cpf", "email", "cidade"],
  "count": 100,
  "filters": {
    "nome_completo": { "genero": "feminino" },
    "email": { "tipo": "corporativo" }
  }
}
```

### Exportar resultado (após geração)
```http
GET /api/export/<key>?format=csv
GET /api/export/<key>?format=json
GET /api/export/<key>?format=excel
```

### Listar campos disponíveis
```http
GET /api/fields
```

---

## Limites

| Item                    | Valor   |
|-------------------------|---------|
| Máx. registros por geração | 50.000 |
| Resultados em cache (server) | 50 últimas gerações |
| Linhas no preview       | 50      |

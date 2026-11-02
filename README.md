# 📊 Aplicação de Análise Financeira

## 📌 1. Visão Geral

A Aplicação de Análise Financeira é uma aplicação web destinada a centralizar e analisar dados financerios públicos de empresas do setor de artigos de luxo.

O projeto pretende facilitar a consulta, interpretação e comparação de informação financeira, através de indicadores, tabelas e representações gráficas.

## 🎯 2. Objetivos

- Centralizar dados financeiros provenientes de fontes públicas.
- Facilitar a consulta e análise da informação financeira.
- Calcular indicadores financeiros relevantes.
- Representar graficamente a evolução dos resultados.
- Comparar o desempenho financeiro entre empresas e exercícios fiscais.

## ⚙️ 3. Funcionalidades

### ✅ Implementadas

- Registo e gestão de empresas.
- Consulta e listagem de empresas.
- Edição e eliminação de empresas, respeitando as regras de integridade da base de dados.
- Validação dos dados intrudozidos através da interface.

### 📋 Previstas

- Importação de dados financeiroes a partir de ficheiros CSV e Excel.
- Armazenamenteo e consulta de registos financeiros.
- Cálculo de indicadores financeiros, incluindo margem operacional, margem líquida e crescimento da receita.
- Consulta de informação financeira através de tabelas e gráficos.
- Comparação histórica do desempenho financeira entre empresas.

## 🏢 4. Âmbito Inicial

A primeira versão centra-se em trÊs empresas do setor de artigos de luxo:
- LVMH
- Kering
- Richemont

O projeto poderá ser alargado futuramente a outras empresas e funcionalidades.

## 🛠️ 5. Tecnologias

- **Linguagem de Programação:** Python
- **Interface web:** Streamlit
- **Análise e manipulação de dados:** Pandas
- **Visualização de dados:** Plotly
- **Base de Dados:** SQLite
- **Testes automatizados:** Pytest
- **Controlo de versões:** Git e GitHub

Outras tecnologias poderão ser acrescentadas durante o desenvolvimento, de acordo com as necessidades da aplicação.

## 📂 6. Estrutura do Projeto

```
financial-analysis-app/
├── data/
├── docs/
│   ├── database/
│   ├── diagrams/
│   ├── learning-notes/
│   ├── planning/
│   └── reports/
├── src/
│   ├── app.py
│   ├── companies.py
│   └── database.py
├── tests/
│   ├── test_companies.py
│   └── test_database.py
├── README.md
├── requirements.txt
└── .gitignore
```
- data/ - ficheiros com dados financeiros.
- docs/ - documentação, relatórios, planeamento, diagramas e modelo de base de dados.
- src/ - código-fonte da aplicaçáo.
- tests/ - testes automatizados.
- requirements.txt - dependências Python do projeto.
- .gitignore - ficheiros e pasta que não deve ser incluídas no controlo de versões.

## 🚀 7. Instalação e Execução

**Pré-requisitos**
- Python 3.12 ou superior.
- Git.

### 7.1. Clonar o repositório

```powershell
git clone https://github.com/lidiapcarvalho/financial-analysis-app.git
```

Entrar na pasta do projeto:

```powershell
cd financial-analysis-app
```

### 7.2. Criar o ambiente virtual

```powershell
python -m venv .venv
```

Ativar o ambiente virtual no Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 7.3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 7.4. Executar a aplicação

```powershell
python -m streamlit run src/app.py
```

A aplicação ficará disponível no endereço local apresentado pelo Streamlit no terminal.

## 🧪 8. Testes

Para executar os testes automatizados, utilizar:

```powershell
python -m pytest
```

## 📊 9. Estado do Projeto

**Fase atual:** desenvolvimento da aplicação.

A estrutura inicial, a base de dados e a gestão de empresas através da interface Streamlit encontram-se implementadas. As restantes funcionalidades são desenvolvidas progressivamente.

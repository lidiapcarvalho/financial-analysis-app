# 📊 Aplicação de Análise Financeira

## 📌 1. Visão Geral

A Aplicação de Análise Financeira é uma aplicação web destinada a centralizar e analisar dados financeiros públicos de empresas do setor de artigos de luxo.

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
- Validação dos dados introduzidos através da interface.
- Análise financeira individual por empresa e exercício fiscal.
- Cálculo de indicadores financeiros:
    - Margem Operacional (Operating Margin);
    - Margem de Lucro Líquida (Net Profit Margin);
    - Taxa de Crescimento da Receita (Revenue Growth);
    - Rendibilidade do Ativo (ROA);
    - Rendibilidade do Capital Próprio (ROE).
- Apresentação de dados financeiros através de tabelas.
- Representação gráfica da evolução dos indicadores financeiros.
- Comparação dos indicadores financeiros entre empresas, por exercício fiscal.
- Testes automatizados das principais funcionalidades.

### 📋 Previstas

- Importação de dados financeiros a partir de ficheiros CSV e Excel através da Interface.
- Gestão de utilizadores e autenticação.
- Guardar, consultar e eliminar comparações financeiras.
- Melhorias na apresentação e validação dos resultados comparativos.

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
- **Importação e leitura de ficheiros Excel:** OpenPyXL
- **Testes automatizados:** Pytest
- **Controlo de versões:** Git e GitHub

Outras tecnologias poderão ser acrescentadas durante o desenvolvimento, de acordo com as necessidades da aplicação.

## 📂 6. Estrutura do Projeto

```
financial-analysis-app/
├── data/
│   └── processed/
├── docs/
│   ├── database/
│   ├── diagrams/
│   ├── learning-notes/
│   ├── planning/
│   └── reports/
├── src/
│   ├── pages/
│   │   ├── 1_Empresas.py
│   │   ├── 2_Registos_Financeiros.py
│   │   ├── 3_Analise_Financeira.py
│   │   └── 4_Comparacao.py
│   ├── app.py
│   ├── app_home.py
│   ├── companies.py
│   ├── database.py
│   ├── financial_indicators.py
│   ├── financial_records.py
│   ├── import_financial_data.py
│   └── __init__.py
├── tests/
│   ├── test_companies.py
│   ├── test_database.py
│   ├── test_financial_indicators.py
│   ├── test_financial_records.py
│   └── test_import_financial_data.py
├── README.md
├── requirements.txt
└── .gitignore
```
- data/ - ficheiros com dados financeiros utilizados no projeto.
- docs/ - documentação técnica, diagramas, notas de aprendizagem, planeamento e relatórios.
- src/ - código-fonte e lógica da aplicaçáo.
- src/pages/ - páginas da interface Streamlit.
- tests/ - testes automatizados das funcionalidades e dos módulos da aplicação.
- requirements.txt - dependências Python do projeto.
- README.md - documentação principal do repositório.
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

O projeto utiliza Pytest para a execução de testes automatizados.

Para executar os testes automatizados, utilizar:

```powershell
python -m pytest
```

## 🔀 9. Controlo de Versões

O projeto utiliza Git e GitHub para controlo de versões e organização do desenvolvimento.
- `main`: branch principal, destinada a manter a versão estável e integrada da aplicação.
- **Branches de funcionalidades:** utilizadas para desenvolver novas funcionalidades e correções de forma isolada.
- **Pull Requests:** utilizadas para rever e integrar as alterações na branch principal.

## 📊 10. Estado do Projeto

**Fase atual:** desenvolvimento e consolidação das funcionalidades da aplicação.

Encontram-se implementadas as funcionalidades de gestão de empresas e registos financeiros, análise financeira individual, cálculo de indicadores, representação gráfica e comparação financeira entre empresas.

O projeto continua em desenvolvimento, estando previstas melhorias na importação de dados, na gestão de utilizadores e na funcionalidade de comparações guardadas.

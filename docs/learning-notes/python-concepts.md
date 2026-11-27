# Python Concepts | Learning Notes

> Este documento reúne conceitos de Python, bibliotecas e ferramentas utilizados durante o desenvolvimento do projeto Financial Analysis App, com explicações e exemplos práticos para consulta futura.

## 1. Criação de diretõrios com pahlib

### `Path`

Permite trabalhar com caminhos de ficheiros e diretórios de forma independente do sistema operativo.

### `.parent`

Devolve o diretório imediamente superior de um determinado caminho.

### `.mkdir()`

Cria um novo diretório:
- `parents=True` - permite criar diretórios intermediários que ainda não existam.
- `exist_ok=True` - evita um erro quando o diretório já existe.

### `tmp_path`

Funcionalide disponibilizada pelo pytest que cria um diretório temporário para cada teste. É útil para testar operações com ficheiros e base de dados sem alterar os dados reais do projeto.

**Exemplo no projeto:**

```python
database_path = Path(database_path)
database_path.parent.mkdir(parents=True, exist_ok=True)
```

Este código garante que a pasta onde será guardada a base de dados existe antes de estabelecer a ligaçáo SQLite.

## 2. Consultas SQL par atualização de dados

### `UPDATE`

Comando SQL utilizado para modificar os dados existentes numa tabela.

### `SET`

Define os campos que serão utilziados e os respetivos novos valores.

### `WHERE`

Identifica o registo que deve ser atualizados, através de uma condição. É importante para evitar alterações acidentais a todos os registos da tabela.

**Exemplo no projeto:**

```sql
UPDATE company
SET name = ?, sector = ?, currency = ?
WHERE id = ?
```

Neste exemplo:
- `UPDATE company` - indica a tabela onde será feita a atualização.
- `SET` - define os novos valores do nome, setor e moeda.
- `WHERE id = ?` - identifica a empresa através do seu ID.

Os ? são parâmetros que recebem os valores através da execução da consulta em Python, evitando a inserção direta de dados na instrução SQL.

## 3. Consultas SQL para verificar relações entre tabelas

### `SELECT`

Comando SQL utilizado para consultar dados existentes numa tabela.

### `WHERE`

Permite filtrar os registos com base numa condição.

### `LIMIT`

Define o número máximo de registos devolvidos pela consulta.

**Exemplo no projeto:**

```sql
SELECT id
FROM financial_record
WHERE company_id = ?
LIMIT 1
```

Neste exemplo:
- `SELECT id` - seleciona o identificador do registo financeiro.
- `FROM financial_record` - indica a tabela a consultar.
- `WHERE company_id = ?` - filtra os registos associados à empresa selecionada.
- `LIMIT 1` - devolve, no máximo, um resultado.

Esta consulta permite verificar se uma possui registos financeiros associados, sem necessidade de carregar todos os registos. No projeto, esta verificação é utilizada para impedir a alteração da moeda de uma empresa que já tenha histórico financeiro.

### `fetchone() e fetchall()`

São métodos utilizados para obter os resultados de uma consulta SQL através de um cursor.

- `fetchone()` - devolve apenas uma linha do resultado.
- `fetchall()` - devolve todas as linhas restantes do resultado.

No projeto, `fetchone()` é adequado para consultas que procuram um único registo ou verificam a existência de informação. Em conjunto com `LIMIT 1`, permite evitar a leitura desnecessária de vários registos.

## 4. Tratamento de exceções

O tratamento de exceções permite identificar e gerir erros durante a execução de um programa, evitando que situações inesperadas interrompam a aplicação sem controlo.

### `try`

Define um bloco de código onde podem ocorrer exceções.

### `except`

Permite capturar e tratar as execeções que ocorrem no bloco try.

### `ValueError`

Exceção utilizada quando um valor recebido não é válido para determinada operação.

**Exemplo no projeto:** tentar atualizar uma empresa que não existe oou submeter campos obrigatórios vazios.

### `sqlite3.IntegrityError`

Exceção do módulo **`sqlite3``**, lançada quando um operação viola uma restrição da base de dados, como a inserção de um nome de empresa duplicado.

**Exemplo no projeto:**
```python
try:
    update_company(company_id, name, sector, currency)

except ValueError as error:
    st.error(str(error))

except sqlite3.IntegrityError as error:
    st.error("Ocorrey um erro ao atualizar a empresa.")
```

Neste exemplo:
- `try` - executa a operação de atualização.
- `except ValueError` - trata erros de validação.
- `except sqlite3.IntegrityError` - trata erros relacionados com as restrições da base de dados.
- `str(error)` - converte a mensagem da exceção numa string para apresentação na interface.

## 5. Testes com pytest

O `pytest` é uma ferramenta de testes para Python que permita verificar se as funções apresentam os resultados esperados e se tratam corretamente situações de erro.

### `pytest.raises()`

Verifica se uma determinada operação gera execeção esperada.

**Exemplo no projeto:**

```python
with pytest.reaises(ValueError):
    update_company(999, "LVMH", "EUR", database_path)
```

Neste exemplo, o teste verifica se a tentativa de atualizar uma empresa inexistente gera um `ValueError`.

### `pytest.mark.parametrize`

Permite executar o mesmo teste várias vezes com diferentes conjuntos de valores, evitando a repitação de código.

**Exemplo no projeto:**

```python
@pytest.mark.parametrize(
    "field",
    ["name", "sector", "currency"]
)
```

Neste caso, o mesmo teste é executado para verificar se os três campos obrigatórios rejeitam valores vazios.

### Fixtures

As fixtures permitem preparar recursos ou condições necessários à execução dos testes.

O `tmp_path` é um exemplo de fixture disponibilizada pelo pytest. Permite criar diretórios temporários, utilizados no projeto para testar operações com bases de dados isolados.

### `monkeypatch`

Fixture do pytest que permite substituir temporariamente funções, atributos ou comportamentos durante um teste.

No projeto, foi utilizada para controlar dependências e evitar que determinados testes dependessem de operações externas ou da base de dados real.

### Testes isolados

A utilização de base de dados temporárias permite executar testes sem alterar a base de dados real do projeto.

Esta abordagem facilita a repetição dos testes e reduz a dependência entre diferentes casos de teste.

## 6. Streamlist - componentes e atualização

O Streamlist é uma bibliotec Python que permite criar aplicações web interativas, sem necessidade de desenvolver diretamente HTML, CSS ou JavaScript.

### `st.selectbox()`

Cria uma lista de seleção que permite ao utilziador escolher uma opção.

**Exemplo no projeto:**

```python
selected_company = st.selectbx(
    "Slecionar empresa",
    companies,
    format_func=lambda company: company[1]
)
```

Neste exemplo, o utilizador seleciona uma empresa pelo nome, embora a variável mantenha todos os dados da empresa selecionada.

O parâmetro `format_func` permite definir como cada opçáo é apresentada na interface.

`lambda`
Permite criar uma pequena função anónima sem necessidade de utilizar a palavra-chave `def`.

No exemplo anterior, `lambda company: company[1]` devolve o segundo elemento de cada registo de empresa para apresentar o respetivo nome.

### `st.form()`

Agrupa vários campos de introdução de dados num formulãrio, permitindo, submetê-los em conjunto.

### `st.form_submit_button()`

Crie o botão que permite submeter os dados do formulário.

**Exemplo no projeto:**

```python
with st.form("edit_company_form"):
    name = st.text_input("Nome da empresa")
    submitted =  st.form_submit_button("Guardar alterações")
```

### `st.session_state`

Permite guardar informação entre diferentes execuções da aplicação Streamlit durante a sessão do utilizador.

No projeto, é importante para preservar seleções e outros dados da interface durante a navegação entre páginas.

### `st.rerun()`

Interrompe a execução atuale volta a executar a aplicação desde o início.

É útil quando os dados são alterados e queremos atualizar imediatamente os elementos apresentados na interface.

**Exemplo no projeto:**

```python
st.sucess("Empresa atualizada com sucesso!")
st.rerun()
```

Neste caso, a aplicação é executada novamente após a atualização dos dados, permitindo que a tabela apresente a informação mais recente.

### `st.navigation() e st.Page`

Permitem organizar uma aplicação Streamlit em várias páginas.

No projeto, foram utilizados para estruturar a navegação entre as diferentes áreas da aplicação, como a gestão de empresas, os registos financeiros, a análise e a comparação.

## 7. SQLite - Operações CRUD e JOIN

### Operações CRUD

As operações CRUD representam as quatro operações fundamentais de gestão de dados:
- `CREATE` - inserir novos registos com `INSERT INTO`.
- `READ` - consultar registos com `SELECT`.
- `UPDATE` - atualizar registos existentes com `UPDATE`.
- `DELETE` - eliminar registos com `DELETE`.

### `INNER JOIN`

O `INNER JOIN` permite combinar dados de duas ou mais tabelas através de uma coluna relacionada.

No projeto, é utilizado para associar os registos financeiros à respetiva empresa:

```sql
FROM financial_record AS fr
INNER JOIN company AS c
    ON fr.company_id = c.id
```
Desta forma, a consulta consegue apresentar os dados financeiros juntamente com o nome e a moeda da empresa.

### Outros conceitos

- **Foreign Key** - estabelece uma relação entre tabelas e garante a integridade referencial.
- `cursor.lastowid` - devolve o ID do último registo inserido.
- `cursor.rowcount` - indica o número de linhas afastadas por uma operação.
- **`?` (placeholders)** - permitem passar valores como parâmetros nas instruções SQL, evitando concatenar diretamente os valores na consulta.
- `sqlite3.connect()` - estabelece uma ligação a uma base de dados SQLite.
- `commit()` - confirma e grava as alterações efetuados numa transação.
- `rollback()` - reverte as alterações de uma transação que ainda não foi confirmada.

### Migração de base de dados

Uma migração permite alterar a estrutura de uma base de dados existente, preservando os dados sempre que possível.

No projeto, foram utilizadas migrações para atualizar progressivamente o esquema da base de dados à medida que novas funcionalidades e tabelas foram introduzidas.

Este mecanismo permite manter a estrutura da base de dados atualizada sem ter de recriar tudo de raiz.

## 8. Pandas e análise de dados

O Pandas é uma biblioteca Python utilizada para manipular, organizar e analisar dados estruturados.

### DataFrame

Estrutura de dados bidimensional, organizada em linhas e colunas, semelhante a uma tabela.

No projeto, os DataFrames são utilizados para organizar os dados financeiros e preparar a informação apresentada nas tabelas e gráficos.

### `pd.read_excel()`

Permite importar dados de ficheiros Excel para um DataFrame.

### `pd.DataFrame()`

Permite criar um DataFrame a partir de dados existentes, como listas ou dicionários.

### `sort_values()`

Permite ordenar os registos de um DataFrame com base numa ou mais colunas.

Estas funcionalidades são úteis para organizar os dados financeiros por empresa e exercício fiscal antes de realizar análises.

## 9. Plotly e visualização de dados

O Plotly é uma biblioteca utilizada para criar gráficos interativos.

No projeto, foi utilizado para representar visualmente a evolução dos indicadores financeiros e facilitar a comparação entre empresas.

### `plotly.express`

Módulo do Plotly que permite criar gráficos através de funções de alto nível.

### `px.line()`

Cria gráficos de linhas, adequados para representar a evolução de indicadores ao longo dos exercícios fiscais.

### `px.bar()`

Cria gráficos de barras, úteis para comparar valores entre diferentes empresas ou períodos.

### `update_layout()`

Permite personalizar o layout dos gráficos, incluindo títulos, legendas e eixos.

## 10. Autenticação e segurança

### Hashing de palavras-passe

O hashing transforma uma palavra-passe num valor codificado através de uma função criptográfica unidirecional.

Ao contrário da encriptação, o hashing não se destina a permitir recuperar a palavra-passe original.

No projeto, as palavras-passe são armazenadas sob a forma de hashes, evitando guardar os valores originais na base de dados.

### Argon2

Argon2 é um algoritmo de hashing de palavras-passe concebido para dificultar ataques de tentativa e erro.

No projeto, foi utilizada a biblioteca `argon2-cffi` para gerar e verificar os hashes das palavras-passe.

### Autenticação e autorização

- **Autenticação** – processo de verificar a identidade de um utilizador através das suas credenciais.
- **Autorização** – processo de determinar quais as funcionalidades ou operações a que um utilizador tem acesso.

No projeto, foram definidos os papéis admin e user, permitindo distinguir os níveis de acesso.

## 11. Git e GitHub

### Git

Sistema de controlo de versões que permite acompanhar as alterações efetuadas nos ficheiros de um projeto.

### GitHub

Plataforma de alojamento de repositórios Git, que facilita a gestão do código e a colaboração.

### Branches

Permitem desenvolver funcionalidades ou corrigir problemas isoladamente, sem alterar diretamente a branch principal.

No projeto, foram utilizadas branches de funcionalidades, seguindo uma organização baseada em tarefas.

### Pull Requests

Permitem propor alterações de uma branch para outra, rever o código e integrar as alterações na branch principal.

### Issues

Permitem registar e acompanhar tarefas, funcionalidades a desenvolver e problemas identificados durante o projeto.

### Comandos utilizados

```
git status
git add .
git commit -m "Mensagem do commit"
git push origin main
git pull origin main
```

- `git status` – apresenta o estado atual do repositório.
- `git add` – prepara as alterações para o commit.
- `git commit` – regista as alterações no histórico local.
- `git push` – envia os commits para o repositório remoto.
- `git pull` – obtém e integra as alterações do repositório remoto.

O **GitHub Projects** foi também utilizado para organizar e acompanhar o progresso do projeto, permitindo encerrar o projeto após a conclusão das tarefas.

> **Nota:** Este documento poderá continuar a ser atualizado com novos conceitos, exemplos e aprendizagens adquiridos durante a evolução do Financial Analysis App e em projetos futuros.


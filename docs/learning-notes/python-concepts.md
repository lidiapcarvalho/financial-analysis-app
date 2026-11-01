# Python Concepts % Learning Notes

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

### Testes isolados

A utilização de base de dados temporárias permite executar testes sem alterar a base de dados real do projeto.

No `pytest`, o recurso `tmp_path` disponibiliza um diretório temporário exclusivo para cada teste.

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

### `st.rerun()`

Interrompe a execução atuale volta a executar a aplicação desde o início.

É útil quando os dados são alterados e queremos atualizar imediatamente os elementos apresentados na interface.

**Exemplo no projeto:**

```python
st.sucess("Empresa atualizada com sucesso!")
st.rerun()
```

Neste caso, a aplicação é executada novamente após a atualização dos dados, permitindo que a tabela apresente a informação mais recente.

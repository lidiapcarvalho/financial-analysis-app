


## Criação de diretõrios com pahlib

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



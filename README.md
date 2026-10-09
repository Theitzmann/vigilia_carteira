# Vigilia

Aplicação pessoal para monitoramento de carteira de ações da B3, com arquitetura
de monólito modular e funcionamento local-first. O pacote Python é
`vigilia_carteira`; o armazenamento previsto é SQLite, via biblioteca padrão
`sqlite3`.

A Fase 1 contempla livro de movimentações, posições, preço médio, saldo,
histórico de cotações, validação de dados e gatilhos matemáticos simples.
Esta inicialização entrega apenas a estrutura instalável, um teste de importação
e as ferramentas de qualidade. Ainda não há lógica financeira, banco de dados,
integrações ou interface.

## Pré-requisitos

- Ubuntu.
- Python 3.12 ou superior.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado.

## Instalação

Na raiz do projeto, instale o pacote e as dependências de desenvolvimento:

```bash
uv sync --dev --locked
```

O comando cria o ambiente `.venv/` e usa as versões registradas no `uv.lock`.
Mantenha esse arquivo no controle de versão. Não é necessário ativar o ambiente
ao executar comandos com `uv run`.

## Testes e qualidade

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Para confirmar a importação do pacote:

```bash
uv run python -c "import vigilia_carteira; print(vigilia_carteira.__name__)"
```

## Organização

- `src/vigilia_carteira/`: pacote Python instalável.
- `tests/`: testes unitários independentes de internet e APIs reais.
- `pyproject.toml`: metadados, dependências e configuração das ferramentas.
- `uv.lock`: versões resolvidas das dependências.
- `AGENTS.md`: escopo, convenções e regras de desenvolvimento.

Consulte `AGENTS.md` antes de alterar o projeto. Dados privados devem ficar em
`data/`, diretório ignorado pelo Git e criado somente quando necessário.
Nunca versione credenciais, arquivos `.env`, bancos SQLite, dados financeiros
reais, logs sensíveis ou backups privados. Um eventual `.env.example` deve conter
somente exemplos sem segredos.

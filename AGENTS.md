# Vigilia — orientações de desenvolvimento

## Identidade e stack

- Projeto Vigilia; pacote Python `vigilia_carteira`.
- Python >= 3.12, Ubuntu, `uv`, SQLite via `sqlite3`, `pytest` e `ruff`.
- Arquitetura: monólito modular, local-first.
- Não adicionar frameworks ou dependências sem necessidade.

## Escopo da Fase 1

- Livro de movimentações financeiras.
- Posições, preço médio e saldo disponível.
- Histórico de cotações da B3.
- Validação e persistência dos dados.
- Gatilhos matemáticos simples.
- Não implementar LLM, Streamlit, CVM, notícias, Parquet, DuckDB, agendamentos
  ou execução de ordens.

## Regras de trabalho

- Antes de cada tarefa, inspecionar o repositório e ler este `AGENTS.md`.
  Verificar `pwd`, `git status --short`, `git branch --show-current` e
  `git ls-files`; ler os arquivos relevantes e preservar alterações existentes.
- Implementar somente o solicitado, com alterações pequenas e adequadas a um commit.
- Não refatorar código não relacionado nem antecipar fases futuras.
- Não inventar dados financeiros ou contratos de APIs. Quando houver dúvida
  sobre APIs externas, solicitar documentação.
- Não alterar decisões arquiteturais sem autorização.
- Ao concluir uma tarefa com alterações, sempre abrir um pull request para revisão.
  Criar a branch, fazer commit e push necessários para abrir o PR.
- Não fazer merge automaticamente.

## Convenções

- Seguir PEP 8 e utilizar type hints.
- Usar `snake_case` em funções, variáveis e módulos; `PascalCase` em classes.
- Separar lógica de negócio, persistência e integrações.
- Usar `Decimal` para valores monetários, preços e quantidades que exigem
  precisão decimal; nunca usar `float` para cálculos monetários.
- Usar datas ISO 8601 e timezone `America/Sao_Paulo` quando aplicável.
- Utilizar SQL parametrizado e evitar duplicação de registros.
- Preservar o histórico de movimentações, inclusive após vendas totais.

## Qualidade

- Executar `uv run pytest`, `uv run ruff check .` e
  `uv run ruff format --check .`.
- Adicionar testes proporcionais a cada funcionalidade.
- Não depender de internet ou APIs reais em testes unitários.
- Usar exclusivamente dados sintéticos em testes.
- Relatar falhas, sem declarar conclusão indevidamente.

## Segurança

- Nunca versionar chaves, tokens, credenciais, `.env`, bancos privados,
  posições reais, movimentações reais, saldos, logs sensíveis ou backups privados.
- Manter dados pessoais fora do Git, no diretório ignorado `data/`.
- Usar `.env.example` sem segredos quando necessário.

## Princípios

- Cálculos financeiros são determinísticos.
- SQLite preserva o histórico.
- Dados externos precisam de validação.
- Ausência de dados não equivale a zero.
- Cotações inválidas não podem disparar gatilhos.
- Correção e rastreabilidade têm prioridade sobre novas funcionalidades.

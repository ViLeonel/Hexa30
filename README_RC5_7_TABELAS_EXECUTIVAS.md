# RC5.7 — Tabelas executivas compartilhadas

Entrega cumulativa sobre a RC5.6.

## Objetivo

Corrigir a folga visual abaixo da última linha do quadro de avaliação e aplicar
o mesmo padrão executivo a todas as tabelas públicas presentes nas quatro telas
do aplicativo.

## Arquitetura

- `hexa_components.py`: contrato genérico das colunas, formatação e renderização
  semântica das tabelas.
- `hexa_pages.py`: composição dos registros e adoção do componente compartilhado.
- `hexa_styles.py`: design system, rolagem responsiva, cabeçalho fixo e correção
  da continuidade visual até a borda inferior.
- `hexa_config.py`: identificação da versão.
- `tests/`: regressões da RC5.6 atualizadas e testes específicos da RC5.7.

## Alterações

1. O quadro trimestral usa o componente compartilhado.
2. `margin: 0 !important` remove a margem residual aplicada à tabela.
3. A última linha remove a borda inferior e ocupa integralmente o cartão.
4. A coluna de destaque mantém o fundo até o final do quadro.
5. Todas as ocorrências públicas de `st.dataframe` foram substituídas:
   - lista de jogadores;
   - rankings de capacidade, potencial, evolução e regressão;
   - avaliações parciais;
   - leitura consolidada de mercado.
6. Tabelas largas possuem rolagem horizontal e primeira coluna fixa.
7. Tabelas longas possuem rolagem vertical e cabeçalho fixo.
8. Percentuais preservam informação textual e recebem barra visual complementar.
9. Conteúdo dinâmico é escapado antes da inserção no HTML.
10. Nenhum JSON canônico foi alterado.

## Versão

`1.1.9-rc5.7-tabelas-executivas`

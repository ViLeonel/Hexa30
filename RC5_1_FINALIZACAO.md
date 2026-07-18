# RC5.1 — Finalização de UX, Convocação Única e Persistência Local

## Identificação

- Versão: `1.1.1-rc5.1-finalizacao-ux`
- Base funcional: RC5 + Hotfix RC5.0.1
- Persistência editorial: JSON trimestral append-only
- Persistência pessoal: `localStorage` do navegador
- Dependências: `streamlit==1.59.2`, `pandas==2.3.3`

## Escopo entregue

### Espaçamento e navegação

- O padding superior do conteúdo foi reduzido de `1.5rem` para `0.75rem`.
- A margem inferior do cabeçalho principal foi reduzida de `2rem` para `1rem`.
- O topo da barra lateral foi compactado.
- O controle de alto contraste foi movido para um expansor no final da barra
  lateral, depois do Radar do projeto.

### Convocação sem duplicidade

A aplicação reconcilia toda a formação antes de instanciar os widgets.

Ordem canônica:

1. titulares;
2. reservas posicionais;
3. vagas livres.

Cada seletor remove das opções todos os atletas usados nas demais 25 vagas,
mantendo apenas o próprio valor atual. Estados antigos com duplicidade preservam
a primeira ocorrência válida e limpam as posteriores.

### Persistência por navegador

O novo módulo `hexa_persistencia_local.py`:

- serializa todas as formações por `id_atleta`;
- restaura a última tática ativa;
- mantém uma seleção independente por formação;
- valida existência e compatibilidade na restauração;
- descarta IDs inválidos;
- salva automaticamente depois de cada rerun causado por interação;
- permite apagar todas as escalações locais;
- funciona sem banco e sem gravar dados no servidor.

Limitações intencionais:

- não sincroniza entre navegador e celular;
- pode ser apagado pelas configurações do navegador;
- pode ser bloqueado por políticas de privacidade;
- não armazena avaliações, observações, mercado ou dados pessoais.

### Avaliação individual

`Situação`, `Saldo projetado` e `Data de referência` deixaram de usar
`st.metric`. Agora usam cartões compactos e responsivos, com fonte menor,
quebra de linha e alternativa textual para leitores de tela.

### Mercado e busca

- Busca: `Ex.: Real Madrid ou Vini Jr`.
- `% do pico` passou a `% do pico de mercado`.
- `Pico` passou a `Pico de mercado`.
- As demais referências ao pico também foram explicitadas.

## Arquivos alterados

- `caminho_hexa_2030.py`
- `hexa_components.py`
- `hexa_config.py`
- `hexa_pages.py`
- `hexa_selectors.py`
- `hexa_session.py`
- `hexa_styles.py`
- `CONTEXTO_PROJETO.md`
- `HISTORICO_REFATORACOES.md`
- `REGRAS_NEGOCIO_E_DADOS.md`
- `tests/test_rc5_contrato.py`

## Arquivos adicionados

- `hexa_persistencia_local.py`
- `tests/test_rc5_1_finalizacao.py`
- `RC5_1_FINALIZACAO.md`
- `DEPLOY_RC5_1.md`
- `RELATORIO_TESTES_RC5_1.md`

## Dados preservados

Nenhum dado editorial, cadastral, tático ou de mercado foi alterado.

- `jogadores_hexa_2030.json`: preservado byte a byte;
- `avaliacoes_trimestrais_hexa_2030.json`: preservado byte a byte;
- arquivo legado preventivo: preservado byte a byte.

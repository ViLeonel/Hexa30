# Relatório de testes — RC5.1

## Ambiente

- Data: 18/07/2026
- Python executado: runtime disponível no ambiente
- Streamlit: `1.59.2`
- pandas: `2.3.3`
- Workspace integrado: RC5 + Hotfix RC5.0.1 + RC5.1
- Dados: 61 atletas e 61 registros trimestrais de T2 2026

## Testes realizados

### Compilação e sintaxe

- `python -m compileall -q .`: aprovado.
- Parse de todos os arquivos Python com gramática Python 3.10: aprovado.
- Import dos módulos alterados e do entrypoint em processo novo: aprovado.
- Verificação estática de todos os nomes importados de módulos `hexa_*`:
  aprovada.
- Varredura de dependências externas: somente `streamlit` e `pandas`.

### Testes automatizados

Comando:

```bash
python -m unittest discover -s tests -v
```

Resultado:

- 37 testes executados;
- 37 testes aprovados;
- 0 falhas;
- 0 erros.

Cobertura funcional verificada:

- contrato temporal da RC5;
- hotfix do entrypoint;
- 61 IDs estáveis;
- T1 2026 ausente;
- indicadores do T2 2026;
- saldos negativos;
- política append-only;
- 11 reservas posicionais e 4 vagas livres;
- remoção de duplicidade posterior;
- prioridade do titular sobre reserva repetida;
- exclusão de atleta ocupado das opções;
- roundtrip da persistência por `id_atleta`;
- descarte de ID inexistente;
- formações persistidas separadamente;
- remoção de todas as formações locais;
- placeholder solicitado;
- terminologia de pico de mercado;
- cartões compactos da avaliação;
- acessibilidade renderizada após o Radar.

### Streamlit AppTest

Foram executadas as quatro páginas no `streamlit.testing.v1.AppTest`.

Resultados:

- Campo de Jogo: 0 exceções;
- Jogadores, Scout e Avaliações: 0 exceções;
- Lista de Jogadores: 0 exceções;
- Análises & Mercado: 0 exceções.

Campo de Jogo:

- 29 seletores renderizados;
- 2 controles de rádio;
- 3 botões;
- 0 exceções.

Cenário de regressão do Anexo 02:

1. Breno Bidon foi pré-carregado em uma vaga de reserva;
2. a página foi renderizada;
3. Breno Bidon não apareceu nas opções de:
   - Mezzala Esquerdo;
   - Mezzala Direito;
   - Vaga livre 1.

Ficha individual de Alisson:

- 0 exceções;
- tabela trimestral renderizada;
- situação `Completa` presente;
- data `30/06/2026` presente;
- os três textos deixaram de usar `st.metric`.

### Componente JavaScript

- `node --check` no código do componente: aprovado.
- Teste com `localStorage` simulado em Node:
  - sincronização: aprovada;
  - carregamento: aprovado;
  - exclusão: aprovada.

### Inicialização do servidor

O Streamlit foi inicializado em processo real.

- servidor iniciou;
- endpoint `/_stcore/health`;
- resposta: `HTTP 200`;
- conteúdo: `ok`.

### Integridade dos dados

Os três arquivos permaneceram byte a byte iguais à RC5:

- `jogadores_hexa_2030.json`
  - SHA-256: `ab7ee9718cd2c34dd0393b9d746359b9cf2ba70fcf1bc557b696d1a5331cdbfb`
- `avaliacoes_trimestrais_hexa_2030.json`
  - SHA-256: `eb846b4886080beb2e1bbce119a650cc1f93c9b9d14940446c97cbfbc18a3e8d`
- `arquivo/avaliacoes_editoriais_legado_pre_t2_2026.json`
  - SHA-256: `b592f9e7f3c4ab27ba8cf7adcb2ea7c9292ca6ca8862bbb63e719312021ddba9`

## Não verificado

Não foi possível executar navegação visual real com Chromium porque o ambiente
bloqueou o acesso do navegador automatizado ao endereço local com
`ERR_BLOCKED_BY_ADMINISTRATOR`.

Portanto, ainda dependem de smoke manual após o deploy:

- gravação real no `localStorage` de Chrome, Firefox, Edge, Brave e Safari;
- restauração após fechar e reabrir a aba;
- inspeção visual do espaçamento em cada navegador;
- reflow e zoom real de 200%;
- VoiceOver, NVDA, JAWS e TalkBack;
- modo privado e políticas que bloqueiam armazenamento local;
- sincronização no Streamlit Community Cloud.

A lógica Python, o componente JavaScript isolado, o contrato de estado e o
servidor Streamlit foram efetivamente testados.

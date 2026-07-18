# Relatório de Testes — RC5

## Escopo

Validação do pacote de sobreposição `RC5_AVALIACOES_HISTORICO`, dos dados
importados da planilha final e da integração temporal com as quatro páginas.

## Ambiente

- Python: 3.13 no ambiente de execução;
- Streamlit: 1.59.2;
- pandas: 2.3.3;
- planilha fonte:
  `avaliacoes_trimestrais_atletas_hexa_2030.xlsm`;
- SHA-256 da planilha:
  `a3b474dba6c667f0a2114006c1098be0c013ad100340a3730b1d8d082067f700`.

Os módulos inalterados `hexa_taticas.py`, `hexa_data.py`, `hexa_auth.py` e
`hexa_messages.py` não estavam materializados integralmente no diretório local.
Para os testes isolados de import e Streamlit foi usado um workspace temporário
com stubs compatíveis com os contratos públicos usados pela RC5. Esses stubs não
fazem parte do pacote entregue.

## Testes executados

### 1. Compilação

Comando:

```bash
python -m compileall -q .
```

Resultado: aprovado para todos os arquivos Python do pacote e do workspace de
integração.

### 2. Suíte automatizada

Comando:

```bash
python -m unittest discover -s tests -v
```

Resultado: **21 testes aprovados**.

Cobertura funcional:

- 61 avaliações em T2 2026;
- ausência total de T1 2026;
- data de referência 30/06/2026;
- 61 IDs únicos;
- 47 atletas com alguma avaliação;
- 43 avaliações completas;
- 4 avaliações parciais;
- 14 atletas não avaliados;
- 180 notas preenchidas;
- capacidade média 7,154255319148936;
- potencial médio 7,920212765957447;
- saldo médio 0,7659574468085106;
- saldo negativo com pares completos;
- último trimestre efetivamente avaliado;
- média histórica anterior;
- preservação do arquivo legado;
- interface sem leitura dos campos legados;
- nomes públicos Vini Leonel/Vini e Beto Muñoz/Beto;
- política append-only;
- bloqueio de correção retroativa silenciosa;
- escrita atômica;
- 11 slots táticos e quatro vagas livres;
- exclusão de indisponíveis e duplicidades nas reservas.

### 3. Importação real da planilha

O importador foi executado contra o `.xlsm` final e uma cópia do JSON original.

Resultado:

```text
Importação concluída: 61 registro(s) lido(s);
61 registro(s) na base temporal.
```

Conferências:

- os 61 registros gerados são iguais aos registros do JSON entregue;
- o JSON de jogadores gerado é igual ao JSON entregue;
- o arquivo legado contém os 61 atletas;
- nenhum cálculo derivado da planilha foi usado como fonte de verdade.

### 4. Imports e nomes importados

Foram importados com sucesso:

- `hexa_config`;
- `hexa_avaliacoes`;
- `hexa_session`;
- `hexa_selectors`;
- `hexa_components`;
- `hexa_pages`;
- `hexa_styles`;
- `hexa_admin`;
- `caminho_hexa_2030`.

Uma verificação AST confirmou a existência de todos os símbolos importados entre
os oito arquivos alterados que possuem imports locais.

### 5. Streamlit AppTest

As quatro páginas foram abertas por navegação programática:

- Campo de Jogo;
- Jogadores, Scout e Avaliações;
- Lista de Jogadores;
- Análises & Mercado.

Resultado: nenhuma exceção.

Na ficha individual também foram testados:

- Alisson: avaliação completa;
- Arthur: avaliação parcial;
- Diego Callai: sem avaliação.

Resultado: nenhuma exceção; o estado vazio foi exibido para o atleta sem notas.

Na página Análises & Mercado, o AppTest confirmou:

- 61 atletas;
- 47 com alguma avaliação;
- 43 completos;
- cobertura completa de 70,5%;
- capacidade média 7,15;
- potencial médio 7,92;
- saldo médio +0,77.

### 6. Inicialização real do servidor

Comando equivalente:

```bash
python -m streamlit run caminho_hexa_2030.py \
  --server.headless=true \
  --server.port=8765
```

Resultado:

```text
GET /_stcore/health → HTTP 200 / ok
```

### 7. Dependências

A varredura AST encontrou somente:

- `streamlit`;
- `pandas`.

As versões instaladas no teste corresponderam ao `requirements.txt`:

- Streamlit 1.59.2;
- pandas 2.3.3.

O importador usa apenas a biblioteca padrão.

## Observação do ambiente

Os subprocessos registraram no `stderr` um aviso de aquecimento interno do
`artifact_tool` já presente no ambiente de execução. O aviso não pertence ao
projeto, e todos os comandos acima retornaram código zero após as correções dos
testes.

## Pontos não verificados

- suíte completa do repositório real com todos os módulos inalterados;
- assinaturas estruturais do `hexa_taticas.py` real;
- autenticação real via Streamlit Secrets;
- GitHub Actions;
- deploy efetivo no Streamlit Community Cloud;
- inspeção visual em Chrome, Firefox, Edge, Brave e Safari;
- leitor de tela real;
- navegação integral por teclado;
- concorrência de escrita no ambiente hospedado;
- macros VBA da planilha, pois não são usadas pelo aplicativo.

Esses itens devem ser cobertos pelo CI e pelo smoke manual após copiar o pacote
para o repositório completo.

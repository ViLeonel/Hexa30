# RC5 — Avaliações Trimestrais e Histórico

## Objetivo

Substituir integralmente, na interface pública, o modelo editorial legado por
avaliações trimestrais de capacidade atual e potencial 2030, sempre associadas a
um período e a uma data de referência.

A primeira avaliação oficial é **T2 2026**, com data de referência
**30/06/2026**. O T1 2026 não integra o histórico.

## Arquitetura

### Cadastro e tática

`jogadores_hexa_2030.json` continua sendo a fonte canônica de:

- identidade do atleta;
- posição principal e posições múltiplas;
- clube e idade;
- grupos e tipo legado;
- dados cadastrais e de mercado.

A RC5 adiciona `id_atleta` estável aos 61 jogadores. Nenhuma posição editorial,
grupo, tipo ou informação cadastral foi substituída pela planilha.

### Avaliações temporais

`avaliacoes_trimestrais_hexa_2030.json` passa a ser a fonte canônica das
avaliações. A chave lógica é:

```text
id_atleta + periodo
```

Cada registro contém somente dados brutos:

- identificação;
- ano, trimestre e data de referência;
- posição e clube como snapshot do período;
- capacidade atual e potencial 2030 de Vini;
- capacidade atual e potencial 2030 de Beto;
- observações individuais.

Médias, saldos, divergências e histórico são recalculados por
`hexa_avaliacoes.py`. Resultados derivados da planilha não são importados.

### Arquivamento preventivo

`arquivo/avaliacoes_editoriais_legado_pre_t2_2026.json` preserva uma cópia
auditável dos antigos campos:

- `nota_vini`;
- `nota_roberto`;
- `pontos_fortes`;
- `pontos_fracos`;
- `historico`.

Os campos continuam no JSON cadastral durante esta transição para não romper o
contrato histórico de persistência, mas nenhum componente público da RC5 os lê
ou exibe.

## Regras de cálculo

### Média da capacidade e do potencial

Usa somente as notas disponíveis. Ausência permanece `null`; zero é uma nota
válida.

### Status

- **Completa:** Vini e Beto preencheram capacidade e potencial.
- **Parcial:** há pelo menos uma nota, mas os quatro campos não estão completos.
- **Não avaliada:** nenhum dos quatro campos possui nota.

### Saldo projetado

Para cada analista que preencheu o par completo:

```text
potencial 2030 − capacidade atual
```

O saldo do atleta é a média das diferenças individuais disponíveis. Pode ser
positivo, zero ou negativo.

### Divergência

Somente existe quando os dois analistas preencheram a mesma dimensão:

```text
abs(nota Vini − nota Beto)
```

Capacidade atual e potencial são comparados separadamente.

### Variação temporal

A variação usa o último período anterior efetivamente avaliado, e não a linha
anterior do arquivo. A média histórica anterior usa todas as notas anteriores de
capacidade atual de Vini e Beto, sem incluir o período corrente.

## Indicadores de regressão do T2 2026

- atletas cadastrados: 61;
- atletas com alguma avaliação: 47;
- avaliações completas: 43;
- avaliações parciais: 4;
- atletas não avaliados: 14;
- notas preenchidas: 180 de 244;
- capacidade atual média: 7,1542553191;
- potencial 2030 médio: 7,9202127660;
- saldo projetado médio: +0,7659574468.

Os quatro registros parciais são Arthur, Igor Jesus, Igor Paixão e Pedro
Morisco.

## Mudanças de interface

### Campo de Jogo

- cartões mostram capacidade atual, potencial e status do período;
- resumo da convocação mostra cobertura, médias e saldo;
- data de referência aparece no contexto global;
- seleção posicional de reservas da RC4 foi preservada.

### Jogadores, Scout e Avaliações

- exibe notas de Vini e Beto por dimensão;
- mostra média, saldo, status, snapshot e data de referência;
- exibe observações individuais;
- prepara gráfico histórico para quando houver mais de um trimestre;
- não exibe pontos fortes, pontos fracos ou histórico legado.

### Lista de Jogadores

- mostra capacidade atual média, potencial, saldo e status;
- preserva filtros cadastrais;
- período e data aparecem no topo.

### Análises & Mercado

- mostra cobertura e indicadores do período;
- separa rankings completos de avaliações parciais;
- compara consensos e divergências de capacidade e potencial separadamente;
- distingue explicitamente a data editorial da data de mercado.

## Importação trimestral

O script `scripts/importar_avaliacoes_planilha.py` lê o `.xlsm` usando apenas a
biblioteca padrão do Python.

Exemplo:

```bash
python scripts/importar_avaliacoes_planilha.py \
  avaliacoes_trimestrais_atletas_hexa_2030.xlsm \
  --jogadores jogadores_hexa_2030.json \
  --saida avaliacoes_trimestrais_hexa_2030.json \
  --arquivo-legado arquivo/avaliacoes_editoriais_legado_pre_t2_2026.json
```

Política:

- importação append-only;
- repetição idêntica é idempotente;
- alteração retroativa é bloqueada por padrão;
- correção retroativa exige `--permitir-correcao-retroativa`;
- escrita atômica;
- backup `.bak` quando o destino já existe;
- hash SHA-256 e data de importação registrados;
- JSON irrecuperável nunca é substituído silenciosamente.

## Compatibilidade

A RC5 não acrescenta dependências. Permanecem:

```text
streamlit==1.59.2
pandas==2.3.3
```

O JSON temporal é lido diretamente pela biblioteca padrão.

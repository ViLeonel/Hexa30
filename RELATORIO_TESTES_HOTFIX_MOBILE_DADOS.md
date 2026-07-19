# Relatório de testes — Hotfix mobile e dados externos

Data da execução: 19/07/2026

## Testes realizados

### Dependências

Comando executado:

```bash
python -m pip install -r /mnt/data/requirements.txt
```

Resultado: concluído com código de saída 0. Foram instalados
`streamlit==1.59.2` e `pandas==2.3.3`.

### Compilação

Foram compilados:

- os quatro módulos alterados;
- o teste adicionado;
- todos os arquivos Python materializados em `/mnt/data`.

Resultado: aprovado, sem erro de sintaxe.

### Testes automatizados do hotfix

```bash
python -m unittest discover -s tests -v
```

Resultado: **4 testes aprovados**.

Cobertura específica:

- sidebar em modo `auto`;
- cabeçalho nativo não ocultado;
- navegação antes do login;
- nacionalidade removida;
- campos externos `_site` usados corretamente.

### Renderização do componente de dados externos

Foi executado `render_dados_transfermarkt()` com os dados reais de Andrey Santos
e captura do HTML gerado.

Resultado:

- `Nacionalidades` ausente;
- representação `['Brasil']` ausente;
- `Médio Centro` presente;
- `Médio Defensivo` presente.

### Ordem da barra lateral

O entrypoint foi importado com dublês controlados das dependências de interface.
A sequência observada foi:

```text
título → separador → navegação → separador → login
```

Resultado: aprovado.

### Imports

Imports reais aprovados:

- `hexa_config`;
- `hexa_styles`;
- `hexa_taticas`;
- `hexa_avaliacoes`;
- `hexa_session`;
- `hexa_persistencia_local`;
- `hexa_audit`.

Também foram verificados estaticamente 32 nomes importados pelos módulos
alterados contra os módulos materializados. Resultado: nenhuma referência
ausente.

### JSON e integridade temporal

Arquivos validados por parse JSON:

- `jogadores_hexa_2030.json`: 61 atletas;
- `enriquecimentos_tm.json`: 58 registros;
- `avaliacoes_trimestrais_hexa_2030.json`: 61 registros.

A validação de avaliações confirmou:

- período `2026-T2`;
- 47 atletas com alguma avaliação;
- 43 avaliações completas.

### Regras táticas

Resultado:

- 6 formações válidas;
- 11 slots em cada formação;
- nenhuma posição fora do vocabulário oficial;
- `validar_taticas()` sem erros.

### Inicialização Streamlit

Foi iniciado um servidor Streamlit real em modo headless com os módulos
alterados e um dublê mínimo de `hexa_data`, exclusivamente para isolar o hotfix.

Resultado:

- endpoint `/_stcore/health`: `ok`;
- processo encerrado normalmente;
- nenhuma dependência nova do projeto.

## Integridade dos dados

Nenhum JSON foi incluído ou modificado pelo hotfix.

SHA-256 preservados:

```text
ab7ee9718cd2c34dd0393b9d746359b9cf2ba70fcf1bc557b696d1a5331cdbfb  jogadores_hexa_2030.json
72dd628b1c5dcdfe83125c02b254b389f1ec3ae4d61372888d011bd064bcab58  enriquecimentos_tm.json
eb846b4886080beb2e1bbce119a650cc1f93c9b9d14940446c97cbfbc18a3e8d  avaliacoes_trimestrais_hexa_2030.json
```

## Não realizado

Não foi possível executar no sandbox:

- a suíte histórica completa do repositório, porque não estavam materializados
  `hexa_auth.py`, `hexa_messages.py`, `hexa_models.py`,
  `hexa_repository.py` e `hexa_selectors.py`;
- a inicialização do aplicativo completo com essas implementações reais;
- interação visual real com o botão de abrir e fechar a sidebar;
- testes em Chrome, Firefox, Edge, Brave e Safari;
- VoiceOver, NVDA/JAWS, TalkBack e zoom visual real de 200%.

Esses itens permanecem obrigatórios antes do merge.

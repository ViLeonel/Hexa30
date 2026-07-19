# Relatório de testes — RC5.3 Refinamento visual

## Resultado

Aprovado para revisão e smoke manual no repositório completo.

## Testes realizados

### Dependências

Comando:

```bash
python -m pip install -r requirements.txt
```

Resultado: aprovado.

Versões verificadas:

- Streamlit: `1.59.2`
- pandas: `2.3.3`

### Compilação

Comando:

```bash
python -m compileall -q REFINAMENTO_VISUAL_RC5_3
```

Resultado: aprovado, retorno 0.

### Testes automatizados

Comando:

```bash
python -m unittest discover -s tests -v
```

Resultado: 11 testes aprovados.

Cobertura dos testes:

- sidebar responsiva do hotfix;
- cabeçalho nativo preservado;
- navegação antes do login;
- nacionalidade removida da ficha pública;
- campos externos corretos;
- escala tipográfica central;
- ausência de `font-weight: 800`;
- tema TOML e fonte configurados;
- remoção de `st.metric`;
- eliminação do título redundante;
- KPIs semânticos e com escape HTML;
- dados contratuais em `<dl>`, sem colchetes e sem campos vazios;
- nomes importados pelo módulo de páginas.

### Configuração do Streamlit

`streamlit config show` foi executado no diretório do pacote e aceitou
`.streamlit/config.toml` com retorno 0.

### Verificação de imports

Foram verificados estaticamente 94 nomes importados entre módulos disponíveis.
Não houve nome ausente.

O sandbox não possui estes módulos do repositório completo:

- `hexa_auth.py`
- `hexa_messages.py`
- `hexa_models.py`
- `hexa_repository.py`
- `hexa_selectors.py`

Por isso, a importação e inicialização do entrypoint completo não foram
executadas.

### Dados canônicos

Todos os JSONs foram lidos com sucesso:

- `jogadores_hexa_2030.json`: 61 atletas;
- `enriquecimentos_tm.json`: 58 registros;
- `avaliacoes_trimestrais_hexa_2030.json`: 61 avaliações.

SHA-256 observados antes do empacotamento:

- jogadores: `ab7ee9718cd2c34dd0393b9d746359b9cf2ba70fcf1bc557b696d1a5331cdbfb`
- enriquecimentos: `72dd628b1c5dcdfe83125c02b254b389f1ec3ae4d61372888d011bd064bcab58`
- avaliações: `eb846b4886080beb2e1bbce119a650cc1f93c9b9d14940446c97cbfbc18a3e8d`

O pacote não contém JSONs e não altera dados editoriais.

### Integridade tática

- 6 formações verificadas;
- todas possuem 11 slots;
- 14 posições oficiais;
- nenhuma posição inválida nos 61 atletas;
- todos os campos editoriais e táticos protegidos estão presentes.

### Smoke visual isolado

Um aplicativo isolado foi executado com os componentes alterados.

- `streamlit.testing.v1.AppTest`: nenhuma exceção;
- KPI renderizado;
- lista contratual `<dl>` renderizada;
- expander renderizado;
- servidor headless iniciado;
- endpoint `/_stcore/health`: `ok`.

## Pontos não verificados

- inicialização do aplicativo completo, pela ausência dos cinco módulos listados;
- autenticação administrativa real;
- integração com o `localStorage` no navegador;
- inspeção visual real em Chrome, Firefox, Edge, Brave e Safari;
- screenshot automatizado: o Chromium disponível no sandbox encerrou por
  limitação do processo gráfico do ambiente.

## Risco residual

O principal risco é visual e responsivo, não de dados. O smoke manual deve
confirmar que o tema do Streamlit Cloud não está sendo sobrescrito por
configuração externa e que a hierarquia se mantém nos navegadores-alvo.

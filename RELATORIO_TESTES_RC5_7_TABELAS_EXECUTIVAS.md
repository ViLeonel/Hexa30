# Relatório de testes — RC5.7 Tabelas executivas

## Resultado

- Suíte automatizada: **12 testes aprovados de 12**.
- Compilação: **6 arquivos Python aprovados de 6**.
- AppTest isolado: **zero exceções**.
- Servidor Streamlit isolado: **HTTP 200 / ok**.

## Testes realizados

### Código

- compilação de `hexa_components.py`;
- compilação de `hexa_pages.py`;
- compilação de `hexa_styles.py`;
- compilação de `hexa_config.py`;
- compilação dos dois arquivos de teste;
- verificação por AST dos nomes importados de `hexa_components`;
- nenhum nome importado ausente;
- importação real de `hexa_components`, `hexa_pages`, `hexa_styles` e
  `hexa_config` em ambiente isolado com dependências não fornecidas simuladas.

### Tabelas

- formatação decimal, percentual, monetária e com sinal;
- escape de HTML em conteúdo dinâmico;
- legenda e rótulo semântico;
- coluna de destaque;
- barras percentuais;
- modificadores para tabelas largas e longas;
- quadro trimestral usando o componente compartilhado;
- ausência de `st.dataframe` e `st.table` nas quatro páginas públicas;
- correção CSS da margem inferior;
- remoção da borda inferior na última linha;
- continuidade da coluna destacada até o final do quadro.

### Dados e regras

- `jogadores_hexa_2030.json`: válido, 61 jogadores;
- `avaliacoes_trimestrais_hexa_2030.json`: válido;
- `enriquecimentos_tm.json`: válido, 58 registros;
- seis formações com exatamente 11 titulares;
- `validar_taticas`: nenhum erro.

## Testes de execução

Foi criado um aplicativo Streamlit isolado com o componente real da RC5.7:

- `AppTest`: zero exceções;
- inicialização do servidor: aprovada;
- `GET /_stcore/health`: `HTTP 200`, corpo `ok`.

## Não realizado

- execução do entrypoint completo, pois os módulos reais de autenticação,
  administração, mensagens, sessão e persistência não estavam presentes no
  pacote disponibilizado nesta rodada;
- inspeção visual real em Chrome, Firefox, Edge, Brave e Safari;
- deploy efetivo no Streamlit Community Cloud.

## Observação do ambiente

O ambiente de testes possuía Streamlit `1.59.2` e pandas `2.2.3`. O projeto fixa
pandas `2.3.3`; repita a suíte após `pip install -r requirements.txt`.

A inicialização do Python emitiu um aviso externo do `artifact_tool` antes dos
testes. O aviso não veio do aplicativo e não alterou o resultado da suíte.

# RC5.3 — Refinamento visual

Entrega cumulativa sobre a RC5.1 e o hotfix mobile/dados RC5.2.

## Escopo implementado

1. Escala tipográfica central por tokens CSS.
2. Fonte e hierarquia nativas configuradas em `.streamlit/config.toml`.
3. Remoção dos pesos `800` do design system.
4. Remoção de títulos e informações redundantes na tela de análises e no banco.
5. Substituição de `st.metric` por KPIs compactos, semânticos e responsivos.
6. Dados externos e contratuais convertidos para lista de definições `<dl>`.
7. Campos contratuais vazios deixam de ser exibidos.
8. Hotfix mobile/dados anterior preservado integralmente.

## Arquivos cumulativos desta entrega

- `.streamlit/config.toml`
- `caminho_hexa_2030.py`
- `hexa_admin.py`
- `hexa_components.py`
- `hexa_config.py`
- `hexa_pages.py`
- `hexa_styles.py`
- `tests/test_hotfix_mobile_dados.py`
- `tests/test_refinamento_visual.py`

Os JSONs canônicos não estão no pacote e não são modificados por esta entrega.

## Decisões de design

A fonte do tema é `sans-serif`, que usa a família sans-serif incorporada ao
Streamlit e evita dependência de CDN ou arquivo externo. A escala usa 16 px como
base, títulos entre 1 rem e 2,5 rem e pesos máximos de 700.

Os KPIs possuem rótulo, valor e contexto textual. A cor é apenas um reforço
visual pela borda lateral; o significado não depende exclusivamente dela.

Os dados contratuais usam `<dl>`, `<dt>` e `<dd>`, ficam em duas colunas no
desktop e uma coluna no mobile. Valores ausentes são omitidos em vez de gerar
várias linhas com “Não informado”.

## Versão

`1.1.3-rc5.3-refinamento-visual`

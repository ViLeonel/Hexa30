# Arquitetura — O Caminho para o Hexa 2030

## Estrutura

- `caminho_hexa_2030.py`: entrada do Streamlit e composição das quatro telas.
- `data.py`: leitura, normalização, self-healing, enriquecimentos externos e gravação atômica do JSON.
- `taticas.py`: posições oficiais, formações, limite de 11 titulares + 15 reservas e compatibilidade tática.
- `components.py`: campo, banco de reservas, perfil, avaliações somente para leitura, dossiê e mercado.
- `styles.py`: design system WCAG e regras responsivas.
- `jogadores_hexa_2030.json`: fonte canônica e única da base de atletas.
- `requirements.txt`: dependências do Streamlit Cloud.

## Regras de preservação

Os enriquecimentos externos nunca sobrescrevem:

- notas do Vini e do Roberto;
- pontos fortes e fracos;
- histórico das discussões;
- posições táticas do projeto;
- grupo e classificação histórica `tipo`.

O campo `tipo` permanece no JSON por preservação histórica, mas não é mostrado nem editado no aplicativo.

## Convocação

Cada formação começa vazia. O usuário escolhe:

- até 11 titulares, respeitando a compatibilidade por posição;
- até 15 reservas, sem repetir atletas dos titulares;
- total máximo de 26 convocados.

## Dados externos

Campos importados de fontes externas usam o prefixo `tm_`. Valores financeiros são armazenados em texto e também em milhões de euros para cálculos. As posições externas são exibidas como referência e não alteram a Regra do Treinador.

# Arquitetura — O Caminho para o Hexa 2030

## Estrutura

- `caminho_hexa_2030.py`: entrada do Streamlit e composição das telas.
- `data.py`: leitura, validação, migração, enriquecimento e gravação atômica do JSON.
- `taticas.py`: posições oficiais, abreviações, formações e compatibilidade tática.
- `components.py`: componentes visuais reutilizáveis.
- `styles.py`: configuração de página e design system WCAG/mobile-first.
- `jogadores_hexa_2030.json`: fonte canônica do elenco e dos conteúdos editoriais.
- `requirements.txt`: dependências do Streamlit Cloud.

## Fonte única de dados

O JSON é a única base completa de jogadores. O Python contém somente migrações incrementais e dados externos novos usados pelo mecanismo de self-healing. Não há uma segunda cópia integral do elenco dentro do código.

## Preservação de dados

Os campos abaixo nunca são substituídos por enriquecimentos externos:

- `nota_vini`
- `nota_roberto`
- `pontos_fortes`
- `pontos_fracos`
- `historico`
- `posicao`
- `posicoes_multiplas`
- `grupo`
- `tipo`

As gravações são atômicas e mantêm `jogadores_hexa_2030.json.bak` como backup local da versão anterior.

## Deploy

Mantenha todos os arquivos na raiz do repositório. O entrypoint do Streamlit continua sendo:

`caminho_hexa_2030.py`

Após substituir os arquivos no GitHub, o Streamlit Community Cloud deve detectar o novo commit e reiniciar o app.

## Observação de persistência

O sistema de arquivos do Streamlit Community Cloud não deve ser tratado como banco permanente. Alterações feitas pelos sliders e formulários podem se perder em reinícios ou novos deploys. Para persistência real, a próxima evolução recomendada é mover o JSON mutável para Supabase/PostgreSQL ou outro banco externo.

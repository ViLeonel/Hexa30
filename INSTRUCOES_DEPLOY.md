# Deploy no GitHub e Streamlit Cloud

1. Descompacte o pacote.
2. Envie todos os arquivos para a raiz do repositório, substituindo as versões anteriores.
3. Confirme que estes arquivos estão no mesmo nível:
   - `caminho_hexa_2030.py`
   - `data.py`
   - `taticas.py`
   - `components.py`
   - `styles.py`
   - `jogadores_hexa_2030.json`
   - `requirements.txt`
4. Faça o commit no branch `main`.
5. No Streamlit Cloud, mantenha `caminho_hexa_2030.py` como entrypoint.
6. Reinicie o app caso o redeploy não ocorra automaticamente.

O JSON continua sendo a fonte temporária de dados. Alterações feitas pelo formulário de cadastro no ambiente do Streamlit Cloud não têm garantia de sobreviver a uma reconstrução; para o estágio atual, atualizações permanentes devem ser consolidadas no JSON do GitHub.

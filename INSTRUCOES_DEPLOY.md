# Instruções de substituição no GitHub

1. Faça um download de segurança dos arquivos atuais do repositório.
2. Na raiz do repositório `caminhoparaohexa`, substitua:
   - `caminho_hexa_2030.py`
   - `jogadores_hexa_2030.json`
   - `requirements.txt`
3. Adicione, também na raiz:
   - `data.py`
   - `taticas.py`
   - `components.py`
   - `styles.py`
4. O arquivo principal configurado no Streamlit continua sendo `caminho_hexa_2030.py`.
5. Faça o commit das alterações. O Streamlit Community Cloud deverá reconstruir o app porque o `requirements.txt` também foi alterado.

Não envie para o GitHub arquivos locais terminados em `.bak`, `.tmp`, pastas `__pycache__` ou o ZIP deste pacote.

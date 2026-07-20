# Deploy — Hotfix 1.1.6 Card de perfil

## 1. Criar a branch

```bash
git checkout main
git pull
git checkout -b hotfix/card-perfil-nameerror
```

## 2. Aplicar o pacote

Extraia o ZIP na raiz do repositório.

Arquivos alterados:

```text
hexa_components.py
hexa_config.py
tests/test_hotfix_card_perfil.py
README_HOTFIX_CARD_PERFIL.md
DEPLOY_HOTFIX_CARD_PERFIL.md
RELATORIO_TESTES_HOTFIX_CARD_PERFIL.md
MANIFESTO_SHA256.txt
```

Não altere ou apague os JSONs canônicos, `requirements.txt`,
`.streamlit/secrets.toml` ou os demais módulos.

## 3. Validar localmente

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

## 4. Smoke manual

1. Abra `Jogadores, Scout e Avaliações`.
2. Selecione Allan.
3. Confirme que a ficha abre sem `NameError`.
4. Confirme `Ciclo 2030`, `Avaliação Completa`, `PD - MEI - MCD` e idade `26`.
5. Teste um atleta com avaliação parcial.
6. Teste um atleta sem avaliação.
7. Confirme que `Dados externos e contratuais` continua acima de `Valor de mercado`.

## 5. Publicar

```bash
git add hexa_components.py hexa_config.py tests/test_hotfix_card_perfil.py   README_HOTFIX_CARD_PERFIL.md DEPLOY_HOTFIX_CARD_PERFIL.md   RELATORIO_TESTES_HOTFIX_CARD_PERFIL.md MANIFESTO_SHA256.txt
git commit -m "fix: corrige NameError no card de perfil"
git push -u origin hotfix/card-perfil-nameerror
```

Após o merge, aguarde o redeploy do Streamlit Community Cloud. Se necessário,
use `Manage app` → `Reboot app`.

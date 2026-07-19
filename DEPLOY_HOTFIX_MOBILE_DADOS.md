# Deploy — Hotfix mobile e dados externos

## 1. Criar a branch

```bash
git checkout main
git pull
git checkout -b hotfix/mobile-sidebar-dados-externos
```

## 2. Aplicar o pacote

Extraia o ZIP na raiz do repositório e confirme os arquivos:

```text
caminho_hexa_2030.py
hexa_config.py
hexa_styles.py
hexa_components.py
tests/test_hotfix_mobile_dados.py
```

Não substitua nem remova:

- `jogadores_hexa_2030.json`;
- `avaliacoes_trimestrais_hexa_2030.json`;
- `enriquecimentos_tm.json`;
- `requirements.txt`;
- `.streamlit/secrets.toml`;
- os demais módulos `hexa_*.py`.

## 3. Validar no repositório completo

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

## 4. Smoke manual obrigatório

### Mobile

Teste em 320, 375, 390 e 430 px:

1. abra o aplicativo;
2. confirme que a sidebar começa recolhida;
3. abra a sidebar pelo controle nativo;
4. escolha cada página;
5. recolha a sidebar;
6. confirme que o controle de abertura continua visível;
7. repita o ciclo pelo menos três vezes;
8. teste rolagem, orientação horizontal e zoom de 200%.

### Dados externos

Abra Andrey Santos e confirme:

- ausência do campo `Nacionalidades`;
- `Posição na fonte externa: Médio Centro`;
- `Posições externas: Médio Defensivo`;
- ausência de colchetes e aspas de listas Python.

### Desktop

Confirme que:

- a sidebar continua aberta por padrão em tela larga;
- a navegação aparece antes de `Acesso administrativo`;
- login, logout, período e acessibilidade continuam funcionando.

## 5. Publicar

```bash
git add caminho_hexa_2030.py hexa_config.py hexa_styles.py   hexa_components.py tests/test_hotfix_mobile_dados.py   README_HOTFIX_MOBILE_DADOS.md DEPLOY_HOTFIX_MOBILE_DADOS.md   RELATORIO_TESTES_HOTFIX_MOBILE_DADOS.md MANIFESTO_SHA256.txt

git commit -m "fix: restaura sidebar mobile e corrige dados externos"
git push -u origin hotfix/mobile-sidebar-dados-externos
```

Abra o Pull Request, execute a suíte completa e faça o merge somente após o
smoke manual.

## 6. Streamlit Community Cloud

1. mantenha `caminho_hexa_2030.py` como **Main file path**;
2. preserve os Secrets OIDC;
3. após o merge, abra **Manage app**;
4. use **Reboot app**;
5. acompanhe os logs;
6. repita o smoke mobile e desktop.

## Rollback

```bash
git revert <hash-do-merge>
git push
```

Depois use **Reboot app** no Streamlit Community Cloud.

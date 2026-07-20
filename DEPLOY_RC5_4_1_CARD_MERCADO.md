# Deploy — RC5.4.1 Ajuste fino do card e ordem do mercado

## 1. Criar a branch

```bash
git checkout main
git pull
git checkout -b rc5-4-1-card-mercado
```

## 2. Aplicar o pacote

Extraia o ZIP na raiz do repositório, preservando a estrutura.

Arquivos alterados:

```text
hexa_components.py
hexa_pages.py
hexa_styles.py
hexa_config.py
README_RC5_4_1_CARD_MERCADO.md
DEPLOY_RC5_4_1_CARD_MERCADO.md
RELATORIO_TESTES_RC5_4_1_CARD_MERCADO.md
MANIFESTO_SHA256.txt
```

Não substitua nem apague:

- `jogadores_hexa_2030.json`
- `avaliacoes_trimestrais_hexa_2030.json`
- `enriquecimentos_tm.json`
- `.streamlit/secrets.toml`
- os demais módulos `hexa_*.py`
- `requirements.txt`

## 3. Validar localmente

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

## 4. Smoke manual obrigatório

### Card do jogador
1. Abra Allan e Alexsandro.
2. Confirme `Ciclo 2030` à esquerda e `Avaliação Completa` à direita.
3. Confirme o nome em destaque.
4. Confirme as posições curtas logo abaixo do nome.
5. Confirme a ausência da posição longa no canto inferior direito.
6. Confirme clube atual, capacidade atual, potencial em 2030 e idade em 2030.

### Ordem da ficha
1. Abra a ficha de um atleta com dados contratuais e de mercado.
2. Confirme que `Dados externos e contratuais` vem antes de `Valor de mercado`.
3. Confirme que a aparência do card continua responsiva em 320, 375, 390 e 430 px.

## 5. Publicar

```bash
git add hexa_components.py hexa_pages.py hexa_styles.py hexa_config.py   README_RC5_4_1_CARD_MERCADO.md DEPLOY_RC5_4_1_CARD_MERCADO.md   RELATORIO_TESTES_RC5_4_1_CARD_MERCADO.md MANIFESTO_SHA256.txt
git commit -m "fix: ajusta card do jogador e ordem do mercado"
git push -u origin rc5-4-1-card-mercado
```

Abra o Pull Request, execute o smoke manual e faça o merge somente após a conferência final.

## 6. Streamlit Community Cloud

Após o merge:

1. aguarde o redeploy automático;
2. se necessário, abra `Manage app`;
3. use `Reboot app`;
4. execute o smoke manual.

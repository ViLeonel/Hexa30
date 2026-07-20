# Deploy — RC5.7 Tabelas executivas

## 1. Criar a branch

```bash
git checkout main
git pull
git checkout -b rc5-7-tabelas-executivas
```

## 2. Aplicar o pacote

Extraia o ZIP na raiz do repositório.

Arquivos alterados:

```text
hexa_components.py
hexa_pages.py
hexa_styles.py
hexa_config.py
tests/test_rc5_6_refino_executivo.py
tests/test_rc5_7_tabelas_executivas.py
```

Não apague nem substitua:

- `jogadores_hexa_2030.json`;
- `avaliacoes_trimestrais_hexa_2030.json`;
- `enriquecimentos_tm.json`;
- `.streamlit/secrets.toml`;
- os demais módulos `hexa_*.py`;
- `requirements.txt`.

## 3. Validar localmente

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

## 4. Smoke manual obrigatório

### Avaliação trimestral

1. Abra um atleta com avaliação completa.
2. Confirme que a coluna `Média` chega até a borda inferior do quadro.
3. Confirme que não existe faixa vazia abaixo da última linha.
4. Repita com avaliação parcial e sem avaliação.

### Tabelas compartilhadas

Confira:

- `Jogadores`;
- quatro rankings em `Indicadores`;
- `Avaliações parciais`;
- tabela consolidada de mercado.

Em cada tabela, valide:

1. bordas, tipografia e coluna de destaque;
2. rolagem horizontal sem corte;
3. primeira coluna fixa em tabelas largas;
4. cabeçalho fixo em tabelas longas;
5. barras percentuais sem substituir o valor textual;
6. foco de teclado visível.

### Responsividade

Teste em 320, 375, 390 e 430 px, desktop e zoom de 200%.

## 5. Publicar

```bash
git add hexa_components.py hexa_pages.py hexa_styles.py hexa_config.py   tests/test_rc5_6_refino_executivo.py   tests/test_rc5_7_tabelas_executivas.py   README_RC5_7_TABELAS_EXECUTIVAS.md   DEPLOY_RC5_7_TABELAS_EXECUTIVAS.md   RELATORIO_TESTES_RC5_7_TABELAS_EXECUTIVAS.md   MANIFESTO_SHA256.txt

git commit -m "feat: aplica tabelas executivas em todo o app"
git push -u origin rc5-7-tabelas-executivas
```

Abra o Pull Request e faça o merge somente após o smoke manual.

## 6. Streamlit Community Cloud

Após o merge:

1. aguarde o redeploy automático;
2. abra `Manage app` se a versão anterior permanecer;
3. selecione `Reboot app`;
4. execute novamente o smoke manual.

## Rollback

Reverta o commit da RC5.7. Nenhum JSON precisa de rollback.

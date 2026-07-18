# Deploy da RC5

## 1. Criar uma branch

```bash
git checkout -b rc5-avaliacoes-trimestrais
```

## 2. Copiar o conteúdo do pacote para a raiz do repositório

A cópia deve preservar as pastas `arquivo/`, `scripts/` e `tests/`.

Arquivos principais novos ou alterados:

```text
caminho_hexa_2030.py
hexa_admin.py
hexa_avaliacoes.py
hexa_components.py
hexa_config.py
hexa_pages.py
hexa_selectors.py
hexa_session.py
hexa_styles.py
avaliacoes_trimestrais_hexa_2030.json
jogadores_hexa_2030.json
arquivo/avaliacoes_editoriais_legado_pre_t2_2026.json
scripts/importar_avaliacoes_planilha.py
tests/test_rc5_avaliacoes.py
tests/test_rc5_contrato.py
tests/test_rc5_importador.py
```

Não remova os módulos não incluídos no pacote, como `hexa_data.py`,
`hexa_taticas.py`, `hexa_auth.py`, `hexa_messages.py`, `hexa_models.py` e
`hexa_repository.py`.

## 3. Revisar as diferenças

```bash
git status
git diff --stat
git diff -- jogadores_hexa_2030.json
```

No JSON de jogadores, a mudança intencional é a inclusão de `id_atleta`.
Os campos editoriais e táticos existentes devem permanecer.

## 4. Validar localmente

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

Smoke manual:

1. Campo de Jogo: selecione formação, titulares e reservas; confira o contexto
   T2 2026 e as métricas temporais.
2. Jogadores, Scout e Avaliações: abra um atleta completo, um parcial e um sem
   avaliação.
3. Lista de Jogadores: filtre e confira status, capacidade, potencial e saldo.
4. Análises & Mercado: confira 61/47/43/4/14 e a separação entre avaliação e
   mercado.
5. Mude o modo de alto contraste e teste uma largura móvel.

## 5. Commit e push

```bash
git add .
git commit -m "feat: RC5 avaliações trimestrais e histórico"
git push -u origin rc5-avaliacoes-trimestrais
```

Abra um pull request e confirme os testes de CI antes do merge.

## 6. Streamlit Community Cloud

Após o merge:

1. abra o aplicativo no painel do Streamlit Community Cloud;
2. confirme que o **Main file path** continua
   `caminho_hexa_2030.py`;
3. use **Reboot app** para reiniciar o processo e limpar o cache;
4. acompanhe os logs de inicialização;
5. repita o smoke manual das quatro páginas;
6. confirme que a data de referência exibida é 30/06/2026;
7. confirme que os valores de mercado mantêm suas próprias datas.

## Rollback

Se houver falha:

```bash
git revert <hash-do-merge-da-rc5>
git push
```

Depois use **Reboot app** novamente. O arquivo legado permite auditar as
avaliações anteriores sem reativá-las na interface.

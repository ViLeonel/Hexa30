# Deploy — RC5.3 Refinamento visual

## 1. Criar a branch

```bash
git checkout main
git pull
git checkout -b rc5-3-refinamento-visual
```

## 2. Aplicar o pacote

Extraia o ZIP na raiz do repositório, preservando a estrutura de pastas.

Atenção ao arquivo oculto:

```text
.streamlit/config.toml
```

Não substitua nem apague `.streamlit/secrets.toml`.

Os JSONs canônicos não fazem parte do pacote e devem permanecer intactos.

## 3. Validar localmente

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

## 4. Smoke manual obrigatório

### Desktop

1. Abra Campo de Jogo, Jogadores e Análises & Mercado.
2. Confirme que os títulos têm hierarquia consistente e alinhamento à esquerda.
3. Confirme que os KPIs são compactos, uniformes e não quebram valores.
4. Confirme que “Compilado de avaliações para o Ciclo 2030” não é repetido.
5. Confirme que a barra de período da análise não repete os números dos KPIs.
6. Abra um atleta com dados contratuais e verifique a lista em duas colunas.
7. Confirme que campos vazios não são exibidos.

### Mobile

Teste em 320, 375, 390 e 430 px:

1. reabrir a barra lateral depois de recolhê-la;
2. títulos sem corte horizontal;
3. KPIs em uma coluna;
4. dados contratuais em uma coluna;
5. alvos de toque e foco de teclado;
6. zoom de 200%.

### Alto contraste

Ative a preferência de alto contraste e confirme bordas visíveis em:

- KPIs;
- dados contratuais;
- cartões de avaliação;
- campo e banco.

## 5. Publicar

```bash
git add .streamlit/config.toml \
  caminho_hexa_2030.py \
  hexa_admin.py \
  hexa_components.py \
  hexa_config.py \
  hexa_pages.py \
  hexa_styles.py \
  tests/
git commit -m "feat: refina tipografia, KPIs e dados contratuais"
git push -u origin rc5-3-refinamento-visual
```

Abra o Pull Request e faça o merge somente após o smoke manual.

## 6. Streamlit Community Cloud

O tema é lido do arquivo `.streamlit/config.toml`. Após o merge:

1. abra `Manage app`;
2. use `Reboot app` se a nova aparência não surgir;
3. confirme a versão `1.1.3-rc5.3-refinamento-visual`;
4. repita o smoke em desktop e mobile.

## Rollback

Reverta o commit da RC5.3. Nenhum JSON precisa de rollback porque esta entrega
não altera dados editoriais, avaliações trimestrais ou enriquecimentos.

# Deploy — RC5.1

## 1. Preparar uma branch

```bash
git checkout main
git pull
git checkout -b rc5-1-finalizacao-ux
```

## 2. Copiar o pacote

Extraia o ZIP e copie seu conteúdo para a raiz do repositório. Confirme que o
novo arquivo `hexa_persistencia_local.py` ficou ao lado do entrypoint.

Não apague:

- `.streamlit/secrets.toml` local;
- configurações OIDC no Streamlit Community Cloud;
- JSONs canônicos atuais.

## 3. Validar localmente

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
streamlit run caminho_hexa_2030.py
```

## 4. Smoke manual

### Campo de Jogo

1. Escolha um atleta em uma vaga.
2. Abra outro seletor compatível e confirme que ele não aparece.
3. Recarregue a página e confirme a restauração.
4. Troque de tática, monte outra seleção e volte à anterior.
5. Confirme que cada formação preserva seu próprio estado.
6. Teste `Limpar titulares e reservas`.
7. Teste `Apagar escalações salvas neste navegador`.

### Outras páginas

- ficha individual sem truncamento em situação, saldo e data;
- busca com `Real Madrid ou Vini Jr`;
- tabela com `% do pico de mercado`;
- acessibilidade no final da barra lateral;
- alto contraste funcionando depois do rerun.

## 5. Publicar

```bash
git add .
git commit -m "feat: RC5.1 finaliza UX e persistência local"
git push -u origin rc5-1-finalizacao-ux
```

Abra o Pull Request e faça o merge após os testes.

## 6. Streamlit Community Cloud

O Community Cloud normalmente detecta o commit automaticamente. Se a versão
antiga continuar ativa:

1. abra `Manage app`;
2. selecione `Reboot app`;
3. aguarde a inicialização;
4. execute o smoke manual.

## Rollback

Reverta o commit da RC5.1. Os dados trimestrais não precisam de rollback porque
não foram modificados. O item salvo no navegador pode permanecer, mas será
ignorado por uma versão sem o módulo de persistência.

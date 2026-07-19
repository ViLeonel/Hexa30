# Hotfix 1.1.2 — Mobile e dados externos

Pacote incremental para sobrepor na raiz do repositório **O Caminho para o Hexa 2030**.

## Arquitetura preservada

- `caminho_hexa_2030.py`: composição da barra lateral e roteamento;
- `hexa_config.py`: configuração central e versão;
- `hexa_styles.py`: design system e CSS;
- `hexa_components.py`: apresentação dos dados externos;
- `tests/test_hotfix_mobile_dados.py`: regressões específicas do hotfix.

Nenhum JSON, regra tática, avaliação trimestral, persistência local ou dependência
foi alterado.

## Alterações

1. A sidebar passa a usar `initial_sidebar_state="auto"`.
2. O cabeçalho nativo do Streamlit não é mais ocultado, preservando o controle
   de reabertura da sidebar no mobile.
3. A navegação pública aparece antes do bloco de acesso administrativo.
4. O campo público de nacionalidades foi removido da ficha.
5. As posições externas agora leem `tm_posicao_site` e
   `tm_posicoes_secundarias_site`.
6. Listas de posições externas são exibidas como texto separado por vírgulas.
7. Versão atualizada para `1.1.2-hotfix-mobile-dados`.

## Instalação

Extraia o ZIP sobre a raiz do repositório. Não apague nem substitua os JSONs
canônicos, o `requirements.txt`, os Secrets OIDC ou os módulos que não fazem
parte deste pacote.

Leia `DEPLOY_HOTFIX_MOBILE_DADOS.md` antes da publicação.

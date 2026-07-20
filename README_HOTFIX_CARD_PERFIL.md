# Hotfix 1.1.6 — Card de perfil

Correção emergencial sobre a RC5.4.1.

## Causa raiz

O card chamava `_idade_em_2030(dados)`, mas a função existente no módulo é
`_idade_projetada_2030(dados)`. Isso gerava `NameError` ao abrir qualquer ficha
de atleta.

Também foi restaurado o uso de `formatar_status_avaliacao`, garantindo os
rótulos públicos:

- Avaliação Completa
- Avaliação Parcial
- Sem Avaliação

## Arquivos alterados

- `hexa_components.py`
- `hexa_config.py`
- `tests/test_hotfix_card_perfil.py`

## Dados preservados

Nenhum JSON canônico foi alterado.

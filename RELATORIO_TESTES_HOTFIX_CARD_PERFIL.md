# Relatório de testes — Hotfix 1.1.6 Card de perfil

## Causa raiz confirmada

O pacote RC5.4.1 chamava `_idade_em_2030(dados)`, nome que não existe no módulo.
A função disponível é `_idade_projetada_2030(dados)`. A chamada inválida
provocava `NameError` ao selecionar um atleta.

Também foi corrigido o fallback do estado sem avaliação e restaurado o uso
de `formatar_status_avaliacao`, preservando os rótulos públicos definidos
pela RC5.4.

## Alterações verificadas

- `_idade_em_2030` removido do código.
- `_idade_projetada_2030` usado pelo card.
- `formatar_status_avaliacao` aplicado ao status.
- fallback interno ajustado para `Não avaliada`.
- versão atualizada para `1.1.6-hotfix-card-perfil`.

## Testes realizados

- Compilação de `hexa_components.py`: aprovada.
- Compilação de `hexa_config.py`: aprovada.
- Compilação de `tests/test_hotfix_card_perfil.py`: aprovada.
- `compileall` do pacote RC5.4.1 com o hotfix sobreposto: aprovado.
- Suíte automatizada da RC5.4 + hotfix: 11 testes, 11 aprovados.
- Renderização do card com avaliação completa: aprovada.
- Renderização do card com avaliação parcial: aprovada.
- Renderização do card sem avaliação: aprovada.
- Projeção de idade de 22 em 2026 para 26 em 2030: aprovada.
- Verificação de `Ciclo 2030`, posições curtas e ausência de posição longa: aprovada.
- Smoke isolado do Streamlit: servidor iniciado e `/_stcore/health` respondeu HTTP 200 / `ok`.

## Integridade dos JSONs
- `jogadores_hexa_2030.json`: JSON válido; SHA-256 `ab7ee9718cd2c34dd0393b9d746359b9cf2ba70fcf1bc557b696d1a5331cdbfb`; 77850 bytes.
- `avaliacoes_trimestrais_hexa_2030.json`: JSON válido; SHA-256 `eb846b4886080beb2e1bbce119a650cc1f93c9b9d14940446c97cbfbc18a3e8d`; 33664 bytes.
- `enriquecimentos_tm.json`: JSON válido; SHA-256 `72dd628b1c5dcdfe83125c02b254b389f1ec3ae4d61372888d011bd064bcab58`; 66623 bytes.

Nenhum JSON foi incluído ou modificado pelo hotfix.

## Testes não realizados

- Inicialização do entrypoint completo com todos os módulos reais do repositório.
- Suíte histórica completa fora do pacote RC5.4 disponibilizado.
- Smoke visual real no Streamlit Community Cloud após o deploy.

O smoke do Streamlit executado nesta entrega foi isolado para o card corrigido.
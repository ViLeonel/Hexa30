# CONTEXTO DO PROJETO — O CAMINHO PARA O HEXA 2030

## Objetivo
Aplicativo Streamlit para:
- acompanhar jogadores brasileiros com horizonte na Copa de 2030;
- registrar avaliações editoriais de Vini e Beto;
- montar escalações táticas;
- selecionar titulares e reservas;
- analisar idade, posição, clube e valor de mercado;
- preservar o histórico qualitativo das conversas sobre cada atleta.

## Responsáveis
- Vini Leonel
- Beto Muñoz

A conversa entre os dois é a fonte editorial central do projeto. Dados externos complementam, mas não substituem, a avaliação própria.

## Hospedagem
- Código versionado no GitHub.
- Aplicação hospedada no Streamlit Community Cloud.
- Arquivos principais ficam na raiz do repositório.
- Imports locais usam nomes prefixados por `hexa_` para reduzir conflitos.

## Estado arquitetural
- Entry point: `caminho_hexa_2030.py`
- Componentes: `hexa_components.py`
- Dados e regras de normalização: `hexa_data.py`
- Contrato e persistência: `hexa_repository.py`
- Estilos: `hexa_styles.py`
- Regras táticas: `hexa_taticas.py`
- Base: `jogadores_hexa_2030.json`
- Dependências: `requirements.txt`

## Dados editoriais protegidos
- notas de Vini e Beto;
- pontos fortes;
- pontos fracos;
- histórico;
- posições definidas pelo projeto;
- grupo;
- tipo legado.

## Dados externos
Campos cadastrais e de mercado podem ser atualizados por enriquecimento seguro:
- nome completo;
- nascimento;
- naturalidade;
- altura;
- nacionalidades;
- pé;
- empresário;
- clube;
- chegada ao clube;
- contrato;
- renovação;
- equipador;
- posição informada pela fonte;
- valor atual;
- maior valor;
- datas de atualização.

## Decisões recentes de UX
- busca de atleta pesquisável;
- nenhum atleta pré-selecionado;
- titulares e reservas começam vazios;
- notas somente para leitura;
- remoção visual da classificação `tipo`;
- remoção de corte de jogador;
- remoção de compartilhamento público;
- formulário com “Sugerir jogador” e “Sugerir melhoria”;
- limite de 11 titulares e 15 reservas.

## Protocolo de entrega
Toda alteração de código deve gerar arquivos completos, testados e prontos para deploy. O usuário não deve receber apenas linhas para substituir.
- Modelos e schema: `hexa_models.py`

## Concorrência da persistência JSON
- Cada carregamento recebe uma versão SHA-256 da fonte.
- Escritas da interface usam bloqueio otimista.
- Sessões antigas não podem sobrescrever uma versão mais recente.
- Conflitos exigem recarregar a aplicação.
- A gravação continua atômica e mantém backup.
- Um arquivo `.meta.json` registra versão, data UTC e origem da alteração.
- O JSON continua não sendo uma solução de persistência multiusuário completa.

## Estado de release

A arquitetura consolidada está identificada como `1.0.0-rc1`.
Os contratos públicos são protegidos por testes, o grafo de imports não possui
ciclos e o GitHub Actions valida Python 3.10 a 3.14.

## Auditoria operacional

Alterações persistidas podem gerar eventos em `auditoria_jogadores.jsonl`.
O histórico é separado da fonte canônica dos atletas e não deve ser usado para
substituir `historico`, que continua sendo conteúdo editorial de Vini e Beto.


---

## Estado de release — RC5 Avaliações Trimestrais e Histórico

A partir da RC5:

- `jogadores_hexa_2030.json` continua canônico para cadastro, posições, clube,
  mercado e regras táticas;
- cada jogador possui `id_atleta` estável;
- `avaliacoes_trimestrais_hexa_2030.json` é a fonte canônica das avaliações;
- `hexa_avaliacoes.py` valida e recalcula indicadores temporais;
- a primeira referência oficial é T2 2026, em 30/06/2026;
- T1 2026 não faz parte do histórico;
- avaliações antigas ficam arquivadas e inativas na interface pública;
- ausências permanecem nulas e nunca são convertidas em zero;
- correções retroativas exigem ação explícita;
- cada página que apresenta avaliação informa período e data de referência;
- dados de mercado continuam com datas próprias e não equivalem a desempenho.

## Fluxo trimestral

A planilha compartilhada é a fonte editorial de entrada. A publicação segue:

```text
planilha validada
→ importador append-only
→ JSON temporal
→ testes
→ revisão no GitHub
→ deploy no Streamlit Community Cloud
```

A chave lógica de uma avaliação é `id_atleta + periodo`.

## Estado após a RC5.1

A RC5.1 finaliza a primeira etapa pública com:

- espaçamento superior mais compacto no conteúdo e na barra lateral;
- acessibilidade recolhida no final da barra lateral;
- reconciliação global da convocação antes dos widgets;
- proibição de duplicidade entre titulares, reservas posicionais e vagas livres;
- persistência automática da última seleção por formação no `localStorage`;
- armazenamento por `id_atleta`, nunca pelo nome de exibição;
- restauração segura com descarte de IDs inexistentes e incompatibilidades;
- cartões compactos para situação, saldo projetado e data de referência;
- terminologia explícita para pico de valor de mercado;
- busca com exemplo neutro: `Real Madrid ou Vini Jr`.

A seleção local pertence exclusivamente ao navegador e dispositivo do usuário.
Ela não é enviada ao servidor e não sincroniza entre dispositivos.


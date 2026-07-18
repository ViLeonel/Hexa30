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
- formulário lateral com “Sugerir jogador” e “Sugerir melhoria”;
- lista pública sem função de adicionar atleta;
- limite de 11 titulares e 15 reservas;
- banco com 11 vagas posicionais espelhadas na tática e 4 vagas livres;
- vagas livres ordenadas pela prioridade posicional da formação;
- nomes públicos dos analistas: Vini Leonel/Vini e Beto Muñoz/Beto.

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

A entrega atual está identificada como `1.0.0-rc4-ux-convocacao`.
A RC4 preserva os contratos de dados das versões anteriores e altera somente
apresentação, navegação e estado da convocação. A validação completa em Python
3.10 a 3.14 continua a cargo da matriz configurada no GitHub Actions.

## Auditoria operacional

Alterações persistidas podem gerar eventos em `auditoria_jogadores.jsonl`.
O histórico é separado da fonte canônica dos atletas e não deve ser usado para
substituir `historico`, que continua sendo conteúdo editorial de Vini e Beto.

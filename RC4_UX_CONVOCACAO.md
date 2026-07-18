# RC4 — UX e Convocação

## Identificação

- Versão: `1.0.0-rc4-ux-convocacao`
- Entrypoint preservado: `caminho_hexa_2030.py`
- Dependências preservadas: `streamlit==1.59.2`, `pandas==2.3.3`
- Fonte canônica preservada: `jogadores_hexa_2030.json`

## Arquitetura e raciocínio

A RC4 mantém o entrypoint como roteador e concentra:

- identidade, menus e nomes dos analistas em `hexa_config.py`;
- composição das quatro telas em `hexa_pages.py`;
- regras puras do estado da convocação em `hexa_session.py`;
- transformações de tabelas e texto editorial em `hexa_selectors.py`;
- responsividade, troféu vetorial e design system em `hexa_styles.py`;
- exibição da versão corrente na área privada em `hexa_admin.py`.

Nenhuma regra de persistência, schema, auditoria ou enriquecimento externo foi
alterada. A função técnica `adicionar_jogador()` permanece disponível no módulo
de dados para uso futuro da área administrativa, mas deixou de ser importada ou
exposta pela interface pública.

## Alterações implementadas

### Cabeçalho principal

- Troféu genérico substituído por SVG autoral, local e responsivo, inspirado na
  silhueta de troféus mundiais.
- O SVG não depende de CDN, fonte de ícones nem arquivo externo.
- A ilustração é decorativa (`aria-hidden`) e o título continua textual.
- Nova descrição explica o propósito e o fluxo de uso do aplicativo.

### Banco de reservas

- 11 vagas posicionais espelham, na mesma ordem, os 11 slots da formação ativa.
- Cada vaga aceita somente atletas compatíveis com as posições editoriais do slot.
- 4 vagas livres aceitam qualquer posição oficial.
- Nas vagas livres, os jogadores são ordenados pela sequência posicional da
  formação ativa e, em seguida, pelo nome.
- Titulares e reservas não podem se repetir.
- O estado antigo do multiselect é migrado em sessão para os novos slots.
- A troca de formação mantém estados separados por chave estável.
- O botão de limpeza remove titulares, reservas posicionais, vagas livres e a
  chave legada da formação ativa.

### Textos e navegação

- `Perfis & Scout` → `Jogadores, Scout e Avaliações`.
- `Gestão do Roster` → `Lista de Jogadores`.
- `Análise de Opiniões` → `Análises & Mercado`.
- Removida a frase sobre a pesquisa começar vazia.
- Removido o subtítulo da lista e o formulário público de cadastro.
- Adicionado o subtítulo `Compilado de avaliações para o Ciclo 2030`.
- Mantida a seção independente `Leitura de mercado`.

### Identidade editorial

- Nomes longos: `Vini Leonel` e `Beto Muñoz`.
- Nomes curtos: `Vini` e `Beto`.
- A chave interna `nota_roberto` permanece inalterada.
- Históricos antigos são ajustados somente na apresentação; o JSON não é
  reescrito.
- `Vinicius Junior`, como nome de atleta, não é modificado.

## Arquivos alterados

- `hexa_admin.py`
- `hexa_config.py`
- `hexa_pages.py`
- `hexa_selectors.py`
- `hexa_session.py`
- `hexa_styles.py`
- `CONTEXTO_PROJETO.md`
- `HISTORICO_REFATORACOES.md`

## Arquivos adicionados

- `tests/test_rc4_convocacao.py`
- `tests/test_rc4_ux.py`
- `RC4_UX_CONVOCACAO.md`
- `RELATORIO_TESTES_RC4.txt`
- `MANIFESTO_SHA256.txt`

`requirements.txt` está incluído sem alteração para facilitar o deploy.

## Integridade dos dados

Os JSONs canônicos não integram o pacote de substituição e não foram editados.

- `jogadores_hexa_2030.json`
  - 61 atletas
  - SHA-256: `cefc26680b407f645eb72d013e3c1e78ada06cdc764c2bdef79df06053a659c1`
- `enriquecimentos_tm.json`
  - 58 registros
  - SHA-256: `72dd628b1c5dcdfe83125c02b254b389f1ec3ae4d61372888d011bd064bcab58`

Todos os 61 atletas possuem os campos protegidos verificados:

`nota_vini`, `nota_roberto`, `pontos_fortes`, `pontos_fracos`, `historico`,
`posicao`, `posicoes_multiplas`, `grupo` e `tipo`.

## Testes realizados

- compilação dos seis arquivos Python alterados e dos dois testes;
- parse com gramática do Python 3.10;
- verificação estática de símbolos importados entre os arquivos alterados;
- varredura de dependências externas;
- instalação isolada de `streamlit==1.59.2` e `pandas==2.3.3`;
- 11 testes unitários específicos da RC4 aprovados em harness isolado;
- smoke test com `streamlit.testing.v1.AppTest` nas quatro telas;
- smoke test do entrypoint com dublês apenas para módulos não materializados;
- 27 selectboxes na tela de campo:
  - 1 formação;
  - 11 titulares;
  - 11 reservas posicionais;
  - 4 vagas livres;
- exclusão de um titular das opções de reserva;
- ordenação tática nas vagas livres;
- abertura de perfil selecionado com `Beto` visível e sem o nome público antigo;
- parse dos dois JSONs e verificação dos campos protegidos;
- comparação SHA-256 dos JSONs antes e depois.

## Resultados

- Testes RC4: 11 aprovados.
- Exceções nos smoke tests das quatro telas: 0.
- Exceções no smoke test do entrypoint isolado: 0.
- JSONs modificados: 0.
- Dependências novas: 0.

## Limites da validação

Os módulos não alterados `hexa_taticas.py`, `hexa_components.py`,
`hexa_messages.py`, `hexa_auth.py`, `hexa_repository.py` e `hexa_models.py`,
assim como a suíte histórica completa, não estavam materializados no sandbox.
Por isso, os testes locais usaram dublês apenas para essas dependências.

Ainda precisam ser executados no repositório completo:

- `python -m unittest discover -s tests -v` com toda a suíte histórica;
- `python scripts/rc1_smoke.py`;
- inicialização real com todos os módulos do repositório;
- matriz GitHub Actions em Python 3.10–3.14;
- inspeção visual em Chrome, Firefox, Edge, Brave e Safari;
- navegação integral por teclado;
- VoiceOver, NVDA/JAWS e TalkBack;
- zoom real de 200%.

## Deploy no GitHub

1. Crie uma branch:

```bash
git checkout -b rc4-ux-convocacao
```

2. Extraia o ZIP e copie seu conteúdo para a raiz do repositório, preservando a
pasta `tests/`. Não substitua os JSONs canônicos.

3. Execute no repositório completo:

```bash
python -m pip install -r requirements.txt
python -m compileall -q .
python -m unittest discover -s tests -v
python scripts/rc1_smoke.py
streamlit run caminho_hexa_2030.py
```

4. Revise a interface e publique:

```bash
git add hexa_admin.py hexa_config.py hexa_pages.py hexa_selectors.py \
  hexa_session.py hexa_styles.py CONTEXTO_PROJETO.md \
  HISTORICO_REFATORACOES.md tests/test_rc4_convocacao.py \
  tests/test_rc4_ux.py RC4_UX_CONVOCACAO.md RELATORIO_TESTES_RC4.txt \
  MANIFESTO_SHA256.txt requirements.txt

git commit -m "feat: RC4 de UX e convocação posicional"
git push -u origin rc4-ux-convocacao
```

5. Abra um Pull Request e confirme a matriz do GitHub Actions antes do merge.

## Deploy no Streamlit Community Cloud

- Main file path: `caminho_hexa_2030.py`.
- Mantenha `requirements.txt` na raiz.
- Preserve os Secrets OIDC existentes.
- Após o merge, abra o app e use **Reboot app** se o deploy não reiniciar
  automaticamente.
- Faça um smoke manual nas quatro páginas e confirme que:
  - os novos títulos aparecem no menu;
  - o campo abre vazio;
  - há 11 vagas posicionais e 4 livres;
  - não há cadastro público;
  - as tabelas mostram `Vini` e `Beto`.

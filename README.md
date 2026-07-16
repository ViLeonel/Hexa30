# 🏆 O Caminho para o Hexa 2030 — Inteligência Tática e Scout da Seleção Brasileira

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badge-svg.svg)](https://share.streamlit.io/)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)

O **Caminho para o Hexa 2030** é um aplicativo interativo de análise de desempenho e simulação tática voltado ao planejamento e renovação geracional da Seleção Brasileira de Futebol para a Copa do Mundo de 2030. 

Idealizado em São Paulo, Brasil, pelos analistas **Vini Leonel** e **Beto Muñoz**, o projeto nasceu em 15 de julho de 2026 como um método estruturado para registrar debates táticos, calibrar notas de atletas e projetar o envelhecimento do elenco até o mundial. Hoje, a plataforma conta com um motor de busca dinâmico (Web Scraping) integrado aos dados oficiais da CBF para monitoramento de atletas atuando no futebol brasileiro.

---

## 🎨 Design Tático "Azul Canarinho" & Acessibilidade (WCAG)

O aplicativo adota uma identidade visual moderna inspirada no segundo uniforme da Seleção Brasileira, otimizada para longos períodos de leitura e análise técnica (Dark Mode nativo):
*   **Fundo Principal (Soft Navy & Grafite):** Combinação de `#090D16` e `#111827` para eliminar a fadiga visual.
*   **Destaques (Ouro Queimado / Amarelo Matte):** Linhas de campo e badges em `#EAB308` para contraste perfeito.
*   **O "Blue Pitch":** Um campo de futebol estilizado em degradê azul royal e azul marinho, com marcações táticas flexíveis e responsivas (otimizadas para Safari, Chrome, Edge, Brave e celulares Android/iOS).

---

## ⚡ Principais Funcionalidades

### 🏟️ 1. Simulador de Campo Dinâmico (4-3-3 de Carlo Ancelotti)
*   **Escalação Inteligente:** Permite alterar os titulares da equipe diretamente em um campinho tático.
*   **Validação de Posições:** O sistema bloqueia improvisações absurdas. Jogadores atuam estritamente em suas funções de origem (ex: zagueiros na zaga, pontas na ponta), respeitando versatilidades cadastradas pela comissão (ex: Lucas Beraldo atuando como Primeiro Volante ou Gabriel Martinelli como Meia Criativo).
*   **Métricas Coletivas:** Exibição da média geral do time com base nas visões táticas separadas de Vini e de Roberto.

### 📊 2. Integração em Tempo Real com a CBF (Live Scraping)
*   **Busca Dinâmica:** Monitoramento de atletas em solo nacional (como Brazão, Wesley, Kaiki Bruno, Luciano Juba, Breno Bidon, Gabriel Mec e Estêvão).
*   **Web Scraper Nativo:** O app faz requisições automáticas no portal de tabelas da **CBF** para trazer classificação, pontos, jogos e vitórias do clube do atleta em tempo real, com *fallback* inteligente para cache local em caso de instabilidade na rede.

### 👥 3. Dossiê de Atletas & Painel de Divergências
*   **Histórico de Debates:** Exposição clara de pontos fortes, pontos fracos e os argumentos clássicos que dividem a opinião da dupla Vini & Roberto.
*   **Análise de Opiniões:** Gráficos e tabelas automáticas que mostram as maiores concordâncias técnicas e as divergências mais calorosas de mesa de bar.

### 💡 4. Radar do Torcedor (Caixa de Sugestões)
*   Formulário seguro para que visitantes sugiram novos talentos promissores para o radar 2030, gerando um envio direto e amigável por e-mail sem expor os endereços pessoais de contato a robôs de spam.

---

## ⚙️ Instalação e Execução Local

Se você deseja executar o projeto localmente em sua máquina, certifique-se de ter o Python 3.10 ou superior instalado e siga os passos abaixo:

### 1. Clonar o Repositório
```bash
git clone [https://github.com/ViLeonel/Hexa30.git](https://github.com/ViLeonel/Hexa30.git)
cd Hexa30

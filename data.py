"""Persistência, migrações e tratamento de dados do projeto.

O JSON é a fonte canônica do elenco. Este módulo mantém somente migrações e
enriquecimentos incrementais, evitando uma segunda cópia completa da base.
Campos editoriais e táticos do projeto nunca são sobrescritos por dados externos.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from taticas import POSICOES_OFICIAIS, normalizar_lista_posicoes, normalizar_posicao

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "jogadores_hexa_2030.json"

CAMPOS_EDITORIAIS_PROTEGIDOS = {
    "nota_vini",
    "nota_roberto",
    "pontos_fortes",
    "pontos_fracos",
    "historico",
}

CAMPOS_TATICOS_PROTEGIDOS = {
    "posicao",
    "posicoes_multiplas",
    "grupo",
    "tipo",
}

CAMPOS_MINIMOS: dict[str, Any] = {
    "nome": "",
    "posicao": "Centroavante",
    "posicoes_multiplas": [],
    "clube": "N/A",
    "idade": 22,
    "grupo": "Observação",
    "tipo": "Observação",
    "nota_vini": 0.0,
    "nota_roberto": 0.0,
    "pontos_fortes": "",
    "pontos_fracos": "",
    "historico": "",
}

ALIASES_JOGADORES = {
    "Vini Jr.": "Vinicius Junior",
    "Wesley": "Wesley França",
}

# Dados externos extraídos dos anexos enviados pelo usuário em 17/07/2026.
# Posições táticas do projeto não são alteradas por esta estrutura.
ENRIQUECIMENTOS_EXTERNOS: dict[str, dict[str, Any]] = {
    "Antony": {
        "nome": "Antony",
        "nome_completo": "Antony Matheus dos Santos",
        "posicao": "Ponta-direita",
        "posicoes_multiplas": ["Ponta-direita", "Ponta-esquerda"],
        "clube": "Real Betis",
        "idade": 26,
        "grupo": "Observação",
        "tipo": "Observação",
        "nota_vini": 0.0,
        "nota_roberto": 0.0,
        "pontos_fortes": "",
        "pontos_fracos": "",
        "historico": "",
        "tm_nascimento": "24/02/2000",
        "tm_naturalidade": "São Paulo, Brasil",
        "tm_altura": "1,72 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "4ComM",
        "tm_clube_desde": "01/09/2025",
        "tm_contrato": "30/06/2030",
        "tm_equipador": "Puma",
        "tm_posicao_site": "Extremo Direito",
        "tm_posicoes_secundarias_site": ["Extremo Esquerdo"],
        "tm_valor_mercado": "40,00 M. €",
        "tm_valor_mercado_milhoes": 40.0,
        "tm_valor_maximo": "75,00 M. €",
        "tm_valor_maximo_milhoes": 75.0,
        "tm_data_valor_maximo": "14/09/2022",
        "tm_ultima_atualizacao": "04/06/2026",
    },
    "Vinicius Junior": {
        "nome_completo": "Vinicius José Paixão de Oliveira Junior",
        "clube": "Real Madrid CF",
        "idade": 26,
        "tm_nascimento": "12/07/2000",
        "tm_naturalidade": "São Gonçalo, Brasil",
        "tm_altura": "1,76 m",
        "tm_nacionalidades": ["Brasil", "Espanha"],
        "tm_pe": "Direito",
        "tm_empresario": "Roc Nation Sports",
        "tm_clube_desde": "12/07/2018",
        "tm_contrato": "30/06/2027",
        "tm_ultima_renovacao": "31/10/2023",
        "tm_equipador": "Nike",
        "tm_posicao_site": "Extremo Esquerdo",
        "tm_posicoes_secundarias_site": ["Ponta de Lança"],
        "tm_valor_mercado": "140,00 M. €",
        "tm_valor_mercado_milhoes": 140.0,
        "tm_valor_maximo": "200,00 M. €",
        "tm_valor_maximo_milhoes": 200.0,
        "tm_data_valor_maximo": "10/10/2024",
        "tm_ultima_atualizacao": "04/06/2026",
    },
    "Endrick": {
        "nome_completo": "Endrick Felipe Moreira de Sousa",
        "clube": "Real Madrid CF",
        "idade": 19,
        "tm_nascimento": "21/07/2006",
        "tm_naturalidade": "Taguatinga, Brasil",
        "tm_altura": "1,72 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "Roc Nation Sports",
        "tm_clube_desde": "21/07/2024",
        "tm_contrato": "30/06/2030",
        "tm_equipador": "New Balance",
        "tm_posicao_site": "Ponta de Lança",
        "tm_posicoes_secundarias_site": ["Segundo Avançado", "Extremo Direito"],
        "tm_valor_mercado": "40,00 M. €",
        "tm_valor_mercado_milhoes": 40.0,
        "tm_valor_maximo": "60,00 M. €",
        "tm_valor_maximo_milhoes": 60.0,
        "tm_data_valor_maximo": "16/04/2024",
        "tm_ultima_atualizacao": "31/05/2026",
    },
    "Alisson": {
        "nome_completo": "Alisson Ramses Becker",
        "clube": "Liverpool FC",
        "idade": 33,
        "tm_nascimento": "02/10/1992",
        "tm_naturalidade": "Novo Hamburgo, Brasil",
        "tm_altura": "1,93 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Direito",
        "tm_empresario": "NWS - Neis World Sports",
        "tm_clube_desde": "19/07/2018",
        "tm_contrato": "30/06/2027",
        "tm_ultima_renovacao": "04/08/2021",
        "tm_equipador": "Nike",
        "tm_posicao_site": "Guarda-redes",
        "tm_posicoes_secundarias_site": [],
        "tm_valor_mercado": "15,00 M. €",
        "tm_valor_mercado_milhoes": 15.0,
        "tm_valor_maximo": "90,00 M. €",
        "tm_valor_maximo_milhoes": 90.0,
        "tm_data_valor_maximo": "09/12/2019",
        "tm_ultima_atualizacao": "02/06/2026",
    },
    "Andrey Santos": {
        "nome_completo": "Andrey Nascimento dos Santos",
        "clube": "Manchester United FC",
        "idade": 22,
        "tm_nascimento": "03/05/2004",
        "tm_naturalidade": "Rio de Janeiro, Brasil",
        "tm_altura": "1,80 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Direito",
        "tm_empresario": "Bertolucci Sports",
        "tm_clube_desde": "13/07/2026",
        "tm_contrato": "30/06/2031",
        "tm_opcao_contrato": "Opção do clube por mais 1 ano",
        "tm_equipador": "adidas",
        "tm_posicao_site": "Médio Centro",
        "tm_posicoes_secundarias_site": ["Médio Defensivo"],
        "tm_valor_mercado": "40,00 M. €",
        "tm_valor_mercado_milhoes": 40.0,
        "tm_valor_maximo": "45,00 M. €",
        "tm_valor_maximo_milhoes": 45.0,
        "tm_data_valor_maximo": "08/03/2026",
        "tm_ultima_atualizacao": "02/06/2026",
    },
    "Allan": {
        "nome_completo": "Allan Andrade Elias",
        "clube": "SE Palmeiras",
        "idade": 22,
        "tm_nascimento": "19/04/2004",
        "tm_naturalidade": "Florianópolis, Brasil",
        "tm_altura": "1,74 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "Talents Sports",
        "tm_clube_desde": "10/01/2025",
        "tm_contrato": "31/12/2029",
        "tm_ultima_renovacao": "07/06/2025",
        "tm_posicao_site": "Extremo Direito",
        "tm_posicoes_secundarias_site": ["Médio Ofensivo", "Médio Direito"],
        "tm_valor_mercado": "20,00 M. €",
        "tm_valor_mercado_milhoes": 20.0,
        "tm_valor_maximo": "20,00 M. €",
        "tm_valor_maximo_milhoes": 20.0,
        "tm_data_valor_maximo": "25/05/2026",
        "tm_ultima_atualizacao": "25/05/2026",
    },
    "Diego Callai": {
        "nome_completo": "Diego Callai Silva",
        "clube": "Sporting CP B",
        "idade": 21,
        "tm_nascimento": "18/07/2004",
        "tm_naturalidade": "Caxias do Sul, Brasil",
        "tm_altura": "1,92 m",
        "tm_nacionalidades": ["Brasil", "Portugal"],
        "tm_pe": "Direito",
        "tm_empresario": "AS1",
        "tm_clube_desde": "01/01/2025",
        "tm_contrato": "30/06/2030",
        "tm_posicao_site": "Guarda-redes",
        "tm_posicoes_secundarias_site": [],
        "tm_valor_mercado": "1,50 M. €",
        "tm_valor_mercado_milhoes": 1.5,
        "tm_valor_maximo": "1,50 M. €",
        "tm_valor_maximo_milhoes": 1.5,
        "tm_data_valor_maximo": "23/06/2026",
        "tm_ultima_atualizacao": "23/06/2026",
    },
    "Luis Gustavo": {
        "nome_completo": "Luis Gustavo Roncholeta Benedetti",
        "clube": "SE Palmeiras",
        "idade": 20,
        "tm_nascimento": "07/06/2006",
        "tm_naturalidade": "Bauru, Brasil",
        "tm_altura": "1,97 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "Bertolucci Sports",
        "tm_clube_desde": "07/01/2025",
        "tm_contrato": "31/12/2029",
        "tm_ultima_renovacao": "15/04/2025",
        "tm_posicao_site": "Defesa Central",
        "tm_posicoes_secundarias_site": [],
        "tm_valor_mercado": "4,00 M. €",
        "tm_valor_mercado_milhoes": 4.0,
        "tm_valor_maximo": "4,00 M. €",
        "tm_valor_maximo_milhoes": 4.0,
        "tm_data_valor_maximo": "09/12/2025",
        "tm_ultima_atualizacao": "25/05/2026",
    },
    "André": {
        "nome_completo": "André Trindade da Costa Neto",
        "clube": "Wolverhampton Wanderers",
        "idade": 25,
        "tm_nascimento": "16/07/2001",
        "tm_naturalidade": "Ibirataia, Brasil",
        "tm_altura": "1,76 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Direito",
        "tm_empresario": "Carlos Leite",
        "tm_clube_desde": "30/08/2024",
        "tm_contrato": "30/06/2030",
        "tm_ultima_renovacao": "22/05/2026",
        "tm_equipador": "Nike",
        "tm_posicao_site": "Médio Defensivo",
        "tm_posicoes_secundarias_site": ["Médio Centro"],
        "tm_valor_mercado": "25,00 M. €",
        "tm_valor_mercado_milhoes": 25.0,
        "tm_valor_maximo": "28,00 M. €",
        "tm_valor_maximo_milhoes": 28.0,
        "tm_data_valor_maximo": "29/05/2025",
        "tm_ultima_atualizacao": "02/06/2026",
    },
    "Brazão": {
        "nome_completo": "Gabriel Nascimento Resende Brazão",
        "clube": "Santos FC",
        "idade": 25,
        "tm_nascimento": "05/10/2000",
        "tm_naturalidade": "Uberlândia, Brasil",
        "tm_altura": "1,92 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Direito",
        "tm_empresario": "Bertolucci Sports",
        "tm_clube_desde": "26/02/2024",
        "tm_contrato": "31/12/2028",
        "tm_ultima_renovacao": "23/11/2024",
        "tm_equipador": "Puma",
        "tm_posicao_site": "Guarda-redes",
        "tm_posicoes_secundarias_site": [],
        "tm_valor_mercado": "12,00 M. €",
        "tm_valor_mercado_milhoes": 12.0,
        "tm_valor_maximo": "12,00 M. €",
        "tm_valor_maximo_milhoes": 12.0,
        "tm_data_valor_maximo": "11/03/2026",
        "tm_ultima_atualizacao": "25/05/2026",
    },
    "Breno Bidon": {
        "nome_completo": "Breno de Souza Bidon",
        "clube": "SC Corinthians",
        "idade": 21,
        "tm_nascimento": "20/02/2005",
        "tm_naturalidade": "São Paulo, Brasil",
        "tm_altura": "1,78 m",
        "tm_nacionalidades": ["Brasil", "Itália"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "Dodici Sports BR",
        "tm_clube_desde": "01/03/2024",
        "tm_contrato": "31/12/2029",
        "tm_ultima_renovacao": "06/01/2025",
        "tm_posicao_site": "Médio Centro",
        "tm_posicoes_secundarias_site": ["Médio Ofensivo", "Médio Defensivo"],
        "tm_valor_mercado": "22,00 M. €",
        "tm_valor_mercado_milhoes": 22.0,
        "tm_valor_maximo": "22,00 M. €",
        "tm_valor_maximo_milhoes": 22.0,
        "tm_data_valor_maximo": "11/06/2026",
        "tm_ultima_atualizacao": "25/05/2026",
    },
    "Bruno Guimarães": {
        "nome_completo": "Bruno Guimarães Rodrigues Moura",
        "clube": "Newcastle United",
        "idade": 28,
        "tm_nascimento": "16/11/1997",
        "tm_naturalidade": "Rio de Janeiro, Brasil",
        "tm_altura": "1,82 m",
        "tm_nacionalidades": ["Brasil", "Espanha"],
        "tm_pe": "Direito",
        "tm_empresario": "Bertolucci Sports",
        "tm_clube_desde": "30/01/2022",
        "tm_contrato": "30/06/2028",
        "tm_ultima_renovacao": "07/10/2023",
        "tm_equipador": "adidas",
        "tm_posicao_site": "Médio Centro",
        "tm_posicoes_secundarias_site": ["Médio Defensivo"],
        "tm_valor_mercado": "70,00 M. €",
        "tm_valor_mercado_milhoes": 70.0,
        "tm_valor_maximo": "85,00 M. €",
        "tm_valor_maximo_milhoes": 85.0,
        "tm_data_valor_maximo": "08/10/2023",
        "tm_ultima_atualizacao": "02/06/2026",
    },
    "Carlos Miguel": {
        "nome_completo": "Carlos Miguel dos Santos Pereira",
        "clube": "SE Palmeiras",
        "idade": 27,
        "tm_nascimento": "09/10/1998",
        "tm_naturalidade": "Rio das Ostras, Brasil",
        "tm_altura": "2,04 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "Bertolucci Sports",
        "tm_clube_desde": "19/08/2025",
        "tm_contrato": "31/07/2030",
        "tm_equipador": "Nike",
        "tm_posicao_site": "Guarda-redes",
        "tm_posicoes_secundarias_site": [],
        "tm_valor_mercado": "7,00 M. €",
        "tm_valor_mercado_milhoes": 7.0,
        "tm_valor_maximo": "7,00 M. €",
        "tm_valor_maximo_milhoes": 7.0,
        "tm_data_valor_maximo": "25/05/2026",
        "tm_ultima_atualizacao": "25/05/2026",
    },
    "Danilo": {
        "nome_completo": "Danilo dos Santos de Oliveira",
        "clube": "Botafogo FR",
        "idade": 25,
        "tm_nascimento": "29/04/2001",
        "tm_naturalidade": "Salvador, Brasil",
        "tm_altura": "1,77 m",
        "tm_nacionalidades": ["Brasil"],
        "tm_pe": "Esquerdo",
        "tm_empresario": "Bertolucci Sports",
        "tm_clube_desde": "18/07/2025",
        "tm_contrato": "30/06/2029",
        "tm_equipador": "Nike",
        "tm_posicao_site": "Médio Centro",
        "tm_posicoes_secundarias_site": ["Médio Defensivo", "Médio Ofensivo"],
        "tm_valor_mercado": "32,00 M. €",
        "tm_valor_mercado_milhoes": 32.0,
        "tm_valor_maximo": "32,00 M. €",
        "tm_valor_maximo_milhoes": 32.0,
        "tm_data_valor_maximo": "25/05/2026",
        "tm_ultima_atualizacao": "25/05/2026",
    },
}


class DataIntegrityError(RuntimeError):
    """Indica que o JSON não pôde ser lido sem risco de perda de dados."""


def extrair_numero(valor_texto: Any, padrao: float = 0.0) -> float:
    """Extrai o primeiro número de um texto, aceitando vírgula ou ponto decimal."""
    if valor_texto is None:
        return padrao
    if isinstance(valor_texto, (int, float)):
        return float(valor_texto)
    texto = str(valor_texto).strip().lower()
    if not texto or texto == "n/a":
        return padrao
    numeros = re.findall(r"[0-9]+(?:[.,][0-9]+)?", texto)
    if not numeros:
        return padrao
    try:
        return float(numeros[0].replace(",", "."))
    except ValueError:
        return padrao


def extrair_valor_milhoes(valor_texto: Any, padrao: float = 0.0) -> float:
    """Converte valores como '175 mil €' e '40,00 M. €' para milhões de euros."""
    if valor_texto is None:
        return padrao
    if isinstance(valor_texto, (int, float)):
        return float(valor_texto)

    texto = str(valor_texto).strip().lower().replace("\u00a0", " ")
    valor = extrair_numero(texto, padrao)
    if valor == padrao and not re.search(r"\d", texto):
        return padrao

    if re.search(r"\b(mil|k)\b", texto):
        return valor / 1000.0
    if re.search(r"\b(bi|bilh(?:ão|oes|ões)?)\b", texto):
        return valor * 1000.0
    return valor


def extrair_altura_metros(valor_texto: Any, padrao: float = 0.0) -> float:
    valor = extrair_numero(valor_texto, padrao)
    if valor > 3:
        return valor / 100.0
    return valor


def formatar_valor_milhoes(valor: float | int | None) -> str:
    if valor is None:
        return "N/A"
    numero = float(valor)
    if numero <= 0:
        return "N/A"
    if numero < 1:
        return f"€ {numero * 1000:.0f} mil"
    return f"€ {numero:.2f} mi".replace(".", ",")


def percentual_do_pico(dados: Mapping[str, Any]) -> float | None:
    atual = valor_mercado_atual(dados)
    maximo = valor_mercado_maximo(dados)
    if atual <= 0 or maximo <= 0:
        return None
    return min((atual / maximo) * 100.0, 100.0)


def valor_mercado_atual(dados: Mapping[str, Any]) -> float:
    numerico = dados.get("tm_valor_mercado_milhoes")
    if isinstance(numerico, (int, float)):
        return float(numerico)
    return extrair_valor_milhoes(dados.get("tm_valor_mercado"), 0.0)


def valor_mercado_maximo(dados: Mapping[str, Any]) -> float:
    numerico = dados.get("tm_valor_maximo_milhoes")
    if isinstance(numerico, (int, float)):
        return float(numerico)
    return extrair_valor_milhoes(dados.get("tm_valor_maximo"), 0.0)


def _reparar_json_simples(texto: str) -> dict[str, Any] | None:
    """Tenta reparar somente separadores ausentes entre objetos de primeiro nível."""
    reparado = re.sub(r"}\s*(\"[^\"]+\"\s*:\s*{)", r"},\n    \1", texto)
    try:
        resultado = json.loads(reparado)
    except json.JSONDecodeError:
        return None
    return resultado if isinstance(resultado, dict) else None


def _ler_json() -> tuple[dict[str, Any], bool]:
    if not DATA_FILE.exists():
        raise DataIntegrityError(
            f"Arquivo de dados não encontrado: {DATA_FILE.name}. "
            "Inclua o JSON na raiz do repositório."
        )

    texto = DATA_FILE.read_text(encoding="utf-8-sig")
    try:
        dados = json.loads(texto)
        if not isinstance(dados, dict):
            raise DataIntegrityError("O JSON precisa conter um objeto de jogadores no nível principal.")
        return dados, False
    except json.JSONDecodeError as erro_original:
        reparado = _reparar_json_simples(texto)
        if reparado is None:
            raise DataIntegrityError(
                f"O arquivo {DATA_FILE.name} está inválido e não foi sobrescrito. "
                f"Erro: {erro_original}"
            ) from erro_original

        carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = DATA_FILE.with_name(f"{DATA_FILE.stem}.corrompido-{carimbo}.json")
        backup.write_text(texto, encoding="utf-8")
        return reparado, True


def _normalizar_registro(nome_chave: str, registro: Mapping[str, Any]) -> dict[str, Any]:
    dados = dict(registro)
    dados["nome"] = str(dados.get("nome") or nome_chave).strip()

    posicao = normalizar_posicao(dados.get("posicao"))
    posicoes = normalizar_lista_posicoes(dados.get("posicoes_multiplas"))
    if not posicao and posicoes:
        posicao = posicoes[0]
    if not posicao:
        posicao = "Centroavante"
    if posicao not in posicoes:
        posicoes.insert(0, posicao)

    dados["posicao"] = posicao
    dados["posicoes_multiplas"] = posicoes

    for campo, valor_padrao in CAMPOS_MINIMOS.items():
        if campo not in dados or dados[campo] is None:
            dados[campo] = copy.deepcopy(valor_padrao)

    try:
        dados["idade"] = int(dados.get("idade", 22))
    except (TypeError, ValueError):
        dados["idade"] = 22

    for campo in ("nota_vini", "nota_roberto"):
        try:
            dados[campo] = float(dados.get(campo, 0.0))
        except (TypeError, ValueError):
            dados[campo] = 0.0

    # Garante campos numéricos mesmo quando a origem armazenou somente texto.
    if dados.get("tm_valor_mercado") and not isinstance(dados.get("tm_valor_mercado_milhoes"), (int, float)):
        dados["tm_valor_mercado_milhoes"] = extrair_valor_milhoes(dados["tm_valor_mercado"])
    if dados.get("tm_valor_maximo") and not isinstance(dados.get("tm_valor_maximo_milhoes"), (int, float)):
        dados["tm_valor_maximo_milhoes"] = extrair_valor_milhoes(dados["tm_valor_maximo"])

    return dados


def _mesclar_aliases(dados: dict[str, Any]) -> bool:
    alterado = False
    for antigo, novo in ALIASES_JOGADORES.items():
        if antigo not in dados:
            continue
        registro_antigo = dict(dados.pop(antigo))
        if novo not in dados:
            dados[novo] = registro_antigo
        else:
            for campo, valor in registro_antigo.items():
                if campo not in dados[novo] or dados[novo][campo] in (None, "", []):
                    dados[novo][campo] = valor
        dados[novo]["nome"] = novo
        alterado = True
    return alterado


def _aplicar_enriquecimentos(dados: dict[str, Any]) -> bool:
    alterado = False
    campos_protegidos = CAMPOS_EDITORIAIS_PROTEGIDOS | CAMPOS_TATICOS_PROTEGIDOS

    for nome, enriquecimento in ENRIQUECIMENTOS_EXTERNOS.items():
        if nome not in dados:
            dados[nome] = copy.deepcopy(enriquecimento)
            alterado = True
            continue

        registro = dados[nome]
        for campo, valor in enriquecimento.items():
            if campo in campos_protegidos:
                # A regra do treinador e os conteúdos editoriais prevalecem.
                if campo not in registro or registro[campo] in (None, "", []):
                    registro[campo] = copy.deepcopy(valor)
                    alterado = True
                continue

            if registro.get(campo) != valor:
                registro[campo] = copy.deepcopy(valor)
                alterado = True

    return alterado


def salvar_jogadores(dados: Mapping[str, Any]) -> None:
    """Grava JSON de forma atômica e mantém um backup da versão anterior."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporario = DATA_FILE.with_suffix(".json.tmp")
    backup = DATA_FILE.with_suffix(".json.bak")

    conteudo = json.dumps(dados, indent=4, ensure_ascii=False, sort_keys=False)
    temporario.write_text(conteudo + "\n", encoding="utf-8")

    # Valida o arquivo temporário antes de substituir a base.
    json.loads(temporario.read_text(encoding="utf-8"))

    if DATA_FILE.exists():
        shutil.copy2(DATA_FILE, backup)
    temporario.replace(DATA_FILE)


def carregar_jogadores() -> dict[str, dict[str, Any]]:
    """Carrega, migra e enriquece o JSON sem apagar conteúdo editorial."""
    dados_brutos, reparado = _ler_json()
    alterado = reparado or _mesclar_aliases(dados_brutos)

    normalizados: dict[str, dict[str, Any]] = {}
    for nome, registro in dados_brutos.items():
        if not isinstance(registro, Mapping):
            continue
        registro_normalizado = _normalizar_registro(nome, registro)
        chave = registro_normalizado.get("nome") or nome
        normalizados[str(chave)] = registro_normalizado
        if registro_normalizado != registro or chave != nome:
            alterado = True

    if _aplicar_enriquecimentos(normalizados):
        alterado = True

    # Segunda normalização cobre os atletas recém-injetados.
    normalizados = {
        nome: _normalizar_registro(nome, registro)
        for nome, registro in normalizados.items()
    }

    if alterado:
        salvar_jogadores(normalizados)
    return normalizados


def adicionar_jogador(
    jogadores: dict[str, dict[str, Any]],
    dados_novos: Mapping[str, Any],
) -> str:
    nome = str(dados_novos.get("nome", "")).strip()
    if not nome:
        raise ValueError("O nome do jogador é obrigatório.")
    if nome in jogadores:
        raise ValueError(f"O jogador '{nome}' já está cadastrado.")

    registro = copy.deepcopy(CAMPOS_MINIMOS)
    registro.update(dict(dados_novos))
    registro["nome"] = nome
    registro = _normalizar_registro(nome, registro)
    jogadores[nome] = registro
    salvar_jogadores(jogadores)
    return nome


def validar_posicoes(jogadores: Mapping[str, Mapping[str, Any]]) -> list[str]:
    erros: list[str] = []
    for nome, dados in jogadores.items():
        posicao = dados.get("posicao")
        if posicao not in POSICOES_OFICIAIS:
            erros.append(f"{nome}: posição principal inválida ({posicao}).")
        for secundaria in dados.get("posicoes_multiplas", []):
            if secundaria not in POSICOES_OFICIAIS:
                erros.append(f"{nome}: posição secundária inválida ({secundaria}).")
    return erros

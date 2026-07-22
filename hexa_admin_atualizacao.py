"""Interface protegida da Central de Atualização."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import streamlit as st

from hexa_atualizacao import (
    AtualizacaoFileError,
    DocumentoRepository,
    carregar_registros_arquivo,
    preparar_calendario,
    preparar_temporada,
)
from hexa_auth import IdentidadeUsuario, Permissao, usuario_tem_permissao
from hexa_calendarios import CATEGORIAS_COMPETICAO
from hexa_config import CALENDARIOS_DIR, TEMPORADAS_DIR
from hexa_indices_rankings import recalcular_indices_rankings

__all__ = ["render_central_atualizacao"]


def _ator(identidade: IdentidadeUsuario) -> str:
    return identidade.subject or identidade.email or identidade.nome


def _download_documento(
    *,
    documento: Mapping[str, Any],
    nome: str,
    chave: str,
) -> None:
    conteudo = json.dumps(
        documento,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    st.download_button(
        "Baixar JSON atualizado",
        data=conteudo,
        file_name=nome,
        mime="application/json",
        key=chave,
        width="stretch",
    )


def _render_resultado(
    *,
    previa,
    repositorio: DocumentoRepository,
    permitir_gravacao: bool,
) -> None:
    st.success(
        f"Prévia concluída: {previa.atualizados} de "
        f"{previa.recebidos} registros aceitos."
    )
    if previa.avisos:
        with st.expander(
            f"Avisos da validação ({len(previa.avisos)})",
            expanded=True,
        ):
            for aviso in previa.avisos:
                st.warning(aviso)

    st.json(
        {
            "tipo": previa.tipo,
            "ano": previa.ano,
            "recebidos": previa.recebidos,
            "atualizados": previa.atualizados,
            "avisos": len(previa.avisos),
            "atualizado_em_utc": previa.documento["atualizado_em_utc"],
            "indices_recalculados": len(previa.documento.get("totais") or []),
            "rankings_recalculados": sum(
                len(bloco)
                for bloco in (
                    previa.documento.get("indices_rankings", {})
                    .get("rankings", {})
                    .values()
                )
                if isinstance(bloco, Mapping)
            ),
        },
        expanded=False,
    )
    nome = repositorio.caminho(previa.ano).name
    _download_documento(
        documento=previa.documento,
        nome=nome,
        chave=f"download::{previa.tipo}::{previa.ano}",
    )

    st.checkbox(
        "Confirmo que revisei a prévia e os avisos",
        key=f"confirmacao::{previa.tipo}::{previa.ano}",
    )
    confirmado = bool(
        st.session_state.get(
            f"confirmacao::{previa.tipo}::{previa.ano}",
            False,
        )
    )
    if st.button(
        f"Aplicar atualização de {previa.ano}",
        type="primary",
        disabled=not (permitir_gravacao and confirmado),
        key=f"aplicar::{previa.tipo}::{previa.ano}",
        width="stretch",
    ):
        destino = repositorio.salvar(previa.ano, previa.documento)
        st.success(f"Atualização salva em {destino.name}.")
        st.info(
            "No Streamlit Community Cloud, versione o JSON no GitHub para "
            "tornar a atualização permanente."
        )



def _render_recalculo_rankings(
    *,
    ano: int,
    identidade: IdentidadeUsuario,
    permitir_gravacao: bool,
) -> None:
    repositorio = DocumentoRepository(TEMPORADAS_DIR, "temporada")
    documento = repositorio.carregar(ano)
    if documento is None:
        st.caption(
            f"A temporada {ano} ainda não existe; envie estatísticas para criá-la."
        )
        return

    with st.expander("Recalcular índices e rankings", expanded=False):
        st.caption(
            "Reconstrói somente dados derivados. Registros brutos, temporadas "
            "anteriores e dados editoriais não são alterados."
        )
        st.checkbox(
            "Confirmo o recálculo dos dados derivados",
            key=f"confirmacao_recalculo::{ano}",
        )
        confirmado = bool(
            st.session_state.get(f"confirmacao_recalculo::{ano}", False)
        )
        if st.button(
            f"Recalcular temporada {ano}",
            disabled=not (permitir_gravacao and confirmado),
            key=f"recalcular_rankings::{ano}",
            width="stretch",
        ):
            try:
                recalculado = recalcular_indices_rankings(documento)
                historico = list(recalculado.get("historico_recalculos") or [])
                historico.append(
                    {
                        "recalculado_em_utc": datetime.now()
                        .astimezone()
                        .isoformat(),
                        "recalculado_por": _ator(identidade),
                    }
                )
                recalculado["historico_recalculos"] = historico
                destino = repositorio.salvar(ano, recalculado)
            except ValueError as erro:
                st.error(str(erro))
                return
            st.success(
                f"Índices e rankings recalculados em {destino.name}."
            )
            st.info(
                "No Streamlit Community Cloud, versione o JSON no GitHub para "
                "tornar o recálculo permanente."
            )

def render_central_atualizacao(
    jogadores: Mapping[str, Mapping[str, Any]],
    *,
    identidade: IdentidadeUsuario,
) -> None:
    """Valida e atualiza temporadas ou calendários com confirmação explícita."""
    st.markdown("## Central de Atualização")
    st.caption(
        "Atualiza arquivos anuais sem alterar o cadastro editorial dos atletas."
    )

    permitir = usuario_tem_permissao(
        Permissao.EXECUTAR_ATUALIZACAO,
        identidade=identidade,
    )
    if not permitir:
        st.warning(
            "Sua conta não possui permissão para executar atualizações."
        )
        return

    tipo = st.radio(
        "Base a atualizar",
        ("Estatísticas da temporada", "Calendário oficial"),
        horizontal=True,
        key="central_tipo_atualizacao",
    )
    ano = int(
        st.number_input(
            "Ano",
            min_value=2026,
            max_value=2035,
            value=datetime.now().year,
            step=1,
        )
    )
    fonte = st.text_input(
        "Fonte dos dados",
        placeholder="Ex.: arquivo oficial da competição ou fornecedor licenciado",
    )

    if tipo == "Estatísticas da temporada":
        _render_recalculo_rankings(
            ano=ano,
            identidade=identidade,
            permitir_gravacao=permitir,
        )

    arquivo = st.file_uploader(
        "Arquivo estruturado",
        type=("json", "csv", "xlsx"),
        help="Limite de 5 MB. XLSM e arquivos com macros não são aceitos.",
    )

    if tipo == "Calendário oficial":
        with st.expander("Categorias oficiais aceitas"):
            st.write(
                ", ".join(
                    categoria.replace("_", " ")
                    for categoria in CATEGORIAS_COMPETICAO
                )
            )
            st.caption(
                "O contrato contempla estaduais, regionais, ligas e copas "
                "nacionais, Libertadores, Sul-Americana e outros torneios oficiais."
            )

    if arquivo is None:
        st.info(
            "Envie um JSON, CSV ou XLSX para gerar a prévia da atualização."
        )
        return

    try:
        registros = carregar_registros_arquivo(
            nome_arquivo=arquivo.name,
            conteudo=arquivo.getvalue(),
        )
        if tipo == "Estatísticas da temporada":
            repositorio = DocumentoRepository(TEMPORADAS_DIR, "temporada")
            previa = preparar_temporada(
                ano=ano,
                registros=registros,
                jogadores=jogadores,
                documento_anterior=repositorio.carregar(ano),
                fonte=fonte,
                atualizado_por=_ator(identidade),
            )
        else:
            repositorio = DocumentoRepository(CALENDARIOS_DIR, "calendario")
            previa = preparar_calendario(
                ano=ano,
                registros=registros,
                documento_anterior=repositorio.carregar(ano),
                fonte=fonte,
                atualizado_por=_ator(identidade),
            )
    except (AtualizacaoFileError, ValueError) as erro:
        st.error(str(erro))
        return

    _render_resultado(
        previa=previa,
        repositorio=repositorio,
        permitir_gravacao=permitir,
    )

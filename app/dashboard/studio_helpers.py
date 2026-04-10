"""Helpers do Estúdio de Conteúdo (Kanban, cópias IA, persistência)."""

from __future__ import annotations

import json
import os

import streamlit as st

from app.core.database import get_connection

ETAPAS = ["Ideia", "Editando", "Pronto", "Agendado", "Postado"]
ETAPA_COR = {
    "Ideia": ("#8B90A0", "rgba(255,255,255,0.05)"),
    "Editando": ("#FBBF24", "rgba(251,191,36,0.08)"),
    "Pronto": ("#60A5FA", "rgba(96,165,250,0.08)"),
    "Agendado": ("#A78BFA", "rgba(167,139,250,0.08)"),
    "Postado": ("#22C55E", "rgba(34,197,94,0.08)"),
}


def generate_copies_por_rede(msg: str, rede: str = "todas") -> dict:
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()

        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
Você é especialista em marketing de afiliados Shopee no Brasil.
Com base nesta oferta: {msg[:500]}

Gere copies VIRAIS em JSON com as chaves:
- instagram_reels: legenda para Reels com emojis e até 5 hashtags (máx 150 chars)
- tiktok: legenda curta e agressiva para TikTok (máx 100 chars)
- shopee_video: título persuasivo para Shopee Video (máx 80 chars)
- whatsapp: mensagem informal com urgência (máx 200 chars)

Retorne APENAS JSON válido.
        """
        resp = model.generate_content(prompt)
        raw = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(raw)
    except Exception:
        return {
            "instagram_reels": f"🔥 Oferta imperdível! {msg[:80]} #shopee #achados",
            "tiktok": f"Você PRECISA ver isso! 👀 {msg[:60]}",
            "shopee_video": f"Achado incrível! {msg[:50]}",
            "whatsapp": f"🚨 ACHADO DO DIA: {msg[:100]} Corre que acaba!",
        }


def render_stepper(etapa_atual: str) -> None:
    idx_atual = ETAPAS.index(etapa_atual) if etapa_atual in ETAPAS else 0
    cols = st.columns(len(ETAPAS))
    for i, etapa in enumerate(ETAPAS):
        if i < idx_atual:
            css = "step-done"
            icon = "✅"
        elif i == idx_atual:
            css = "step-active"
            icon = "▶"
        else:
            css = "step-todo"
            icon = "○"
        cols[i].markdown(
            f"<div style='text-align:center'><span class='{css}'>{icon} {etapa}</span></div>",
            unsafe_allow_html=True,
        )


def get_achados_por_status(status_fluxo: str):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """
            SELECT id, texto_original, midia_path, link_original, categoria,
                   status_fluxo, legenda_instagram, legenda_tiktok, legenda_shopee,
                   compliance_status, status, cover_path, link_backup_1, link_backup_2,
                   grupo_id, tema_grupo
            FROM achados WHERE status_fluxo = ? ORDER BY id DESC
            """,
            (status_fluxo,),
        )
    except Exception:
        c.execute(
            "SELECT id, texto_original, midia_path, link_original, categoria, 'Ideia', NULL, NULL, NULL, 'PENDENTE', status, NULL, NULL, NULL FROM achados WHERE status NOT IN ('REJECTED') ORDER BY id DESC"
        )
    rows = c.fetchall()
    conn.close()
    return rows


def mover_etapa(achado_id: int, nova_etapa: str) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE achados SET status_fluxo = ? WHERE id = ?", (nova_etapa, achado_id))
    conn.commit()
    conn.close()


def salvar_legendas(achado_id: int, ig: str, tt: str, sh: str) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE achados SET legenda_instagram=?, legenda_tiktok=?, legenda_shopee=? WHERE id=?",
        (ig, tt, sh, achado_id),
    )
    conn.commit()
    conn.close()

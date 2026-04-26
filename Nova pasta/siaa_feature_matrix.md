# 📋 Matriz de Funcionalidades — SIAA-2026

> **Última revisão:** 02/04/2026 · Sistema rodando há +11h contínuas

---

## 📡 PILAR 1 — COLETA

| # | Função | Módulo | Tecnologia | Status | Prioridade |
|:---:|---|---|---|:---:|:---:|
| 1 | Crawler de canais Telegram em tempo real | `crawler_telegram.py` | Python · Telethon SSE | ✅ Concluído | 🔴 Crítica |
| 2 | Extração de links por Regex (Produto vs Coleção) | `crawler_telegram.py` | Python · re · urllib | ✅ Concluído | 🔴 Crítica |
| 3 | Recuperação de histórico (últimas 24h) | `crawler_telegram.py` | Telethon · iter_messages | ✅ Concluído | 🔴 Crítica |
| 4 | Scraping de mídia HD do vendedor Shopee | `shopee_scraper.py` | Python · Playwright | ✅ Concluído | 🟠 Alta |
| 5 | Extração de vídeo do Shopee Video | `shopee_scraper.py` | Playwright · ffmpeg | ✅ Concluído | 🟠 Alta |
| 6 | Busca de ofertas via Shopee Open API | `shopee_api_client.py` | Python · HMAC-SHA256 · requests | 🔧 Aguarda credencial | 🟠 Alta |
| 7 | Entrada manual de produto pelo Dashboard | `dashboard.py` (Aba ➕) | Streamlit · SQLite | ✅ Concluído | 🟡 Média |
| 8 | Classificação automática PRODUTO / COLEÇÃO | `crawler_telegram.py` | Python · re | ✅ Concluído | 🟠 Alta |

---

## 🧠 PILAR 2 — PROCESSAMENTO

| # | Função | Módulo | Tecnologia | Status | Prioridade |
|:---:|---|---|---|:---:|:---:|
| 9 | Banco de dados relacional (achados + produtos) | `database.py` | Python · SQLite3 · WAL Mode | ✅ Concluído | 🔴 Crítica |
| 10 | Verificação de compliance / produto proibido | `dashboard.py` Triagem | Gemini 1.5 Flash · Google AI | ✅ Concluído | 🔴 Crítica |
| 11 | Dashboard de triagem (Aprovação / Rejeição) | `dashboard.py` (Aba 🛒) | Streamlit · SQLite | ✅ Concluído | 🔴 Crítica |
| 12 | Geração de copys virais para 3 plataformas | `hook_generator.py` | Gemini 1.5 Flash | ✅ Concluído | 🟠 Alta |
| 13 | Feed Card com desfoque Gaussian + selos | `card_generator.py` | Python · Pillow (PIL) | ✅ Concluído | 🟠 Alta |
| 14 | Geração de thumbnail via IA (fallback) | `card_generator.py` | OpenAI DALL-E 3 · API REST | ✅ Concluído | 🟡 Média |
| 15 | Agendamento por data/hora e evento | `scheduler_engine.py` | Python · SQLite · schedule | ✅ Concluído | 🟠 Alta |
| 16 | Emissor de Cupons Relâmpago (card visual) | `dashboard.py` (Aba 🎟️) + `card_generator.py` | Streamlit · Pillow | ✅ Concluído | 🟡 Média |
| 17 | Logs estruturados em JSON (NOC) | `logger.py` | Python · logging · JSON | ✅ Concluído | 🟡 Média |
| 18 | Limpeza automática de mídias antigas (3d+) | `main.py` cleanup_downloads | Python · glob · os.remove | ✅ Concluído | 🟢 Baixa |

---

## 💰 PILAR 3 — CONVERSÃO

| # | Função | Módulo | Tecnologia | Status | Prioridade |
|:---:|---|---|---|:---:|:---:|
| 19 | Geração de link de afiliado rastreável | `shopee_api.py` | Python · requests · Shopee API | ✅ Concluído | 🔴 Crítica |
| 20 | Vitrine Linktree premium (GitHub Pages) | `update_vitrine.py` | Python · HTML/CSS · Git CLI | ✅ Concluído | 🔴 Crítica |
| 21 | Deploy automático da vitrine no GitHub Pages | `update_vitrine.py` | subprocess · Git push | ✅ Concluído | 🔴 Crítica |
| 22 | Health Check de estoque a cada 4 horas | `health_check.py` | Python · requests · Playwright | ✅ Concluído | 🔴 Crítica |
| 23 | Anti-Esgotamento: substituição automática de link | `health_check.py` | Shopee Open API · SQLite update | ✅ Concluído | 🔴 Crítica |
| 24 | Auto-DM bot (clone do Manychat) via Webhook | `instagram_bot.py` | FastAPI · uvicorn · Meta Graph v25 | ✅ Concluído | 🟠 Alta |
| 25 | Private Reply com link personalizado (ID do produto) | `instagram_bot.py` | Meta Private Replies API | ✅ Concluído | 🟠 Alta |
| 26 | Rastreamento de cliques por Sub-ID | `shopee_api_client.py` | Shopee API sub_id param | 🔲 Planejado | 🟡 Média |
| 27 | Comissão estimada por produto no Dashboard | `dashboard.py` | SQLite · Shopee API | 🔲 Planejado | 🟡 Média |

---

## 🚀 PILAR 4 — DISTRIBUIÇÃO

| # | Função | Módulo | Tecnologia | Status | Prioridade |
|:---:|---|---|---|:---:|:---:|
| 28 | Postagem no Instagram via API oficial | `meta_api_publisher.py` | Meta Graph API v25 · requests | 🔧 Aguarda token ativo | 🔴 Crítica |
| 29 | Fila de postagem com horários de pico | `auto_post.py` · `scheduler_engine.py` | Python · SQLite · schedule | ✅ Concluído | 🔴 Crítica |
| 30 | Postagem no WhatsApp Groups | `whatsapp_groups.py` | Evolution API · requests | ✅ Concluído | 🟠 Alta |
| 31 | Upload de vídeo no TikTok (Creator Center) | `tiktok_video.py` | Playwright · Chromium | ✅ Concluído | 🟠 Alta |
| 32 | Upload no Shopee Video | `shopee_video.py` | Playwright · app mobile (manual) | 🔧 Manual via celular | 🟠 Alta |
| 33 | Notificações admin no Telegram | `telegram_logs.py` | python-telegram-bot · requests | ✅ Concluído | 🟡 Média |
| 34 | Cron scheduler (12h / 18h / 21h) | `main.py` | Python · schedule lib | ✅ Concluído | 🔴 Crítica |
| 35 | Modo Campanha (11.11, Black Friday etc.) | `theme.json` · `update_vitrine.py` | JSON Config · HTML dinâmico | ✅ Concluído | 🟡 Média |
| 36 | Meta Ads automático (campanhas pagas) | — | Meta Marketing API | 🔲 Planejado | 🟢 Baixa |

---

## 📊 Consolidado Geral

| Status | Qtd | % |
|---|:---:|:---:|
| ✅ Concluído | 27 | 75% |
| 🔧 Aguarda config/credencial | 4 | 11% |
| 🔲 Planejado | 3 | 8% |
| ⛔ Não iniciado | 2 | 6% |
| **Total** | **36** | **100%** |

---

## 🔢 Legenda de Prioridade

| Símbolo | Nível | Descrição |
|:---:|---|---|
| 🔴 | **Crítica** | Sem isso o sistema não gera receita |
| 🟠 | **Alta** | Multiplica alcance e conversão significativamente |
| 🟡 | **Média** | Melhora a experiência e automatização |
| 🟢 | **Baixa** | Nice-to-have, escala futura |

---

> [!IMPORTANT]
> **Único bloqueador crítico pendente:** funções #28 (Instagram via Meta API) exige token com permissões `instagram_content_publish` ativas no Meta App Review. Enquanto isso, postagens podem ser feitas manualmente pelo Dashboard (download da mídia + legenda pronta).

> [!TIP]
> **Próximas 3 features de maior ROI a implementar:** #26 (rastreamento de cliques), #27 (comissão estimada no dash) e #32 (automação total Shopee Video via ADB no celular).

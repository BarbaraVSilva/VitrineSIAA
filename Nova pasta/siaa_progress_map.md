# 🗺️ Mapa de Progresso 360° — SIAA-2026
> **Data da Revisão:** 02/04/2026 · Sessões de desenvolvimento: 6+ iterações desde março/2026

---

# PARTE 1 — 📜 AUDITORIA HISTÓRICA
> *Todas as funcionalidades definidas desde o início do projeto, em ordem cronológica de concepção*

## Fase 1 — Fundação (Março 2026, Semana 1)
> *Objetivo: extrair dados do Telegram e persistir no banco*

| Req # | Funcionalidade Solicitada | Status | Componente Técnico |
|:---:|---|:---:|---|
| R01 | Crawlear canais Telegram de afiliados em tempo real | ✅ Concluído | Python · Telethon · SSE |
| R02 | Filtrar apenas mensagens com link da Shopee | ✅ Concluído | Python · Regex · re |
| R03 | Persistir achados em banco de dados local | ✅ Concluído | SQLite3 · WAL Mode |
| R04 | Criar tabelas `achados` e `produtos` com schema relacionado | ✅ Concluído | SQL · database.py |
| R05 | Detectar tipo do link: PRODUTO vs COLEÇÃO | ✅ Concluído | Python · re · url parsing |
| R06 | Painel de aprovação manual (triagem humana) | ✅ Concluído | Streamlit · SQLite |
| R07 | Gerar link de afiliado rastreável | ✅ Concluído | Python · Shopee API |

## Fase 2 — Inteligência de Mídia (Março 2026, Semana 2)
> *Objetivo: enriquecer os produtos com vídeo e imagem antes de publicar*

| Req # | Funcionalidade Solicitada | Status | Componente Técnico |
|:---:|---|:---:|---|
| R08 | Scraper de mídia HD do vendedor (foto do produto) | ✅ Concluído | Playwright · Chromium |
| R09 | Extração de vídeo nativo do Shopee Video | ✅ Concluído | Playwright · ffmpeg |
| R10 | Geração de Feed Card 1080x1080 com branding | ✅ Concluído | Python · Pillow/PIL |
| R11 | Desfoque Gaussian no fundo do card | ✅ Concluído | Pillow · ImageFilter |
| R12 | Frame/capa extraída de vídeos para postar como foto | ✅ Concluído | ffmpeg · Pillow |
| R13 | Fallback de imagem via DALL-E 3 quando foto ausente | ✅ Concluído | OpenAI DALL-E 3 API |

## Fase 3 — Publicação Multi-Canal (Março/Abril 2026, Semana 3)
> *Objetivo: distribuir os produtos aprovados nas redes sociais*

| Req # | Funcionalidade Solicitada | Status | Componente Técnico |
|:---:|---|:---:|---|
| R14 | Postagem automática no Instagram (sem Selenium/browser) | 🔧 Token pendente | Meta Graph API v25 |
| R15 | Substituição do Selenium por API oficial Meta | ✅ Concluído | meta_api_publisher.py |
| R16 | Postagem no WhatsApp Groups com mídia | ✅ Concluído | Evolution API · requests |
| R17 | Upload automático no TikTok (Creator Center) | ✅ Concluído | Playwright · tiktok_video.py |
| R18 | Upload no Shopee Video (via celular ou automação) | 🔧 Manual por ora | Playwright · app mobile |
| R19 | Agendamento por data/hora (horários de pico) | ✅ Concluído | schedule · scheduler_engine |
| R20 | Vitrine de produtos no GitHub Pages (Link da Bio) | ✅ Concluído | HTML/CSS · Git push |
| R21 | Estratégia de link pra conta nova (sem link direto no IG) | ✅ Concluído | Código #produto na legenda |

## Fase 4 — Inteligência de Conteúdo (Abril 2026)
> *Objetivo: IA gerando todo o conteúdo sem intervenção humana*

| Req # | Funcionalidade Solicitada | Status | Componente Técnico |
|:---:|---|:---:|---|
| R22 | Geração de copys virais por plataforma (IG / TikTok / WA) | ✅ Concluído | Gemini 1.5 Flash |
| R23 | Verificação de compliance antes de exibir no painel | ✅ Concluído | Gemini + dashboard.py |
| R24 | Hook generator (ganchos de abertura para Reels) | ✅ Concluído | hook_generator.py |
| R25 | Modo Campanha automático (11.11, Black Friday) | ✅ Concluído | theme.json · vitrine |
| R26 | Emissor de Cupons com arte visual agressiva | ✅ Concluído | Pillow · card_generator.py |

## Fase 5 — Engajamento e Escala (Abril 2026 — ATUAL)
> *Objetivo: viralização orgânica e substituição de ferramentas pagas*

| Req # | Funcionalidade Solicitada | Status | Componente Técnico |
|:---:|---|:---:|---|
| R27 | Auto-DM bot (substitui Manychat) | ✅ Concluído | FastAPI · Meta Private Replies |
| R28 | Webhook escuta comentários "EU QUERO" em tempo real | ✅ Concluído | FastAPI POST · instagram_bot.py |
| R29 | Envio de link personalizado por ID do produto na DM | ✅ Concluído | SQLite lookup · Meta API |
| R30 | Anti-Esgotamento: substituição automática de link quebrado | ✅ Concluído | health_check · Shopee API |
| R31 | Cliente oficial Shopee Open API (HMAC-SHA256) | ✅ Concluído | shopee_api_client.py |
| R32 | Vitrine redesenhada como Linktree premium | ✅ Concluído | HTML/CSS · update_vitrine.py |
| R33 | Formulário de entrada manual de produto real | ✅ Concluído | Dashboard Aba ➕ |
| R34 | Geração de mídia pós-inserção manual (como Telegram) | ✅ Concluído | Playwright + Pillow + Gemini |

---

# PARTE 2 — 🔍 GAP ANALYSIS
> *O que foi planejado mas ainda tem lacuna entre design e execução completa*

## 🔴 Gaps Críticos (Bloqueiam receita)

| Gap | Descrição | Causa | Solução |
|---|---|---|---|
| **G01** — Instagram Postagem | Meta API configurada mas token sem permissão `instagram_content_publish` | Meta App Review requerido para contas novas | Submeter app para revisão ou usar token temporário de teste |
| **G02** — Shopee Open API Credencial | `SHOPEE_APP_ID` no .env é diferente do registrado no portal | IDs não batem entre App Shopee e .env | Confirmar no portal affiliate.shopee.com.br qual App ID é o correto |

## 🟠 Gaps Relevantes (Reduzem automação)

| Gap | Descrição | Causa | Solução |
|---|---|---|---|
| **G03** — Shopee Video automático | Upload ainda é manual via celular | Shopee Video não tem API pública para upload externo | ADB + scrcpy ou Automate no celular via Wi-Fi |
| **G04** — Rastreamento de cliques | Não sabemos qual post gera venda real | Sub-ID não implementado na geração de link | Adicionar `&sub_id=post_{id}_{plataforma}` no link afiliado |
| **G05** — IG Conta Nova (0 seguidores) | Private Replies só funciona com 24h de contato prévio | Regra do Instagram para contas sem histórico | Primeiro comentário público em resposta → depois DM |

## 🟡 Gaps de Funcionalidade (Melhoram experiência)

| Gap | Descrição | Impacto | Esforço |
|---|---|---|---|
| **G06** — Comissão Estimada no Dash | Sem visibilidade de ganho projetado por produto | Médio | Baixo (fórmula simples: preço × taxa) |
| **G07** — Vitrine sem fotos | Os cards da vitrine só têm texto e link, sem thumbnail | Alto | Médio (image hosting ou base64) |
| **G08** — Telegram Bot bidirecional | Bot só notifica, não recebe comandos | Baixo | Médio |
| **G09** — Logs de postagem no Dashboard | Não há histórico visual de "o que foi postado quando" | Médio | Baixo |

---

# PARTE 3 — 🏗️ ARQUITETURA EM CAMADAS
> *Visão de engenharia organizada por responsabilidade técnica*

---

## 🗄️ CAMADA 1 — DADOS (Scraping / SQL)

```
┌─────────────────────────────────────────────────────────┐
│                    FONTES DE ENTRADA                     │
│  Telegram Channels ──► Telethon SSE ──► Link Parser     │
│  Shopee Catalog    ──► Playwright   ──► Mídia Extractor │
│  Affiliate Portal  ──► HMAC API     ──► Link Generator  │
│  Manual Form       ──► Dashboard    ──► Direct Insert   │
└───────────────────────────┬─────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  SQLite WAL   │
                    │  achados      │◄──── status: PENDING
                    │  produtos     │◄──── status: APPROVED
                    │  agendamentos │◄──── data_execucao
                    └───────────────┘
```

| Função | Arquivo | SQL/Tech | Status |
|---|---|---|:---:|
| Schema criação e migrations | `database.py` | SQLite3 · CREATE TABLE | ✅ |
| Insert de achados do Telegram | `crawler_telegram.py` | INSERT INTO achados | ✅ |
| Insert manual via Dashboard | `dashboard.py` Ab.5 | INSERT INTO achados | ✅ |
| Update de status (APPROVED) | `dashboard.py` Ab.1 | UPDATE achados SET status | ✅ |
| Insert em produtos (aprovação) | `dashboard.py` Ab.1 | INSERT INTO produtos | ✅ |
| Update de link anti-esgotamento | `health_check.py` | UPDATE produtos SET link_afiliado | ✅ |
| Busca de produto para agendamento | `scheduler_engine.py` | SELECT produtos WHERE | ✅ |
| Leitura de estoque | `health_check.py` | SELECT + HEAD request | ✅ |
| Limpeza de mídias antigas | `main.py` cleanup | glob + os.remove | ✅ |

---

## ⚙️ CAMADA 2 — LÓGICA (APIs de Afiliados / Filtros / IA)

```
┌─────────────────────────────────────────────────────────┐
│                   MOTOR DE DECISÃO                       │
│  Compliance ──► Gemini AI ──► SEGURO / PROIBIDO         │
│  Copy Engine ──► Gemini ──► IG · TikTok · WhatsApp      │
│  Card Maker  ──► Pillow  ──► Feed 1080px + Selos        │
│  Link Gen    ──► Shopee API ──► shope.ee/XXXXXX         │
│  Health      ──► HEAD req ──► 200 OK / 404 DEAD         │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         Aprovado       Esgotado      Proibido
              │             │             │
         ─────────     ─────────     ─────────
         Fila Post     API Busca     Rejeitado
                       Similar       no Painel
```

| Função | Arquivo | Tech/API | Status |
|---|---|---|:---:|
| Geração de copys virais | `hook_generator.py` | Gemini 1.5 Flash | ✅ |
| Verificação de compliance | `dashboard.py` | Gemini · JSON parse | ✅ |
| Card Feed 1080px desfocado | `card_generator.py` | Pillow · Gaussian Blur | ✅ |
| Thumbnail DALL-E 3 fallback | `card_generator.py` | OpenAI API · base64 | ✅ |
| Geração de link afiliado | `shopee_api.py` | Shopee Partner API | ✅ |
| Busca de produto substituto | `shopee_api_client.py` | HMAC-SHA256 · requests | 🔧 |
| Filtro de comissão mínima | `shopee_api_client.py` | Shopee API filter | 🔧 |
| Agendamento inteligente | `scheduler_engine.py` | SQLite · schedule lib | ✅ |
| Modo Campanha automático | `theme.json` · `update_vitrine.py` | JSON config | ✅ |

---

## 📤 CAMADA 3 — SAÍDA (Distribuição Multi-Canal)

```
┌─────────────────────────────────────────────────────────┐
│                     CANAIS DE SAÍDA                      │
│                                                          │
│  📸 Instagram ──► Meta Graph API v25 ──► Reel/Feed      │
│  🎵 TikTok    ──► Playwright Creator ──► Vídeo Upload   │
│  💬 WhatsApp  ──► Evolution API      ──► Grupo + Mídia  │
│  🌐 Vitrine   ──► GitHub Pages       ──► Linktree HTML  │
│  📨 Telegram  ──► Bot API            ──► Alertas Admin  │
│  📩 DM Auto   ──► FastAPI Webhook    ──► Private Reply   │
└─────────────────────────────────────────────────────────┘
```

| Canal | Arquivo | Tech/API | Status | Bloqueio |
|---|---|---|:---:|---|
| Instagram Feed/Reels | `meta_api_publisher.py` | Meta Graph v25 | 🔧 | Permissão App |
| TikTok Creator Center | `tiktok_video.py` | Playwright | ✅ | — |
| WhatsApp Groups | `whatsapp_groups.py` | Evolution API | ✅ | — |
| GitHub Pages Vitrine | `update_vitrine.py` | Git push · HTML | ✅ | — |
| Telegram Admin Bot | `telegram_logs.py` | Bot API | ✅ | — |
| Instagram Auto-DM | `instagram_bot.py` | FastAPI · Meta Private Replies | ✅ | Token ativo |
| Shopee Video | `shopee_video.py` | Playwright | 🔧 | Manual celular |

---

# 🎯 RESUMO EXECUTIVO

```
PROGRESSO GERAL: ████████████████████░░░░  82%

COLETA:         ████████████████████████  96%  ✅
PROCESSAMENTO:  ████████████████████████ 100%  ✅
CONVERSÃO:      ████████████████████░░░░  80%  🟡
DISTRIBUIÇÃO:   ████████████████░░░░░░░░  68%  🔧
ENGAJAMENTO:    ██████████████████████░░  90%  ✅
```

## 🔑 Os 3 Gaps que Desbloqueiam Tudo

| Prioridade | Gap | O que resolve | Tempo estimado |
|:---:|---|---|:---:|
| 🥇 1º | Token Instagram com `publish` ativo | Posts automáticos noIG | 1h |
| 🥈 2º | App ID Shopee Open API correto no .env | Anti-esgotamento real + links rastreáveis | 30min |
| 🥉 3º | GitHub Pages configurado (branch main→root) | Vitrine ao vivo para Bio do IG | 5min ✅ Feito |

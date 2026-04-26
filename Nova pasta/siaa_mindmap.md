# 🗺️ Mapa de Funcionalidades — SIAA-2026

## Legenda
> - 🔴 **CORE** — Funcionalidade essencial. Sem ela o sistema não opera.
> - 🟡 **ADICIONAL** — Feature avançada que amplifica resultados.
> - ✅ **Implementado** — Código já existe e está ativo.
> - 🔧 **Parcial** — Implementado mas depende de config externa.
> - 🔲 **Planejado** — Arquitetado, aguarda ativação ou credenciais.

---

```mermaid
mindmap
  root(("🔥 SIAA-2026\nAfiliados Shopee"))

    COLETA["📡 1. COLETA"]
      CORE_COLETA["🔴 CORE"]
        C1["✅ Crawler Telegram\nTelethon SSE em tempo real\ncrawler_telegram.py"]
        C2["✅ Link Splitter\nRegex detecta PRODUTO\nvs COLECAO automaticamente"]
        C3["✅ Histórico 24h\nPuxa mensagens perdidas\nao iniciar o sistema"]
      ADD_COLETA["🟡 ADICIONAL"]
        C4["✅ Shopee Scraper\nPlaywright invisível\nBaixa mídia HD do vendedor"]
        C5["🔧 Shopee Open API\nHMAC-SHA256 autenticado\nTop Offers sem depender do Telegram"]
        C6["✅ Entrada Manual\nFormulário no Dashboard\nProduto direto da Central de Afiliados"]

    PROCESSAMENTO["🧠 2. PROCESSAMENTO"]
      CORE_PROC["🔴 CORE"]
        P1["✅ Banco SQLite\nTabelas achados + produtos\nMultiprocess-safe WAL mode"]
        P2["✅ Compliance Check\nIA detecta produtos proibidos\nbefore dashboard approval"]
        P3["✅ Dashboard Triagem\nAprovar Rejeitar Editar\n5 abas completas no Streamlit"]
        P4["✅ Copy Engine Gemini\nLegendas para IG TikTok WhatsApp\ngoogle-generativeai"]
      ADD_PROC["🟡 ADICIONAL"]
        P5["✅ Card Generator Pillow\nFeed Card 1080x1080\nDesfoque Gaussiano + Selos"]
        P6["✅ DALL-E 3 Fallback\nThumbnail IA quando sem foto\nopenai + card_generator.py"]
        P7["✅ Scheduler Engine\nAgendamento por data hora\nDouble Days Black Friday"]
        P8["✅ Cupom Relâmpago\nCard laranja agressivo\nDisparo no WhatsApp"]

    CONVERSAO["💰 3. CONVERSÃO"]
      CORE_CONV["🔴 CORE"]
        CV1["✅ Geração de Link Afiliado\nget_affiliate_link\napp/core/shopee_api.py"]
        CV2["✅ Vitrine Linktree\nGitHub Pages HTML premium\nCategoria + Recentes + Coleções"]
        CV3["✅ Health Check 4h\nVerifica estoque de todos os links\nhealth_check.py"]
        CV4["✅ Anti-Esgotamento\nFallback automático para\nfornecedor similar com comissão"]
      ADD_CONV["🟡 ADICIONAL"]
        CV5["✅ Auto-DM ManyChat Clone\nFastAPI Webhook Private Replies\nMeta Graph API v25"]
        CV6["🔲 Rastreamento de Cliques\nSub-IDs na Shopee API\nAnalytics de conversão por post"]
        CV7["🔲 Comissão Estimada\nCálculo automático por produto\nMétrica no Dashboard"]
        CV8["🔧 Link na Bio Dinâmico\nVitrine atualiza em push\nURL estável para a Bio do IG"]

    DISTRIBUICAO["🚀 4. DISTRIBUIÇÃO"]
      CORE_DIST["🔴 CORE"]
        D1["🔧 Meta Graph API\nmeta_api_publisher.py\nReels + Feed Instagram sem browser"]
        D2["✅ WhatsApp Groups\nEvolution API\nMídia + Legenda + Link rastreável"]
        D3["✅ GitHub Pages Deploy\ngit_push_vitrine\nAuto-commit após cada aprovação"]
      ADD_DIST["🟡 ADICIONAL"]
        D4["✅ TikTok Creator Center\nPlaywright automático\ntiktok_video.py"]
        D5["🔲 Shopee Video\nPlaywright + conta Creator\nPostagem manual via celular por ora"]
        D6["🔲 Meta Ads Automático\nCriar campanha paga\ndkbot7 meta-ads-automation-ai"]
        D7["✅ Telegram Admin Bot\n@RadarVipSIAA_bot\nAlertas críticos e confirmações"]
        D8["✅ Cron Scheduler\nHorários de pico 12h 18h 21h\nschedule library em main.py"]
```

---

## 📊 Resumo de Status

| Pilar | Core ✅ | Core 🔧 | Adicional ✅ | Adicional 🔲 |
|---|:---:|:---:|:---:|:---:|
| 📡 Coleta | 3/3 | 0 | 2/3 | 1/3 |
| 🧠 Processamento | 4/4 | 0 | 4/4 | 0 |
| 💰 Conversão | 4/4 | 0 | 1/4 | 3/4 |
| 🚀 Distribuição | 1/3 | 2/3 | 3/4 | 2/4 |

> [!TIP]
> **O sistema está ~80% implementado.** Os 20% restantes são: rastreamento de cliques, comissão estimada no dashboard, Meta Ads pagos e automação total do Shopee Video via celular.

> [!IMPORTANT]
> **Prioridade para ir ao ar hoje:** Preencher `META_ACCESS_TOKEN` ativo no `.env` para ativar a Distribuição Core do Instagram. Todo o resto já está funcional.

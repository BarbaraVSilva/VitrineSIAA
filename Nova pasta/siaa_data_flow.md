# 🗺️ Diagrama de Fluxo de Dados — SIAA-2026

## Fluxo Completo: Da Mineração à Publicação

```mermaid
flowchart TD
    %% ── FONTES DE DADOS ──
    subgraph ENTRADA["📡 FONTES DE ENTRADA"]
        TG["📨 Canais Telegram\n(@achadinhosshopee\n@viralizandoshopee etc.)"]
        MANUAL["🧑‍💻 Dashboard\nAdicionar Produto Manual\n(Aba ➕)"]
        SHOPEEAPI["🛍️ Shopee Affiliate\nOpen API v2\n(Top Offers / Busca)"]
    end

    %% ── MINERAÇÃO ──
    subgraph CRAWL["🤖 CAMADA DE MINERAÇÃO"]
        CRAWLER["crawler_telegram.py\nTelethon SSE\nLink Splitter Regex"]
        SCRAPER["shopee_scraper.py\nPlaywright Invisível\nExtração de Mídia HD"]
        APICLIENTE["shopee_api_client.py\nHMAC-SHA256 Auth\nBusca & Geração de Link"]
    end

    %% ── BANCO DE DADOS ──
    subgraph DB["🗄️ BANCO DE DADOS SQLite"]
        ACHADOS[("Tabela: achados\nstatus: PENDING / APPROVED\nmidia_path · link_original")]
        PRODUTOS[("Tabela: produtos\nnome · link_afiliado\nlink_backup_1/2 · categoria\nestoque_ok · last_checked")]
    end

    %% ── PROCESSAMENTO IA ──
    subgraph IA["🧠 CAMADA DE INTELIGÊNCIA ARTIFICIAL"]
        GEMINI["Gemini 1.5 Flash\nCopy Engine\nLegendas Instagram/TikTok/WhatsApp"]
        PILLOW["card_generator.py\nFeed Card 1080x1080\nDesfoque Gaussian + Selos"]
        DALLE["DALL-E 3 (Fallback)\nGera Thumbnail\nse imagem faltar"]
        COMPLIANCE["Compliance Check\nIA detecta produtos\nproibidos pela Shopee"]
    end

    %% ── DASHBOARD ──
    subgraph DASH["📊 DASHBOARD STREAMLIT"]
        TRIAGEM["Aba Triagem\nAprovar / Rejeitar\nEditar Legenda"]
        AGENDADOR["Aba Campanhas\nAgendar Data/Hora\nDouble Days / Black Friday"]
        CUPONS["Aba Cupons\nEmissor Relâmpago\nCard Pillow Laranja"]
        ADDMANUAL["Aba Adicionar Produto\nFormulário Manual\n+ Extração de Mídia"]
    end

    %% ── PUBLICAÇÃO ──
    subgraph PUB["🚀 CAMADA DE PUBLICAÇÃO"]
        METAAPI["meta_api_publisher.py\nMeta Graph API v25\nPostagem Instagram Reels"]
        TIKTOK["tiktok_video.py\nPlaywright Creator Center\nUpload Automático"]
        WHATS["whatsapp_groups.py\nEvolution API\nMídia + Link + Legenda"]
        VITRINE["update_vitrine.py\nLinktree HTML\nGitHub Pages Deploy"]
        AUTOFILA["auto_post.py\nFila Cronometrada\nscheduler_engine.py"]
    end

    %% ── ENGAJAMENTO ──
    subgraph ENGAGE["💬 LOOP DE ENGAJAMENTO"]
        DMBOT["instagram_bot.py\nFastAPI Webhook\nMeta Private Replies"]
        COMMENT["Usuário comenta\n'Eu quero / Link'"]
        DM["Direct Message Automático\nLink afiliado personalizado\n'Achado #105'"]
    end

    %% ── MONITORAMENTO ──
    subgraph HEALTH["♾️ SUPERVISÃO CONTÍNUA"]
        HEALTHCHECK["health_check.py\nVerifica Estoque a cada 4h\nPlaywright HEAD request"]
        TGBOT["Telegram Bot\n@RadarVipSIAA_bot\nAlertas de Admin"]
        FALLBACK["Shopee API Fallback\nBusca produto similar\nAtualiza link no DB"]
    end

    %% ── CONEXÕES: ENTRADA → MINERAÇÃO ──
    TG -->|"Mensagens em tempo real\nTelethon Stream"| CRAWLER
    MANUAL -->|"Formulário preenchido"| SCRAPER
    SHOPEEAPI -->|"Top Offers em alta"| APICLIENTE

    %% ── MINERAÇÃO → DB ──
    CRAWLER -->|"Extrai links + texto\nClassifica PRODUTO/COLEÇÃO"| ACHADOS
    SCRAPER -->|"Salva foto/vídeo\nem /downloads"| ACHADOS
    APICLIENTE -->|"Link afiliado rastreável\nSHA256 assinado"| ACHADOS

    %% ── DB → IA ──
    ACHADOS -->|"PENDING\nAguardando triagem"| COMPLIANCE
    COMPLIANCE -->|"Status SEGURO/PROIBIDO\nbadge no Dashboard"| TRIAGEM

    %% ── DASHBOARD ──
    TRIAGEM -->|"Texto do produto\npara geração de copy"| GEMINI
    TRIAGEM -->|"Imagem do produto\npara branding visual"| PILLOW
    PILLOW -->|"Fallback: sem imagem"| DALLE
    TRIAGEM -->|"Aprovado → status='APPROVED'"| PRODUTOS
    AGENDADOR -->|"data_agendada\nevento (11.11)"| PRODUTOS
    CUPONS -->|"Card Pillow gerado\nWhatsApp dispatch"| WHATS
    ADDMANUAL -->|"Produto real da\nCentral de Afiliados"| ACHADOS

    %% ── APROVAÇÃO → PUBLICAÇÃO ──
    PRODUTOS -->|"Horário bate\nscheduler_engine"| AUTOFILA
    AUTOFILA --> METAAPI
    AUTOFILA --> WHATS
    AUTOFILA --> TIKTOK
    PRODUTOS -->|"Commit + Push Git\ngit_push_vitrine()"| VITRINE

    %% ── PUBLICAÇÃO → REDES ──
    METAAPI -->|"Reel / Foto no Feed\nMeta Graph API v25"| IG(["📸 Instagram"])
    TIKTOK -->|"Vídeo com legenda\nCreator Center"| TT(["🎵 TikTok"])
    WHATS -->|"Imagem + Link\nEvolution API"| WA(["💬 WhatsApp Groups"])
    VITRINE -->|"Linktree Premium\nGitHub Pages"| WEB(["🌐 barbaravsilva.github.io"])

    %% ── ENGAJAMENTO ──
    IG -->|"Comentário: 'Eu quero'"| COMMENT
    COMMENT --> DMBOT
    DMBOT -->|"Busca link no DB\npor ID do produto"| PRODUTOS
    DMBOT --> DM
    DM -->|"Private Reply API\nMeta Graph v25"| IG

    %% ── SUPERVISÃO ──
    HEALTHCHECK -->|"GET request\ncheca 404/stock"| PRODUTOS
    HEALTHCHECK -->|"Link quebrado\nproduto esgotou"| FALLBACK
    FALLBACK -->|"Busca similar\ncomissão > 10%"| APICLIENTE
    FALLBACK -->|"Atualiza link_afiliado\nno DB silenciosamente"| PRODUTOS
    HEALTHCHECK -->|"Alerta crítico\nse falhar tudo"| TGBOT

    %% ── ESTILOS ──
    classDef source fill:#1a2040,stroke:#4B6EFF,color:#E8EAF0
    classDef crawl fill:#1a1530,stroke:#8B5CF6,color:#E8EAF0
    classDef db fill:#1a1a10,stroke:#EAB308,color:#E8EAF0
    classDef ai fill:#0a1a15,stroke:#22C55E,color:#E8EAF0
    classDef dash fill:#1a1010,stroke:#FF6B35,color:#E8EAF0
    classDef pub fill:#1a1530,stroke:#FF6B35,color:#E8EAF0
    classDef engage fill:#0a1015,stroke:#06B6D4,color:#E8EAF0
    classDef health fill:#1a0a0a,stroke:#EF4444,color:#E8EAF0
    classDef social fill:#2a1a00,stroke:#FF6B35,color:#FF6B35,font-weight:bold

    class TG,MANUAL,SHOPEEAPI source
    class CRAWLER,SCRAPER,APICLIENTE crawl
    class ACHADOS,PRODUTOS db
    class GEMINI,PILLOW,DALLE,COMPLIANCE ai
    class TRIAGEM,AGENDADOR,CUPONS,ADDMANUAL dash
    class METAAPI,TIKTOK,WHATS,VITRINE,AUTOFILA pub
    class DMBOT,COMMENT,DM engage
    class HEALTHCHECK,TGBOT,FALLBACK health
    class IG,TT,WA,WEB social
```

---

## 🔑 Legenda dos Módulos

| Cor | Camada | Responsabilidade |
|---|---|---|
| 🔵 Azul | Fontes de Entrada | Telegram, API Shopee, formulário manual |
| 🟣 Roxo | Mineração | Scrapers, crawler Telethon, cliente de API |
| 🟡 Amarelo | Banco de Dados | SQLite — tabelas `achados` e `produtos` |
| 🟢 Verde | IA | Gemini, Pillow, DALL-E, Compliance |
| 🟠 Laranja | Dashboard | Triagem, agendamento, cupons |
| 🔵 Ciano | Engajamento | Auto-DM FastAPI, Private Replies |
| 🔴 Vermelho | Supervisão | HealthCheck, Fallback, Bot Telegram |

## ♾️ Loops Críticos do Sistema

1. **Loop de Anti-Esgotamento:** `health_check` → produto esgota → `shopee_api_client` busca similar → atualiza DB → ninguém percebe
2. **Loop de Viral:** Post no Reels → usuário comenta → `instagram_bot` detecta → manda link no Direct → algoritmo lê mais comentários → entrega para mais pessoas
3. **Loop de Aprovação:** Telegram/Manual → `achados PENDING` → Dashboard Triagem → IA processa → `produtos APPROVED` → fila de postagem

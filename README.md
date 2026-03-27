# 🤖 SIAA-2026 - O Cérebro do Marketing de Afiliados

![SIAA-2026 Banner](file:///C:/Users/Barbara/.gemini/antigravity/brain/95bb7b7c-33e4-465c-8b94-4ea28d6fdcb8/siaa_2026_banner_v1_png_1774639176854.png)

O **SIAA-2026** (Sistema Inteligente de Automação de Afiliados) é uma plataforma "Master" de orquestração projetada para minerar, processar e publicar ofertas de afiliados em múltiplas redes sociais de forma 100% autônoma.

---

## 🏛️ Arquitetura Integrada

O sistema opera como um hub central ("Cérebro") que controla diversos motores:

- **Mining Core:** Crawler de Telegram e Scraper de WhatsApp (via Evolution API) para captura de "achadinhos".
- **Processing Engine:** Editor de imagens/vídeos com tarjas dinâmicas (Pillow) e geração de ganchos virais com **IA (Gemini)**.
- **Publishing Hub:** Auto-post para Shopee Video, Instagram (Meta Webhook) e atualização automática da **Vitrine Web (GitHub Pages)**.
- **Admin Dashboard:** Interface de triagem desenvolvida em **Streamlit**.
- **Backend:** **FastAPI** para recebimento de webhooks em tempo real.

---

## 🔥 Funcionalidades Sênior

- [x] **Orquestração de Processos:** Painel de controle para iniciar/parar motores independentes.
- [x] **Health Check Autônomo:** Verificação periódica de links quebrados ou produtos esgotados na Shopee.
- [x] **AI Hook Generator:** Criação de legendas persuasivas usando modelos de linguagem de última geração.
- [ ] **Dockerização:** Preparado para rodar em containers isolados para escalabilidade na nuvem.

---

## 🛠️ Configuração e Execução

### Pré-requisitos
- Python 3.10+
- SQLite3
- Instalar dependências: `pip install -r requirements.txt`

### Inicialização
1.  Configure as variáveis no `.env` (API Keys da Shopee, Meta, Telegram e Gemini).
2.  Inicie o cérebro central:
    ```bash
    python main.py
    ```
3.  Acesse o Dashboard de Triagem:
    ```bash
    streamlit run app/dashboard/app.py
    ```
4.  O Webhook Server rodará na **Porta 6000** (Padronizada).

---

## 🔒 Segurança

- **Isolamento de Credenciais:** Uso rigoroso de variáveis de ambiente.
- **Database:** SQLite com logs de transações para auditoria de postagens.

---

<p align="center">Desenvolvido com ❤️ por <b>Bárbara V. Silva</b></p>

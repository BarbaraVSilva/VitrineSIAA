"""CSS global do painel Streamlit (dark mode)."""

DASHBOARD_CUSTOM_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  .stApp { background: linear-gradient(135deg, #0D0F14 0%, #111520 50%, #0D0F14 100%); color: #E8EAF0; }
  section[data-testid="stSidebar"] { background: linear-gradient(180deg, #12151F 0%, #0D0F17 100%) !important; border-right: 1px solid rgba(255,107,53,0.15) !important; }
  .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 4px; gap: 4px; border: 1px solid rgba(255,255,255,0.06); }
  .stTabs [data-baseweb="tab"] { border-radius: 8px; color: #8B90A0 !important; font-weight: 500; font-size: 0.85rem; padding: 8px 16px; transition: all 0.2s ease; }
  .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #FF6B35, #FF4500) !important; color: white !important; box-shadow: 0 4px 15px rgba(255,107,53,0.35); }
  .streamlit-expanderHeader { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 12px !important; color: #E8EAF0 !important; font-weight: 600 !important; }
  .streamlit-expanderContent { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 0 0 12px 12px !important; border-top: none !important; }
  .stButton > button[kind="primary"] { background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; padding: 10px 24px !important; box-shadow: 0 4px 20px rgba(255,107,53,0.35) !important; transition: all 0.2s ease !important; }
  .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(255,107,53,0.5) !important; }
  .stButton > button { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #E8EAF0 !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
  .stButton > button:hover { background: rgba(255,107,53,0.15) !important; border-color: rgba(255,107,53,0.4) !important; color: #FF6B35 !important; }
  [data-testid="stMetric"] { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; transition: all 0.2s ease; }
  [data-testid="stMetric"]:hover { border-color: rgba(255,107,53,0.3); box-shadow: 0 0 20px rgba(255,107,53,0.1); }
  [data-testid="stMetricLabel"] { color: #8B90A0 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
  [data-testid="stMetricValue"] { color: #FF6B35 !important; font-size: 2rem !important; font-weight: 800 !important; }
  .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #E8EAF0 !important; }
  .stAlert { border-radius: 12px !important; border-width: 1px !important; }
  hr { border-color: rgba(255,255,255,0.07) !important; }
  [data-testid="stForm"] { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 16px !important; padding: 20px !important; }
  .stDownloadButton > button { background: rgba(255,107,53,0.12) !important; border: 1px solid rgba(255,107,53,0.35) !important; border-radius: 10px !important; color: #FF6B35 !important; font-weight: 600 !important; }
  .kanban-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; transition: all 0.2s ease; }
  .kanban-card:hover { border-color: rgba(255,107,53,0.3); box-shadow: 0 0 16px rgba(255,107,53,0.1); }
  .step-active { background: linear-gradient(135deg,#FF6B35,#FF4500); color:#fff; border-radius:8px; padding:6px 14px; font-weight:700; font-size:0.8rem; }
  .step-done { background: rgba(34,197,94,0.15); color:#22C55E; border-radius:8px; padding:6px 14px; font-weight:600; font-size:0.8rem; }
  .step-todo { background: rgba(255,255,255,0.05); color:#8B90A0; border-radius:8px; padding:6px 14px; font-weight:500; font-size:0.8rem; }
</style>
"""

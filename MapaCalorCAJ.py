import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MeasureControl, Fullscreen, Draw, MousePosition
import json
import re
import os
import unicodedata

# =====================================================
# Configuração inicial com tema personalizado
# =====================================================
st.set_page_config(
    page_title="Mapa de Calor - General Mills • Cajamar > São Paulo", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de cores baseada na imagem (tons de azul, verde e laranja)
COLORS = {
    "primary": "#1E3A8A",      # Azul escuro principal
    "secondary": "#059669",    # Verde esmeralda
    "accent": "#EA580C",       # Laranja vibrante
    "light_bg": "#F0F9FF",     # Azul claro de fundo
    "card_bg": "#FFFFFF",      # Branco para cards
    "text_dark": "#1E293B",    # Texto escuro
    "text_light": "#64748B",   # Texto claro
    "border": "#E2E8F0",       # Borda suave
    "success": "#10B981",      # Verde sucesso
    "warning": "#F59E0B",      # Amarelo alerta
    "error": "#EF4444"         # Vermelho erro
}

# =====================================================
# CSS Global Atualizado
# =====================================================
def css_global():
    st.markdown(
        f"""
        <style>
            /* Configurações gerais */
            .main {{
                background-color: {COLORS["light_bg"]};
            }}
            .block-container {{
                padding-top: 1rem;
                padding-bottom: 1rem;
            }}
            
            /* Header moderno */
            .main-header {{
                background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
                color: white;
                padding: 2rem 1rem;
                border-radius: 0 0 20px 20px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            
            .header-content {{
                display: flex;
                align-items: center;
                gap: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .header-text h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: white;
            }}
            
            .header-text p {{
                font-size: 1.1rem;
                opacity: 0.9;
                margin-bottom: 0;
            }}
            
            .header-logo {{
                width: 120px;
                height: 120px;
                border-radius: 50%;
                border: 4px solid rgba(255,255,255,0.2);
                padding: 8px;
                background: rgba(255,255,255,0.1);
            }}
            
            /* Cards modernos */
            .modern-card {{
                background: {COLORS["card_bg"]};
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid {COLORS["border"]};
                margin-bottom: 1.5rem;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            
            .modern-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            }}
            
            /* Abas estilizadas */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background: transparent;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background: {COLORS["card_bg"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 12px 12px 0 0;
                padding: 1rem 2rem;
                font-weight: 600;
                color: {COLORS["text_light"]};
                transition: all 0.3s ease;
            }}
            
            .stTabs [aria-selected="true"] {{
                background: {COLORS["primary"]} !important;
                color: white !important;
                border-color: {COLORS["primary"]} !important;
            }}
            
            /* Botões modernos */
            .stButton button {{
                background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }}
            
            .stButton button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(30, 58, 138, 0.3);
            }}
            
            /* Painel lateral sticky */
            .sticky-panel {{
                position: sticky;
                top: 20px;
                background: {COLORS["card_bg"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            }}
            
            .panel-title {{
                color: {COLORS["primary"]};
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }}
            
            .panel-subtitle {{
                color: {COLORS["text_light"]};
                font-size: 0.9rem;
                margin-bottom: 1rem;
                border-bottom: 1px solid {COLORS["border"]};
                padding-bottom: 0.5rem;
            }}
            
            /* Ícones e badges */
            .feature-icon {{
                font-size: 2rem;
                margin-bottom: 1rem;
                color: {COLORS["primary"]};
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, {COLORS["primary"]}15, {COLORS["secondary"]}15);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid {COLORS["border"]};
            }}
            
            .stat-number {{
                font-size: 2rem;
                font-weight: 700;
                color: {COLORS["primary"]};
                margin-bottom: 0.5rem;
            }}
            
            .stat-label {{
                color: {COLORS["text_light"]};
                font-size: 0.9rem;
            }}
            
            /* Animações */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .fade-in {{
                animation: fadeIn 0.6s ease-out;
            }}
            
            /* Estilos originais preservados para os mapas */
            .top-banner, .footer-banner {{ 
                width: 100%; 
                height: auto; 
                border-radius: 8px; 
                margin-bottom: 20px; 
            }}
            
            /* Botão de toggle aprimorado */
            #toggle-lyr-unidade-pulse button, #toggle-panel-pulse button {{
                 background-color: {COLORS["accent"]} !important;
                 border-color: {COLORS["accent"]} !important;
                 color: white !important;
                 font-weight: 600;
                 border-radius: 6px;
            }}
            #toggle-lyr-unidade button, #toggle-panel button {{
                 background-color: #ffffff !important;
                 border-color: {COLORS["border"]} !important;
                 color: {COLORS["text_light"]} !important;
                 font-weight: 500;
                 border-radius: 6px;
            }}
            
            @keyframes pulseunidade {{
                0%    {{ transform: scale(1);    box-shadow: 0 0 0 0 {COLORS["accent"]}40; }} 
                70%  {{ transform: scale(1.03); box-shadow: 0 0 0 12px {COLORS["accent"]}00; }}
                100% {{ transform: scale(1);    box-shadow: 0 0 0 0 {COLORS["accent"]}00; }}
            }}
            #toggle-lyr-unidade-pulse button {{
                animation: pulseunidade 1.1s ease-in-out 0s 2;
                border-color: {COLORS["accent"]} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def create_header():
    st.markdown(
        f"""
        <div class="main-header fade-in">
            <div class="header-content">
                <img src="https://logospng.org/wp-content/uploads/general-mills.png" alt="Logo da General Mills" class="header-logo">
                <div class="header-text">
                    <h1>Mapa de Calor - General Mills - Cajamar > São Paulo</h1>
                    <p>Visualize dados de entregas, peso e faturamento da unidade de forma interativa</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================
# Helpers para cards (1 chamada = 1 card completo)
# =====================================================
def render_card(title_html: str, body_html: str):
    st.markdown(
        f"""
        <div class="modern-card fade-in">
            {title_html}
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =====================================================
# Funções utilitárias (mantidas do código original)
# =====================================================
def show_top_banner():
    st.markdown(
        '<img src="https://i.ibb.co/v4d32PvX/banner.jpg" alt="Banner topo" style="width:100%; border-radius:12px; margin-bottom:2rem;" />',
        unsafe_allow_html=True,
    )

def show_footer_banner():
    st.markdown(
        '<img src="https://i.ibb.co/8nQQp8pS/barra-inferrior.png" alt="Banner rodapé" style="width:100%; border-radius:12px; margin-top:2rem;" />',
        unsafe_allow_html=True,
    )

def autodetect_coords(df: pd.DataFrame):
    candidates_lat = [c for c in df.columns if re.search(r"(?:^|\b)(lat|latitude|y)(?:\b|$)", c, re.I)]
    candidates_lon = [c for c in df.columns if re.search(r"(?:^|\b)(lon|long|longitude|x)(?:\b|$)", c, re.I)]
    if candidates_lat and candidates_lon:
        return candidates_lat[0], candidates_lon[0]
    for c in df.columns:
        if re.search(r"coord|coordenad", c, re.I):
            try:
                tmp = df[c].astype(str).str.extract(r"(-?\d+[\.,]?\d*)\s*[,;]\s*(-?\d+[\.,]?\d*)")
                tmp.columns = ["LATITUDE", "LONGITUDE"]
                tmp["LATITUDE"] = tmp["LATITUDE"].str.replace(",", ".", regex=False).astype(float)
                tmp["LONGITUDE"] = tmp["LONGITUDE"].str.replace(",", ".", regex=False).astype(float)
                df["__LAT__"], df["__LON__"] = tmp["LATITUDE"], tmp["LONGITUDE"]
                return "__LAT__", "__LON__"
            except Exception:
                return None
    return None

def add_base_tiles(m: folium.Map):
    tiles = [
        ("CartoDB Positron", "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", "© OpenStreetMap, © CARTO"),
        ("CartoDB Dark", "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", "© OpenStreetMap, © CARTO"),
        ("Esri Satellite", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "Tiles © Esri"),
        ("Open Street Map", "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", "© OpenStreetMap contributors"),
    ]
    for name, url, attr in tiles:
        folium.TileLayer(tiles=url, name=name, attr=attr).add_to(m)

def load_geojson_any(path_candidates):
    for p in path_candidates:
        if p and os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Erro ao ler {p}: {e}")
    return None

def br_money(x):
    try:
        s = str(x).replace("R$", "").strip()
        if "," in s and s.count(".") >= 1:
            s = s.replace(".", "")
        v = float(s.replace(",", "."))
        return f"R$ {v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    except Exception:
        return str(x)

def pick(colnames, *options):
    cols = list(colnames)
    for o in options:
        if o in cols:
            return o
    lower = {c.lower(): c for c in cols}
    for o in options:
        if o.lower() in lower:
            return lower[o.lower()]
    return None

def sniff_read_csv(path: str) -> pd.DataFrame:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            sample = f.read(4096); f.seek(0)
            sep = ";" if sample.count(";") > sample.count(",") else ","
            return pd.read_csv(f, sep=sep)
    except Exception as e:
        st.error(f"Falha ao ler CSV em '{path}': {e}")
        return pd.DataFrame()

def to_float_series(s: pd.Series) -> pd.Series:
    def _conv(v):
        if pd.isna(v): return None
        txt = str(v)
        m = re.search(r"-?\d+[.,]?\d*", txt)
        if not m: return None
        try: return float(m.group(0).replace(",", "."))
        except Exception: return None
    return s.apply(_conv)

def norm_col(c: str) -> str:
    s = unicodedata.normalize("NFKD", str(c))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")

def geojson_bounds(gj: dict):
    if not gj:
        return None
    lats, lons = [], []

    def _ingest_coords(coords):
        if isinstance(coords, (list, tuple)):
            if len(coords) == 2 and isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)):
                lon, lat = coords[0], coords[1]
                lons.append(lon); lats.append(lat)
            else:
                for c in coords:
                    _ingest_coords(c)

    def _walk_feature(f):
        geom = f.get("geometry", {})
        coords = geom.get("coordinates", [])
        _ingest_coords(coords)

    t = gj.get("type")
    if t == "FeatureCollection":
        for f in gj.get("features", []):
            _walk_feature(f)
    elif t == "Feature":
        _walk_feature(gj)
    else:
        _ingest_coords(gj.get("coordinates", []))

    if not lats or not lons:
        return None
    return (min(lats), min(lons)), (max(lats), max(lons))

# =====================================================
# Layout Principal
# =====================================================
css_global()
create_header()

# Abas principais
aba1, aba2, aba3 = st.tabs(["🏠 Página Inicial", "🧭 Malha de Transportes", "🗺️ Mapa de Calor"])

# =====================================================
# 1) Página Inicial - Atualizada (com hover animado nos KPI)
# =====================================================
with aba1:
    # CSS das animações de hover dos KPI
    st.markdown("""
    <style>
      /* cartão base */
      .stat-card{
        position: relative;
        border-radius: 16px;
        transition: transform 160ms ease, box-shadow 160ms ease, background-color 160ms ease, border-color 160ms ease;
        will-change: transform, box-shadow;
        cursor: default;
      }
      /* brilho "sheen" ao passar o mouse */
      .stat-card::after{
        content:"";
        position:absolute;
        top:0; left:-40%;
        width:40%; height:100%;
        background: linear-gradient(120deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.35) 60%, rgba(255,255,255,0) 100%);
        transform: skewX(-20deg) translateX(-120%);
        opacity:0;
        pointer-events:none;
      }
      .stat-card:hover{
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 28px rgba(0,0,0,.15);
      }
      .stat-card:hover::after{
        animation: sheen 900ms ease forwards;
      }
      @keyframes sheen{
        0%   { transform: skewX(-20deg) translateX(-120%); opacity:0; }
        20%  { opacity:1; }
        100% { transform: skewX(-20deg) translateX(260%); opacity:0; }
      }

      /* ícone e número ganham vida no hover */
      .stat-card .feature-icon{
        display:flex; align-items:center; justify-content:center;
        font-size: 28px;
        transition: transform 200ms ease, text-shadow 200ms ease;
        will-change: transform;
      }
      .stat-card:hover .feature-icon{
        transform: translateY(-2px) scale(1.06) rotate(-2deg);
        text-shadow: 0 2px 10px rgba(0,0,0,.15);
      }
      .stat-card .stat-number{
        transition: transform 200ms ease, letter-spacing 200ms ease, text-shadow 200ms ease;
      }
      .stat-card:hover .stat-number{
        transform: translateY(-1px);
        letter-spacing: .4px;
        text-shadow: 0 2px 10px rgba(0,0,0,.12);
      }

      /* acessibilidade: respeita quem prefere menos movimento */
      @media (prefers-reduced-motion: reduce){
        .stat-card, .stat-card * { transition: none !important; animation: none !important; }
      }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="stat-card fade-in">
                <div class="feature-icon">📊</div>
                <div class="stat-number">10.000+</div>
                <div class="stat-label">Entregas</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="stat-card fade-in">
                <div class="feature-icon">〽️</div>
                <div class="stat-number">10.000+</div>
                <div class="stat-label">Peso (ton)</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="stat-card fade-in">
                <div class="feature-icon">💲</div>
                <div class="stat-number">30.000+</div>
                <div class="stat-label">Faturamento (R$)</div>
            </div>
            """, unsafe_allow_html=True
        )

    # espaçamento entre KPI e painel de boas-vindas (mantido)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

      
    # 👉 Painel de boas-vindas
    render_card(
        "<h2>🌟 Bem-vindo ao Atlas Geoespacial de Transportes - General Mills do Brasil</h2>",
        """
        <p>
            Esta plataforma integra <strong>dados geoespaciais</strong> de entregas, pesos e faturamentos para apoiar a toma de deciões estratégias. 
        </p>
        <h3>🎯 Objetivos Principais:</h3>
        <ul>
            <li><strong>Informação</strong>: Disponibilizar dados de forma acessível e objetiva</li>
            <li><strong>Planejamento</strong>: Apoiar decisões baseadas em dados reais de desempenho e cobertura</li>
            <li><strong>Participação</strong>: Engajar os colaboradores às transformações da malha logística</li>
        </ul>
        """
    )
    
    colA, colB = st.columns(2)
    
    with colA:
        render_card(
            "<h3>🧭 Explore as Unidades de Atendimento</h3>",
            (
                "<p>Na aba <strong>'Malha de Transportes'</strong> você encontrará:</p>"
                "<ul>"
                "<li>Centros de Distribuição da General Mills</li>"
                "<li>Centro Fabril</li>"
                "<li>Transit Points (Terceirizados)</li>"
                "<li>Operadores Logísticos de CrossDocking(Terceirizados)</li>"
                "<li>Copacker</li>"
                "</ul>"
            )
        )
    
    with colB:
        render_card(
            "<h3>🗺️ Entenda o nosso atendimento</h3>",
            (
                "<p>No painel <strong>Mapa de Calor</strong> você terá uma visão em formato mapa de calor dos dados:</p>"
                "<ul>"
                "<li>Entregas</li>"
                "<li>Peso</li>"
                "<li>Faturamento</li>"
                "</ul>"
            )
        )

# ==============================================================================================================================================================
# 2) Malha de Transportes - COM MAPAS FUNCIONAIS
# ==============================================================================================================================================================
with aba2:
    # Cabeçalho em card consolidado (um único bloco)
    render_card(
        "<h2>🧭 Malha de Transportes</h2>",
        "<p>Visualize o mapa para conhecer nossas unidades de atendimento</p>",
    )

    # Carrega o arquivo Excel da pasta Github
    EXCEL_FILE_CANDIDATES = ["Unidades de Atendimento.xlsx", "dados/Unidades de Atendimento.xlsx", "/mnt/data/Unidades de Atendimento.xlsx"]
    EXCEL_FILE = next((p for p in EXCEL_FILE_CANDIDATES if os.path.exists(p)), None)

    if EXCEL_FILE is None:
        st.error("❌ Arquivo 'Unidades de Atendimento.xlsx' não encontrado.")
        st.stop()

    try:
        df_unidades_raw = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}")
        st.stop()

    if not df_unidades_raw.empty:
        # Normaliza colunas
        colmap = {c: norm_col(c) for c in df_unidades_raw.columns}
        df_unidade = df_unidades_raw.rename(columns=colmap).copy()
    
        # Detecta lat/lon (já estão nomeadas como "Latitude" e "Longitude")
        lat_col = next((c for c in df_unidades.columns if c in {"latitude", "lat"}), None)
        lon_col = next((c for c in df_unidades.columns if c in {"longitude", "long", "lon"}), None)
        if not lat_col or not lon_col:
            coords = autodetect_coords(df_unidades_raw.copy())
            if coords:
                lat_col, lon_col = coords

        if not lat_col or not lon_col:
            st.error("Não foi possível localizar colunas de latitude/longitude.")
            st.stop()

    dt["__LAT__"] = to_float_series(df[lat_col])
    df["__LON__"] = to_float_series(df[lon_col])

    # Heurística para corrigir inversão e sinal — ajustada para o território brasileiro
    lat_s = pd.to_numeric(df["__LAT__"], errors="coerce")
    lon_s = pd.to_numeric(df["__LON__"], errors="coerce")

    def _pct_inside(a, b):
        try:
            # Brasil: lat entre -35 e +5, lon entre -75 e -34
            m = (a.between(-35.0, 5.0)) & (b.between(-75.0, -34.0))
            return float(m.mean())
        except Exception:
            return 0.0

    cands = [
        ("orig", lat_s, lon_s, _pct_inside(lat_s, lon_s)),
        ("swap", lon_s, lat_s, _pct_inside(lon_s, lat_s)),
        ("neg_lon", lat_s, lon_s.mul(-1.0), _pct_inside(lat_s, lon_s.mul(-1.0))),
        ("swap_neg", lon_s, lat_s.mul(-1.0), _pct_inside(lon_s, lat_s.mul(-1.0))),
    ]
    best = max(cands, key=lambda x: x[3])
    if best[0] != "orig" and best[3] >= cands[0][3]:
        df["__LAT__"], df["__LON__"] = best[1], best[2]

    df_map = df.dropna(subset=["__LAT__", "__LON__"]).copy()

    # Campos para popup/tabela — adaptados ao Excel
    cols = list(df_map.columns)
    def pick_norm(*options):
        return next((c for c in cols if c in [norm_col(o) for o in options]), None)

    c_nome    = pick_norm("Nome da Unidade", "Unidade")          # Nome da unidade (ex: General Mills)
    c_tipo  = pick_norm("Tipo")                  # Tipo: CD, Fábrica, TP, OPL
    c_abastec  = pick_norm("Abastecedor")
    c_cidade = pick_norm("Cidade")               # Cidade como "empresa" visual
    c_uf  = pick_norm("UF")                      # UF como "bairro"

    st.success(f"✅ **{len(df_map)} unidade(s) de atendimento** com coordenadas válidas encontradas")

    # Camadas laterais necessárias (mantidas)
    #base_dir_candidates = ["dados", "/mnt/data"]
    #gj_distritos = load_geojson_any([os.path.join(b, "milha_dist_polig.geojson") for b in base_dir_candidates])
    #gj_sede      = load_geojson_any([os.path.join(b, "Distritos_pontos.geojson") for b in base_dir_candidates])

    # Layout fixo: mapa + painel
    col_map, col_panel = st.columns([5, 2], gap="large")

    # Painel lateral (checkboxes) — renomeado
    with col_panel:
        st.markdown('<div class="sticky-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🎛️ Camadas do Mapa</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-subtitle">Controle a visualização</div>', unsafe_allow_html=True)

        with st.expander("Unidades General Mills", expanded=True):
            show_cd = st.checkbox("Centros de Distribuição", value=True, key="unidade_markers")
            show_fabrica = st.checkbox("Fábricas", value=True, key="unidade_markers")           

        with st.expander("Unidades Terceirizadas", expanded=True):
            show_tp = st.checkbox("Transit Point", value=True, key="unidade_tp")
            show_opl = st.checkbox("OPL", value=True, key="unidade_opl")

        st.markdown('</div>', unsafe_allow_html=True)
    

    # ---------- MAPA FUNCIONAL ----------
        with col_map:
            st.markdown("### 🗺️ Mapa Interativo")

            # Centraliza no Brasil
            m2 = folium.Map(location=[-15.0, -55.0], zoom_start=4, tiles=None)
            add_base_tiles(m2)
            Fullscreen(position='topright').add_to(m2)
            MeasureControl().add_to(m2)
            MousePosition().add_to(m2)
            Draw(export=True).add_to(m2)


            # Função de cor por tipo
            def get_icon_color(tipo):
                t = str(tipo).strip().lower()
                if "cd" == t:
                    return "blue"
                elif "fábrica" in t or "fabrica" in t:
                    return "darkred"
                elif "opl" == t:
                    return "purple"
                elif "tp" == t:
                    return "orange"
                return "gray"
    
            # Adiciona marcadores conforme filtros
            for _, row in df_map.iterrows():
                tipo_val = str(row.get(c_tipo, "")).strip()
                if not tipo_val:
                    continue
                
            # Decide se exibe com base nos checkboxes
            exibir = False
            if tipo_val == "CD" and show_cd:
                exibir = True
            elif tipo_val == "Fábrica" and show_fabrica:
                exibir = True
            elif tipo_val == "TP" and show_tp:
                exibir = True
            elif tipo_val == "OPL" and show_opl:
                exibir = True

            if not exibir:
                continue

            nome      = str(row.get(c_nome, "Unidade")) if c_nome else "Unidade"
            abastec   = str(row.get(c_abastec, "-")) if c_abastec else "-"
            cidade    = str(row.get(c_cidade, "-")) if c_cidade else "-"
            uf        = str(row.get(c_uf, "-")) if c_uf else "-"

            popup_html = f"""
            <div style="font-family:Arial; font-size:13px">
                <h4 style="margin:4px 0 8px 0">📍 {nome}</h4>
                <p><b>Tipo:</b> {tipo_val}</p>
                <p><b>Abastecido por:</b> {abastec}</p>
                <p><b>Localização:</b> {cidade} - {uf}</p>
            </div>
            """

        folium.Marker(
            location=[row["__LAT__"], row["__LON__"]],
            tooltip=f"{tipo_val}: {nome}",
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=get_icon_color(tipo_val), icon="building", prefix="fa")
        ).add_to(m2)

        # Ajusta zoom para abranger todas as unidades visíveis
        if show_cd or show_fabrica or show_tp or show_opl:
            visible_df = df_map[
                ((df_map[c_tipo] == "CD") & show_cd) |
                ((df_map[c_tipo] == "Fábrica") & show_fabrica) |
                ((df_map[c_tipo] == "TP") & show_tp) |
                ((df_map[c_tipo] == "OPL") & show_opl)
            ]
            if not visible_df.empty:
                sw = [visible_df["__LAT__"].min(), visible_df["__LON__"].min()]
                ne = [visible_df["__LAT__"].max(), visible_df["__LON__"].max()]
                m2.fit_bounds([sw, ne], padding=(30, 30))
        
        folium.LayerControl(collapsed=False).add_to(m2)
        folium_static(m2, width=1200, height=700)


# ========== TABELA ==========
    st.markdown("### 📋 Tabela de Unidades")
    display_cols = [c for c in [c_tipo, c_abastec, c_nome, c_cidade, c_uf] if c]
    if display_cols:
        st.dataframe(df_map[display_cols], use_container_width=True)
    else:
        st.dataframe(df_map, use_container_width=True)



# ==============================================================================================================================================================
# 3) Mapa de Calor — FERRAMENTAS PADRONIZADAS
# ==============================================================================================================================================================

"""
with aba3:
    # Import robusto (local) para capturar viewport quando possível
    try:
        from streamlit_folium import st_folium as _st_folium
        _HAS_ST_FOLIUM = True
    except Exception:
        _HAS_ST_FOLIUM = False

    render_card(
        "<h2>🗺️ Mapa de Calor</h2>",
        "<p>Explore as camadas para compreender a distribuição de entregas, peso e faturamento</p>",
    )

    # Painel Fixo
    show_panel = True 
    
    if "m3_view" not in st.session_state:
        st.session_state["m3_view"] = {"center": [-5.680, -39.200], "zoom": 11}
    if "m3_should_fit" not in st.session_state:
        st.session_state["m3_should_fit"] = True

    # Carregar dados GeoJSON - ATUALIZADO COM ESPELHOS D'ÁGUA
    base_dir_candidates = ["dados", "/mnt/data"]
    files = {
        "Distritos": "milha_dist_polig.geojson",
        "Sede Distritos": "Distritos_pontos.geojson",
        "Localidades": "Localidades.geojson",
        "Escolas": "Escolas_publicas.geojson",
        "Unidades de Saúde": "Unidades_saude.geojson",
        "Tecnologias Sociais": "teclogias_sociais.geojson",
        "Poços Cidade": "pocos_cidade_mil.geojson",
        "Poços Zona Rural": "pocos_rural_mil.geojson",
        "Estradas": "estradas_milha.geojson",
        "Outorgas Vigentes": "outorgas_milha.geojson",
        "Espelhos d'Água": "espelhos_dagua.geojson",  # NOVA CAMADA ADICIONADA
    }
    data_geo = {
        name: load_geojson_any([os.path.join(b, fname) for b in base_dir_candidates])
        for name, fname in files.items()
    }

    # Layout do mapa/painel (Fixo)
    col_map, col_panel = st.columns([5, 2], gap="large")

    # Painel de camadas (Fixo) - ATUALIZADO COM ESPELHOS D'ÁGUA
    with col_panel:
        st.markdown('<div class="sticky-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🎯 Camadas do Mapa</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-subtitle">Selecione o que deseja visualizar</div>', unsafe_allow_html=True)

        with st.expander("🗾 Território", expanded=True):
            show_distritos = st.checkbox("Distritos", value=True, key="lyr_distritos")
            show_sede_distritos = st.checkbox("Sede Distritos", value=True, key="lyr_sede")
            show_localidades = st.checkbox("Localidades", value=False, key="lyr_local")

        with st.expander("🏥 Infraestrutura", expanded=False):
            show_escolas = st.checkbox("Escolas", value=False, key="lyr_escolas")
            show_unidades = st.checkbox("Unidades de Saúde", value=False, key="lyr_unid")
            show_estradas = st.checkbox("Estradas", value=False, key="lyr_estradas")

        with st.expander("💧 Recursos Hídricos", expanded=False):
            show_tecnologias = st.checkbox("Tecnologias Sociais", value=False, key="lyr_tec")
            show_outorgas = st.checkbox("Outorgas Vigentes", value=False, key="lyr_outorgas")
            show_espelhos_agua = st.checkbox("Espelhos d'Água", value=False, key="lyr_espelhos")  # NOVO CHECKBOX
            st.markdown("**Poços**")
            show_pocos_cidade = st.checkbox("Poços Cidade", value=False, key="lyr_pc")
            show_pocos_rural = st.checkbox("Poços Zona Rural", value=False, key="lyr_pr")

        st.markdown('</div>', unsafe_allow_html=True)

    # =======================
    # MAPA (usando mesma abordagem da aba Unidades de Atendimento)
    # =======================
    with col_map:
        st.markdown("### 🗺️ Mapa Interativo")

        # Usa SEMPRE o último centro/zoom salvo
        center = st.session_state["m3_view"]["center"]
        zoom   = st.session_state["m3_view"]["zoom"]

        m3 = folium.Map(
            location=center, 
            zoom_start=zoom, 
            tiles=None,
            control_scale=True
        )
        add_base_tiles(m3)
        
        # --- FERRAMENTAS DO MAPA ORGANIZADAS POR POSIÇÃO ---
        
        # LADO ESQUERDO (TOPLEFT)
        
        # 1. Fullscreen - AGORA EM 'topleft'
        Fullscreen(
            position='topleft', 
            title='Tela Cheia', 
            title_cancel='Sair', 
            force_separate_button=True
        ).add_to(m3)
        
        # LADO DIREITO (TOPRIGHT)
        
        # 2. Ferramentas de Desenho - AGORA EM 'topright'
        Draw(
            export=True,
            position='topright',
            draw_options={
                'marker': True,
                'circle': True,
                'polyline': True,
                'polygon': True,
                'rectangle': True
            }
        ).add_to(m3)
        
        # 3. Controle de Medidas - AGORA EM 'topright'
        m3.add_child(MeasureControl(
            primary_length_unit="meters", 
            secondary_length_unit="kilometers", 
            primary_area_unit="hectares",
            position='topright'
        ))
        
        # LADO INFERIOR ESQUERDO (BOTTOMLEFT)
        
        # 4. Posição do Mouse - BOTTOMLEFT (posição mantida)
        MousePosition(
            position='bottomleft',
            separator=' | ',
            empty_string='Coordenadas indisponíveis',
            lng_first=True,
            num_digits=4,
            prefix='Coordenadas:'
        ).add_to(m3)
        
        # Fit somente na primeira carga para centralizar
        if st.session_state["m3_should_fit"] and data_geo.get("Distritos"):
            b = geojson_bounds(data_geo["Distritos"])
            if b:
                (min_lat, min_lon), (max_lat, max_lon) = b
                m3.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
            st.session_state["m3_should_fit"] = False

        # --- Camadas ---
        # Território
        if show_distritos and data_geo.get("Distritos"):
            folium.GeoJson(
                data_geo["Distritos"],
                name="Distritos",
                style_function=lambda x: {"fillColor": "#9fe2fc", "fillOpacity": 0.2, "color": "#000000", "weight": 1},
                tooltip=folium.GeoJsonTooltip(fields=list(data_geo["Distritos"]["features"][0]["properties"].keys())[:3])
            ).add_to(m3)

        if show_sede_distritos and data_geo.get("Sede Distritos"):
            layer_sd = folium.FeatureGroup(name="Sede Distritos")
            for ftr in data_geo["Sede Distritos"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                nome = ftr["properties"].get("nome_do_distrito", "Sede")
                folium.Marker([y, x], tooltip=nome, icon=folium.Icon(color="green", icon="home")).add_to(layer_sd)
            layer_sd.add_to(m3)

        if show_localidades and data_geo.get("Localidades"):
            layer_loc = folium.FeatureGroup(name="Localidades")
            for ftr in data_geo["Localidades"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                props = ftr["properties"]
                nome = props.get("Localidade", "Localidade")
                distrito = props.get("Distrito", "-")
                popup = f"<b>Localidade:</b> {nome}<br><b>Distrito:</b> {distrito}"
                folium.Marker([y, x], tooltip=nome, popup=popup, icon=folium.Icon(color="purple", icon="flag")).add_to(layer_loc)
            layer_loc.add_to(m3)

        # Infraestrutura
        if show_escolas and data_geo.get("Escolas"):
            layer_esc = folium.FeatureGroup(name="Escolas")
            for ftr in data_geo["Escolas"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                props = ftr["properties"]
                nome = props.get("no_entidad", props.get("Name", "Escola"))
                popup = (
                    "<div style='font-family:Arial;font-size:13px'>"
                    f"<b>Escola:</b> {nome}<br>"
                    f"<b>Endereço:</b> {props.get('endereco','-')}"
                    "</div>"
                )
                folium.Marker([y, x], tooltip=nome, popup=popup, icon=folium.Icon(color="red", icon="education")).add_to(layer_esc)
            layer_esc.add_to(m3)

        if show_unidades and data_geo.get("Unidades de Saúde"):
            layer_saude = folium.FeatureGroup(name="Unidades de Saúde")
            for ftr in data_geo["Unidades de Saúde"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                props = ftr["properties"]
                nome = props.get("nome", props.get("Name", "Unidade"))
                popup = (
                    "<div style='font-family:Arial;font-size:13px'>"
                    f"<b>Unidade:</b> {nome}<br>"
                    f"<b>Bairro:</b> {props.get('bairro','-')}<br>"
                    f"<b>Município:</b> {props.get('municipio','-')}"
                    "</div>"
                )
                folium.Marker([y, x], tooltip=nome, popup=popup, icon=folium.Icon(color="green", icon="plus-sign")).add_to(layer_saude)
            layer_saude.add_to(m3)

        # NOVA CAMADA: ESTRADAS
        if show_estradas and data_geo.get("Estradas"):
            layer_estradas = folium.FeatureGroup(name="Estradas")
            folium.GeoJson(
                data_geo["Estradas"],
                name="Estradas",
                style_function=lambda x: {
                    "color": "#8B4513",  # Cor marrom para estradas
                    "weight": 2,         # Linha mais grossa
                    "opacity": 0.8
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=list(data_geo["Estradas"]["features"][0]["properties"].keys())[:3],
                    aliases=["Propriedade:"] * 3  # Rótulos para as propriedades
                )
            ).add_to(layer_estradas)
            layer_estradas.add_to(m3)

        # Recursos Hídricos
        if show_tecnologias and data_geo.get("Tecnologias Sociais"):
            layer_tec = folium.FeatureGroup(name="Tecnologias Sociais")
            for ftr in data_geo["Tecnologias Sociais"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                props = ftr["properties"]
                nome = props.get("Comunidade", props.get("Name", "Tecnologia Social"))
                popup = "<div style='font-family:Arial;font-size:13px'><b>Local:</b> {}</div>".format(nome)
                folium.Marker([y, x], tooltip=nome, popup=popup, icon=folium.Icon(color="orange", icon="tint")).add_to(layer_tec)
            layer_tec.add_to(m3)

        # CAMADA ATUALIZADA: OUTORGAS MILHA
        if show_outorgas and data_geo.get("Outorgas Vigentes"):
            layer_outorgas = folium.FeatureGroup(name="Outorgas Vigentes")
            for ftr in data_geo["Outorgas Vigentes"]["features"]:
                props = ftr["properties"]
                
                # Usar coordenadas geográficas diretamente do GeoJSON
                coords = ftr["geometry"]["coordinates"]
                lng, lat = coords[0], coords[1]
                
                # Criar popup simplificado conforme solicitado
                popup_content = f"""
                <div style='font-family:Arial;font-size:12px;max-width:300px'>
                    <b>Requerente:</b> {props.get('REQUERENTE', 'N/A')}<br>
                    <b>Tipo Manancial:</b> {props.get('TIPO MANANCIAL', 'N/A')}<br>
                    <b>Tipo de Uso:</b> {props.get('TIPO DE USO', 'N/A')}<br>
                    <b>Manancial:</b> {props.get('MANANCIAL', 'N/A')}<br>
                    <b>Fim da Vigência:</b> {props.get('FIM DA VIGÊNCIA', 'N/A')}<br>
                    <b>Volume Outorgado:</b> {props.get('VOLUME OUTORGADO (m³)', 'N/A')} m³
                </div>
                """
                
                # Definir cor baseada no tipo de uso
                tipo_uso = props.get('TIPO DE USO', '').upper()
                if 'IRRIGACAO' in tipo_uso:
                    icon_color = 'green'
                elif 'ABASTECIMENTO_HUMANO' in tipo_uso:
                    icon_color = 'blue'
                elif 'INDUSTRIA' in tipo_uso:
                    icon_color = 'red'
                elif 'SERVICO_E_COMERCIO' in tipo_uso:
                    icon_color = 'purple'
                else:
                    icon_color = 'gray'
                
                folium.Marker(
                    [lat, lng],
                    tooltip=props.get('REQUERENTE', 'Outorga'),
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=icon_color, icon='file-text', prefix='fa')
                ).add_to(layer_outorgas)
            
            layer_outorgas.add_to(m3)

        # NOVA CAMADA: ESPELHOS D'ÁGUA
        if show_espelhos_agua and data_geo.get("Espelhos d'Água"):
            layer_espelhos = folium.FeatureGroup(name="Espelhos d'Água")
            folium.GeoJson(
                data_geo["Espelhos d'Água"],
                name="Espelhos d'Água",
                style_function=lambda x: {
                    "fillColor": "#1E90FF",  # Azul para corpos d'água
                    "fillOpacity": 0.7,      # Opacidade moderada
                    "color": "#000080",      # Borda azul escuro
                    "weight": 2,             # Espessura da borda
                    "opacity": 0.8
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["CODIGOES0", "AREA1"],
                    aliases=["Código:", "Área (ha):"],
                    style=("font-family: Arial; font-size: 12px;")
                ),
                popup=folium.GeoJsonPopup(
                    fields=["CODIGOES0", "AREA1"],
                    aliases=["Código:", "Área (ha):"],
                    style=("font-family: Arial; font-size: 12px; max-width: 300px;")
                )
            ).add_to(layer_espelhos)
            layer_espelhos.add_to(m3)

        if show_pocos_cidade and data_geo.get("Poços Cidade"):
            layer_pc = folium.FeatureGroup(name="Poços Cidade")
            for ftr in data_geo["Poços Cidade"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                props = ftr["properties"]
                nome = props.get("Localidade", props.get("Name", "Poço"))
                popup = (
                    "<div style='font-family:Arial;font-size:13px'>"
                    f"<b>Localidade:</b> {nome}<br>"
                    f"<b>Profundidade:</b> {props.get('Profundida','-')}<br>"
                    f"<b>Vazão (L/h):</b> {props.get('Vazão_LH_2','-')}"
                    "</div>"
                )
                folium.Marker([y, x], tooltip=nome, popup=popup, icon=folium.Icon(color="blue", icon="tint")).add_to(layer_pc)
            layer_pc.add_to(m3)

        if show_pocos_rural and data_geo.get("Poços Zona Rural"):
            layer_pr = folium.FeatureGroup(name="Poços Zona Rural")
            for ftr in data_geo["Poços Zona Rural"]["features"]:
                x, y = ftr["geometry"]["coordinates"]
                props = ftr["properties"]
                nome = props.get("Localidade", props.get("Name", "Poço"))
                popup = (
                    "<div style='font-family:Arial;font-size:13px'>"
                    f"<b>Localidade:</b> {nome}<br>"
                    f"<b>Profundidade:</b> {props.get('Profundida','-')}<br>"
                    f"<b>Vazão (L/h):</b> {props.get('Vazão_LH_2','-')}"
                    "</div>"
                )
                folium.Marker([y, x], tooltip=nome, popup=popup, icon=folium.Icon(color="cadetblue", icon="tint")).add_to(layer_pr)
            layer_pr.add_to(m3)

        # 5. LayerControl (Controle de Camadas) - AGORA EM 'topleft'
        folium.LayerControl(collapsed=True, position='topleft').add_to(m3)

        # Render preservando viewport quando possível
        if _HAS_ST_FOLIUM:
            try:
                out = _st_folium(m3, width=1200, height=700)
            except TypeError:
                out = _st_folium(m3)
            # Atualiza centro/zoom se a lib fornecer
            if isinstance(out, dict):
                last_center = out.get("last_center") or out.get("center")
                zoom_val = out.get("zoom") or out.get("last_zoom")
                if last_center and ("lat" in last_center and "lng" in last_center):
                    st.session_state["m3_view"]["center"] = [last_center["lat"], last_center["lng"]]
                if zoom_val is not None:
                    try:
                        st.session_state["m3_view"]["zoom"] = int(zoom_val)
                    except Exception:
                        pass
        else:
            # Fallback: sem captura de viewport 
            folium_static(m3, width=1200, height=700)
"""

# =====================================================
# Rodapé
# =====================================================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: {COLORS["text_light"]}; padding: 2rem;'>
        <p><strong>Atlas Geoespacial de Transportes</strong> - Desenvolvido para transparência e planejamento estratégico</p>
        <p style='font-size: 0.9rem;'>© 2025 Transporte Corporativo</p>
    </div>
    """,
    unsafe_allow_html=True
)

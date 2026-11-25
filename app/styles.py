"""
Capa visual (tema oscuro) del dashboard de SaludVital.
Solo estilos: CSS, formato de gráficos Plotly y bloques HTML pequeños.
"""
from __future__ import annotations
import streamlit as st

# ── Tokens ───────────────────────────────────────────────────────
BG = "#0B1215"
SURFACE = "#131C21"
SIDEBAR = "#080E11"
LINE = "#223038"
INK = "#E8EEF0"
MUTED = "#8DA2A8"
ACCENT = "#E05A6D"      # burdeo aclarado para fondo oscuro
TEAL = "#4FB3A8"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap');
:root {{ --bg:{BG}; --surface:{SURFACE}; --line:{LINE}; --ink:{INK}; --muted:{MUTED}; --accent:{ACCENT}; --teal:{TEAL}; }}

html, body, [class*="css"], .stApp, button, input {{ font-family:'Figtree','Segoe UI',sans-serif !important; }}
.stApp {{ background:var(--bg); color:var(--ink); }}
#MainMenu, footer {{ visibility:hidden; }}
[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ padding-top:2.2rem; padding-bottom:3rem; max-width:1400px; }}

/* Encabezado de página */
.page-header {{ margin:0 0 1.5rem 0; }}
.page-header h1 {{ font-size:2rem; font-weight:800; letter-spacing:-.02em; color:var(--ink); margin:0; padding:0; line-height:1.15; }}
.page-header p {{ color:var(--muted); font-size:1rem; margin:.35rem 0 0 0; }}

/* Títulos y tarjetas */
h3, [data-testid="stHeading"] h3 {{ color:var(--ink) !important; font-weight:700 !important; font-size:1.02rem !important; padding-top:0 !important; }}
[data-testid="stColumn"]:has(h3), [data-testid="column"]:has(h3) {{
    background:var(--surface); border:1px solid var(--line); border-radius:14px;
    padding:1.1rem 1.3rem 1.2rem 1.3rem;
}}
[data-testid="stMarkdownContainer"] li {{ margin-bottom:.55rem; line-height:1.5; color:var(--ink); }}
[data-testid="stMarkdownContainer"] li::marker {{ color:var(--accent); }}
hr {{ border:none !important; border-top:1px solid var(--line) !important; margin:1.6rem 0 !important; }}

/* KPI */
[data-testid="stMetric"] {{
    background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--accent);
    border-radius:12px; padding:1rem 1.15rem; height:100%;
}}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {{ color:var(--muted) !important; font-size:.85rem !important; font-weight:600 !important; }}
[data-testid="stMetricValue"] {{ color:var(--ink) !important; font-weight:800 !important; font-size:1.8rem !important; letter-spacing:-.02em; }}

/* Notas y tablas */
[data-testid="stAlert"] {{ border-radius:12px; border:1px solid var(--line); background:var(--surface); color:var(--muted); }}
[data-testid="stAlert"] p {{ font-size:.86rem; line-height:1.55; color:var(--muted); }}
[data-testid="stDataFrame"] {{ border:1px solid var(--line); border-radius:12px; overflow:hidden; }}

/* ── Barra lateral ── */
[data-testid="stSidebar"] {{ background:{SIDEBAR}; border-right:1px solid var(--line); }}
[data-testid="stSidebar"] hr {{ border-top:1px solid var(--line) !important; margin:1rem 0 !important; }}
.brand {{ display:flex; align-items:center; gap:.7rem; padding:.2rem 0; }}
.brand-mark {{ width:38px; height:38px; border-radius:10px; background:var(--accent); display:grid; place-items:center; flex:none; }}
.brand-name {{ font-size:1.2rem; font-weight:800; color:#fff; line-height:1.1; }}
.brand-sub {{ font-size:.76rem; color:var(--muted); margin-top:2px; }}
.side-title {{ font-size:.85rem; font-weight:700; color:var(--ink); margin:.2rem 0 .6rem 0; }}

/* Navegación */
[data-testid="stSidebar"] [role="radiogroup"] {{ gap:.15rem; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding:.5rem .75rem; border-radius:9px; width:100%; cursor:pointer; transition:background .15s; }}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display:none; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background:rgba(255,255,255,.05); }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background:rgba(224,90,109,.16); box-shadow:inset 3px 0 0 var(--accent); }}
[data-testid="stSidebar"] [role="radiogroup"] label p {{ font-size:.94rem; font-weight:500; color:var(--muted); }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{ color:#fff; font-weight:700; }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ font-size:.8rem; font-weight:600; color:var(--muted); }}

/* Selectores tipo chip (filtros) */
[data-testid="stSidebar"] [data-testid="stPills"] button,
[data-testid="stSidebar"] button[data-testid^="stBaseButton-pills"] {{
    border-radius:999px; border:1px solid var(--line); background:transparent;
    color:var(--muted); font-size:.82rem; font-weight:600; padding:.15rem .75rem; min-height:0;
    transition:all .15s;
}}
[data-testid="stSidebar"] button[data-testid^="stBaseButton-pills"]:hover {{ border-color:var(--muted); color:#fff; }}
[data-testid="stSidebar"] button[data-testid="stBaseButton-pillsActive"] {{
    background:var(--accent); border-color:var(--accent); color:#fff;
}}
[data-testid="stSidebar"] button[data-testid^="stBaseButton-pills"] p {{ color:inherit; }}

/* Fecha y fallback multiselect */
[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div,
[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background:var(--surface) !important; border:1px solid var(--line) !important; border-radius:9px !important;
}}
[data-testid="stSidebar"] input {{ color:var(--ink) !important; }}

/* Botón limpiar: discreto */
[data-testid="stSidebar"] .stButton button {{
    width:100%; background:transparent; border:1px solid var(--line); color:var(--muted);
    border-radius:9px; font-weight:600; transition:all .15s;
}}
[data-testid="stSidebar"] .stButton button:hover {{ border-color:var(--accent); color:#fff; }}
/* ── Mejoras visuales ── */
.stApp {{ background:radial-gradient(1100px 500px at 85% -10%, rgba(224,90,109,.10), transparent 60%), var(--bg); }}
::-webkit-scrollbar {{ width:10px; height:10px; }}
::-webkit-scrollbar-thumb {{ background:#2A3A43; border-radius:8px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
.page-header {{ padding-bottom:1rem; border-bottom:1px solid var(--line); position:relative; }}
.page-header::after {{ content:""; position:absolute; left:0; bottom:-1px; width:72px; height:3px; border-radius:3px; background:linear-gradient(90deg,var(--accent),var(--teal)); }}
.page-header h1 {{ background:linear-gradient(90deg,#fff,#C9D6DA); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.section-title {{ font-size:.78rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; color:var(--muted); margin:1.4rem 0 .6rem 0; }}

/* Tarjetas con elevación */
[data-testid="stColumn"]:has(h3), [data-testid="column"]:has(h3) {{
    box-shadow:0 1px 0 rgba(255,255,255,.03) inset, 0 8px 24px rgba(0,0,0,.25); transition:border-color .2s, transform .2s;
}}
[data-testid="stColumn"]:has(h3):hover, [data-testid="column"]:has(h3):hover {{ border-color:#34464F; }}
[data-testid="stMetric"] {{
    background:linear-gradient(160deg,#16222A 0%,var(--surface) 70%);
    box-shadow:0 6px 18px rgba(0,0,0,.25); transition:transform .18s, border-color .18s;
}}
[data-testid="stMetric"]:hover {{ transform:translateY(-2px); border-color:#34464F; border-left-color:var(--accent); }}
[data-testid="stMetricLabel"] p {{ text-transform:uppercase; letter-spacing:.04em; font-size:.74rem !important; }}

/* Tablas y alertas */
[data-testid="stDataFrame"] {{ box-shadow:0 6px 18px rgba(0,0,0,.2); }}
[data-testid="stAlert"] {{ border-left:3px solid var(--teal); }}

/* Filtros: resumen activo */
.filter-summary {{ display:flex; flex-wrap:wrap; gap:.35rem; margin:.2rem 0 .8rem 0; }}
.fchip {{ font-size:.72rem; font-weight:600; color:#fff; background:rgba(224,90,109,.18); border:1px solid rgba(224,90,109,.45);
    border-radius:999px; padding:.12rem .6rem; }}
.fchip.off {{ color:var(--muted); background:transparent; border-color:var(--line); }}
.count-card {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:.55rem .8rem; margin:.4rem 0 .8rem 0;
    display:flex; justify-content:space-between; align-items:baseline; }}
.count-card b {{ font-size:1.25rem; color:#fff; }}
.count-card span {{ font-size:.74rem; color:var(--muted); }}
[data-testid="stSidebar"] [data-testid="stExpander"] {{ border:1px solid var(--line); border-radius:10px; background:var(--surface); }}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {{ font-size:.85rem; font-weight:700; color:var(--ink); }}
[data-testid="stSidebar"] .stButton button:focus-visible, button:focus-visible {{ outline:2px solid var(--accent) !important; outline-offset:1px; }}
</style>
"""

BRAND_HTML = """
<div class="brand">
  <div class="brand-mark">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"><path d="M12 4v16M4 12h16"/></svg>
  </div>
  <div><div class="brand-name">SaludVital</div><div class="brand-sub">Centro Médico Ambulatorio</div></div>
</div>
"""


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="page-header"><h1>{title}</h1>{sub}</div>', unsafe_allow_html=True)


def sidebar_brand() -> None:
    st.sidebar.markdown(BRAND_HTML, unsafe_allow_html=True)


def sidebar_section(label: str) -> None:
    st.sidebar.markdown(f'<div class="side-title">{label}</div>', unsafe_allow_html=True)


def chip_filter(label: str, options: list, key: str) -> list:
    """Selector múltiple tipo chips. Usa st.pills y cae a multiselect en versiones antiguas."""
    if hasattr(st, "pills"):
        sel = st.sidebar.pills(label, options, selection_mode="multi", key=key)
        return list(sel) if sel else []
    return st.sidebar.multiselect(label, options=options, key=key)


# ── Gráficos Plotly ──────────────────────────────────────────────
def _style_figure(fig):
    fig.update_layout(
        template="plotly_dark",
        colorway=["#E05A6D", "#4FB3A8", "#3B82F6", "#F59E0B", "#8B5CF6", "#10B981", "#EC4899"],
        hovermode="closest",
        font=dict(family="Figtree, Segoe UI, sans-serif", size=13, color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=24, b=8),
        hoverlabel=dict(bgcolor="#1B2830", font=dict(color="#FFFFFF"), bordercolor=LINE),
        legend=dict(title_text="", orientation="h", yanchor="bottom", y=-0.28, x=0, font=dict(size=12, color=MUTED)),
    )
    fig.update_xaxes(showgrid=False, automargin=True, zeroline=False, linecolor=LINE, tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=12))
    fig.update_yaxes(automargin=True, title_text=None, gridcolor="#1A262D", zeroline=False, linecolor="rgba(0,0,0,0)", tickfont=dict(color=MUTED), title_font=dict(color=MUTED, size=12))
    fig.update_traces(textfont=dict(color=INK, size=12), cliponaxis=False, selector=dict(type="bar"))
    fig.update_traces(marker=dict(line=dict(color=SURFACE, width=2)), selector=dict(type="pie"))
    try:
        fig.update_traces(marker_cornerradius=5, selector=dict(type="bar"))
    except Exception:
        pass
    return fig


def _wrap_plotly_chart(original):
    def styled(fig, *args, **kwargs):
        try:
            fig = _style_figure(fig)
        except Exception:
            pass
        kwargs.setdefault("theme", None)
        kwargs.setdefault("config", {"displayModeBar": False})
        return original(fig, *args, **kwargs)
    styled._saludvital_styled = True
    return styled


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    if not getattr(st.plotly_chart, "_saludvital_styled", False):
        st.plotly_chart = _wrap_plotly_chart(st.plotly_chart)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================
# Page & styling
# =========================
st.set_page_config(page_title="PFM ROI Simulator — Beursversie", page_icon="💡", layout="wide")
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Instrument+Sans', sans-serif !important; }
[data-baseweb="tag"] { background-color: #9E77ED !important; color: white !important; }
:root { --pfm-purple:#762181; --pfm-red:#F04438; --pfm-amber:#F59E0B; --pfm-green:#16A34A; }
button[kind="secondary"]{ background-color: var(--pfm-red) !important; color:white !important; border-radius:16px !important; font-weight:600 !important; border:none !important; }
button[kind="secondary"]:hover{ background-color:#d13c30 !important; }
.card { border: 1px solid #eee; border-radius: 14px; padding: 14px 16px; background:#fff; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.kpi  { font-size: 1.25rem; font-weight: 800; font-variant-numeric: tabular-nums; }
.kpi-sub { font-size: .9rem; color:#666; }
.big-card { border:1px solid #FEAC76; background:#FFF7F2; border-radius:14px; padding:18px 20px; }
.big-card .title { font-weight: 800; font-size: 1.1rem; }
.big-card .value { font-weight: 900; font-size: 1.4rem; margin-top:.25rem; }
.badge { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.8rem; font-weight:700; margin-left:6px;}
.badge-green  { background:#E9F9EE; color:#14804A; }
.badge-amber  { background:#FEF3C7; color:#92400E; }
.badge-red    { background:#FEE2E2; color:#991B1B; }
.mt-8 { margin-top: 8px; } .mt-12{ margin-top:12px;} .mt-16{ margin-top:16px;}
</style>
""", unsafe_allow_html=True)

st.title("PFM ROI Simulator — Beursversie")
st.caption("Laat in 60 seconden zien hoe snel mensentellen rendeert.")

# =========================
# Helpers
# =========================
EPS = 1e-9

def fmt_eur(x, decimals=0):
    try:
        s = f"€{x:,.{decimals}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "€0"

def fmt_pct(x, decimals=1):
    return f"{x*100:.{decimals}f}%".replace(".", ",")

# =========================
# Inputs
# =========================
left, right = st.columns([1,1])
with left:
    st.subheader("📥 Basisgegevens")
    visitors_day = st.number_input("Bezoekers per dag", min_value=0, value=800, step=50)
    conv_pct     = st.slider("Conversie (%)", 1, 80, 20, 1) / 100.0
    atv_eur      = st.number_input("Gem. bonbedrag (ATV, €)", min_value=0.0, value=45.0, step=1.0)
    open_days    = st.slider("Openingsdagen per week", 1, 7, 7, 1)

    st.subheader("💰 Investering & marge")
    capex        = st.number_input("Eenmalige investering (€)", min_value=0.0, value=3500.0, step=100.0)
    opex_month   = st.number_input("Maandabonnement (€)", min_value=0.0, value=129.0, step=10.0)
    gross_margin = st.slider("Brutomarge (%)", 10, 90, 60, 1) / 100.0

with right:
    st.subheader("🎛️ Wat-als scenario's")
    uplift_conv  = st.slider("Conversie-boost (%)", 0, 50, 5, 1) / 100.0
    uplift_spv   = st.slider("SPV-boost via upsell/cross-sell (%)", 0, 50, 5, 1) / 100.0
    sat_share    = st.slider("Aandeel omzet op zaterdag (%)", 0, 50, 18, 1) / 100.0
    sat_boost    = st.slider("Extra conversie op zaterdag (%)", 0, 50, 10, 1) / 100.0

# =========================
# Calculations
# =========================
visitors_week = visitors_day * open_days
visitors_month = visitors_week * 4.345
visitors_year = visitors_week * 52

trans_week  = visitors_week * conv_pct
trans_month = visitors_month * conv_pct
trans_year  = visitors_year * conv_pct

turn_week  = trans_week * atv_eur
turn_month = trans_month * atv_eur
turn_year  = trans_year * atv_eur

spv = (turn_week / (visitors_week + EPS))

# Scenario: SPV uplift (alles), conversie uplift (alles), extra zaterdag
conv_new      = conv_pct * (1.0 + uplift_conv)
atv_new       = atv_eur * (1.0 + uplift_spv)

# Saturday component (applies only to saturday share of visitors/turnover)
turn_year_base  = turn_year
turn_year_saturday = turn_year_base * sat_share
turn_year_non_sat  = turn_year_base * (1 - sat_share)

trans_year_base    = trans_year
trans_year_sat     = trans_year_base * sat_share
visitors_year_sat  = visitors_year * sat_share

# saturday boosted conversion
trans_year_sat_new = visitors_year_sat * conv_new * (1.0 + sat_boost)
trans_year_non_sat_new = (visitors_year * (1 - sat_share)) * conv_new

# recompute turnover with new ATV
turn_year_new = (trans_year_sat_new + trans_year_non_sat_new) * atv_new

uplift_year_abs = max(0.0, turn_year_new - turn_year_base)
uplift_month_abs = uplift_year_abs / 12.0
uplift_week_abs = uplift_year_abs / 52.0

# Profit effect (gross margin) and payback
extra_profit_month = uplift_month_abs * gross_margin - opex_month
payback_months = np.inf if extra_profit_month <= 0 else capex / extra_profit_month
roi_year_pct = (uplift_year_abs * gross_margin - opex_month * 12 - capex) / max(1.0, (capex + opex_month * 12))
roi_year_pct = max(-1.0, roi_year_pct)

# Contribution split (approx): from conversion vs SPV
# Conv-only scenario
conv_only_turn = ((visitors_year * sat_share) * (conv_pct * (1+sat_boost)) + (visitors_year * (1 - sat_share)) * conv_pct) * atv_eur
conv_only_uplift = max(0.0, conv_only_turn - turn_year_base)
# SPV-only scenario
spv_only_turn = trans_year_base * (atv_eur * (1 + uplift_spv))
spv_only_uplift = max(0.0, spv_only_turn - turn_year_base)
split_total = max(EPS, conv_only_uplift + spv_only_uplift)
share_conv = conv_only_uplift / split_total
share_spv  = spv_only_uplift / split_total

# =========================
# KPI header
# =========================
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="card"><div>🧮 <b>Baseline omzet/jaar</b></div><div class="kpi">{fmt_eur(turn_year_base)}</div><div class="kpi-sub">Conversie {fmt_pct(conv_pct)} • ATV {fmt_eur(atv_eur,2)}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="card"><div>⚡ <b>Uplift (jaar)</b></div><div class="kpi">{fmt_eur(uplift_year_abs)}</div><div class="kpi-sub">≈ {fmt_eur(uplift_month_abs)}/mnd</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="card"><div>💵 <b>Extra winst/mnd</b></div><div class="kpi">{fmt_eur(extra_profit_month)}</div><div class="kpi-sub">marge {fmt_pct(gross_margin)}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="card"><div>⏱️ <b>Terugverdientijd</b></div><div class="kpi">{ "n.v.t." if np.isinf(payback_months) else f"{payback_months:.1f} mnd".replace(".",",") }</div><div class="kpi-sub">ROI-jaar {fmt_pct(roi_year_pct,1)}</div></div>', unsafe_allow_html=True)

# =========================
# AI-aanbevelingen (boven visuals)
# =========================
st.markdown("### 🤖 Aanbevelingen (AI)")
bullets = []
if uplift_year_abs <= 0:
    bullets.append("Verhoog eerst de **ATV** (bundels, kassabundels) of **conversie** via instap-actie; huidige parameters leveren geen positieve ROI op.")
else:
    if uplift_conv > uplift_spv:
        bullets.append("Zet in op **conversie-optimalisatie** tijdens piekuren (greet & lead, extra FTE op drempel, verkorte wachttijd)." )
    if uplift_spv >= uplift_conv:
        bullets.append("Activeer **upsell/cross-sell** routines (bundels, accessoires); train team op gemiddeld bonbedrag.")
    if sat_boost > 0 and sat_share > 0.12:
        bullets.append("Maak van **zaterdag** je winstmachine: korte promotions per uur, snelle kassavoering, zichtbare bestsellers bij entree.")
    if (not np.isinf(payback_months)) and payback_months < 12:
        bullets.append("Communiceer **payback < 12 mnd** als headline; dit triggert snelle besluitvorming.")
    if extra_profit_month <= 0:
        bullets.append("Verlaag kosten of verhoog marge: heronderhandel abonnement/kosten of richt op categorieën met hogere marge.")
if not bullets:
    bullets.append("Performance stabiel. Test micro-experimenten: 2 weken lang 1 upsell-script + personeelsrooster op piekuren.")

for b in bullets:
    st.write(f"- {b}")

# =========================
# Visuals
# =========================
st.markdown("### 📊 Visualisaties")

# 1) Baseline vs Nieuw (jaar)
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name="Baseline", x=["Omzet/jaar"], y=[turn_year_base]))
fig_bar.add_trace(go.Bar(name="Nieuw (scenario)", x=["Omzet/jaar"], y=[turn_year_new]))
fig_bar.update_layout(barmode="group", height=320, margin=dict(l=20,r=20,t=10,b=10), legend=dict(orientation="h"))
fig_bar.update_yaxes(tickformat=",.0f", title="€ / jaar")
st.plotly_chart(fig_bar, use_container_width=True)

# 2) Donut — bijdrage conversie vs SPV aan uplift
fig_pie = go.Figure(data=[go.Pie(labels=["Conversie", "SPV"], values=[share_conv, share_spv], hole=.55)])
fig_pie.update_layout(height=320, margin=dict(l=20,r=20,t=10,b=10), showlegend=True)
st.plotly_chart(fig_pie, use_container_width=True)

# 3) Sliderkaart samenvatting
st.markdown(
    f'''
<div class="big-card">
  <div class="title">📌 Samenvatting</div>
  <div class="value">{fmt_eur(uplift_year_abs)} uplift/jaar — extra winst {fmt_eur(extra_profit_month)}/mnd — terugverdientijd { "n.v.t." if np.isinf(payback_months) else f"{payback_months:.1f} mnd".replace(".",",") }</div>
  <div class="mt-8">Conversie↑ {fmt_pct(uplift_conv)} • SPV↑ {fmt_pct(uplift_spv)} • Zaterdag extra {fmt_pct(sat_boost)} op {fmt_pct(sat_share)} van omzet</div>
</div>
''',
    unsafe_allow_html=True
)

# =========================
# Export (beurslead)
# =========================
st.markdown("### 📥 Export voor lead")
company = st.text_input("Bedrijfsnaam (optioneel)", "")
contact  = st.text_input("Contactpersoon (optioneel)", "")
if st.button("Genereer korte rapportage (Markdown)"):
    lines = [
        f"# PFM ROI — Quick Scan",
        f"**Bedrijf:** {company or '-'}  ",
        f"**Contact:** {contact or '-'}  ",
        "",
        f"**Baseline omzet/jaar:** {fmt_eur(turn_year_base)}",
        f"**Uplift (jaar):** {fmt_eur(uplift_year_abs)}",
        f"**Extra winst/mnd:** {fmt_eur(extra_profit_month)}",
        f"**Terugverdientijd:** {'n.v.t.' if np.isinf(payback_months) else f'{payback_months:.1f} mnd'.replace('.',',')}",
        "",
        "## Aanbevelingen",
    ] + [f"- {b}" for b in bullets]
    md = "\n".join(lines)
    path = "/mnt/data/roi-quickscan.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    st.success("Rapport gegenereerd.")
    st.markdown(f"[Download ROI Quick Scan](sandbox:{path})")

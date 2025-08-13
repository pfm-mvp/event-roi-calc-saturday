import streamlit as st
import numpy as np
import plotly.graph_objects as go

# =========================
# Page & styling
# =========================
st.set_page_config(page_title="PFM ROI Simulator — Expo Edition (EN)", page_icon="💡", layout="wide")

# Branding colors
PFM_PURPLE = "#762181"
PFM_RED    = "#F04438"
PFM_AMBER  = "#F59E0B"
PFM_GREEN  = "#16A34A"
PFM_ORANGE = "#FEAC76"

expo = st.toggle("Expo mode (bigger UI for trade show screens)", value=True)

# kleuren bovenaan blijven zoals jij ze had
PFM_PURPLE = "#762181"
PFM_RED    = "#F04438"
PFM_AMBER  = "#F59E0B"
PFM_GREEN  = "#16A34A"
PFM_ORANGE = "#FEAC76"

# --- CSS: alleen maat/radius + thumb/hover (geen kleur op rail) ---
BASE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700;800&display=swap');
:root {{ --pfm-purple:{PFM_PURPLE}; --pfm-red:{PFM_RED}; --pfm-amber:{PFM_AMBER}; --pfm-green:{PFM_GREEN}; --pfm-orange:{PFM_ORANGE}; }}
html, body, [class*="css"] {{ font-family: 'Instrument Sans', sans-serif !important; }}

.card {{ border: 1px solid #eee; border-radius: 16px; padding: 14px 16px; background:#fff; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
.kpi  {{ font-variant-numeric: tabular-nums; font-weight: 800; }}
.kpi-sub {{ color:#666; }}
.payback-card {{ border:1px solid var(--pfm-orange); background: #FFF7F2; }}
.payback-title {{ font-weight:700; }}

/* PFM red button */
.stButton > button {{ background-color: var(--pfm-red) !important; color: white !important; border:none !important; border-radius: 12px !important; font-weight:700 !important; height:44px; }}

/* Slider track segmenten – omgedraaid */
.stSlider [data-baseweb="slider"] > div > div:nth-child(1) {{
    background-color: #FAFAFA !important; /* inactief deel (rechts in DOM) */
    height: 6px !important;
    border-radius: 3px !important;
}}
.stSlider [data-baseweb="slider"] > div > div:nth-child(2) {{
    background-color: var(--pfm-purple) !important; /* actief deel (links in DOM) */
    height: 6px !important;
    border-radius: 3px !important;
}}

/* Thumb */
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: var(--pfm-purple) !important;
    border: 2px solid white !important;
    width: 22px !important;
    height: 22px !important;
    margin-top: -1px !important; /* jouw perfecte centrering */
    border-radius: 50% !important;
    transition: background-color .15s ease, box-shadow .15s ease;
}}
.stSlider [data-baseweb="slider"] [role="slider"]:hover,
.stSlider [data-baseweb="slider"] [role="slider"]:focus {{
    background-color: #9350a3 !important;
    box-shadow: 0 0 0 6px rgba(118,33,129,0.12) !important;
}}
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)

# --- JS: zet een gradient op de rail (links paars, rechts #FAFAFA) ---
SLIDER_JS = """
<script>
(function(){
  function paint(slider){
    // BaseWeb structuur: [data-baseweb="slider"] > div (trackwrap) > div (rail)
    const rail = slider.querySelector(':scope > div > div');
    const thumb = slider.querySelector('[role="slider"]');
    if (!rail || !thumb) return;

    const now = parseFloat(thumb.getAttribute('aria-valuenow'));
    const min = parseFloat(thumb.getAttribute('aria-valuemin')) || 0;
    const max = parseFloat(thumb.getAttribute('aria-valuemax')) || 100;
    const pct = Math.max(0, Math.min(100, ((now - min) / (max - min)) * 100));

    // Gradient met !important zodat thema-kleuren nooit winnen
    rail.style.setProperty('background', 
      `linear-gradient(to right, var(--pfm-purple) 0%, var(--pfm-purple) ${pct}%, #FAFAFA ${pct}%, #FAFAFA 100%)`,
      'important'
    );
  }

  function attach(slider){
    const thumb = slider.querySelector('[role="slider"]');
    if (!thumb) return;
    ['input','change','mousemove','keydown','pointermove','pointerup','pointerdown'].forEach(ev=>{
      thumb.addEventListener(ev, ()=>paint(slider), {passive:true});
    });
    paint(slider);
  }

  function scan(){ document.querySelectorAll('.stSlider [data-baseweb="slider"]').forEach(attach); }

  window.addEventListener('load', scan);
  const mo = new MutationObserver(scan);
  mo.observe(document.body, { childList:true, subtree:true });
})();
</script>
"""

st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(SLIDER_JS, unsafe_allow_html=True)

EXPO_CSS = """
<style>
h1, h2, h3, .stMarkdown p { font-size: 1.12em !important; }
.card .kpi { font-size: 1.7rem !important; }
.card .kpi-sub { font-size: 1.05rem !important; }
</style>
"""

st.markdown(BASE_CSS, unsafe_allow_html=True)
if expo:
    st.markdown(EXPO_CSS, unsafe_allow_html=True)

st.title("PFM ROI Simulator — Expo Edition")
st.caption("Show ROI in 60 seconds. Fully interactive, preset-driven.")

# =========================
# Helpers
# =========================
def fmt_eur(x, decimals=0):
    try:
        s = f"€{x:,.{decimals}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "€0"

def fmt_pct(x, decimals=1):
    return f"{x*100:.{decimals}f}%".replace(".", ",")

# =========================
# Presets
# =========================
PRESETS = {
    "Fashion Retail": {
        "visitors_day": 800, "conv_pct": 0.20, "atv_eur": 45.0, "open_days": 7,
        "capex": 1500.0, "opex_month": 30.0, "gross_margin": 0.60,
        "uplift_conv": 0.05, "uplift_spv": 0.05, "sat_share": 0.18, "sat_boost": 0.10,
        "desc": "Fashion: steady weekday traffic, weekend peaks; upsell and fitting-room conversion drive ROI."
    },
    "Optics & Eyewear": {
        "visitors_day": 250, "conv_pct": 0.35, "atv_eur": 140.0, "open_days": 6,
        "capex": 1500.0, "opex_month": 30.0, "gross_margin": 0.65,
        "uplift_conv": 0.04, "uplift_spv": 0.06, "sat_share": 0.20, "sat_boost": 0.08,
        "desc": "Optics: higher ATV with appointment-like footfall; staffing around Saturday boosts conversion."
    },
    "Sports & Outdoor": {
        "visitors_day": 600, "conv_pct": 0.22, "atv_eur": 60.0, "open_days": 7,
        "capex": 1500.0, "opex_month": 30.0, "gross_margin": 0.58,
        "uplift_conv": 0.05, "uplift_spv": 0.07, "sat_share": 0.22, "sat_boost": 0.12,
        "desc": "Sports: seasonal peaks; demo zones and weekend traffic make SPV and conversion pop."
    },
    "Drugstore & Personal Care": {
        "visitors_day": 900, "conv_pct": 0.28, "atv_eur": 22.0, "open_days": 7,
        "capex": 1500.0, "opex_month": 30.0, "gross_margin": 0.40,
        "uplift_conv": 0.03, "uplift_spv": 0.04, "sat_share": 0.16, "sat_boost": 0.06,
        "desc": "Drugstore: high frequency, lower ATV; queue reduction and cross-sell lift weekend ROI."
    },
}

# A. Defaults
for k, v in [
    ("visitors_day", 800), ("conv_pct", 0.20), ("atv_eur", 45.0), ("open_days", 7),
    ("capex", 1500.0), ("opex_month", 30.0), ("gross_margin", 0.60),
    ("uplift_conv", 0.05), ("uplift_spv", 0.05), ("sat_share", 0.18), ("sat_boost", 0.10),
    ("num_stores", 50),  # ← default 50
    ("preset_desc", ""),
]:
    st.session_state.setdefault(k, v)

# =========================
# Preset & scope row (aligned): dropdown | number of stores | button
# =========================
st.markdown("#### Preset & scope")
c1, c2, c3 = st.columns([3, 1, 1])

with c1:
    preset_name = st.selectbox(
        "Preset profile",
        list(PRESETS.keys()),
        index=0,
        key="preset_select",
        label_visibility="collapsed",
    )

# B. In de 'Preset & scope' rij
with c2:
    st.session_state["num_stores"] = st.number_input(
        "Number of stores",
        min_value=1, step=1, value=int(st.session_state["num_stores"]),
        label_visibility="collapsed",
    )
    st.caption("Number of stores")  # label onder het veld

with c3:
    if st.button("Apply preset", use_container_width=True):
        p = PRESETS[preset_name]
        for key in ["visitors_day","conv_pct","atv_eur","open_days",
                    "capex","opex_month","gross_margin","uplift_conv",
                    "uplift_spv","sat_share","sat_boost"]:
            st.session_state[key] = p[key]
        # Preserve current number of stores
        st.session_state["preset_desc"] = p.get("desc","")
        st.rerun()

if st.session_state.get("preset_desc"):
    st.info(st.session_state["preset_desc"])

# =========================
# Inputs
# =========================
left, right = st.columns([1,1])
with left:
    st.subheader("Inputs (per store)")
    st.session_state["visitors_day"] = st.number_input("Visitors per day", min_value=0, value=int(st.session_state["visitors_day"]), step=25)
    st.session_state["conv_pct"]     = st.slider("Conversion rate (%)", 1, 80, int(round(st.session_state["conv_pct"]*100)), 1) / 100.0
    st.session_state["atv_eur"]      = st.number_input("Average ticket value (ATV, €)", min_value=0.0, value=float(st.session_state["atv_eur"]), step=1.0)
    st.session_state["open_days"]    = st.slider("Open days per week", 1, 7, int(st.session_state["open_days"]), 1)

    st.subheader("Investment & margin (per store)")
    st.session_state["capex"]        = st.number_input("One-off investment (€)", min_value=0.0, value=float(st.session_state["capex"]), step=50.0)
    st.session_state["opex_month"]   = st.number_input("Monthly subscription (€)", min_value=0.0, value=float(st.session_state["opex_month"]), step=5.0)
    st.session_state["gross_margin"] = st.slider("Gross margin (%)", 10, 90, int(round(st.session_state["gross_margin"]*100)), 1) / 100.0

with right:
    st.subheader("What-if scenarios (apply to all stores)")
    st.session_state["uplift_conv"]  = st.slider("Conversion uplift (%)", 0, 50, int(round(st.session_state["uplift_conv"]*100)), 1) / 100.0
    st.session_state["uplift_spv"]   = st.slider("SPV uplift via upsell/cross-sell (%)", 0, 50, int(round(st.session_state["uplift_spv"]*100)), 1) / 100.0
    # Expo-proof explanation under SPV
    st.caption(
        "SPV increases the **average basket** across all sales. "
        "**+1% SPV ≈ +1% revenue** (Revenue = Visitors × Conversion × SPV). "
        "Fast wins via bundles, accessories, add‑ons."
    )
    st.session_state["sat_share"]    = st.slider("Share of turnover on Saturdays (%)", 0, 50, int(round(st.session_state["sat_share"]*100)), 1) / 100.0
    st.session_state["sat_boost"]    = st.slider("Extra conversion on Saturdays (%)", 0, 50, int(round(st.session_state["sat_boost"]*100)), 1) / 100.0

# =========================
# Calculations (chain totals = per-store × number of stores)
# =========================
V = st.session_state
n_stores    = int(V["num_stores"])
vis_day     = V["visitors_day"]
conv_pct    = V["conv_pct"]
atv_eur     = V["atv_eur"]
open_days   = V["open_days"]
capex       = V["capex"]
opex_month  = V["opex_month"]
gross_margin= V["gross_margin"]
uplift_conv = V["uplift_conv"]
uplift_spv  = V["uplift_spv"]
sat_share   = V["sat_share"]
sat_boost   = V["sat_boost"]

# Per store baseline
visitors_week_store  = vis_day * open_days
visitors_year_store  = visitors_week_store * 52
trans_year_store     = visitors_year_store * conv_pct
turn_year_store      = trans_year_store * atv_eur

conv_new   = conv_pct * (1.0 + uplift_conv)
atv_new    = atv_eur * (1.0 + uplift_spv)

# Chain totals (baseline)
visitors_year_total = visitors_year_store * n_stores
trans_year_total    = trans_year_store * n_stores
turn_year_total     = turn_year_store * n_stores

# Scenario totals with Saturday boost on conversion
visitors_year_sat_total      = visitors_year_total * sat_share
trans_year_sat_new_total     = visitors_year_sat_total * conv_new * (1.0 + sat_boost)
trans_year_non_sat_new_total = (visitors_year_total * (1 - sat_share)) * conv_new
turn_year_new_total          = (trans_year_sat_new_total + trans_year_non_sat_new_total) * atv_new

uplift_year_abs_total  = max(0.0, turn_year_new_total - turn_year_total)
uplift_month_abs_total = uplift_year_abs_total / 12.0

# Costs & profit (chain-level)
capex_total      = capex * n_stores
opex_month_total = opex_month * n_stores
extra_profit_month_total = uplift_month_abs_total * gross_margin - opex_month_total
payback_months = float("inf") if extra_profit_month_total <= 0 else capex_total / extra_profit_month_total
roi_year_pct   = (uplift_year_abs_total * gross_margin - opex_month_total * 12 - capex_total) / max(1.0, (capex_total + opex_month_total * 12))
roi_year_pct   = max(-1.0, roi_year_pct)

# --- Split for donut (conversion vs SPV), chain-level ---
# Conv-only uplift: conversion changes (incl. Saturday extra), ATV baseline
conv_only_turn_total   = (((visitors_year_total * sat_share) * (conv_pct * (1 + sat_boost)) +
                           (visitors_year_total * (1 - sat_share)) * conv_pct) * atv_eur)
conv_only_uplift_total = max(0.0, conv_only_turn_total - turn_year_total)

# SPV-only uplift: ATV increases, conversions baseline
spv_only_turn_total    = trans_year_total * (atv_eur * (1 + uplift_spv))
spv_only_uplift_total  = max(0.0, spv_only_turn_total - turn_year_total)

split_total = max(1e-9, conv_only_uplift_total + spv_only_uplift_total)
share_conv  = conv_only_uplift_total / split_total
share_spv   = spv_only_uplift_total / split_total

# Pre-format for EU hover tooltips
baseline_eur   = fmt_eur(turn_year_total)
scenario_eur   = fmt_eur(turn_year_new_total)
conv_uplift_eur= fmt_eur(conv_only_uplift_total)
spv_uplift_eur = fmt_eur(spv_only_uplift_total)

# =========================
# KPI Cards (chain totals)
# =========================
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="card"><div><b>🧮 Baseline revenue/year (chain)</b></div><div class="kpi">{baseline_eur}</div><div class="kpi-sub">× {n_stores} stores</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="card"><div><b>⚡ Uplift (year)</b></div><div class="kpi">{fmt_eur(uplift_year_abs_total)}</div><div class="kpi-sub">≈ {fmt_eur(uplift_month_abs_total)} / month</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="card"><div><b>💵 Extra profit/month</b></div><div class="kpi">{fmt_eur(extra_profit_month_total)}</div><div class="kpi-sub">Margin {fmt_pct(gross_margin)}</div></div>', unsafe_allow_html=True)
with k4:
    card_cls = "card payback-card" if (payback_months != float("inf") and payback_months < 12) else "card"
    payback_text = "n/a" if payback_months == float("inf") else f"{payback_months:.1f}".replace(".", ",") + " mo"
    st.markdown(f'<div class="{card_cls}"><div class="payback-title">⏱️ Payback time (chain)</div><div class="kpi">{payback_text}</div><div class="kpi-sub">ROI-year {fmt_pct(roi_year_pct,1)}</div></div>', unsafe_allow_html=True)

# =========================
# Visuals (EU hover tooltips) — chain totals
# =========================
st.markdown("### 📊 Visuals")
h = 420 if expo else 360

# Bar with EU labels + EU hover
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Baseline",
    x=["Revenue/year (chain)"], y=[turn_year_total], marker_color=PFM_AMBER,
    text=[baseline_eur], textposition="outside", cliponaxis=False,
    customdata=[[baseline_eur]],
    hovertemplate="Baseline: %{customdata[0]}<extra></extra>"
))
fig_bar.add_trace(go.Bar(
    name="New (scenario)",
    x=["Revenue/year (chain)"], y=[turn_year_new_total], marker_color=PFM_PURPLE,
    text=[scenario_eur], textposition="outside", cliponaxis=False,
    customdata=[[scenario_eur]],
    hovertemplate="New (scenario): %{customdata[0]}<extra></extra>"
))
fig_bar.update_layout(
    barmode="group",
    height=h,
    margin=dict(l=20, r=20, t=10, b=10),
    legend=dict(orientation="h"),
    bargap=0.5,  # iets ruimte tussen de staven
    bargroupgap=0.20     # ruimte tussen de twee bars in dezelfde groep
)

fig_bar.update_traces(
    marker_line_width=0.5,
    marker_line_color="rgba(0,0,0,0.15)"
)
st.plotly_chart(fig_bar, use_container_width=True)

# Donut: Conversion (red) vs SPV (purple) with EU hover
fig_pie = go.Figure(data=[go.Pie(
    labels=["Conversion", "SPV"],
    values=[share_conv, share_spv],
    hole=.55,
    marker=dict(colors=[PFM_RED, PFM_PURPLE]),
    textinfo="percent+label",
    customdata=[[conv_uplift_eur],[spv_uplift_eur]],
    hovertemplate="%{label}: %{percent} — uplift %{customdata[0]}<extra></extra>"
)])
fig_pie.update_layout(height=h-40, margin=dict(l=20,r=20,t=10,b=10), showlegend=True)
st.plotly_chart(fig_pie, use_container_width=True)

# =========================
# Recommendations
# =========================
st.markdown("### 🤖 Recommendations")
bullets = []
if uplift_year_abs_total <= 0:
    bullets.append("Increase **ATV** (bundles, checkout add-ons) or **conversion** at entry; current inputs do not yield a positive ROI.")
else:
    if uplift_conv > uplift_spv:
        bullets.append("Focus on **conversion** during peak hours (greet & lead, extra front-of-store staffing, queue trimming).")
    if uplift_spv >= uplift_conv:
        bullets.append("Activate **upsell/cross-sell** routines (bundles, accessories); coach teams on average ticket value.")
    if sat_boost > 0 and sat_share > 0.12:
        bullets.append("Make **Saturday** your profit engine: hourly micro-promos, fast checkout, hero products at the entrance.")
    if payback_months != float("inf") and payback_months < 12:
        bullets.append("Headliner: **payback < 12 months** — decision-makers react fast to this.")
    if extra_profit_month_total <= 0:
        bullets.append("Adjust costs or margins: renegotiate subscription or focus on higher-margin categories.")
if not bullets:
    bullets.append("Stable performance. Try micro-experiments: 2 weeks with 1 upsell script + staff roster tuned to peaks.")
for b in bullets:
    st.write(f"- {b}")

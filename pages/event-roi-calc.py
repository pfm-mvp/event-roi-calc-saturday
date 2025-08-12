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
.stButton > button {{ background-color: var(--pfm-red) !important; color: white !important; border:none !important; border-radius: 12px !important; font-weight:700 !important; height:44px; }}
</style>
"""

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

# Session defaults
for k, v in [
    ("visitors_day", 800), ("conv_pct", 0.20), ("atv_eur", 45.0), ("open_days", 7),
    ("capex", 1500.0), ("opex_month", 30.0), ("gross_margin", 0.60),
    ("uplift_conv", 0.05), ("uplift_spv", 0.05), ("sat_share", 0.18), ("sat_boost", 0.10),
    ("preset_desc", ""),
]:
    st.session_state.setdefault(k, v)

# Preset selector + aligned button
c1, c2 = st.columns([3,1])
with c1:
    preset_name = st.selectbox("Preset profile", list(PRESETS.keys()), index=0, key="preset_select")
with c2:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    if st.button("Apply preset", use_container_width=True):
        p = PRESETS[preset_name]
        for key in ["visitors_day","conv_pct","atv_eur","open_days","capex","opex_month","gross_margin","uplift_conv","uplift_spv","sat_share","sat_boost"]:
            st.session_state[key] = p[key]
        st.session_state["preset_desc"] = p.get("desc","")
        st.rerun()

if st.session_state.get("preset_desc"):
    st.info(st.session_state["preset_desc"])

# =========================
# Inputs
# =========================
left, right = st.columns([1,1])
with left:
    st.subheader("Inputs")
    st.session_state["visitors_day"] = st.number_input("Visitors per day", min_value=0, value=int(st.session_state["visitors_day"]), step=25)
    st.session_state["conv_pct"]     = st.slider("Conversion rate (%)", 1, 80, int(round(st.session_state["conv_pct"]*100)), 1) / 100.0
    st.session_state["atv_eur"]      = st.number_input("Average ticket value (ATV, €)", min_value=0.0, value=float(st.session_state["atv_eur"]), step=1.0)
    st.session_state["open_days"]    = st.slider("Open days per week", 1, 7, int(st.session_state["open_days"]), 1)

    st.subheader("Investment & margin")
    st.session_state["capex"]        = st.number_input("One-off investment (€)", min_value=0.0, value=float(st.session_state["capex"]), step=50.0)
    st.session_state["opex_month"]   = st.number_input("Monthly subscription (€)", min_value=0.0, value=float(st.session_state["opex_month"]), step=5.0)
    st.session_state["gross_margin"] = st.slider("Gross margin (%)", 10, 90, int(round(st.session_state["gross_margin"]*100)), 1) / 100.0

with right:
    st.subheader("What-if scenarios")
    st.session_state["uplift_conv"]  = st.slider("Conversion uplift (%)", 0, 50, int(round(st.session_state["uplift_conv"]*100)), 1) / 100.0
    st.session_state["uplift_spv"]   = st.slider("SPV uplift (%)", 0, 50, int(round(st.session_state["uplift_spv"]*100)), 1) / 100.0
    st.session_state["sat_share"]    = st.slider("Share of turnover on Saturdays (%)", 0, 50, int(round(st.session_state["sat_share"]*100)), 1) / 100.0
    st.session_state["sat_boost"]    = st.slider("Extra conversion on Saturdays (%)", 0, 50, int(round(st.session_state["sat_boost"]*100)), 1) / 100.0

# =========================
# Calculations
# =========================
V = st.session_state
visitors_day = V["visitors_day"]
conv_pct     = V["conv_pct"]
atv_eur      = V["atv_eur"]
open_days    = V["open_days"]

capex        = V["capex"]
opex_month   = V["opex_month"]
gross_margin = V["gross_margin"]

uplift_conv  = V["uplift_conv"]
uplift_spv   = V["uplift_spv"]
sat_share    = V["sat_share"]
sat_boost    = V["sat_boost"]

visitors_week  = visitors_day * open_days
visitors_year  = visitors_week * 52
trans_year     = visitors_year * conv_pct
turn_year      = trans_year * atv_eur

conv_new       = conv_pct * (1.0 + uplift_conv)
atv_new        = atv_eur * (1.0 + uplift_spv)

visitors_year_sat = visitors_year * sat_share
trans_year_sat_new     = visitors_year_sat * conv_new * (1.0 + sat_boost)
trans_year_non_sat_new = (visitors_year * (1 - sat_share)) * conv_new
turn_year_new  = (trans_year_sat_new + trans_year_non_sat_new) * atv_new

uplift_year_abs  = max(0.0, turn_year_new - turn_year)
uplift_month_abs = uplift_year_abs / 12.0

extra_profit_month = uplift_month_abs * gross_margin - opex_month
payback_months = float("inf") if extra_profit_month <= 0 else capex / extra_profit_month
roi_year_pct   = (uplift_year_abs * gross_margin - opex_month * 12 - capex) / max(1.0, (capex + opex_month * 12))
roi_year_pct   = max(-1.0, roi_year_pct)

# --- Split for donut (conversion vs SPV) ---
# Conv-only: Saturday gets extra conversion, non-Saturday stays baseline conversion; ATV baseline.
conv_only_turn   = ((visitors_year * sat_share) * (conv_pct * (1 + sat_boost)) +
                    (visitors_year * (1 - sat_share)) * conv_pct) * atv_eur
conv_only_uplift = max(0.0, conv_only_turn - turn_year)

# SPV-only: keep conversions baseline, apply SPV uplift to ATV.
spv_only_turn    = trans_year * (atv_eur * (1 + uplift_spv))
spv_only_uplift  = max(0.0, spv_only_turn - turn_year)

split_total      = max(1e-9, conv_only_uplift + spv_only_uplift)
share_conv       = conv_only_uplift / split_total
share_spv        = spv_only_uplift / split_total

# Pre-format for EU hover tooltips
baseline_eur = fmt_eur(turn_year)
scenario_eur = fmt_eur(turn_year_new)
conv_uplift_eur = fmt_eur(conv_only_uplift)
spv_uplift_eur  = fmt_eur(spv_only_uplift)

# =========================
# KPI Cards
# =========================
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="card"><div><b>🧮 Baseline revenue/year</b></div><div class="kpi">{baseline_eur}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="card"><div><b>⚡ Uplift (year)</b></div><div class="kpi">{fmt_eur(uplift_year_abs)}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="card"><div><b>💵 Extra profit/month</b></div><div class="kpi">{fmt_eur(extra_profit_month)}</div></div>', unsafe_allow_html=True)
with k4:
    card_cls = "card payback-card" if (payback_months != float("inf") and payback_months < 12) else "card"
    payback_text = "n/a" if payback_months == float("inf") else f"{payback_months:.1f}".replace(".", ",") + " mo"
    st.markdown(f'<div class="{card_cls}"><div class="payback-title">⏱️ Payback time</div><div class="kpi">{payback_text}</div><div class="kpi-sub">ROI-year {fmt_pct(roi_year_pct,1)}</div></div>', unsafe_allow_html=True)

# =========================
# Visuals (EU hover tooltips)
# =========================
st.markdown("### 📊 Visuals")
h = 420 if expo else 360

# --- Bar with EU labels + EU hover ---
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Baseline",
    x=["Revenue/year"], y=[turn_year], marker_color=PFM_AMBER,
    text=[baseline_eur], textposition="outside", cliponaxis=False,
    customdata=[[baseline_eur]],
    hovertemplate="Baseline: %{customdata[0]}<extra></extra>"
))
fig_bar.add_trace(go.Bar(
    name="New (scenario)",
    x=["Revenue/year"], y=[turn_year_new], marker_color=PFM_PURPLE,
    text=[scenario_eur], textposition="outside", cliponaxis=False,
    customdata=[[scenario_eur]],
    hovertemplate="New (scenario): %{customdata[0]}<extra></extra>"
))
fig_bar.update_layout(barmode="group", height=h, margin=dict(l=20,r=20,t=10,b=10), legend=dict(orientation="h"))
st.plotly_chart(fig_bar, use_container_width=True)

# --- Donut: Conversion (red) vs SPV (purple) with EU hover ---
# Values are shares; hover shows both share and absolute uplift in €.
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
if uplift_year_abs <= 0:
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
    if extra_profit_month <= 0:
        bullets.append("Adjust costs or margins: renegotiate subscription or focus on higher-margin categories.")
if not bullets:
    bullets.append("Stable performance. Try micro-experiments: 2 weeks with 1 upsell script + staff roster tuned to peaks.")
for b in bullets:
    st.write(f"- {b}")

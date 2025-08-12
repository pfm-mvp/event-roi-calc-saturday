import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="PFM ROI Simulator — Expo Edition (EN)", page_icon="💡", layout="wide")

expo = st.toggle("Expo mode (bigger UI for trade show screens)", value=True)

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700;800&display=swap');
:root { --pfm-purple:#762181; --pfm-red:#F04438; --pfm-amber:#F59E0B; --pfm-green:#16A34A; }
html, body, [class*="css"] { font-family: 'Instrument Sans', sans-serif !important; }
[data-baseweb="tag"] { background-color: #9E77ED !important; color: white !important; }
.card { border: 1px solid #eee; border-radius: 16px; padding: 14px 16px; background:#fff; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.kpi  { font-variant-numeric: tabular-nums; font-weight: 800; }
.kpi-sub { color:#666; }
.big-card { border:1px solid #FEAC76; background:#FFF7F2; border-radius:16px; padding:18px 20px; }
.big-card .title { font-weight: 800; }
.big-card .value { font-weight: 900; }
.badge { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.8rem; font-weight:700; margin-left:6px;}
.badge-green  { background:#E9F9EE; color:#14804A; }
.badge-amber  { background:#FEF3C7; color:#92400E; }
.badge-red    { background:#FEE2E2; color:#991B1B; }
</style>
"""

EXPO_CSS = """
<style>
h1, h2, h3, .stMarkdown p { font-size: 1.15em !important; }
.card .kpi { font-size: 1.8rem !important; }
.card .kpi-sub { font-size: 1.1rem !important; }
.big-card .title { font-size: 1.2rem !important; }
.big-card .value { font-size: 1.6rem !important; }
</style>
"""

st.markdown(BASE_CSS, unsafe_allow_html=True)
if expo:
    st.markdown(EXPO_CSS, unsafe_allow_html=True)

st.title("PFM ROI Simulator — Expo Edition")
st.caption("Show ROI in 60 seconds. Fully interactive, preset-driven.")

EPS = 1e-9
def fmt_eur(x, decimals=0):
    try:
        s = f"€{x:,.{decimals}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "€0"

def fmt_pct(x, decimals=1):
    return f"{x*100:.{decimals}f}%".replace(".", ",")

PRESETS = {
    "Fashion Retail": {
        "visitors_day": 800, "conv_pct": 0.20, "atv_eur": 45.0, "open_days": 7,
        "capex": 3500.0, "opex_month": 129.0, "gross_margin": 0.60,
        "uplift_conv": 0.05, "uplift_spv": 0.05, "sat_share": 0.18, "sat_boost": 0.10,
        "desc": "Fashion: steady weekday traffic, weekend peaks; upsell and fitting-room conversion drive ROI."
    },
    "Optics & Eyewear": {
        "visitors_day": 250, "conv_pct": 0.35, "atv_eur": 140.0, "open_days": 6,
        "capex": 5000.0, "opex_month": 159.0, "gross_margin": 0.65,
        "uplift_conv": 0.04, "uplift_spv": 0.06, "sat_share": 0.20, "sat_boost": 0.08,
        "desc": "Optics: higher ATV with appointment-like footfall; staffing around Saturday boosts conversion."
    },
    "Sports & Outdoor": {
        "visitors_day": 600, "conv_pct": 0.22, "atv_eur": 60.0, "open_days": 7,
        "capex": 4000.0, "opex_month": 139.0, "gross_margin": 0.58,
        "uplift_conv": 0.05, "uplift_spv": 0.07, "sat_share": 0.22, "sat_boost": 0.12,
        "desc": "Sports: seasonal peaks; demo zones and weekend traffic make SPV and conversion pop."
    },
    "Drugstore & Personal Care": {
        "visitors_day": 900, "conv_pct": 0.28, "atv_eur": 22.0, "open_days": 7,
        "capex": 3000.0, "opex_month": 119.0, "gross_margin": 0.40,
        "uplift_conv": 0.03, "uplift_spv": 0.04, "sat_share": 0.16, "sat_boost": 0.06,
        "desc": "Drugstore: high frequency, lower ATV; queue reduction and cross-sell lift weekend ROI."
    },
}

for k, v in [
    ("visitors_day", 800), ("conv_pct", 0.20), ("atv_eur", 45.0), ("open_days", 7),
    ("capex", 3500.0), ("opex_month", 129.0), ("gross_margin", 0.60),
    ("uplift_conv", 0.05), ("uplift_spv", 0.05), ("sat_share", 0.18), ("sat_boost", 0.10),
    ("preset_desc", ""),
]:
    st.session_state.setdefault(k, v)

col_p1, col_p2 = st.columns([1,1])
with col_p1:
    preset_name = st.selectbox("Preset profile", list(PRESETS.keys()), index=0)
with col_p2:
    if st.button("Apply preset", type="primary"):
        p = PRESETS[preset_name]
        for key in ["visitors_day","conv_pct","atv_eur","open_days","capex","opex_month","gross_margin","uplift_conv","uplift_spv","sat_share","sat_boost"]:
            st.session_state[key] = p[key]
        st.session_state["preset_desc"] = p.get("desc","")
        st.rerun()

if st.session_state.get("preset_desc"):
    st.info(st.session_state["preset_desc"])

left, right = st.columns([1,1])
with left:
    st.subheader("Inputs")
    st.session_state["visitors_day"] = st.number_input("Visitors per day", min_value=0, value=int(st.session_state["visitors_day"]), step=25, key="visitors_day_input")
    st.session_state["conv_pct"]     = st.slider("Conversion rate (%)", 1, 80, int(round(st.session_state["conv_pct"]*100)), 1) / 100.0
    st.session_state["atv_eur"]      = st.number_input("Average ticket value (ATV, €)", min_value=0.0, value=float(st.session_state["atv_eur"]), step=1.0, key="atv_input")
    st.session_state["open_days"]    = st.slider("Open days per week", 1, 7, int(st.session_state["open_days"]), 1)

    st.subheader("Investment & margin")
    st.session_state["capex"]        = st.number_input("One-off investment (€)", min_value=0.0, value=float(st.session_state["capex"]), step=100.0, key="capex_input")
    st.session_state["opex_month"]   = st.number_input("Monthly subscription (€)", min_value=0.0, value=float(st.session_state["opex_month"]), step=10.0, key="opex_input")
    st.session_state["gross_margin"] = st.slider("Gross margin (%)", 10, 90, int(round(st.session_state["gross_margin"]*100)), 1) / 100.0

with right:
    st.subheader("What-if scenarios")
    st.session_state["uplift_conv"]  = st.slider("Conversion uplift (%)", 0, 50, int(round(st.session_state["uplift_conv"]*100)), 1) / 100.0
    st.session_state["uplift_spv"]   = st.slider("SPV uplift via upsell/cross-sell (%)", 0, 50, int(round(st.session_state["uplift_spv"]*100)), 1) / 100.0
    st.session_state["sat_share"]    = st.slider("Share of annual turnover on Saturdays (%)", 0, 50, int(round(st.session_state["sat_share"]*100)), 1) / 100.0
    st.session_state["sat_boost"]    = st.slider("Extra conversion on Saturdays (%)", 0, 50, int(round(st.session_state["sat_boost"]*100)), 1) / 100.0

V = st.session_state
visitors_day = V["visitors_day"] if isinstance(V["visitors_day"], (int,float)) else V["visitors_day_input"]
conv_pct     = V["conv_pct"]
atv_eur      = V["atv_eur"] if isinstance(V["atv_eur"], (int,float)) else V["atv_input"]
open_days    = V["open_days"]

capex        = V["capex"] if isinstance(V["capex"], (int,float)) else V["capex_input"]
opex_month   = V["opex_month"] if isinstance(V["opex_month"], (int,float)) else V["opex_input"]
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

conv_only_turn = ((visitors_year * sat_share) * (conv_pct * (1+sat_boost)) + (visitors_year * (1 - sat_share)) * conv_pct) * atv_eur
conv_only_uplift = max(0.0, conv_only_turn - turn_year)
spv_only_turn = trans_year * (atv_eur * (1 + uplift_spv))
spv_only_uplift = max(0.0, spv_only_turn - turn_year)
split_total = max(1e-9, conv_only_uplift + spv_only_uplift)
share_conv  = conv_only_uplift / split_total
share_spv   = spv_only_uplift / split_total

def fmt_eur_local(x, decimals=0):
    s = f"€{x:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct_local(x, decimals=1):
    return f"{x*100:.{decimals}f}%".replace(".", ",")

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="card"><div>🧮 <b>Baseline revenue/year</b></div><div class="kpi">{fmt_eur_local(turn_year)}</div><div class="kpi-sub">Conv {fmt_pct_local(conv_pct)} • ATV {fmt_eur_local(atv_eur,2)}</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="card"><div>⚡ <b>Uplift (year)</b></div><div class="kpi">{fmt_eur_local(uplift_year_abs)}</div><div class="kpi-sub">≈ {fmt_eur_local(uplift_month_abs)} / month</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="card"><div>💵 <b>Extra profit/month</b></div><div class="kpi">{fmt_eur_local(extra_profit_month)}</div><div class="kpi-sub">Margin {fmt_pct_local(gross_margin)}</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="card"><div>⏱️ <b>Payback time</b></div><div class="kpi">{"n/a" if payback_months == float("inf") else f"{payback_months:.1f} mo".replace(".",",")}</div><div class="kpi-sub">ROI-year {fmt_pct_local(roi_year_pct,1)}</div></div>', unsafe_allow_html=True)

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

st.markdown("### 📊 Visuals")
h = 380 if not expo else 460

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name="Baseline", x=["Revenue/year"], y=[turn_year], marker_color="#F59E0B"))
fig_bar.add_trace(go.Bar(name="New (scenario)", x=["Revenue/year"], y=[turn_year_new], marker_color="#762181"))
fig_bar.update_layout(barmode="group", height=h, margin=dict(l=20,r=20,t=10,b=10), legend=dict(orientation="h"))
fig_bar.update_yaxes(tickformat=",.0f", title="€ / year")
st.plotly_chart(fig_bar, use_container_width=True)

fig_pie = go.Figure(data=[go.Pie(labels=["Conversion", "SPV"], values=[share_conv, share_spv], hole=.55,
                                 marker=dict(colors=["#16A34A", "#762181"]),
                                 textinfo="percent+label")])
fig_pie.update_layout(height=h-40, margin=dict(l=20,r=20,t=10,b=10), showlegend=True)
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown(
    f'''
<div class="big-card">
  <div class="title">📌 Summary</div>
  <div class="value">{fmt_eur_local(uplift_year_abs)} uplift/year — extra profit {fmt_eur_local(uplift_month_abs)}/month — payback {"n/a" if payback_months == float("inf") else f"{payback_months:.1f} mo".replace(".",",")}</div>
  <div class="mt-8">Conv↑ {fmt_pct_local(uplift_conv)} • SPV↑ {fmt_pct_local(uplift_spv)} • Saturday extra {fmt_pct_local(sat_boost)} on {fmt_pct_local(sat_share)} of revenue</div>
</div>
''',
    unsafe_allow_html=True
)

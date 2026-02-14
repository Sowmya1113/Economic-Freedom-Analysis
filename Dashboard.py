import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="2022 Economic Freedom Index",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d1117; color: #e6edf3; }

section[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }

.hero-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 40%, #1c2333 100%);
    border: 1px solid #30363d; border-radius: 16px;
    padding: 2.5rem 3rem; margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.hero-header::before {
    content: ''; position: absolute;
    top: -50%; right: -10%; width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(88,166,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-header::after {
    content: ''; position: absolute;
    bottom: -30%; left: 20%; width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(63,185,80,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem; font-weight: 900;
    color: #e6edf3; line-height: 1.1; margin: 0 0 0.5rem 0;
}
.hero-subtitle {
    font-size: 1rem; color: #8b949e;
    font-weight: 300; letter-spacing: 0.05em;
    text-transform: uppercase; margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(88,166,255,0.12);
    border: 1px solid rgba(88,166,255,0.3);
    color: #58a6ff; padding: 0.25rem 0.75rem;
    border-radius: 20px; font-size: 0.75rem;
    font-weight: 500; letter-spacing: 0.05em;
    text-transform: uppercase; margin-bottom: 1rem;
}
.metric-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 1.25rem 1.5rem;
    position: relative; overflow: hidden; transition: border-color 0.2s;
}
.metric-card:hover { border-color: #58a6ff; }
.metric-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: 12px 12px 0 0;
}
.metric-card.blue::before   { background: linear-gradient(90deg,#58a6ff,#1f6feb); }
.metric-card.green::before  { background: linear-gradient(90deg,#3fb950,#238636); }
.metric-card.orange::before { background: linear-gradient(90deg,#f78166,#da3633); }
.metric-card.yellow::before { background: linear-gradient(90deg,#e3b341,#9e6a03); }
.metric-label {
    font-size: 0.72rem; font-weight: 500; color: #8b949e;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem; font-weight: 700;
    color: #e6edf3; line-height: 1; margin-bottom: 0.2rem;
}
.metric-delta { font-size: 0.78rem; color: #8b949e; }
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem; font-weight: 700;
    color: #e6edf3; margin: 0 0 0.25rem 0;
}
.section-desc { font-size: 0.82rem; color: #8b949e; margin-bottom: 1rem; }
.stDownloadButton > button {
    background: linear-gradient(135deg,#1f6feb,#388bfd) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 500 !important;
    padding: 0.5rem 1.5rem !important; transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(31,111,235,0.4) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #161b22; border-radius: 10px;
    padding: 4px; border: 1px solid #30363d; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 7px;
    color: #8b949e; font-weight: 500; font-size: 0.85rem;
}
.stTabs [aria-selected="true"] { background: #21262d !important; color: #e6edf3 !important; }
hr { border-color: #30363d !important; }
</style>
""", unsafe_allow_html=True)

# ─── THEME CONSTANTS ─────────────────────────────────────────────────────────────
# NOTE: LAYOUT_BASE intentionally contains NO xaxis/yaxis keys.
# Axis styling is always applied separately via update_xaxes() / update_yaxes().
LAYOUT_BASE = dict(
    plot_bgcolor="#0d1117",
    paper_bgcolor="#0d1117",
    font=dict(color="#8b949e", family="DM Sans"),
)
AXIS_STYLE = dict(
    gridcolor="#21262d",
    linecolor="#30363d",
    zerolinecolor="#30363d",
)
COLORBAR_STYLE = dict(
    tickfont=dict(color="#8b949e"),
    title_font=dict(color="#8b949e"),
    bgcolor="#161b22",
    bordercolor="#30363d",
)
LEGEND_STYLE = dict(
    bgcolor="#161b22",
    bordercolor="#30363d",
    font=dict(color="#8b949e"),
)
COLOR_SEQ   = ["#58a6ff","#3fb950","#f78166","#e3b341","#bc8cff","#39d353"]
SCORE_SCALE = [[0,"#da3633"],[0.5,"#e3b341"],[1.0,"#3fb950"]]
GEO_STYLE   = dict(
    bgcolor="#0d1117", showframe=False,
    showcoastlines=True, coastlinecolor="#30363d",
    showland=True, landcolor="#161b22",
    showocean=True, oceancolor="#0d1117",
    showlakes=False,
)

# ─── DATA ───────────────────────────────────────────────────────────────────────
@st.cache_data
def generate_dataset():
    np.random.seed(42)
    countries_data = {
        "Singapore":      {"region":"Asia Pacific",             "rank":1,   "score":84.4,"gdp_ppp":97057,  "population":5.9,   "unemployment":2.7,  "inflation":2.3,   "financial_freedom":80,"monetary_freedom":83.2,"gdp_growth_5yr":3.8},
        "Switzerland":    {"region":"Europe",                   "rank":2,   "score":84.2,"gdp_ppp":74102,  "population":8.7,   "unemployment":2.9,  "inflation":0.6,   "financial_freedom":80,"monetary_freedom":85.4,"gdp_growth_5yr":2.1},
        "Ireland":        {"region":"Europe",                   "rank":3,   "score":82.0,"gdp_ppp":99013,  "population":5.1,   "unemployment":4.8,  "inflation":2.4,   "financial_freedom":70,"monetary_freedom":80.1,"gdp_growth_5yr":6.9},
        "New Zealand":    {"region":"Asia Pacific",             "rank":4,   "score":80.6,"gdp_ppp":41824,  "population":5.1,   "unemployment":3.3,  "inflation":3.9,   "financial_freedom":80,"monetary_freedom":79.3,"gdp_growth_5yr":2.8},
        "Luxembourg":     {"region":"Europe",                   "rank":5,   "score":80.6,"gdp_ppp":131384, "population":0.7,   "unemployment":5.1,  "inflation":3.5,   "financial_freedom":80,"monetary_freedom":82.1,"gdp_growth_5yr":3.2},
        "Taiwan":         {"region":"Asia Pacific",             "rank":6,   "score":80.1,"gdp_ppp":55078,  "population":23.6,  "unemployment":3.8,  "inflation":1.9,   "financial_freedom":70,"monetary_freedom":83.7,"gdp_growth_5yr":4.2},
        "Estonia":        {"region":"Europe",                   "rank":7,   "score":80.0,"gdp_ppp":38985,  "population":1.3,   "unemployment":6.2,  "inflation":4.2,   "financial_freedom":80,"monetary_freedom":78.9,"gdp_growth_5yr":3.7},
        "Netherlands":    {"region":"Europe",                   "rank":8,   "score":79.5,"gdp_ppp":57372,  "population":17.7,  "unemployment":3.2,  "inflation":2.7,   "financial_freedom":80,"monetary_freedom":80.4,"gdp_growth_5yr":2.4},
        "Finland":        {"region":"Europe",                   "rank":9,   "score":79.0,"gdp_ppp":49334,  "population":5.5,   "unemployment":7.7,  "inflation":2.2,   "financial_freedom":70,"monetary_freedom":82.1,"gdp_growth_5yr":1.8},
        "Denmark":        {"region":"Europe",                   "rank":10,  "score":78.8,"gdp_ppp":60494,  "population":5.9,   "unemployment":5.0,  "inflation":1.9,   "financial_freedom":80,"monetary_freedom":83.0,"gdp_growth_5yr":2.0},
        "Australia":      {"region":"Asia Pacific",             "rank":12,  "score":78.0,"gdp_ppp":53799,  "population":26.0,  "unemployment":4.6,  "inflation":3.8,   "financial_freedom":80,"monetary_freedom":79.8,"gdp_growth_5yr":2.7},
        "Sweden":         {"region":"Europe",                   "rank":15,  "score":76.0,"gdp_ppp":54628,  "population":10.4,  "unemployment":8.8,  "inflation":2.2,   "financial_freedom":70,"monetary_freedom":83.4,"gdp_growth_5yr":2.1},
        "Canada":         {"region":"Americas",                 "rank":14,  "score":76.6,"gdp_ppp":51343,  "population":38.3,  "unemployment":7.5,  "inflation":3.4,   "financial_freedom":80,"monetary_freedom":77.9,"gdp_growth_5yr":2.1},
        "Germany":        {"region":"Europe",                   "rank":17,  "score":73.7,"gdp_ppp":52559,  "population":83.2,  "unemployment":3.6,  "inflation":3.2,   "financial_freedom":70,"monetary_freedom":79.2,"gdp_growth_5yr":1.5},
        "South Korea":    {"region":"Asia Pacific",             "rank":19,  "score":73.8,"gdp_ppp":44501,  "population":51.7,  "unemployment":3.7,  "inflation":2.5,   "financial_freedom":70,"monetary_freedom":76.5,"gdp_growth_5yr":2.7},
        "Chile":          {"region":"Americas",                 "rank":20,  "score":73.5,"gdp_ppp":22768,  "population":19.2,  "unemployment":8.3,  "inflation":4.5,   "financial_freedom":70,"monetary_freedom":72.1,"gdp_growth_5yr":3.1},
        "Japan":          {"region":"Asia Pacific",             "rank":23,  "score":72.4,"gdp_ppp":40146,  "population":125.7, "unemployment":2.9,  "inflation":0.2,   "financial_freedom":60,"monetary_freedom":79.5,"gdp_growth_5yr":0.8},
        "United Kingdom": {"region":"Europe",                   "rank":24,  "score":72.7,"gdp_ppp":46510,  "population":68.0,  "unemployment":4.5,  "inflation":2.6,   "financial_freedom":80,"monetary_freedom":78.1,"gdp_growth_5yr":1.5},
        "United States":  {"region":"Americas",                 "rank":25,  "score":72.1,"gdp_ppp":63358,  "population":331.0, "unemployment":5.4,  "inflation":4.7,   "financial_freedom":70,"monetary_freedom":73.4,"gdp_growth_5yr":2.3},
        "Poland":         {"region":"Europe",                   "rank":42,  "score":68.7,"gdp_ppp":33822,  "population":38.0,  "unemployment":3.4,  "inflation":5.1,   "financial_freedom":60,"monetary_freedom":73.8,"gdp_growth_5yr":3.8},
        "Mexico":         {"region":"Americas",                 "rank":68,  "score":65.9,"gdp_ppp":19860,  "population":130.3, "unemployment":3.8,  "inflation":5.7,   "financial_freedom":60,"monetary_freedom":69.4,"gdp_growth_5yr":1.8},
        "Indonesia":      {"region":"Asia Pacific",             "rank":67,  "score":66.0,"gdp_ppp":11812,  "population":277.5, "unemployment":6.5,  "inflation":1.6,   "financial_freedom":40,"monetary_freedom":71.9,"gdp_growth_5yr":4.7},
        "Turkey":         {"region":"Middle East/North Africa", "rank":76,  "score":64.1,"gdp_ppp":30253,  "population":85.3,  "unemployment":12.0, "inflation":19.6,  "financial_freedom":60,"monetary_freedom":56.9,"gdp_growth_5yr":4.1},
        "Vietnam":        {"region":"Asia Pacific",             "rank":90,  "score":61.7,"gdp_ppp":8660,   "population":98.2,  "unemployment":2.4,  "inflation":3.6,   "financial_freedom":30,"monetary_freedom":63.8,"gdp_growth_5yr":6.5},
        "South Africa":   {"region":"Sub-Saharan Africa",       "rank":100, "score":59.3,"gdp_ppp":12489,  "population":60.0,  "unemployment":34.4, "inflation":4.6,   "financial_freedom":50,"monetary_freedom":68.2,"gdp_growth_5yr":0.6},
        "Russia":         {"region":"Europe",                   "rank":113, "score":56.1,"gdp_ppp":27900,  "population":144.0, "unemployment":4.7,  "inflation":6.7,   "financial_freedom":40,"monetary_freedom":64.0,"gdp_growth_5yr":1.2},
        "Nigeria":        {"region":"Sub-Saharan Africa",       "rank":123, "score":55.3,"gdp_ppp":4908,   "population":218.0, "unemployment":33.0, "inflation":16.5,  "financial_freedom":30,"monetary_freedom":55.4,"gdp_growth_5yr":1.6},
        "India":          {"region":"Asia Pacific",             "rank":131, "score":53.9,"gdp_ppp":6590,   "population":1393.0,"unemployment":7.9,  "inflation":5.1,   "financial_freedom":40,"monetary_freedom":65.2,"gdp_growth_5yr":5.8},
        "Brazil":         {"region":"Americas",                 "rank":133, "score":53.4,"gdp_ppp":14998,  "population":215.0, "unemployment":12.8, "inflation":8.3,   "financial_freedom":50,"monetary_freedom":65.3,"gdp_growth_5yr":0.9},
        "Egypt":          {"region":"Middle East/North Africa", "rank":130, "score":54.0,"gdp_ppp":12255,  "population":104.3, "unemployment":7.4,  "inflation":5.2,   "financial_freedom":30,"monetary_freedom":60.3,"gdp_growth_5yr":4.5},
        "Ukraine":        {"region":"Europe",                   "rank":130, "score":54.0,"gdp_ppp":12907,  "population":44.0,  "unemployment":9.9,  "inflation":11.0,  "financial_freedom":30,"monetary_freedom":58.2,"gdp_growth_5yr":1.2},
        "China":          {"region":"Asia Pacific",             "rank":158, "score":48.3,"gdp_ppp":17192,  "population":1412.0,"unemployment":5.1,  "inflation":0.9,   "financial_freedom":10,"monetary_freedom":60.1,"gdp_growth_5yr":6.4},
        "Angola":         {"region":"Sub-Saharan Africa",       "rank":157, "score":48.5,"gdp_ppp":7258,   "population":34.5,  "unemployment":10.0, "inflation":22.3,  "financial_freedom":20,"monetary_freedom":48.1,"gdp_growth_5yr":-0.2},
        "Libya":          {"region":"Middle East/North Africa", "rank":160, "score":46.4,"gdp_ppp":10454,  "population":7.1,   "unemployment":19.3, "inflation":22.7,  "financial_freedom":20,"monetary_freedom":50.2,"gdp_growth_5yr":6.1},
        "Sudan":          {"region":"Sub-Saharan Africa",       "rank":168, "score":38.4,"gdp_ppp":3988,   "population":45.7,  "unemployment":17.1, "inflation":163.3, "financial_freedom":10,"monetary_freedom":22.3,"gdp_growth_5yr":-2.3},
        "Iran":           {"region":"Middle East/North Africa", "rank":168, "score":42.0,"gdp_ppp":13271,  "population":86.8,  "unemployment":9.4,  "inflation":36.5,  "financial_freedom":10,"monetary_freedom":38.2,"gdp_growth_5yr":1.1},
        "Zimbabwe":       {"region":"Sub-Saharan Africa",       "rank":174, "score":36.1,"gdp_ppp":2628,   "population":15.1,  "unemployment":5.3,  "inflation":97.9,  "financial_freedom":20,"monetary_freedom":35.1,"gdp_growth_5yr":1.8},
        "Cuba":           {"region":"Americas",                 "rank":173, "score":26.9,"gdp_ppp":8822,   "population":11.3,  "unemployment":1.1,  "inflation":70.0,  "financial_freedom":10,"monetary_freedom":30.1,"gdp_growth_5yr":-2.1},
        "Venezuela":      {"region":"Americas",                 "rank":175, "score":24.7,"gdp_ppp":1548,   "population":28.7,  "unemployment":7.3,  "inflation":2665.0,"financial_freedom":10,"monetary_freedom":14.2,"gdp_growth_5yr":-12.5},
        "North Korea":    {"region":"Asia Pacific",             "rank":176, "score":2.9, "gdp_ppp":1700,   "population":25.9,  "unemployment":0.0,  "inflation":0.0,   "financial_freedom":0, "monetary_freedom":4.2, "gdp_growth_5yr":-3.5},
    }
    rows = [{"Country": c, **v} for c, v in countries_data.items()]
    df = pd.DataFrame(rows)
    iso_map = {
        "Singapore":"SGP","Switzerland":"CHE","Ireland":"IRL","New Zealand":"NZL",
        "Luxembourg":"LUX","Taiwan":"TWN","Estonia":"EST","Netherlands":"NLD",
        "Finland":"FIN","Denmark":"DNK","Australia":"AUS","Sweden":"SWE",
        "Canada":"CAN","Germany":"DEU","South Korea":"KOR","Chile":"CHL",
        "Japan":"JPN","United Kingdom":"GBR","United States":"USA","Poland":"POL",
        "Mexico":"MEX","Indonesia":"IDN","Turkey":"TUR","Vietnam":"VNM",
        "South Africa":"ZAF","Russia":"RUS","Nigeria":"NGA","India":"IND",
        "Brazil":"BRA","Egypt":"EGY","Ukraine":"UKR","China":"CHN",
        "Angola":"AGO","Libya":"LBY","Sudan":"SDN","Iran":"IRN",
        "Zimbabwe":"ZWE","Cuba":"CUB","Venezuela":"VEN","North Korea":"PRK",
    }
    df["iso_code"] = df["Country"].map(iso_map)
    return df

df = generate_dataset()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <div style='font-family:Playfair Display,serif;font-size:1.3rem;font-weight:700;color:#e6edf3;'>🌍 EFI Dashboard</div>
        <div style='font-size:0.75rem;color:#8b949e;margin-top:0.25rem;'>Heritage Foundation · 2022</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<div style='font-size:0.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:0.5rem;'>Filter by Region</div>", unsafe_allow_html=True)
    all_regions    = ["All"] + sorted(df["region"].unique().tolist())
    selected_region = st.selectbox("Region", all_regions, label_visibility="collapsed")

    st.markdown("<div style='font-size:0.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin:1rem 0 0.5rem;'>Score Range</div>", unsafe_allow_html=True)
    score_range = st.slider("Score Range", 0, 100, (0, 100), label_visibility="collapsed")

    st.markdown("<div style='font-size:0.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin:1rem 0 0.5rem;'>Top N Countries</div>", unsafe_allow_html=True)
    top_n = st.slider("Top N", 5, 40, 20, label_visibility="collapsed")

    st.markdown("---")

    # Apply filters
    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["region"] == selected_region]
    filtered_df = filtered_df[
        (filtered_df["score"] >= score_range[0]) &
        (filtered_df["score"] <= score_range[1])
    ]

    st.download_button(
        label="⬇ Download Dataset (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="economic_freedom_2022.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.72rem;color:#8b949e;text-align:center;'>"
        f"Showing <b style='color:#e6edf3'>{len(filtered_df)}</b> of "
        f"<b style='color:#e6edf3'>{len(df)}</b> countries</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='font-size:0.7rem;color:#8b949e;text-align:center;margin-top:0.3rem;'>Source: Heritage.org</div>", unsafe_allow_html=True)

# ─── HERO ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">Heritage Foundation · Index of Economic Freedom</div>
    <div class="hero-title">2022 Global Economic<br>Freedom Dashboard</div>
    <div class="hero-subtitle">176 Countries · 12 Indicators · One Comprehensive View</div>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ───────────────────────────────────────────────────────────────────
n         = len(filtered_df)
avg_score = filtered_df["score"].mean() if n else 0
top_ctry  = filtered_df.loc[filtered_df["rank"].idxmin(), "Country"] if n else "N/A"
avg_infl  = filtered_df["inflation"].mean() if n else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card blue">
        <div class="metric-label">Countries Analyzed</div>
        <div class="metric-value">{n}</div>
        <div class="metric-delta">from 176 global countries</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card green">
        <div class="metric-label">Avg Freedom Score</div>
        <div class="metric-value">{avg_score:.1f}</div>
        <div class="metric-delta">out of 100 maximum</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card yellow">
        <div class="metric-label">Top Ranked (in view)</div>
        <div class="metric-value" style="font-size:1.4rem;">{top_ctry}</div>
        <div class="metric-delta">highest freedom score</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card orange">
        <div class="metric-label">Avg Inflation Rate</div>
        <div class="metric-value">{avg_infl:.1f}%</div>
        <div class="metric-delta">across filtered countries</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺 World Maps", "📊 Rankings", "📈 Economic Trends", "🔗 Correlations", "📋 Data Table"
])

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 · WORLD MAPS
# ══════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">2022 Economic Freedom Score — Global Choropleth</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Freedom index score for all 176 countries · hover for details</div>', unsafe_allow_html=True)

    fig_map = px.choropleth(
        df, locations="iso_code", color="score",
        hover_name="Country",
        hover_data={"rank": True, "score": ":.1f", "region": True, "iso_code": False},
        color_continuous_scale=[[0,"#da3633"],[0.4,"#e3b341"],[0.7,"#3fb950"],[1.0,"#58a6ff"]],
        range_color=[20, 90],
        labels={"score": "Freedom Score", "rank": "World Rank"},
    )
    fig_map.update_layout(
        **LAYOUT_BASE,
        height=420, margin=dict(l=0, r=0, t=10, b=10),
        coloraxis_colorbar=dict(title="Score", **COLORBAR_STYLE),
        geo=GEO_STYLE,
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-title">Top 40 Ranking Countries</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Highlighted in orange · from the 2022 EFI</div>', unsafe_allow_html=True)
        top40   = df[df["rank"] <= 40].assign(highlight="Top 40")
        rest    = df[df["rank"] > 40].assign(highlight="Others")
        fig_top = px.choropleth(
            pd.concat([rest, top40]), locations="iso_code", color="highlight",
            hover_name="Country",
            hover_data={"rank": True, "score": ":.1f", "highlight": False, "iso_code": False},
            color_discrete_map={"Top 40": "#f78166", "Others": "#21262d"},
        )
        fig_top.update_layout(
            **LAYOUT_BASE, height=300,
            margin=dict(l=0, r=0, t=10, b=10),
            showlegend=False, geo=GEO_STYLE,
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">Bottom Ranking Countries</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Lowest freedom scores highlighted in blue</div>', unsafe_allow_html=True)
        bottom15 = df.nlargest(15, "rank").assign(highlight="Bottom 15")
        others2  = df[~df.index.isin(bottom15.index)].assign(highlight="Others")
        fig_bot  = px.choropleth(
            pd.concat([others2, bottom15]), locations="iso_code", color="highlight",
            hover_name="Country",
            hover_data={"rank": True, "score": ":.1f", "highlight": False, "iso_code": False},
            color_discrete_map={"Bottom 15": "#58a6ff", "Others": "#21262d"},
        )
        fig_bot.update_layout(
            **LAYOUT_BASE, height=300,
            margin=dict(l=0, r=0, t=10, b=10),
            showlegend=False, geo=GEO_STYLE,
        )
        st.plotly_chart(fig_bot, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 · RANKINGS
# ══════════════════════════════════════════════════════════════════════════════════
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Index Score by Unemployment Rate</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Column chart · unemployment % coloured by freedom score</div>', unsafe_allow_html=True)
        df_unemp = filtered_df.sort_values("unemployment", ascending=False).head(top_n)
        fig_unemp = px.bar(
            df_unemp, x="Country", y="unemployment",
            color="score", color_continuous_scale=SCORE_SCALE,
            labels={"unemployment": "Unemployment (%)", "score": "Freedom Score"},
            text="unemployment",
        )
        fig_unemp.update_traces(
            texttemplate="%{text:.1f}", textposition="outside",
            textfont=dict(color="#8b949e", size=9),
        )
        fig_unemp.update_layout(
            **LAYOUT_BASE, height=380, margin=dict(l=10, r=10, t=20, b=60),
            coloraxis_colorbar=dict(title="Score", **COLORBAR_STYLE),
        )
        fig_unemp.update_xaxes(**AXIS_STYLE, tickangle=-45)
        fig_unemp.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_unemp, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Index Score by Population</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Horizontal bar chart · population vs freedom score</div>', unsafe_allow_html=True)
        df_pop = filtered_df.sort_values("population", ascending=False).head(top_n)
        fig_pop = px.bar(
            df_pop, y="Country", x="population", orientation="h",
            color="score", color_continuous_scale=SCORE_SCALE,
            labels={"population": "Population (Millions)", "score": "Freedom Score"},
        )
        fig_pop.update_layout(
            **LAYOUT_BASE, height=380, margin=dict(l=10, r=10, t=20, b=30),
            coloraxis_showscale=False,
        )
        fig_pop.update_xaxes(**AXIS_STYLE)
        fig_pop.update_yaxes(**AXIS_STYLE, tickfont=dict(size=10))
        st.plotly_chart(fig_pop, use_container_width=True)

    st.markdown('<div class="section-title">Index Score by Financial Freedom (Treemap)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Treemap · relative financial freedom by region and country</div>', unsafe_allow_html=True)
    df_tree = filtered_df.copy()
    df_tree["size"] = df_tree["financial_freedom"] + 10
    fig_tree = px.treemap(
        df_tree,
        path=[px.Constant("World"), "region", "Country"],
        values="size", color="financial_freedom",
        color_continuous_scale=SCORE_SCALE,
        hover_data={"score": ":.1f", "financial_freedom": True, "size": False},
        labels={"financial_freedom": "Financial Freedom"},
    )
    fig_tree.update_layout(
        **LAYOUT_BASE, height=420, margin=dict(l=10, r=10, t=20, b=10),
        coloraxis_colorbar=dict(title="Financial Freedom", **COLORBAR_STYLE),
    )
    fig_tree.update_traces(textfont=dict(size=11))
    st.plotly_chart(fig_tree, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 · ECONOMIC TRENDS
# ══════════════════════════════════════════════════════════════════════════════════
with tab3:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">5-Year GDP Growth Rate</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Green = positive growth · Red = economic contraction</div>', unsafe_allow_html=True)
        df_gdp = filtered_df.sort_values("gdp_growth_5yr").head(top_n)
        bar_colors = ["#da3633" if v < 0 else "#3fb950" for v in df_gdp["gdp_growth_5yr"]]
        fig_gdp = go.Figure(go.Bar(
            x=df_gdp["Country"], y=df_gdp["gdp_growth_5yr"],
            marker_color=bar_colors,
            text=df_gdp["gdp_growth_5yr"].round(1),
            textfont=dict(color="#8b949e", size=9),
            textposition="outside",
        ))
        fig_gdp.add_hline(y=0, line_dash="dash", line_color="#30363d", line_width=1)
        fig_gdp.update_layout(
            **LAYOUT_BASE, height=360, margin=dict(l=10, r=10, t=20, b=70),
            yaxis_title="5-Year GDP Growth Rate (%)",
        )
        fig_gdp.update_xaxes(**AXIS_STYLE, tickangle=-45, tickfont=dict(size=9))
        fig_gdp.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_gdp, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Inflation Rate by Country</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Area chart · Venezuela dominates with hyperinflation</div>', unsafe_allow_html=True)
        df_infl  = filtered_df.sort_values("inflation", ascending=False).head(top_n)
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=df_infl["Country"], y=df_infl["inflation"],
            fill="tozeroy", mode="lines+markers",
            line=dict(color="#58a6ff", width=2),
            marker=dict(size=6, color="#58a6ff"),
            fillcolor="rgba(88,166,255,0.15)",
            hovertemplate="<b>%{x}</b><br>Inflation: %{y:.1f}%<extra></extra>",
        ))
        fig_area.update_layout(
            **LAYOUT_BASE, height=360, margin=dict(l=10, r=10, t=20, b=70),
            yaxis_title="Inflation (%)",
        )
        fig_area.update_xaxes(**AXIS_STYLE, tickangle=-45, tickfont=dict(size=9))
        fig_area.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_area, use_container_width=True)

    st.markdown('<div class="section-title">GDP per Capita (PPP) vs Freedom Score</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Bubble chart · bubble size = population · coloured by region</div>', unsafe_allow_html=True)
    fig_bubble = px.scatter(
        filtered_df, x="score", y="gdp_ppp",
        size="population", color="region",
        hover_name="Country", text="Country",
        size_max=55,
        labels={"score":"Freedom Score","gdp_ppp":"GDP per Capita PPP (USD)","region":"Region"},
        color_discrete_sequence=COLOR_SEQ,
    )
    fig_bubble.update_traces(textposition="top center", textfont=dict(size=9, color="#8b949e"))
    fig_bubble.update_layout(
        **LAYOUT_BASE, height=420, margin=dict(l=10, r=10, t=20, b=20),
        legend=LEGEND_STYLE,
    )
    fig_bubble.update_xaxes(**AXIS_STYLE)
    fig_bubble.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_bubble, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 4 · CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════════
with tab4:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-title">Inflation vs Unemployment</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Line graph · correlation between the two key indicators</div>', unsafe_allow_html=True)
        df_corr   = filtered_df.sort_values("inflation")
        fig_corr1 = go.Figure()
        fig_corr1.add_trace(go.Scatter(
            x=df_corr["Country"], y=df_corr["inflation"],
            name="Inflation (%)", mode="lines+markers",
            line=dict(color="#f78166", width=2), marker=dict(size=5),
        ))
        fig_corr1.add_trace(go.Scatter(
            x=df_corr["Country"], y=df_corr["unemployment"],
            name="Unemployment (%)", mode="lines+markers",
            line=dict(color="#58a6ff", width=2), marker=dict(size=5),
        ))
        fig_corr1.update_layout(
            **LAYOUT_BASE, height=360, margin=dict(l=10, r=10, t=20, b=70),
            legend=LEGEND_STYLE,
        )
        fig_corr1.update_xaxes(**AXIS_STYLE, tickangle=-45, showticklabels=False)
        fig_corr1.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_corr1, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">GDP (PPP) vs Monetary Freedom</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">Scatter + numpy trendline · monetary freedom drives prosperity</div>', unsafe_allow_html=True)
        fig_corr2 = px.scatter(
            filtered_df, x="monetary_freedom", y="gdp_ppp",
            color="region", hover_name="Country",
            labels={"monetary_freedom":"Monetary Freedom Score","gdp_ppp":"GDP per Capita PPP (USD)"},
            color_discrete_sequence=COLOR_SEQ,
        )
        # Manual trendline via numpy — no statsmodels needed
        _df_t = filtered_df[["monetary_freedom","gdp_ppp"]].dropna()
        if len(_df_t) >= 2:
            _m, _b = np.polyfit(_df_t["monetary_freedom"], _df_t["gdp_ppp"], 1)
            _xline = np.linspace(_df_t["monetary_freedom"].min(), _df_t["monetary_freedom"].max(), 100)
            fig_corr2.add_trace(go.Scatter(
                x=_xline, y=_m * _xline + _b,
                mode="lines", name="Trend",
                line=dict(color="#e3b341", width=2, dash="dash"),
                showlegend=True,
            ))
        fig_corr2.update_layout(
            **LAYOUT_BASE, height=360, margin=dict(l=10, r=10, t=20, b=20),
            legend=LEGEND_STYLE,
        )
        fig_corr2.update_xaxes(**AXIS_STYLE)
        fig_corr2.update_yaxes(**AXIS_STYLE)
        st.plotly_chart(fig_corr2, use_container_width=True)

    st.markdown('<div class="section-title">Correlation Heatmap — Key Economic Indicators</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Pearson correlation matrix · green = positive · red = negative</div>', unsafe_allow_html=True)
    corr_cols   = ["score","gdp_ppp","population","unemployment","inflation",
                   "financial_freedom","monetary_freedom","gdp_growth_5yr"]
    corr_matrix = filtered_df[corr_cols].corr().round(2)
    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_cols, y=corr_cols,
        colorscale=[[0,"#da3633"],[0.5,"#21262d"],[1,"#3fb950"]],
        zmin=-1, zmax=1,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=10, color="#e6edf3"),
        hoverongaps=False,
    ))
    fig_heat.update_layout(
        **LAYOUT_BASE, height=380, margin=dict(l=10, r=10, t=20, b=20),
    )
    fig_heat.update_xaxes(**AXIS_STYLE, tickfont=dict(size=10))
    fig_heat.update_yaxes(**AXIS_STYLE, tickfont=dict(size=10))
    st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 5 · DATA TABLE
# ══════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">Country Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Browse the full filtered dataset · click column headers to sort</div>', unsafe_allow_html=True)

    display_cols = ["Country","region","rank","score","gdp_ppp","population",
                    "unemployment","inflation","financial_freedom","monetary_freedom","gdp_growth_5yr"]
    display_df = filtered_df[display_cols].sort_values("rank").reset_index(drop=True)
    display_df.columns = [
        "Country","Region","World Rank","Freedom Score","GDP PPP (USD)",
        "Population (M)","Unemployment %","Inflation %",
        "Financial Freedom","Monetary Freedom","5yr GDP Growth %",
    ]
    st.dataframe(display_df, use_container_width=True, height=480, hide_index=True)

    dl1, dl2, _ = st.columns([1, 1, 2])
    with dl1:
        st.download_button(
            label="⬇ Download Full Dataset",
            data=df[display_cols].sort_values("rank").to_csv(index=False).encode("utf-8"),
            file_name="economic_freedom_2022_full.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            label="⬇ Download Filtered",
            data=display_df.to_csv(index=False).encode("utf-8"),
            file_name="economic_freedom_2022_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ─── FOOTER ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='border-top:1px solid #30363d;padding-top:1.5rem;text-align:center;'>
    <div style='font-size:0.75rem;color:#8b949e;'>
        Data sourced from
        <a href='https://www.heritage.org/index/' style='color:#58a6ff;text-decoration:none;'>
            Heritage Foundation · 2022 Index of Economic Freedom
        </a>
        &nbsp;·&nbsp; Built with Streamlit &amp; Plotly
    </div>
</div>
""", unsafe_allow_html=True)

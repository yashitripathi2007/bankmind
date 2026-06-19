"""
BankMind Intelligence Hub
━━━━━━━━━━━━━━━━━━━━━━━━━━
"Turning customer data into actionable banking opportunities."

Track A – Data Analyst Submission
Author: Yashi
Dataset: UCI Bank Marketing Dataset (bank-full.csv)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import (
    load_data,
    apply_filters,
    kpi_stats,
    chart_job_subscription,
    chart_balance_subscription,
    chart_age_group,
    chart_housing_loan,
    chart_opportunity_leaderboard,
    generate_insights,
    high_opportunity_segments,
    opp_label,
    COLORS,
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BankMind Intelligence Hub",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS  (premium fintech look)
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0D1B2A 0%, #1A2A3A 100%);
    color: #E8EDF2;
}

/* ── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #111E2C !important;
    border-right: 1px solid #1E3A5F;
}
[data-testid="stSidebar"] * {
    color: #C8D4E0 !important;
}

/* ── KPI Card ────────────────────────────────── */
.kpi-card {
    background: linear-gradient(135deg, #1A2A3A 0%, #1E3A5F 100%);
    border: 1px solid #2E86AB44;
    border-radius: 16px;
    padding: 22px 24px;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 24px rgba(46,134,171,0.10);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(46,134,171,0.22);
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #8B95A1;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #F6AE2D;
    line-height: 1;
}
.kpi-sub {
    font-size: 12px;
    color: #8B95A1;
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-trend-up   { color: #2DC653; font-size: 13px; }
.kpi-trend-down { color: #E84855; font-size: 13px; }
.kpi-trend-neu  { color: #F6AE2D; font-size: 13px; }

/* ── Section Cards ───────────────────────────── */
.section-card {
    background: rgba(26, 42, 58, 0.85);
    border: 1px solid #1E3A5F55;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.25);
}

/* ── Insight Alert ───────────────────────────── */
.insight-card {
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}
.insight-success { background: rgba(45,198,83,0.10); border-left: 3px solid #2DC653; }
.insight-info    { background: rgba(46,134,171,0.12); border-left: 3px solid #2E86AB; }
.insight-warning { background: rgba(246,174,45,0.10); border-left: 3px solid #F6AE2D; }
.insight-error   { background: rgba(232,72,85,0.10);  border-left: 3px solid #E84855; }

.insight-icon  { font-size: 22px; line-height: 1; flex-shrink: 0; margin-top: 2px; }
.insight-title { font-weight: 600; font-size: 14px; color: #E8EDF2; margin-bottom: 4px; }
.insight-body  { font-size: 13px; color: #A0B0C0; line-height: 1.55; }

/* ── Opportunity Card ────────────────────────── */
.opp-card {
    background: linear-gradient(135deg, #1A2A3A, #0D1B2A);
    border: 1px solid #2E86AB33;
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    height: 100%;
}
.opp-card-icon  { font-size: 28px; }
.opp-card-title { font-size: 11px; font-weight: 600; letter-spacing: 1px;
                  text-transform: uppercase; color: #8B95A1; margin: 6px 0 2px; }
.opp-card-value { font-size: 22px; font-weight: 700; color: #F6AE2D; }
.opp-card-rate  { font-size: 12px; color: #2DC653; margin-top: 4px; }

/* ── Page Header ─────────────────────────────── */
.page-header {
    background: linear-gradient(90deg, #1E3A5F, #0D1B2A);
    border-bottom: 2px solid #F6AE2D44;
    padding: 18px 24px;
    border-radius: 12px;
    margin-bottom: 28px;
}
.page-title { font-size: 26px; font-weight: 700; color: #F6AE2D; margin: 0; }
.page-tagline { font-size: 13px; color: #8B95A1; margin: 4px 0 0; }

/* ── Divider ─────────────────────────────────── */
.section-divider {
    border: none;
    border-top: 1px solid #1E3A5F;
    margin: 28px 0;
}

/* ── Rec Card ────────────────────────────────── */
.rec-card {
    background: rgba(30,58,95,0.35);
    border: 1px solid #2E86AB44;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.rec-num   { font-size: 11px; font-weight: 700; letter-spacing: 1px;
             color: #F6AE2D; text-transform: uppercase; }
.rec-title { font-size: 15px; font-weight: 600; color: #E8EDF2; margin: 4px 0; }
.rec-body  { font-size: 13px; color: #A0B0C0; }

/* ── Score Badge ─────────────────────────────── */
.score-badge-high   { background: rgba(45,198,83,0.15); color: #2DC653;
                      padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.score-badge-medium { background: rgba(246,174,45,0.15); color: #F6AE2D;
                      padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.score-badge-low    { background: rgba(232,72,85,0.15); color: #E84855;
                      padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }

/* ── Metric override ──────────────────────────── */
[data-testid="stMetric"] {
    background: transparent !important;
}

/* ── Tab styling ─────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(13,27,42,0.5);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    color: #8B95A1 !important;
}
.stTabs [aria-selected="true"] {
    background: #1E3A5F !important;
    color: #F6AE2D !important;
}

/* ── Button ──────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1E3A5F, #2E86AB);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(46,134,171,0.4);
}

/* ── Scrollbar ───────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D1B2A; }
::-webkit-scrollbar-thumb { background: #1E3A5F; border-radius: 3px; }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

@st.cache_data
def get_data():
    return load_data("data/bank-full.csv")


try:
    df_raw = get_data()
except FileNotFoundError:
    st.error(
        "⚠️  `data/bank-full.csv` not found. "
        "Download from https://archive.ics.uci.edu/dataset/222/bank+marketing "
        "and place it in the `data/` folder."
    )
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR – FILTER PANEL
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 BankMind Hub")
    st.markdown("*Intelligence Platform*")
    st.markdown("---")
    st.markdown("### 🎛️ Filter Panel")

    age_range = st.slider(
        "Age Range",
        int(df_raw["age"].min()),
        int(df_raw["age"].max()),
        (18, 80),
    )

    job_options = sorted(df_raw["job"].unique().tolist())
    selected_jobs = st.multiselect("Job Type", job_options, placeholder="All jobs")

    marital_opts = sorted(df_raw["marital"].unique().tolist())
    selected_marital = st.multiselect("Marital Status", marital_opts, placeholder="All")

    edu_opts = sorted(df_raw["education"].unique().tolist())
    selected_edu = st.multiselect("Education Level", edu_opts, placeholder="All")

    housing_filter = st.selectbox("Housing Loan", ["All", "Yes", "No"])
    loan_filter = st.selectbox("Personal Loan", ["All", "Yes", "No"])

    if st.button("🔄 Reset Filters"):
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style='font-size:11px;color:#8B95A1;line-height:1.6'>
        📊 Source: UCI Bank Marketing<br>
        📁 Dataset: bank-full.csv<br>
        🔢 Records: {:,}
        </div>
        """.format(len(df_raw)),
        unsafe_allow_html=True,
    )

# Apply filters
df = apply_filters(
    df_raw,
    age_range=age_range,
    jobs=selected_jobs,
    marital=selected_marital,
    education=selected_edu,
    housing=housing_filter,
    loan=loan_filter,
)

# Guard
if df.empty:
    st.warning("No data matches the current filters. Please adjust and try again.")
    st.stop()

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <p class="page-title">🏦 BankMind Intelligence Hub</p>
        <p class="page-tagline">Turning customer data into actionable banking opportunities.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Executive Overview",
        "🔍 Customer Insights",
        "🎯 Opportunity Analyzer",
        "🔎 Customer Explorer",
    ]
)

# ═══════════════════════════════════════════════════════════
#  TAB 1 – EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════
with tab1:
    stats = kpi_stats(df)

    # ── KPI ROW ──────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi_html(label, value, sub, trend_icon, trend_class):
        return f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">
                <span class="{trend_class}">{trend_icon}</span>
                {sub}
            </div>
        </div>
        """

    with k1:
        st.markdown(
            kpi_html("Total Customers", f"{stats['total']:,}", "In filtered view",
                     "👥", "kpi-trend-neu"),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            kpi_html("Subscription Rate", f"{stats['sub_rate']:.1f}%",
                     "Converted prospects", "▲" if stats["sub_rate"] > 11 else "▼",
                     "kpi-trend-up" if stats["sub_rate"] > 11 else "kpi-trend-down"),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            kpi_html("Avg. Account Balance", f"€{stats['avg_bal']:,.0f}",
                     "Mean yearly balance", "💳", "kpi-trend-neu"),
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            kpi_html("Housing Loan Holders", f"{stats['housing_pct']:.1f}%",
                     "Potential debt burden", "▼", "kpi-trend-down"),
            unsafe_allow_html=True,
        )
    with k5:
        st.markdown(
            kpi_html("Personal Loan Holders", f"{stats['loan_pct']:.1f}%",
                     "Active personal debt", "▼", "kpi-trend-down"),
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── OVERVIEW CHARTS ───────────────────────────────────
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.plotly_chart(chart_job_subscription(df), use_container_width=True, key="chart_job_overview")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.plotly_chart(chart_age_group(df), use_container_width=True, key="chart_age_overview")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── EXECUTIVE SUMMARY ────────────────────────────────
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("### 📋 Executive Summary — Key Findings")

    insights = generate_insights(df)
    # Show first 5 in executive summary
    cols = st.columns(2)
    for i, ins in enumerate(insights[:6]):
        level_class = f"insight-{ins['level']}"
        html = f"""
        <div class="insight-card {level_class}">
            <div class="insight-icon">{ins['icon']}</div>
            <div>
                <div class="insight-title">{ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
            </div>
        </div>
        """
        with cols[i % 2]:
            st.markdown(html, unsafe_allow_html=True)

    # ── DOWNLOAD BUTTON ───────────────────────────────────
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    csv_bytes = df.drop(columns=["age_group", "balance_tier"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Export Filtered Data as CSV",
        data=csv_bytes,
        file_name="bankmind_filtered_export.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════
#  TAB 2 – CUSTOMER INSIGHTS
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔍 Customer Insights Dashboard")
    st.markdown(
        "<p style='color:#8B95A1;font-size:13px'>"
        f"Analysing {len(df):,} customers after applied filters."
        "</p>",
        unsafe_allow_html=True,
    )

    # Chart 1 – Job categories
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 💼 Chart 1 — Top Performing Job Categories")
    st.plotly_chart(chart_job_subscription(df), use_container_width=True, key="chart_job_insights")
    best_job = df.groupby("job")["subscribed"].mean().idxmax()
    best_rate = df.groupby("job")["subscribed"].mean().max() * 100
    st.info(
        f"💡 **Insight:** `{best_job.title()}` customers lead with a **{best_rate:.1f}%** "
        f"subscription rate. Campaigns concentrated on this segment deliver the highest ROI per contact."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 2 – Balance vs Subscription
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 💰 Chart 2 — Account Balance vs Subscription Outcome")
    st.plotly_chart(chart_balance_subscription(df), use_container_width=True, key="chart_balance_insights")
    high = df[df["balance"] > df["balance"].median()]["subscribed"].mean() * 100
    low  = df[df["balance"] <= df["balance"].median()]["subscribed"].mean() * 100
    st.info(
        f"💡 **Insight:** Customers with balances above the median (€{df['balance'].median():,.0f}) "
        f"convert at **{high:.1f}%** vs **{low:.1f}%** for those below. "
        "Higher balances generally demonstrate stronger subscription intent."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 3 – Age groups
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 👤 Chart 3 — Age Group Performance")
    st.plotly_chart(chart_age_group(df), use_container_width=True, key="chart_age_insights")
    ag_rates = df.groupby("age_group", observed=True)["subscribed"].mean() * 100
    best_ag = ag_rates.idxmax()
    st.info(
        f"💡 **Insight:** The **{best_ag}** segment demonstrates the strongest conversion potential "
        f"at **{ag_rates.max():.1f}%**. This cohort likely includes customers at peak savings capacity, "
        "planning for retirement or financial consolidation."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chart 4 – Housing loan
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("#### 🏠 Chart 4 — Housing Loan Impact on Subscription")
    st.plotly_chart(chart_housing_loan(df), use_container_width=True, key="chart_housing_insights")
    hl = df.groupby("housing")["subscribed"].mean() * 100
    st.info(
        f"💡 **Business Interpretation:** Customers without a housing loan subscribe at "
        f"**{hl.get('no', 0):.1f}%** vs **{hl.get('yes', 0):.1f}%** for those with one. "
        "Existing mortgage commitments appear to reduce disposable income and product appetite — "
        "targeting non-mortgage holders could significantly improve campaign efficiency."
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  TAB 3 – OPPORTUNITY ANALYZER
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🎯 Customer Opportunity Analyzer")

    segs = high_opportunity_segments(df)

    # ── OPPORTUNITY CARDS ─────────────────────────────────
    st.markdown("#### 🏆 High Opportunity Segments")
    oc1, oc2, oc3, oc4 = st.columns(4)

    def opp_card(icon, title, value, rate_label, rate_value):
        return f"""
        <div class="opp-card">
            <div class="opp-card-icon">{icon}</div>
            <div class="opp-card-title">{title}</div>
            <div class="opp-card-value">{value}</div>
            <div class="opp-card-rate">{rate_label}: {rate_value:.1f}%</div>
        </div>
        """

    with oc1:
        st.markdown(
            opp_card("💼", "Top Job Category", segs["top_job"].title(),
                     "Conversion Rate", segs["top_job_rate"]),
            unsafe_allow_html=True,
        )
    with oc2:
        st.markdown(
            opp_card("👤", "Best Age Group", segs["top_age"],
                     "Conversion Rate", segs["top_age_rate"]),
            unsafe_allow_html=True,
        )
    with oc3:
        st.markdown(
            opp_card("🎓", "Top Education", segs["top_edu"].title(),
                     "Conversion Rate", segs["top_edu_rate"]),
            unsafe_allow_html=True,
        )
    with oc4:
        st.markdown(
            opp_card("💰", "High Balance Tier", f">{segs['median_bal']:,.0f}€",
                     "Conversion Rate", segs["high_bal_rate"]),
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── OPPORTUNITY SCORE LEADERBOARD ────────────────────
    st.markdown("#### 🔢 Opportunity Score Leaderboard")
    st.caption(
        "Score 0–100 combining balance, age-group conversion premium, and debt status. "
        "Higher = more actionable prospect."
    )

    score_seg = (
        df.groupby(["job", "age_group"], observed=True)
        .agg(
            avg_score=("opp_score", "mean"),
            sub_rate=("subscribed", "mean"),
            count=("subscribed", "count"),
        )
        .reset_index()
        .sort_values("avg_score", ascending=False)
        .head(12)
    )
    score_seg["avg_score"] = score_seg["avg_score"].round(1)
    score_seg["sub_rate"]  = (score_seg["sub_rate"] * 100).round(1)
    score_seg["age_group"] = score_seg["age_group"].astype(str)
    score_seg["Tier"] = score_seg["avg_score"].apply(opp_label)

    st.dataframe(
        score_seg.rename(columns={
            "job": "Job", "age_group": "Age Group",
            "avg_score": "Opp. Score", "sub_rate": "Conv. Rate (%)", "count": "Customers",
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── OPPORTUNITY HEATMAP ───────────────────────────────
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.plotly_chart(chart_opportunity_leaderboard(df), use_container_width=True, key="chart_opp_leaderboard")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # ── AI RECOMMENDATIONS ───────────────────────────────
    st.markdown("### 🤖 AI-Powered Recommendation Center")
    st.caption("Auto-generated from dataset statistics — no manual curation.")

    recs = [
        {
            "num": "01",
            "title": f"Prioritise {segs['top_job'].title()} Customers",
            "body": (
                f"{segs['top_job'].title()} customers show a **{segs['top_job_rate']:.1f}%** conversion rate — "
                "the highest of all job categories. Allocate at least 30% of campaign outreach to this segment "
                "for maximum ROI."
            ),
        },
        {
            "num": "02",
            "title": "Target Customers Without Housing Loans",
            "body": (
                f"Non-mortgage holders convert significantly more often than housing loan holders. "
                "Use housing loan status as a primary segmentation filter in your CRM to avoid "
                "wasting RM time on low-conversion prospects."
            ),
        },
        {
            "num": "03",
            "title": "Focus Campaign Spend on High-Balance Accounts",
            "body": (
                f"Customers with balances above €{segs['median_bal']:,.0f} (median) convert at "
                f"**{segs['high_bal_rate']:.1f}%**. Term deposit products align with the financial "
                "goals of asset-rich customers — make balance a top sorting criterion."
            ),
        },
        {
            "num": "04",
            "title": f"Age Group {segs['top_age']}: Your Sweet Spot",
            "body": (
                f"The **{segs['top_age']}** cohort demonstrates a **{segs['top_age_rate']:.1f}%** "
                "subscription rate. These customers are likely at peak earning capacity or approaching "
                "retirement — position products around security and yield."
            ),
        },
        {
            "num": "05",
            "title": "Exclude Dual-Debt Customers From Mass Campaigns",
            "body": (
                "Customers holding both housing AND personal loans show the lowest conversion rates. "
                "Excluding this cohort from mass campaigns reduces cost-per-acquisition and frees "
                "RM bandwidth for genuinely high-potential contacts."
            ),
        },
        {
            "num": "06",
            "title": f"Education Targeting: {segs['top_edu'].title()} Level Leads",
            "body": (
                f"{segs['top_edu'].title()}-educated customers convert at **{segs['top_edu_rate']:.1f}%**. "
                "Higher financial literacy correlates with product receptiveness — tailor messaging "
                "with data-driven yield comparisons rather than basic explanations."
            ),
        },
    ]

    for rec in recs:
        st.markdown(
            f"""
            <div class="rec-card">
                <div class="rec-num">Recommendation {rec['num']}</div>
                <div class="rec-title">{rec['title']}</div>
                <div class="rec-body">{rec['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════
#  TAB 4 – CUSTOMER EXPLORER
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔎 Customer Explorer")
    st.caption("Search and explore individual customer records from the filtered dataset.")

    # ── SEARCH CONTROLS ───────────────────────────────────
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        search_job = st.selectbox("Filter by Job", ["All"] + sorted(df["job"].unique().tolist()))
    with sc2:
        bal_min, bal_max = int(df["balance"].min()), int(df["balance"].max())
        search_bal = st.slider("Balance Range (€)", bal_min, bal_max, (bal_min, bal_max))
    with sc3:
        search_age = st.slider("Age Range", int(df["age"].min()), int(df["age"].max()),
                               (int(df["age"].min()), int(df["age"].max())))
    with sc4:
        search_sub = st.selectbox("Subscription Status", ["All", "Yes", "No"])

    # Apply explorer filters
    explorer_df = df.copy()
    if search_job != "All":
        explorer_df = explorer_df[explorer_df["job"] == search_job]
    explorer_df = explorer_df[
        (explorer_df["balance"] >= search_bal[0]) &
        (explorer_df["balance"] <= search_bal[1]) &
        (explorer_df["age"] >= search_age[0]) &
        (explorer_df["age"] <= search_age[1])
    ]
    if search_sub != "All":
        explorer_df = explorer_df[explorer_df["y"] == search_sub.lower()]

    st.markdown(f"**{len(explorer_df):,} records match** your search criteria.")

    display_cols = ["age", "job", "marital", "education", "balance",
                    "housing", "loan", "opp_score", "y"]
    renamed = {
        "age": "Age", "job": "Job", "marital": "Marital",
        "education": "Education", "balance": "Balance (€)",
        "housing": "Housing Loan", "loan": "Personal Loan",
        "opp_score": "Opp. Score", "y": "Subscribed",
    }
    show_df = (
        explorer_df[display_cols]
        .rename(columns=renamed)
        .head(200)
        .reset_index(drop=True)
    )

    st.dataframe(show_df, use_container_width=True, height=450)

    # Download explorer results
    exp_csv = explorer_df[display_cols].rename(columns=renamed).to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️  Export Explorer Results",
        data=exp_csv,
        file_name="bankmind_explorer_export.csv",
        mime="text/csv",
    )

    # ── MINI STATS ────────────────────────────────────────
    if not explorer_df.empty:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("#### 📊 Quick Stats for Current Selection")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Records", f"{len(explorer_df):,}")
        m2.metric("Avg. Balance", f"€{explorer_df['balance'].mean():,.0f}")
        m3.metric("Subscription Rate", f"{explorer_df['subscribed'].mean()*100:.1f}%")
        m4.metric("Avg. Opp. Score", f"{explorer_df['opp_score'].mean():.1f}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align:center;color:#8B95A1;font-size:12px;padding:12px 0 20px'>
        🏦 BankMind Intelligence Hub &nbsp;|&nbsp;
        UCI Bank Marketing Dataset &nbsp;|&nbsp;
        Built with Streamlit + Plotly &nbsp;|&nbsp;
        VITB AI Innovators Hub — Track A
    </div>
    """,
    unsafe_allow_html=True,
)

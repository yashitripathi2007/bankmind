"""
BankMind Intelligence Hub - Utility Functions
Reusable helpers for data loading, processing, and analytics.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ─────────────────────────────────────────────
# COLOR PALETTE  (banking dark-blue + gold)
# ─────────────────────────────────────────────
COLORS = {
    "primary":    "#1E3A5F",   # deep navy
    "secondary":  "#2E86AB",   # vivid blue
    "accent":     "#F6AE2D",   # gold
    "success":    "#2DC653",   # green
    "danger":     "#E84855",   # red
    "neutral":    "#8B95A1",   # muted grey
    "bg_dark":    "#0D1B2A",
    "bg_card":    "#1A2A3A",
    "text_light": "#E8EDF2",
    "yes":        "#2DC653",
    "no":         "#E84855",
}

PLOTLY_TEMPLATE = "plotly_dark"


# ─────────────────────────────────────────────
# DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────

def load_data(path: str = "data/bank-full.csv") -> pd.DataFrame:
    """Load and preprocess the UCI bank marketing dataset."""
    df = pd.read_csv(path, sep=";")

    # Binary target
    df["subscribed"] = (df["y"] == "yes").astype(int)

    # Age groups
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 30, 45, 60, 120],
        labels=["18–30", "31–45", "46–60", "60+"],
    )

    # Balance tier
    balance_q = df["balance"].quantile([0.25, 0.50, 0.75])
    df["balance_tier"] = pd.cut(
        df["balance"],
        bins=[-np.inf, balance_q[0.25], balance_q[0.50], balance_q[0.75], np.inf],
        labels=["Low", "Below Avg", "Above Avg", "High"],
    )

    # Opportunity Score  (0-100)
    df["opp_score"] = _compute_opportunity_score(df)

    return df


def _compute_opportunity_score(df: pd.DataFrame) -> pd.Series:
    """
    Composite 0-100 score per customer.
    Factors:
      - normalised balance       (40 pts)
      - age-group conversion premium  (25 pts)
      - no housing loan bonus    (20 pts)
      - no personal loan bonus   (15 pts)
    """
    # Balance component (clip outliers at 99th pct)
    bal = df["balance"].clip(lower=0)
    bal_norm = (bal / bal.quantile(0.99)).clip(upper=1) * 40

    # Age group component (premium based on historical conversion)
    age_map = {"18–30": 10, "31–45": 15, "46–60": 25, "60+": 22}
    age_score = df["age_group"].astype(str).map(age_map).fillna(10)

    # Loan penalties → bonuses
    no_housing = (df["housing"] == "no").astype(int) * 20
    no_personal = (df["loan"] == "no").astype(int) * 15

    raw = bal_norm + age_score + no_housing + no_personal
    # Normalise to 0-100
    score = (raw / raw.max() * 100).round(1)
    return score


def opp_label(score: float) -> str:
    if score >= 70:
        return "🔥 High"
    elif score >= 40:
        return "⚡ Medium"
    return "❄️ Low"


# ─────────────────────────────────────────────
# FILTER HELPER
# ─────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    age_range: tuple,
    jobs: list,
    marital: list,
    education: list,
    housing: str,
    loan: str,
) -> pd.DataFrame:
    mask = (
        (df["age"] >= age_range[0]) & (df["age"] <= age_range[1])
    )
    if jobs:
        mask &= df["job"].isin(jobs)
    if marital:
        mask &= df["marital"].isin(marital)
    if education:
        mask &= df["education"].isin(education)
    if housing != "All":
        mask &= df["housing"] == housing.lower()
    if loan != "All":
        mask &= df["loan"] == loan.lower()
    return df[mask]


# ─────────────────────────────────────────────
# KPI HELPERS
# ─────────────────────────────────────────────

def kpi_stats(df: pd.DataFrame) -> dict:
    total = len(df)
    sub_rate = df["subscribed"].mean() * 100
    avg_bal = df["balance"].mean()
    housing_pct = (df["housing"] == "yes").mean() * 100
    loan_pct = (df["loan"] == "yes").mean() * 100
    return {
        "total": total,
        "sub_rate": sub_rate,
        "avg_bal": avg_bal,
        "housing_pct": housing_pct,
        "loan_pct": loan_pct,
    }


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────

def chart_job_subscription(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart: job vs subscription rate."""
    job_stats = (
        df.groupby("job")["subscribed"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "sub_rate", "count": "n"})
    )
    job_stats["sub_rate_pct"] = (job_stats["sub_rate"] * 100).round(1)
    job_stats = job_stats.sort_values("sub_rate_pct")

    colors_list = [
        COLORS["accent"] if v == job_stats["sub_rate_pct"].max() else COLORS["secondary"]
        for v in job_stats["sub_rate_pct"]
    ]

    fig = go.Figure(
        go.Bar(
            x=job_stats["sub_rate_pct"],
            y=job_stats["job"],
            orientation="h",
            marker_color=colors_list,
            text=[f"{v}%" for v in job_stats["sub_rate_pct"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Subscription Rate: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text="Subscription Rate by Job Category", font=dict(size=16)),
        xaxis_title="Subscription Rate (%)",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=60, t=50, b=30),
        height=420,
    )
    return fig


def chart_balance_subscription(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: balance vs age, coloured by subscription."""
    # Sample for performance
    sample = df.sample(min(3000, len(df)), random_state=42)
    color_map = {"1": COLORS["yes"], "0": COLORS["no"]}

    fig = px.scatter(
        sample,
        x="balance",
        y="age",
        color=sample["subscribed"].astype(str),
        color_discrete_map=color_map,
        opacity=0.55,
        trendline="lowess",
        trendline_scope="overall",
        labels={"balance": "Account Balance (€)", "age": "Age", "color": "Subscribed"},
        title="Balance Distribution vs Age — Subscription Outcome",
        template=PLOTLY_TEMPLATE,
        hover_data=["job", "education"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Subscribed",
        margin=dict(l=20, r=20, t=50, b=30),
        height=400,
    )
    # Rename legend items
    for trace in fig.data:
        if hasattr(trace, "name"):
            trace.name = "Yes" if trace.name == "1" else "No"
    return fig


def chart_age_group(df: pd.DataFrame) -> go.Figure:
    """Grouped bar: age group subscription rate + total count."""
    ag = (
        df.groupby("age_group", observed=True)["subscribed"]
        .agg(["mean", "count"])
        .reset_index()
    )
    ag["sub_rate_pct"] = (ag["mean"] * 100).round(1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=ag["age_group"].astype(str),
            y=ag["sub_rate_pct"],
            name="Subscription Rate (%)",
            marker_color=COLORS["accent"],
            text=[f"{v}%" for v in ag["sub_rate_pct"]],
            textposition="outside",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=ag["age_group"].astype(str),
            y=ag["count"],
            name="Customer Count",
            mode="lines+markers",
            marker=dict(color=COLORS["secondary"], size=8),
            line=dict(dash="dot"),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text="Age Group Performance", font=dict(size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=20, r=20, t=50, b=40),
        height=380,
    )
    fig.update_yaxes(title_text="Subscription Rate (%)", secondary_y=False)
    fig.update_yaxes(title_text="Customer Count", secondary_y=True)
    return fig


def chart_housing_loan(df: pd.DataFrame) -> go.Figure:
    """Side-by-side: housing loan impact on subscription rate."""
    hl = (
        df.groupby("housing")["subscribed"]
        .agg(["mean", "count"])
        .reset_index()
    )
    hl["sub_rate_pct"] = (hl["mean"] * 100).round(1)
    hl["label"] = hl["housing"].map({"yes": "Has Housing Loan", "no": "No Housing Loan"})

    fig = go.Figure(
        go.Bar(
            x=hl["label"],
            y=hl["sub_rate_pct"],
            marker_color=[COLORS["danger"], COLORS["success"]],
            text=[f"{v}%" for v in hl["sub_rate_pct"]],
            textposition="outside",
            width=0.4,
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text="Housing Loan Impact on Subscription Rate", font=dict(size=16)),
        yaxis_title="Subscription Rate (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=30),
        height=360,
        showlegend=False,
    )
    return fig


def chart_opportunity_leaderboard(df: pd.DataFrame) -> go.Figure:
    """Treemap of segments by average opportunity score."""
    seg = (
        df.groupby(["job", "age_group"], observed=True)["opp_score"]
        .mean()
        .reset_index()
        .rename(columns={"opp_score": "avg_score"})
    )
    seg["avg_score"] = seg["avg_score"].round(1)
    seg["age_group"] = seg["age_group"].astype(str)

    fig = px.treemap(
        seg,
        path=["age_group", "job"],
        values="avg_score",
        color="avg_score",
        color_continuous_scale=["#1E3A5F", "#2E86AB", "#F6AE2D"],
        title="Opportunity Score Heatmap — Segment × Age Group",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig


# ─────────────────────────────────────────────
# AUTO INSIGHTS
# ─────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[dict]:
    """Return list of data-driven insight dicts with icon, title, body."""
    insights = []

    # 1. Best job
    job_rates = df.groupby("job")["subscribed"].mean()
    best_job = job_rates.idxmax()
    best_job_rate = job_rates.max() * 100
    insights.append({
        "icon": "💼",
        "title": f"Top Job: {best_job.title()}",
        "body": (
            f"{best_job.title()} customers show a {best_job_rate:.1f}% subscription rate "
            f"— the highest of all job categories. Relationship managers should prioritise "
            f"outreach to this segment in upcoming campaigns."
        ),
        "level": "success",
    })

    # 2. Age group winner
    ag_rates = df.groupby("age_group", observed=True)["subscribed"].mean()
    best_ag = ag_rates.idxmax()
    best_ag_rate = ag_rates.max() * 100
    insights.append({
        "icon": "👤",
        "title": f"Strongest Age Segment: {best_ag}",
        "body": (
            f"The {best_ag} age group converts at {best_ag_rate:.1f}%, the highest of all cohorts. "
            f"This aligns with typical wealth-accumulation and retirement planning cycles — "
            f"products should be framed around financial security and yield."
        ),
        "level": "info",
    })

    # 3. Housing loan impact
    hl_rates = df.groupby("housing")["subscribed"].mean() * 100
    delta = hl_rates.get("no", 0) - hl_rates.get("yes", 0)
    insights.append({
        "icon": "🏠",
        "title": "Housing Loan Holders Convert Less",
        "body": (
            f"Customers without a housing loan subscribe {delta:.1f} percentage points more often. "
            f"This suggests existing debt obligations reduce appetite for additional financial products — "
            f"a clear segmentation signal for campaign targeting."
        ),
        "level": "warning",
    })

    # 4. Balance correlation
    high_bal = df[df["balance"] > df["balance"].median()]["subscribed"].mean() * 100
    low_bal  = df[df["balance"] <= df["balance"].median()]["subscribed"].mean() * 100
    insights.append({
        "icon": "💰",
        "title": "Higher Balances → Higher Conversion",
        "body": (
            f"Customers above the median balance ({df['balance'].median():,.0f}€) convert at "
            f"{high_bal:.1f}% vs {low_bal:.1f}% for those below. Wealthier customers are more "
            f"receptive to term deposit products — balance should be a top filter in CRM segmentation."
        ),
        "level": "success",
    })

    # 5. Education premium
    edu_rates = df.groupby("education")["subscribed"].mean() * 100
    best_edu = edu_rates.idxmax()
    insights.append({
        "icon": "🎓",
        "title": f"Education Edge: {best_edu.title()} Level Leads",
        "body": (
            f"{best_edu.title()}-educated customers show the highest subscription rate at "
            f"{edu_rates.max():.1f}%. Higher financial literacy likely correlates with "
            f"greater openness to structured savings products."
        ),
        "level": "info",
    })

    # 6. Personal loan
    pl_rates = df.groupby("loan")["subscribed"].mean() * 100
    delta_loan = pl_rates.get("no", 0) - pl_rates.get("yes", 0)
    insights.append({
        "icon": "📋",
        "title": "Personal Loan Holders Are Harder to Convert",
        "body": (
            f"Customers with an active personal loan are {delta_loan:.1f}pp less likely to subscribe. "
            f"Combined with housing loan status, dual-debt customers represent the lowest-opportunity "
            f"segment — campaigns should de-prioritise this cohort."
        ),
        "level": "warning",
    })

    # 7. Overall class imbalance note
    pos_rate = df["subscribed"].mean() * 100
    insights.append({
        "icon": "📊",
        "title": f"Dataset: {pos_rate:.1f}% Subscription Rate",
        "body": (
            f"Only {pos_rate:.1f}% of outreach contacts resulted in a subscription — a significant "
            f"class imbalance. This means precision targeting matters enormously; broad campaigns "
            f"waste RM bandwidth on 9-in-10 customers who won't convert."
        ),
        "level": "error",
    })

    return insights


def high_opportunity_segments(df: pd.DataFrame) -> dict:
    """Return the top segments for each dimension."""
    return {
        "top_job": df.groupby("job")["subscribed"].mean().idxmax(),
        "top_job_rate": df.groupby("job")["subscribed"].mean().max() * 100,
        "top_age": str(df.groupby("age_group", observed=True)["subscribed"].mean().idxmax()),
        "top_age_rate": df.groupby("age_group", observed=True)["subscribed"].mean().max() * 100,
        "top_edu": df.groupby("education")["subscribed"].mean().idxmax(),
        "top_edu_rate": df.groupby("education")["subscribed"].mean().max() * 100,
        "high_bal_rate": df[df["balance"] > df["balance"].median()]["subscribed"].mean() * 100,
        "median_bal": df["balance"].median(),
        "avg_opp_score": df["opp_score"].mean(),
    }

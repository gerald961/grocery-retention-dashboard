import streamlit as st
import pandas as pd

st.set_page_config(page_title="Retention Driver Finder", layout="wide")

st.title("🧠 Retention Driver Finder")
st.caption("Stakeholder-ready insight from reorder behavior by aisle.")

# ---- Load data ----
@st.cache_data
def load_data():
    return pd.read_csv("aisle_reorder_metrics.csv")

df = load_data()

# Ensure types
df["reorder_probability"] = pd.to_numeric(df["reorder_probability"], errors="coerce")
df["total_purchases"] = pd.to_numeric(df["total_purchases"], errors="coerce")
df["total_reorders"] = pd.to_numeric(df["total_reorders"], errors="coerce")
df = df.dropna(subset=["reorder_probability", "total_purchases"]).copy()

# ---- Controls ----
st.sidebar.header("Controls")
min_purchases = st.sidebar.slider(
    "Minimum purchases (reduce noise)",
    0,
    int(df["total_purchases"].max()),
    100000,
    step=50000
)

df = df[df["total_purchases"] >= min_purchases].copy()
df = df.sort_values("reorder_probability", ascending=False)

baseline = st.sidebar.selectbox(
    "Baseline aisle (for X× comparison)",
    df["aisle"].tolist(),
    index=min(9, len(df)-1)
)

baseline_rp = float(df.loc[df["aisle"] == baseline, "reorder_probability"].iloc[0])
top = df.iloc[0]
multiple = (float(top["reorder_probability"]) / baseline_rp) if baseline_rp else None

# ---- Hero Insight ----
st.subheader("🔥 Executive Insight")
st.write(
    f"**Top retention aisle:** **{top['aisle']}**  |  "
    f"Reorder probability: **{top['reorder_probability']:.2f}**  |  "
    f"Purchases: **{int(top['total_purchases']):,}**"
)

if multiple:
    st.success(
        f"Compared to **{baseline}** (rp={baseline_rp:.2f}), "
        f"**{top['aisle']}** is about **{multiple:.1f}×** higher — a strong retention driver."
    )

st.markdown(
    """
**What this means (plain English):**
- High-retention aisles are **replenishment categories** (customers come back for them).
- These aisles drive **repeat shopping behavior** and should be protected from stockouts.
"""
)

# ---- Simple recommendations ----
st.subheader("✅ Suggested actions")
st.markdown(
    """
- **Protect inventory** in top retention aisles (avoid stockouts).
- **Bundle** low-retention items with high-retention staples.
- **Use promos** on mid-retention aisles to lift repeat buying.
"""
)

# ---- Stakeholder table ----
st.subheader("📊 Aisle performance table")
show_cols = ["aisle", "reorder_probability", "total_purchases", "total_reorders"]
st.dataframe(df[show_cols], use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Top 10 aisles")
    st.dataframe(df.head(10)[show_cols], use_container_width=True)
with c2:
    st.subheader("Bottom 10 aisles")
    st.dataframe(df.tail(10)[show_cols], use_container_width=True)
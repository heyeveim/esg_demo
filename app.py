import streamlit as st
import pandas as pd

st.set_page_config(page_title="ESG Event Study Demo", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("final_robustness_table_scored.csv")
    df["Event_Date"] = df["Event_Date"].astype(str)
    return df

df = load_data()

# ---------- Title / Intro ----------
st.title("ESG Disclosure Event Study Demo")

st.markdown("""
### What this demo shows
This app presents the output of an ESG disclosure event study that evaluates how each disclosure event behaves in the market.

For each event, the framework combines **price reaction**, **volume behavior**, and an **interpretation layer** into a single **Signal Score**.  
That score is then translated into communication-oriented labels such as:

- **Confirmatory**
- **Mixed / Ambiguous**
- **Weak stabilizing**
- **Near neutral**
- **Uncertainty leaning**

This demo is designed to make the event-level output easier to review interactively by **firm** and **event date**.
""")

with st.expander("How to read this app"):
    st.markdown("""
**Suggested reading flow**
1. Use the sidebar to choose a **firm** and **event date**
2. Review the **Selected Event Summary**
3. Check the **Plain-English Interpretation**
4. Review the **Key Supporting Metrics**
5. Compare the selected event against the firm's **full event history**
6. Use the **trend chart** to see how the firm's signal changes across events

**How to interpret Signal Score**
- Higher values generally indicate more **stabilizing / confirmatory** behavior
- Lower values indicate more **uncertainty-leaning / mixed** behavior
- The bins are intended as a **communication layer** rather than a hard trading signal

**Class vs. Signal Bin**
- **Class** is the higher-level event interpretation label
- **Signal_Bin** is a communication-oriented bucket derived from the continuous **Signal Score**
- They are related, but they do not have to match one-for-one
""")

# ---------- Sidebar ----------
st.sidebar.header("Filters")

firm_list = sorted(df["Firm"].dropna().unique().tolist())
selected_firm = st.sidebar.selectbox("Select firm", firm_list)

firm_df = df[df["Firm"] == selected_firm].copy()
event_list = firm_df["Event_Date"].tolist()
selected_event = st.sidebar.selectbox("Select event date", event_list)

selected_row = firm_df[firm_df["Event_Date"] == selected_event].iloc[0]

# ---------- Top Summary ----------
st.markdown("---")
st.subheader("Project Snapshot")

total_events = len(df)
total_firms = df["Firm"].nunique()
avg_signal = df["Signal_Score"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Total Events", total_events)
c2.metric("Firms Covered", total_firms)
c3.metric("Sample Mean Signal Score", f"{avg_signal:.4f}")
st.caption("In this small demo dataset, positive and negative event scores roughly offset each other, so the sample mean is near zero.")

# ---------- Selected Event Summary ----------
st.markdown("---")
st.subheader("Selected Event Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Firm", str(selected_row["Firm"]))
col2.metric("Event Date", str(selected_row["Event_Date"]))
col3.metric("Class", str(selected_row["Class"]))
col4.metric("Signal Score", f"{float(selected_row['Signal_Score']):.4f}")

bin_value = selected_row["Signal_Bin"] if "Signal_Bin" in selected_row.index else "N/A"
st.info(f"**Interpretation Bin:** {bin_value}")

# ---------- Plain-English Interpretation ----------
st.subheader("Plain-English Interpretation")

signal_score = float(selected_row["Signal_Score"])
event_class = str(selected_row["Class"])
signal_bin = str(selected_row["Signal_Bin"]) if "Signal_Bin" in selected_row.index else "N/A"

explanation = f"""
For **{selected_firm}** on **{selected_event}**, the event is labeled **{event_class}** and receives a **Signal Score of {signal_score:.4f}**.

In this framework, that score falls into the **{signal_bin}** interpretation bucket.  
The class and the bin are related but serve slightly different purposes: the class summarizes the event type, while the bin translates the score into a more communication-friendly interpretation.
"""
st.write(explanation)

# ---------- Key Supporting Metrics ----------
st.subheader("Key Supporting Metrics")

preferred_metrics = [
    "Delta_Avg_AR",
    "Vol_Ratio_Post_Pre",
    "Vol_Signal",
    "Price_Signal",
    "Volume_Signal",
    "Vol_Signal_z",
    "Price_Signal_z",
    "Volume_Signal_z",
    "End_CAR_tmax",
    "Signal_Score",
    "Signal_Bin"
]

available_metrics = [c for c in preferred_metrics if c in firm_df.columns]

if available_metrics:
    metric_display = pd.DataFrame({
        "Metric": available_metrics,
        "Value": [selected_row[m] for m in available_metrics]
    })
    st.dataframe(metric_display, use_container_width=True)
else:
    st.write("No preferred metrics were found in the uploaded result table.")

# ---------- Selected Event Details ----------
st.subheader("Selected Event Details")
st.caption("Full event-level record for the selected event.")
st.dataframe(pd.DataFrame([selected_row]), use_container_width=True)

# ---------- Firm-Level History ----------
st.markdown("---")
st.subheader(f"All Events for {selected_firm}")
st.caption("Compare the selected event against the firm's other disclosure events.")
st.dataframe(firm_df, use_container_width=True)

# ---------- Trend Chart ----------
st.subheader("Signal Score Trend")
chart_df = firm_df[["Event_Date", "Signal_Score"]].copy()
chart_df["sort_date"] = pd.to_datetime(chart_df["Event_Date"], errors="coerce")
chart_df = chart_df.sort_values(["sort_date", "Event_Date"])
chart_df = chart_df.set_index("Event_Date")

st.line_chart(chart_df["Signal_Score"])

# ---------- Distribution / Comparison ----------
st.subheader("Firm Event Distribution")

if "Signal_Bin" in firm_df.columns:
    bin_counts = firm_df["Signal_Bin"].value_counts().reset_index()
    bin_counts.columns = ["Signal_Bin", "Count"]
    st.dataframe(bin_counts, use_container_width=True)
else:
    st.write("Signal_Bin column not available for distribution summary.")

# ---------- Method Notes ----------
st.markdown("---")
st.subheader("Method Notes")

st.markdown("""
This app is a lightweight review layer built on top of the project's event-level output table.

**Underlying idea**
- Each disclosure event is evaluated using market response features
- The framework combines these inputs into a continuous **Signal Score**
- The score is translated into communication-friendly categories for easier interpretation

**Class vs. Signal Bin**
- **Class** is the higher-level event interpretation label
- **Signal_Bin** is a communication-oriented bucket derived from the continuous **Signal Score**
- They are related, but they do not have to match exactly one-for-one

**What this app is for**
- Reviewing event-level outputs interactively
- Comparing events within a firm
- Communicating results in a way that is easier for non-technical stakeholders to read

**What this app is not**
- It is not a full production system
- It is not a live market feed
- It is not meant to be interpreted as direct investment advice
""")

# ---------- Data Dictionary ----------
st.subheader("Quick Data Dictionary")

dictionary_rows = [
    ["Firm", "Issuer / company name"],
    ["Event_Date", "Disclosure event date"],
    ["Class", "High-level event interpretation label"],
    ["Signal_Score", "Combined continuous score from the interpretation framework"],
    ["Signal_Bin", "Communication-oriented bucket derived from the score"],
    ["Delta_Avg_AR", "Average abnormal return-related signal input"],
    ["Vol_Ratio_Post_Pre", "Post-event vs. pre-event volume ratio"],
    ["End_CAR_tmax", "Cumulative abnormal return endpoint metric, if available"],
]

dictionary_df = pd.DataFrame(dictionary_rows, columns=["Field", "Meaning"])
st.dataframe(dictionary_df, use_container_width=True)

# ---------- Download ----------
st.markdown("---")
st.subheader("Download Current Firm Slice")

csv_bytes = firm_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"Download {selected_firm} event table as CSV",
    data=csv_bytes,
    file_name=f"{selected_firm.lower()}_event_history.csv",
    mime="text/csv"
)

st.caption("Demo built from the event-level scored output table.")

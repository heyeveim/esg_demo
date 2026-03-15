import streamlit as st
import pandas as pd

st.set_page_config(page_title="ESG Event Study Demo", layout="wide")

st.title("ESG Disclosure Event Study Demo")
st.write("Interactive demo of event-level scoring outputs.")

df = pd.read_csv("final_robustness_table_scored.csv")

df["Event_Date"] = df["Event_Date"].astype(str)

st.sidebar.header("Filters")

firm_list = sorted(df["Firm"].dropna().unique())
selected_firm = st.sidebar.selectbox("Select firm", firm_list)

filtered = df[df["Firm"] == selected_firm].copy()

event_list = filtered["Event_Date"].tolist()
selected_event = st.sidebar.selectbox("Select event date", event_list)

selected_row = filtered[filtered["Event_Date"] == selected_event].iloc[0]

st.subheader("Selected Event Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Firm", selected_row["Firm"])
col2.metric("Class", selected_row["Class"])
col3.metric("Signal Score", round(float(selected_row["Signal_Score"]), 4))

st.subheader("Selected Event Details")
st.dataframe(pd.DataFrame([selected_row]))

st.subheader(f"All Events for {selected_firm}")
st.dataframe(filtered)

st.subheader("Signal Score Trend")
chart_df = filtered[["Event_Date", "Signal_Score"]].copy()
chart_df = chart_df.sort_values("Event_Date")
chart_df = chart_df.set_index("Event_Date")
st.line_chart(chart_df)


import streamlit as st
import pandas as pd

st.set_page_config(page_title="ESG Event Study Demo", layout="wide")

st.title("ESG Disclosure Event Study Demo")
st.write("Interactive demo of event-level scoring outputs.")

df = pd.read_csv("final_robustness_table_scored.csv")

st.subheader("Raw Data Preview")
st.dataframe(df)

st.subheader("Column Names")
st.write(df.columns.tolist())

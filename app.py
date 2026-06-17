from __future__ import annotations

import json

import streamlit as st

from ai_support_tam.tam_brief import build_account_brief
from ai_support_tam.triage import triage_ticket


st.set_page_config(page_title="Support + TAM AI", layout="wide")
st.title("Support + TAM AI")

tab_triage, tab_tam = st.tabs(["Ticket triage", "Account brief"])

with tab_triage:
    subject = st.text_input("Subject", "SSO login loop after SAML rotation")
    body = st.text_area("Body", "All users cannot access the app after SAML metadata rotation. Leadership needs an ETA.")
    if st.button("Triage ticket", type="primary"):
        result = triage_ticket({"subject": subject, "body": body})
        st.json(result.model_dump())

with tab_tam:
    account_id = st.text_input("Account ID", "ACCT-001")
    if st.button("Generate brief", type="primary"):
        brief = build_account_brief(account_id)
        st.subheader("Executive summary")
        st.write(brief.executive_summary)
        st.subheader("Open risks")
        st.write(brief.open_risks)
        st.subheader("Flagged issues")
        st.code(json.dumps([flag.model_dump() for flag in brief.flagged_issues], indent=2), language="json")
        st.subheader("Talking points")
        st.write(brief.recommended_talking_points)

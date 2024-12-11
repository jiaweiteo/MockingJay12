import streamlit as st

ROLES = [None, "ItemOwner", "Secretariat"]

st.header("Change Role (DEV Only)")
role = st.selectbox("Choose your role", ROLES)
if st.button("Change"):
    st.session_state.role = role
    st.rerun()

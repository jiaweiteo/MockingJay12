import streamlit as st
from utils.constants import Role

ROLES = [
    Role.GENERAL.value,
    Role.PERSONAL_ASSISTANT.value,
    Role.ITEM_OWNER.value,
    Role.SECRETARIAT.value
]

st.header("Change Role (DEV Only)")
role = st.selectbox("Choose your role", ROLES)
if st.button("Change"):
    st.session_state.role = role
    st.rerun()

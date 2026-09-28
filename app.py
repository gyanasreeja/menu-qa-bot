import streamlit as st
from ragchain import ask

st.set_page_config(page_title="Menu Q&A Bot", page_icon="🍽️")
st.title("🍽️ Menu Q&A Bot")
st.caption("Ask anything about our menu: veg options, spice level, prices, allergens.")

# Keep chat history across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if question := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Checking the menu..."):
            answer = ask(question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
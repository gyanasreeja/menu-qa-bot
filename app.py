import streamlit as st

import DB
from ragchain import ask

st.set_page_config(page_title="Menu Q&A Bot", page_icon="🍽️", layout="centered")
DB.init_db()

# ---------- Styling ----------
st.markdown(
    """
<style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 2rem; max-width: 820px;}
    .hero {
        background: linear-gradient(135deg, #ff7a18 0%, #af002d 100%);
        padding: 1.6rem 1.8rem; border-radius: 18px; color: white;
        margin-bottom: 1.4rem; box-shadow: 0 8px 24px rgba(175,0,45,.25);
    }
    .hero h1 {margin: 0; font-size: 2rem; color: white;}
    .hero p {margin: .3rem 0 0; opacity: .92;}
    .stChatMessage {border-radius: 14px; padding: .6rem .8rem;}
    div[data-testid="stSidebar"] .stButton button {
        text-align: left; width: 100%; border-radius: 10px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .qa-card {
        border: 1px solid rgba(128,128,128,.3); border-radius: 14px;
        padding: 1rem 1.2rem; margin-bottom: 1rem;
    }
    .qa-time {font-size: .78rem; opacity: .6;}
</style>
""",
    unsafe_allow_html=True,
)

SUGGESTIONS = [
    "🥦 Vegetarian starters",
    "🌶️ Hot & spicy dishes",
    "💰 Dishes under ₹100",
    "🌾 Gluten-free mains",
    "🥛 Vegan options",
    "🍰 Desserts without nuts",
]

# ---------- Session state ----------
st.session_state.setdefault("user", None)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("viewing", None)   # a saved search being viewed
st.session_state.setdefault("pending", None)   # question from suggestion chip


def hero(subtitle):
    st.markdown(
        f'<div class="hero"><h1>🍽️ Menu Q&A Bot</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


# ---------- Auth screen ----------
def auth_screen():
    hero("Log in to ask about our menu and keep your search history.")
    tab_login, tab_reg = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Log in", use_container_width=True, type="primary"):
                user = DB.authenticate(u, p)
                if user:
                    st.session_state.user = user
                    # Restore this user's previous conversation (oldest -> newest)
                    hist = list(reversed(DB.get_history(user["id"], limit=20)))
                    msgs = []
                    for h in hist:
                        msgs += [
                            {"role": "user", "content": h["question"]},
                            {"role": "assistant", "content": h["answer"]},
                        ]
                    st.session_state.messages = msgs
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_reg:
        with st.form("register_form"):
            u = st.text_input("Choose a username")
            p1 = st.text_input("Password (min 6 characters)", type="password")
            p2 = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create account", use_container_width=True, type="primary"):
                if p1 != p2:
                    st.error("Passwords don't match.")
                else:
                    ok, msg = DB.register_user(u, p1)
                    (st.success if ok else st.error)(msg)


# ---------- Main screen ----------
def sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"### 👤 {user['username']}")
        c1, c2 = st.columns(2)
        if c1.button("➕ New chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.viewing = None
            st.rerun()
        if c2.button("🚪 Logout", use_container_width=True):
            for k in ("user", "messages", "viewing", "pending"):
                st.session_state[k] = None if k in ("user", "viewing", "pending") else []
            st.rerun()

        st.divider()
        st.markdown("#### 🕘 Previous searches")
        history = DB.get_history(user["id"])
        if not history:
            st.caption("No searches yet. Ask something!")
        for h in history:
            col_a, col_b = st.columns([5, 1])
            label = h["question"] if len(h["question"]) <= 32 else h["question"][:30] + "…"
            if col_a.button(label, key=f"h_{h['id']}", help=h["question"]):
                st.session_state.viewing = h
                st.rerun()
            if col_b.button("✕", key=f"d_{h['id']}", help="Delete"):
                DB.delete_search(user["id"], h["id"])
                if st.session_state.viewing and st.session_state.viewing["id"] == h["id"]:
                    st.session_state.viewing = None
                st.rerun()

        if history:
            st.divider()
            if st.button("🗑️ Clear all history", use_container_width=True):
                DB.clear_history(user["id"])
                st.session_state.viewing = None
                st.session_state.messages = []
                st.rerun()


def run_question(question):
    user = st.session_state.user
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Checking the menu..."):
            try:
                answer = ask(question, st.session_state.messages[:-1])
            except Exception as e:
                answer = f"⚠️ Something went wrong ({type(e).__name__}). If you're on Groq's free plan you may have hit the rate limit; please wait a moment and try again."
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    if not answer.startswith("⚠️"):
        DB.save_search(user["id"], question, answer)


def main_screen():
    sidebar()
    hero("Ask anything about our menu: veg options, spice level, prices, allergens.")

    # Viewing a saved search from the sidebar
    v = st.session_state.viewing
    if v:
        st.markdown(
            f'<div class="qa-card"><div class="qa-time">{v["created_at"]} (UTC)</div></div>',
            unsafe_allow_html=True,
        )
        with st.chat_message("user"):
            st.markdown(v["question"])
        with st.chat_message("assistant"):
            st.markdown(v["answer"])
        if st.button("⬅️ Back to chat"):
            st.session_state.viewing = None
            st.rerun()
        return

    # Existing conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Suggestion chips on an empty chat
    if not st.session_state.messages:
        st.markdown("**Try asking:**")
        cols = st.columns(3)
        for i, s in enumerate(SUGGESTIONS):
            if cols[i % 3].button(s, key=f"s_{i}", use_container_width=True):
                st.session_state.pending = s.split(" ", 1)[1]
                st.rerun()

    if st.session_state.pending:
        q, st.session_state.pending = st.session_state.pending, None
        run_question(q)
        st.rerun()

    if question := st.chat_input("What would you like to know?"):
        run_question(question)
        st.rerun()


if st.session_state.user:
    main_screen()
else:
    auth_screen()
import streamlit as st
import hmac
import base64
from openai import OpenAI
from streamlit_option_menu import option_menu


# --- USER AUTHENTICATION ---


def check_password():
    # Returns True if the user had a correct password.

    # HEADER
    st.markdown(
    """
    <h1 style="font-size: 58px; text-align: center; 
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5); 
    background: rgb(0,69,79);
    background: linear-gradient(90deg, rgba(0,69,79,1) 8%, rgba(7,85,101,1) 30%, rgba(5,160,191,1) 48%);
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent;">
    Welcome to Ingenium</h1>
    """,
    unsafe_allow_html=True
    )
    


    # LOGO
    # st.markdown('<style>img {border-radius: 20px}</style>', unsafe_allow_html=True)
    # st.sidebar.image("Ingenium_logo.png")
    
    def login_form():
        # Form with widgets to collect user information
        st.write("")
        st.write("")
        st.write("")
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        # Checks whether a password entered by the user is correct
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


# ---SIDEBAR---
st.markdown('<style>img {border-radius: 20px}</style>', unsafe_allow_html=True)
st.sidebar.image("Ingenium_logo.png")
st.write("")
st.write("")


 # NAVIGATION BAR
with st.sidebar:
    selected = option_menu(
    menu_title="Main Menu",
    options=["Home", "Projects", "Contact"],
    icons=["house", "book", "envelope"],
    menu_icon="cast",
    )

# Initialize session state variables for user profile form
if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "send_button_disabled" not in st.session_state:
    st.session_state.send_button_disabled = False

#  Create a profile
def disable():
    st.session_state.disabled = True

form1 = st.sidebar.form(key="Options")

form1.header("Query Filter")
projects = form1.selectbox("Which project are you working on?", ("Church End", "Balmoral"))
retrieval_mode = form1.selectbox("Mode", ("Conversational Mode", "Source Retrieval Mode",))
document_type = form1.multiselect("Document Type      *Optional", ("Specifications", "Reports", "Schedules", "Product Data Sheets", "Product Installation Guides",))

data = {
    "job_role": projects,
    "experience": retrieval_mode,
    "project_stage": document_type,
}

form1.form_submit_button("Submit")


# BUILDING THE CHATBOT

with st.chat_message (name="assistant"):
    st.write("Welcome to Ingenium - please ask me any construction related queries you have...")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Please enter your questions here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

# Generate assistant response
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
                
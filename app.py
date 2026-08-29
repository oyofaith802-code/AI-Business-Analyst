import streamlit as st
import tempfile
import os
import pandas as pd

from auth import (
    create_users_table,
    register_user,
    login_user
)

from business_analyst import answer_business_question

from document_loader import process_document

from document_memory import (
    create_document_memory_table,
    save_document,
    get_user_documents,
    document_exists,
    delete_document
)

from excel_database import (
    import_excel_workbook,
    register_excel_tables
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CREATE TABLES
# ============================================================

try:
    create_users_table()
except Exception:
    pass

try:
    create_document_memory_table()
except Exception:
    pass


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None


# ============================================================
# LOGIN / SIGNUP
# ============================================================

if not st.session_state.authenticated:

    st.title("📊 AI Business Analyst")

    st.caption(
        "Your intelligent business data and document assistant."
    )

    login_tab, signup_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account"
        ]
    )


    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Login")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            key="login_button",
            width="stretch"
        ):

            email = login_email.strip().lower()

            if not email:

                st.warning(
                    "Please enter your email."
                )

            elif not login_password:

                st.warning(
                    "Please enter your password."
                )

            else:

                try:

                    user = login_user(
                        email,
                        login_password
                    )

                    if user == "NOT_VERIFIED":

                        st.warning(
                            "Please verify your email before logging in."
                        )

                    elif user is None:

                        st.error(
                            "Invalid email or password."
                        )

                    else:

                        st.session_state.authenticated = True

                        st.session_state.user_email = email

                        st.session_state.messages = []

                        st.session_state.selected_document = None

                        st.rerun()

                except Exception as e:

                    st.error(
                        f"Login error: {e}"
                    )


    # ========================================================
    # SIGN UP
    # ========================================================

    with signup_tab:

        st.subheader("Create Account")

        signup_email = st.text_input(
            "Email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        signup_confirm = st.text_input(
            "Confirm password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "Create Account",
            key="signup_button",
            width="stretch"
        ):

            email = signup_email.strip().lower()

            if not email:

                st.warning(
                    "Please enter your email."
                )

            elif not signup_password:

                st.warning(
                    "Please enter a password."
                )

            elif signup_password != signup_confirm:

                st.error(
                    "Passwords do not match."
                )

            elif len(signup_password) < 6:

                st.warning(
                    "Password must be at least 6 characters."
                )

            else:

                try:

                    token = register_user(
                        email,
                        signup_password
                    )

                    if token is None:

                        st.error(
                            "Could not create account. "
                            "The email may already exist."
                        )

                    else:

                        st.success(
                            "Account created successfully."
                        )

                        st.info(
                            "Check your email and verify your "
                            "account before logging in."
                        )

                except Exception as e:

                    st.error(
                        f"Registration error: {e}"
                    )


    st.stop()


# ============================================================
# LOGGED-IN USER
# ============================================================

user_email = st.session_state.user_email


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 AI Business Analyst")

    st.caption(
        user_email
    )


    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "🚪 Logout",
        width="stretch"
    ):

        st.session_state.authenticated = False

        st.session_state.user_email = ""

        st.session_state.messages = []

        st.session_state.selected_document = None

        st.rerun()


    st.divider()


    # ========================================================
    # DOCUMENT MANAGEMENT
    # ========================================================

    st.header("📁 My Documents")


    try:

        documents = get_user_documents(
            user_email
        )

    except Exception as e:

        documents = []

        st.error(
            f"Could not load documents: {e}"
        )


    if not documents:

        st.caption(
            "No documents uploaded yet."
        )


    # ========================================================
    # DOCUMENT LIST
    # ========================================================

    for document in documents:

        filename = document["filename"]

        file_type = document["file_type"]

        chunk_count = document["chunk_count"]

        uploaded_at = document["uploaded_at"]


        with st.container(
            border=True
        ):

            st.write(
                f"📄 **{filename}**"
            )

            st.caption(
                f"Type: {file_type}"
            )

            st.caption(
                f"Chunks: {chunk_count}"
            )

            if uploaded_at:

                st.caption(
                    uploaded_at.strftime(
                        "%d %b %Y, %H:%M"
                    )
                )


            col1, col2 = st.columns(
                2
            )


            with col1:

                if st.button(
                    "View",
                    key=f"view_{filename}",
                    width="stretch"
                ):

                    st.session_state.selected_document = filename

                    st.rerun()


            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_{filename}",
                    width="stretch"
                ):

                    try:

                        deleted = delete_document(
                            user_email,
                            filename
                        )

                        if deleted > 0:

                            if (
                                st.session_state.selected_document
                                == filename
                            ):

                                st.session_state.selected_document = None


                            st.success(
                                f"{filename} deleted."
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "Document was not found."
                            )

                    except Exception as e:

                        st.error(
                            f"Delete failed: {e}"
                        )


    # ========================================================
    # UPLOAD
    # ========================================================

    st.divider()

    st.header("📤 Upload File")


    uploaded_file = st.file_uploader(
        "Choose a file",
        type=[
            "pdf",
            "docx",
            "txt",
            "csv",
            "xlsx",
            "xls"
        ],
        key="document_uploader"
    )


    if uploaded_file is not None:

        filename = uploaded_file.name

        st.caption(
            f"Selected: {filename}"
        )


        if st.button(
            "Upload",
            width="stretch"
        ):

            temp_path = None

            try:

                suffix = os.path.splitext(
                    filename
                )[1].lower()


                # =================================================
                # EXCEL FILES
                # =================================================

                if suffix in [
                    ".xlsx",
                    ".xls"
                ]:

                    st.info(
                        "📊 Importing Excel workbook..."
                    )


                    # ---------------------------------------------
                    # IMPORT EXCEL INTO POSTGRESQL
                    # ---------------------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    ) as tmp:

                        tmp.write(
                            uploaded_file.getbuffer()
                        )

                        temp_path = tmp.name


                    import_results = import_excel_workbook(
                        temp_path,
                        filename,
                        user_email
                    )


                    if not import_results:

                        raise ValueError(
                            "No usable sheets were found "
                            "in the Excel workbook."
                        )


                    successful_tables = []


                    for result in import_results:

                        if result.get("error"):

                            st.warning(
                                f"Sheet "
                                f"{result.get('sheet_name', 'Unknown')} "
                                f"could not be imported: "
                                f"{result.get('error')}"
                            )

                            continue


                        table_name = result.get(
                            "table_name"
                        )


                        if table_name:

                            successful_tables.append(
                                table_name
                            )


                    if not successful_tables:

                        raise ValueError(
                            "The Excel workbook could not be imported."
                        )


                    # ---------------------------------------------
                    # REGISTER EXCEL WORKBOOK
                    # ---------------------------------------------

                    register_excel_tables(
                        user_email,
                        filename,
                        import_results
                    )


                    # ---------------------------------------------
                    # SUCCESS
                    # ---------------------------------------------

                    st.success(
                        f"✅ {filename} imported successfully."
                    )


                    st.write(
                        f"**Sheets imported:** "
                        f"{len(successful_tables)}"
                    )


                    for table_name in successful_tables:

                        st.caption(
                            f"🗄️ {table_name}"
                        )


                    st.session_state.selected_document = (
                        filename
                    )


                    st.rerun()


                # =================================================
                # OTHER FILES
                # =================================================

                else:

                    # ---------------------------------------------
                    # CHECK DUPLICATE DOCUMENT
                    # ---------------------------------------------

                    exists = document_exists(
                        user_email,
                        filename
                    )


                    if exists:

                        st.warning(
                            f"**{filename}** has already been uploaded."
                        )

                        st.stop()


                    # ---------------------------------------------
                    # SAVE TEMP FILE
                    # ---------------------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    ) as tmp:

                        tmp.write(
                            uploaded_file.getbuffer()
                        )

                        temp_path = tmp.name


                    # ---------------------------------------------
                    # PROCESS DOCUMENT
                    # ---------------------------------------------

                    document = process_document(
                        temp_path
                    )


                    if not document:

                        raise ValueError(
                            "The document could not be processed."
                        )


                    document_chunks = document.get(
                        "chunks",
                        []
                    )


                    if not document_chunks:

                        raise ValueError(
                            "No readable content was found "
                            "in the file."
                        )


                    save_document(
                        user_email,
                        filename,
                        document.get(
                            "file_type",
                            "document"
                        ),
                        document_chunks
                    )


                    st.success(
                        f"✅ {filename} uploaded successfully."
                    )


                    st.session_state.selected_document = (
                        filename
                    )


                    st.rerun()


            except Exception as e:

                st.error(
                    f"❌ Upload failed: {e}"
                )


            finally:

                if temp_path:

                    try:

                        if os.path.exists(
                            temp_path
                        ):

                            os.remove(
                                temp_path
                            )

                    except Exception:

                        pass
                    # ============================================================
# SELECTED DOCUMENT
# ============================================================

if st.session_state.selected_document:

    selected = (
        st.session_state.selected_document
    )

    st.info(
        f"📄 Selected file: **{selected}**"
    )


# ============================================================
# MAIN PAGE
# ============================================================

st.title(
    "📊 AI Business Analyst"
)

st.caption(
    f"Welcome back, {user_email}"
)


# ============================================================
# QUESTION AREA
# ============================================================

st.subheader(
    "Ask your business question"
)


question = st.text_input(
    "Question",
    placeholder=(
        "Example: Which product generated the most sales?"
    ),
    key="question_input"
)


ask = st.button(
    "🔎 Analyze",
    width="stretch"
)


# ============================================================
# ANALYZE QUESTION
# ============================================================

if ask:

    if not question.strip():

        st.warning(
            "Please enter a business question."
        )

    else:

        with st.spinner(
            "Analyzing your business..."
        ):

            try:

                response = answer_business_question(
                    user_email,
                    question.strip()
                )

            except Exception as e:

                response = {
                    "route": "ERROR",
                    "answer": (
                        f"An error occurred: {e}"
                    )
                }


        # ====================================================
        # SAVE MESSAGE
        # ====================================================

        st.session_state.messages.append(
            {
                "question": question.strip(),

                "route": response.get(
                    "route",
                    "UNKNOWN"
                ),

                "answer": response.get(
                    "answer",
                    ""
                )
            }
        )


# ============================================================
# DISPLAY LATEST ANSWER
# ============================================================

if st.session_state.messages:

    st.divider()

    st.subheader(
        "📈 Analysis"
    )


    latest = (
        st.session_state.messages[-1]
    )


    route = latest["route"]


    # ========================================================
    # ROUTE INDICATOR
    # ========================================================

    if route == "DATABASE":

        st.info(
            "🗄️ Database Analysis"
        )

    elif route == "DOCUMENT":

        st.info(
            "📄 Document Analysis"
        )

    elif route == "BOTH":

        st.info(
            "📊 Database + 📄 Document Analysis"
        )

    else:

        st.warning(
            f"Route: {route}"
        )


    # ========================================================
    # ANSWER
    # ========================================================

    st.markdown(
        latest["answer"]
    )


# ============================================================
# CONVERSATION HISTORY
# ============================================================

if len(
    st.session_state.messages
) > 1:

    st.divider()

    st.subheader(
        "💬 Previous Questions"
    )


    for message in reversed(
        st.session_state.messages[:-1]
    ):

        with st.expander(
            message["question"]
        ):

            st.caption(
                f"Route: {message['route']}"
            )

            st.markdown(
                message["answer"]
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Business Analyst • PostgreSQL • Ollama • "
    "Document Intelligence • Excel Intelligence"
)
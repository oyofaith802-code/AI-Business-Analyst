# ============================================================
# AI BUSINESS ANALYST
# MAIN DASHBOARD
#
# Features:
# - Authentication
# - Email verification
# - Subscription / plan limits
# - Automatic plan recommendation
# - Paystack checkout
# - Payment verification
# - Dataset uploads
# - Dataset preview
# - Chat memory
# - Follow-up questions
# - Dataset reasoning
# - SQL generation
# - SQL validation
# - SQL execution
# - Automatic SQL repair
# - Business insights
# - Conversation saving
# - Usage tracking
# ============================================================

import streamlit as st
import pandas as pd

from sqlalchemy import text

from database import engine


# ============================================================
# AUTHENTICATION
# ============================================================

from auth import (
    create_users_table,
    register_user,
    login_user,
)


# ============================================================
# SUBSCRIPTION
# ============================================================

from subscription import (
    create_free_subscription,
)


# ============================================================
# DATASET UPLOAD
# ============================================================

from dataset_upload import (
    process_upload,
)


# ============================================================
# DATASET PROFILE
# ============================================================

from dataset_profile_storage import (
    get_user_dataset_profiles,
)


# ============================================================
# TABLE SELECTION
# ============================================================

from table_selector import (
    select_relevant_tables,
)


# ============================================================
# DATASET REASONING
# ============================================================

from dataset_reasoning import (
    analyze_question,
)


# ============================================================
# SQL AGENT
# ============================================================

from sql_agent import (
    generate_sql,
)


# ============================================================
# SQL VALIDATOR
# ============================================================

from sql_validator import (
    validate_sql,
)


# ============================================================
# SQL AUTO REPAIR
# ============================================================

from sql_error_agent import (
    fix_sql_error,
)


# ============================================================
# CHART GENERATOR
# ============================================================

from chart_generator import (
    create_chart,
)


# ============================================================
# PLAN MANAGER
# ============================================================

from plan_manager import (
    question_allowed,
    record_question,
    upload_allowed,
    record_upload,
)


# ============================================================
# USAGE UI
# ============================================================

from usage_ui import (
    show_account_dashboard,
)


# ============================================================
# CHAT MEMORY
# ============================================================

from chat_memory import (
    create_chat_memory_table,
    save_chat,
    get_chat_history,
    build_memory_context,
)


# ============================================================
# PAYMENT / UPGRADE
# ============================================================

from upgrade_ui import (
    show_upgrade_ui,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

try:

    create_users_table()

except Exception:

    pass


try:

    create_chat_memory_table()

except Exception:

    pass


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {

    "authenticated":
        False,

    "user_email":
        "",

    "selected_dataset":
        None,

    "result":
        None,

    "last_sql":
        "",

    "last_answer":
        "",

    "last_question":
        "",

    "show_upgrade":
        False,

    "payment_reference":
        None,

    "payment_plan":
        None,

    "payment_checkout_url":
        None,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #777;
        font-size: 17px;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GET USER DATASETS
# ============================================================

def get_user_datasets(user_email):

    try:

        profiles = get_user_dataset_profiles(
            user_email
        )

        return [
            item["dataset_name"]
            for item in profiles
        ]

    except Exception as e:

        st.warning(
            f"Could not load datasets: {e}"
        )

        return []


# ============================================================
# LOAD DATASET PREVIEW
# ============================================================

def load_dataset_preview(
    dataset_name
):

    try:

        query = text(
            f"""
            SELECT *
            FROM "{dataset_name}"
            LIMIT 100
            """
        )

        with engine.connect() as conn:

            result = conn.execute(
                query
            )

            rows = result.fetchall()

            columns = result.keys()

        return pd.DataFrame(
            rows,
            columns=columns
        )

    except Exception as e:

        st.error(
            f"Could not load dataset: {e}"
        )

        return None


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text(sql)
            )

            rows = result.fetchall()

            columns = result.keys()

        return pd.DataFrame(
            rows,
            columns=columns
        )

    except Exception as e:

        return {
            "success":
                False,

            "error":
                str(e),
        }


# ============================================================
# FOLLOW-UP DETECTION
# ============================================================

def is_follow_up_question(
    question
):

    normalized = (
        question
        .strip()
        .lower()
    )

    follow_up_phrases = [

        "why",
        "why?",

        "which one",
        "which one?",

        "what about",

        "what about the other one",

        "the other one",

        "that category",

        "that one",

        "this category",

        "this one",

        "compare them",

        "compare those",

        "show me more",

        "tell me more",

        "why is it higher",

        "why is it lower",

        "what happened",

        "and why",

        "how so",
    ]

    for phrase in follow_up_phrases:

        if normalized == phrase:

            return True

        if normalized.startswith(
            phrase + " "
        ):

            return True

    return False


# ============================================================
# BUILD CONTEXTUAL QUESTION
# ============================================================

def build_contextual_question(
    user_email,
    dataset_name,
    question,
):

    try:

        history = get_chat_history(
            user_email,
            dataset_name,
            limit=5,
        )

    except Exception:

        history = []

    if not history:

        return question

    if not is_follow_up_question(
        question
    ):

        return question

    context_parts = []

    for item in reversed(history):

        previous_question = item.get(
            "question",
            "",
        )

        previous_answer = item.get(
            "answer",
            "",
        )

        if previous_question:

            context_parts.append(
                f"""
Previous question:
{previous_question}

Previous answer:
{previous_answer}
"""
            )

    history_text = "\n".join(
        context_parts
    )

    return f"""
The user is continuing a previous conversation.

Previous conversation:

{history_text}

Current follow-up question:

{question}

Interpret the current question using the
previous conversation and the current dataset.

Answer the user's current question while
preserving the meaning of the previous context.

Do not invent information.
"""


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def authentication_page():

    st.markdown(
        '<div class="main-title">'
        '📊 AI Business Analyst'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-powered business intelligence for your business data.'
        '</div>',
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account",
        ]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.markdown(
            "## Welcome Back"
        )

        email = st.text_input(
            "Email",
            key="login_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button(
            "🔐 Login",
            type="primary",
            use_container_width=True,
        ):

            if not email or not password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                result = login_user(
                    email,
                    password,
                )

                if not result.get(
                    "success",
                    False,
                ):

                    error = result.get(
                        "error",
                        "Login failed.",
                    )

                    if error == "NOT_VERIFIED":

                        st.warning(
                            "Please verify your email before logging in."
                        )

                    else:

                        st.error(
                            error
                        )

                else:

                    st.session_state.authenticated = True

                    st.session_state.user_email = (
                        result["email"]
                    )

                    create_free_subscription(
                        result["email"]
                    )

                    st.success(
                        "Login successful."
                    )

                    st.rerun()

    # ========================================================
    # REGISTER
    # ========================================================

    with register_tab:

        st.markdown(
            "## Create Your Account"
        )

        register_email = st.text_input(
            "Email",
            key="register_email",
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password",
        )

        if st.button(
            "📝 Create Account",
            type="primary",
            use_container_width=True,
        ):

            if not register_email:

                st.warning(
                    "Email is required."
                )

            elif not register_password:

                st.warning(
                    "Password is required."
                )

            elif register_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                result = register_user(
                    register_email,
                    register_password,
                )

                if result.get(
                    "success",
                    False,
                ):

                    create_free_subscription(
                        register_email
                    )

                    st.success(
                        result.get(
                            "message",
                            "Account created successfully.",
                        )
                    )

                    if result.get(
                        "verification_sent",
                        False,
                    ):

                        st.info(
                            "Check your email and verify your account before logging in."
                        )

                else:

                    st.error(
                        result.get(
                            "error",
                            "Registration failed.",
                        )
                    )


# ============================================================
# SHOW LOGIN PAGE
# ============================================================

if not st.session_state.authenticated:

    authentication_page()

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

user_email = st.session_state.user_email


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 📊 AI Business Analyst"
    )

    st.divider()

    st.write(
        "👤 **Account**"
    )

    st.caption(
        user_email
    )

    st.divider()

    # ========================================================
    # ACCOUNT DASHBOARD
    # ========================================================

    try:

        show_account_dashboard(
            user_email
        )

    except Exception as e:

        st.warning(
            f"Could not load account dashboard: {e}"
        )

    st.divider()

    # ========================================================
    # UPGRADE
    # ========================================================

    if st.button(
        "🚀 Upgrade Plan",
        use_container_width=True,
    ):

        st.session_state.show_upgrade = True

        st.rerun()

    st.divider()

    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        st.session_state.authenticated = False

        st.session_state.user_email = ""

        st.session_state.selected_dataset = None

        st.session_state.result = None

        st.session_state.last_sql = ""

        st.session_state.last_answer = ""

        st.session_state.last_question = ""

        st.session_state.show_upgrade = False

        st.session_state.payment_reference = None

        st.session_state.payment_plan = None

        st.session_state.payment_checkout_url = None

        st.rerun()


# ============================================================
# UPGRADE PAGE
# ============================================================

if st.session_state.show_upgrade:

    st.markdown(
        '<div class="main-title">'
        '🚀 Upgrade Your Plan'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'Choose the plan that fits your business analysis needs.'
        '</div>',
        unsafe_allow_html=True,
    )

    try:

        show_upgrade_ui(
            user_email
        )

    except Exception as e:

        st.error(
            f"Could not load upgrade system: {e}"
        )

    st.divider()

    if st.button(
        "← Back to Dashboard",
        use_container_width=True,
    ):

        st.session_state.show_upgrade = False

        st.rerun()

    st.stop()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '📊 AI Business Analyst'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Upload your business data and ask questions in natural language.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    "## 📤 Upload Business Data"
)

st.write(
    "Upload CSV, Excel, JSON, Parquet, PDF, or Word files."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=[
        "csv",
        "xlsx",
        "xls",
        "json",
        "parquet",
        "pdf",
        "docx",
    ],
)


if uploaded_file is not None:

    if st.button(
        "📤 Upload Dataset",
        type="primary",
    ):

        try:

            allowed = upload_allowed(
                user_email
            )

        except Exception as e:

            st.error(
                f"Could not check upload limit: {e}"
            )

            allowed = False

        if not allowed:

            st.error(
                "You have reached your upload limit for your current plan."
            )

            st.info(
                "Upgrade your plan to upload more datasets."
            )

        else:

            with st.spinner(
                "Uploading and processing your dataset..."
            ):

                upload_result = process_upload(
                    uploaded_file,
                    user_email,
                )

            if upload_result.get(
                "success",
                False,
            ):

                try:

                    record_upload(
                        user_email
                    )

                except Exception as e:

                    st.warning(
                        f"Upload saved, but usage could not be recorded: {e}"
                    )

                st.success(
                    "✅ Dataset uploaded successfully."
                )

                st.write(
                    f"**Dataset:** "
                    f"{upload_result.get('table_name')}"
                )

                st.write(
                    f"**Rows:** "
                    f"{upload_result.get('rows', 0):,}"
                )

                st.write(
                    f"**Columns:** "
                    f"{upload_result.get('columns', 0):,}"
                )

                st.write(
                    f"**File type:** "
                    f"{upload_result.get('file_type')}"
                )

                st.rerun()

            else:

                st.error(
                    upload_result.get(
                        "error",
                        "Upload failed.",
                    )
                )


# ============================================================
# DATASET SECTION
# ============================================================

st.divider()

st.markdown(
    "## 📁 Your Datasets"
)

datasets = get_user_datasets(
    user_email
)

if not datasets:

    st.info(
        "No datasets uploaded yet. Upload your first business dataset above."
    )

    st.stop()


selected_dataset = st.selectbox(
    "Select a dataset",
    datasets,
)

st.session_state.selected_dataset = (
    selected_dataset
)

st.success(
    f"Using dataset: **{selected_dataset}**"
)


# ============================================================
# DATASET PREVIEW
# ============================================================

with st.expander(
    "👀 Preview Dataset"
):

    preview = load_dataset_preview(
        selected_dataset
    )

    if preview is not None:

        st.dataframe(
            preview,
            use_container_width=True,
        )


# ============================================================
# CHAT HISTORY
# ============================================================

with st.expander(
    "💬 Conversation History"
):

    try:

        history = get_chat_history(
            user_email,
            selected_dataset,
            limit=10,
        )

        if not history:

            st.info(
                "No previous questions for this dataset."
            )

        else:

            for item in history:

                question_text = item.get(
                    "question",
                    "",
                )

                answer_text = item.get(
                    "answer",
                    "",
                )

                created_at = item.get(
                    "created_at",
                    "",
                )

                st.markdown(
                    f"**You:** {question_text}"
                )

                st.markdown(
                    f"**AI:** {answer_text}"
                )

                if created_at:

                    st.caption(
                        str(created_at)
                    )

                st.divider()

    except Exception as e:

        st.warning(
            f"Could not load conversation history: {e}"
        )


# ============================================================
# BUSINESS QUESTION
# ============================================================

st.markdown(
    "## 💬 Ask Your Business Question"
)

question = st.text_area(
    "Business question",
    placeholder=(
        "Examples:\n"
        "• What is our total revenue?\n"
        "• What is our revenue by category?\n"
        "• Which category is performing better?\n"
        "• What are our top 5 products by revenue?\n"
        "• What is our revenue by month?\n"
        "• Why?\n"
        "• What about the other one?"
    ),
    height=160,
)

analyze_button = st.button(
    "🔍 Analyze",
    type="primary",
    use_container_width=True,
)


# ============================================================
# ANALYSIS PIPELINE
# ============================================================

if analyze_button:

    if not question.strip():

        st.warning(
            "Please enter a business question."
        )

        st.stop()

    original_question = (
        question.strip()
    )

    st.session_state.last_question = (
        original_question
    )

    # --------------------------------------------------------
    # QUESTION LIMIT
    # --------------------------------------------------------

    try:

        allowed = question_allowed(
            user_email
        )

    except Exception as e:

        st.error(
            f"Could not check question limit: {e}"
        )

        st.stop()

    if not allowed:

        st.error(
            "You have reached your monthly question limit."
        )

        st.info(
            "Upgrade your plan to continue asking questions."
        )

        st.stop()

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    with st.spinner(
        "💬 Checking conversation context..."
    ):

        try:

            memory_context = build_memory_context(
                user_email,
                selected_dataset,
                original_question,
                limit=5,
            )

        except Exception:

            memory_context = ""

    # --------------------------------------------------------
    # CONTEXTUAL QUESTION
    # --------------------------------------------------------

    contextual_question = (
        build_contextual_question(
            user_email=user_email,
            dataset_name=selected_dataset,
            question=original_question,
        )
    )

    if is_follow_up_question(
        original_question
    ):

        st.info(
            "💬 Using previous conversation to understand this follow-up."
        )

    # --------------------------------------------------------
    # TABLE SELECTION
    # --------------------------------------------------------

    with st.spinner(
        "🔍 Finding relevant data..."
    ):

        try:

            selected_tables = (
                select_relevant_tables(
                    contextual_question,
                    user_email,
                )
            )

        except Exception as e:

            st.error(
                f"Table selection failed: {e}"
            )

            st.stop()

    if not selected_tables:

        selected_tables = [
            selected_dataset
        ]

    # --------------------------------------------------------
    # QUESTION REASONING
    # --------------------------------------------------------

    with st.spinner(
        "🧠 Understanding your question..."
    ):

        try:

            analysis = analyze_question(
                contextual_question,
                selected_tables,
                user_email,
            )

        except Exception as e:

            st.error(
                f"Question analysis failed: {e}"
            )

            st.stop()

    if isinstance(
        analysis,
        dict,
    ):

        answerable = analysis.get(
            "answerable",
            False,
        )

        reason = analysis.get(
            "reason",
            "",
        )

    else:

        answerable = False

        reason = str(
            analysis
        )

    if not answerable:

        st.error(
            "❌ This question cannot be answered."
        )

        st.write(
            reason
        )

        st.stop()

    # --------------------------------------------------------
    # SQL GENERATION
    # --------------------------------------------------------

    with st.spinner(
        "⚙️ Generating analysis..."
    ):

        try:

            sql = generate_sql(
                contextual_question,
                selected_tables,
                user_email,
            )

        except Exception as e:

            st.error(
                f"SQL generation failed: {e}"
            )

            st.stop()

    # --------------------------------------------------------
    # SQL VALIDATION
    # --------------------------------------------------------

    with st.spinner(
        "🔐 Validating analysis..."
    ):

        try:

            validation = validate_sql(
                sql
            )

        except Exception as e:

            st.error(
                f"SQL validation failed: {e}"
            )

            st.stop()

    # --------------------------------------------------------
    # REPAIR VALIDATION ERROR
    # --------------------------------------------------------

    if not validation.get(
        "valid",
        False,
    ):

        st.warning(
            "⚠️ Generated SQL failed validation. Attempting repair..."
        )

        validation_errors = (
            validation.get(
                "errors",
                [],
            )
        )

        error_message = "\n".join(
            str(error)
            for error in validation_errors
        )

        try:

            sql = fix_sql_error(
                sql=sql,
                error_message=error_message,
                tables=selected_tables,
                user_email=user_email,
            )

            repaired_validation = (
                validate_sql(
                    sql
                )
            )

            if not repaired_validation.get(
                "valid",
                False,
            ):

                st.error(
                    "❌ Repaired SQL still failed validation."
                )

                st.stop()

            st.success(
                "✅ SQL was automatically repaired."
            )

        except Exception as e:

            st.error(
                f"SQL repair failed: {e}"
            )

            st.stop()

    # --------------------------------------------------------
    # EXECUTE SQL
    # --------------------------------------------------------

    with st.spinner(
        "🗄️ Analyzing your data..."
    ):

        execution_result = (
            execute_sql(
                sql
            )
        )

    # --------------------------------------------------------
    # EXECUTION ERROR
    # --------------------------------------------------------

    if (
        isinstance(
            execution_result,
            dict,
        )
        and not execution_result.get(
            "success",
            False,
        )
    ):

        sql_error = (
            execution_result.get(
                "error",
                "Unknown SQL error.",
            )
        )

        st.warning(
            "⚠️ SQL execution failed. Attempting automatic repair..."
        )

        try:

            repaired_sql = fix_sql_error(
                sql=sql,
                error_message=sql_error,
                tables=selected_tables,
                user_email=user_email,
            )

            repaired_validation = (
                validate_sql(
                    repaired_sql
                )
            )

            if not repaired_validation.get(
                "valid",
                False,
            ):

                st.error(
                    "❌ Repaired SQL failed validation."
                )

                st.stop()

            st.success(
                "✅ SQL automatically repaired."
            )

            sql = repaired_sql

            execution_result = (
                execute_sql(
                    sql
                )
            )

        except Exception as e:

            st.error(
                f"Automatic SQL repair failed: {e}"
            )

            st.stop()

    # --------------------------------------------------------
    # FINAL EXECUTION CHECK
    # --------------------------------------------------------

    if isinstance(
        execution_result,
        dict,
    ):

        st.error(
            execution_result.get(
                "error",
                "SQL execution failed.",
            )
        )

        st.stop()

    result = execution_result

    # --------------------------------------------------------
    # EMPTY RESULT
    # --------------------------------------------------------

    if result.empty:

        st.warning(
            "No results were found."
        )

        st.stop()

    # --------------------------------------------------------
    # RECORD QUESTION USAGE
    # --------------------------------------------------------

    try:

        record_question(
            user_email
        )

    except Exception as e:

        st.warning(
            f"Analysis completed, but usage could not be recorded: {e}"
        )

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    st.session_state.result = result

    st.session_state.last_sql = sql

    # ========================================================
    # RESULTS
    # ========================================================

    st.markdown(
        "## 📊 Results"
    )

    st.dataframe(
        result,
        use_container_width=True,
    )

    # ========================================================
    # CHART
    # ========================================================

    st.markdown(
        "## 📈 Visualization"
    )

    try:

        chart_result = create_chart(
            result,
            title=original_question,
        )

        if chart_result is not None:

            if hasattr(
                chart_result,
                "figure",
            ):

                st.pyplot(
                    chart_result.figure
                )

            else:

                st.write(
                    chart_result
                )

    except Exception as e:

        st.warning(
            f"Chart could not be displayed: {e}"
        )

    # ========================================================
    # SQL
    # ========================================================

    with st.expander(
        "🔍 View Generated SQL"
    ):

        st.code(
            sql,
            language="sql",
        )

    # ========================================================
    # BUSINESS INSIGHT
    # ========================================================

    st.markdown(
        "## 🧠 Business Insight"
    )

    answer_text = ""

    try:

        from ollama import chat

        result_text = result.to_string(
            index=False
        )

        insight_prompt = f"""
You are a professional AI Business Analyst.

The user asked:

{original_question}

Previous conversation context:

{memory_context}

Database result:

{result_text}

Answer the user's CURRENT question using ONLY
the database result and relevant previous conversation.

Rules:

1. Do not invent numbers.
2. Do not invent facts.
3. Answer the current question directly.
4. If this is a follow-up such as "Why?",
   use the previous conversation.
5. Preserve names exactly.
6. Compare results when relevant.
7. Give one useful business insight.
8. Keep the answer concise.
9. Do not claim causation unless the data demonstrates it.
10. Use the same language as the user's question.

Format:

Answer:

[direct answer]

Business insight:

[one useful insight]
"""

        response = chat(
            model="llama3.2",
            messages=[
                {
                    "role":
                        "user",

                    "content":
                        insight_prompt,
                }
            ],
            options={
                "temperature":
                    0,
            },
        )

        answer_text = (
            response[
                "message"
            ][
                "content"
            ].strip()
        )

        st.session_state.last_answer = (
            answer_text
        )

        st.write(
            answer_text
        )

    except Exception as e:

        st.warning(
            f"Could not generate business insight: {e}"
        )

    # ========================================================
    # SAVE CHAT MEMORY
    # ========================================================

    try:

        saved = save_chat(
            user_email=user_email,
            dataset_name=selected_dataset,
            question=original_question,
            answer=answer_text,
            sql_query=sql,
        )

        if saved:

            st.success(
                "💬 Conversation saved to memory."
            )

    except Exception as e:

        st.warning(
            f"Could not save conversation memory: {e}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Business Analyst • "
    "Data-driven business intelligence"
)
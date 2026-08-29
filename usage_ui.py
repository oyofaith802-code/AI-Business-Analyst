import streamlit as st

from plan_manager import get_usage_summary
from dataset_profile_storage import get_user_dataset_profiles


# ============================================================
# GET CURRENT PLAN
# ============================================================

def get_current_plan(user_email):

    try:

        from subscription import get_subscription

        subscription = get_subscription(
            user_email
        )

        if subscription:

            return str(
                subscription.get(
                    "plan",
                    "free"
                )
            ).title()

    except Exception:

        pass

    return "Free"


# ============================================================
# SHOW PLAN STATUS
# ============================================================

def show_plan_status(user_email):

    try:

        summary = get_usage_summary(
            user_email
        )

    except Exception as e:

        st.warning(
            f"Could not load usage information: {e}"
        )

        return


    plan_name = get_current_plan(
        user_email
    )


    st.markdown(
        f"### 💳 {plan_name} Plan"
    )


    # ========================================================
    # QUESTIONS
    # ========================================================

    questions_used = summary.get(
        "questions_used",
        0
    )

    questions_limit = summary.get(
        "questions_limit",
        0
    )


    st.write(
        f"💬 Questions: "
        f"**{questions_used} / {questions_limit}**"
    )


    if questions_limit > 0:

        progress = min(
            questions_used / questions_limit,
            1.0
        )

        st.progress(
            progress
        )


    # ========================================================
    # UPLOADS
    # ========================================================

    uploads_used = summary.get(
        "uploads_used",
        0
    )

    uploads_limit = summary.get(
        "uploads_limit",
        0
    )


    st.write(
        f"📤 Uploads: "
        f"**{uploads_used} / {uploads_limit}**"
    )


    if uploads_limit > 0:

        progress = min(
            uploads_used / uploads_limit,
            1.0
        )

        st.progress(
            progress
        )


# ============================================================
# ACCOUNT DASHBOARD
# ============================================================

def show_account_dashboard(user_email):

    st.markdown(
        "## 👤 Account Overview"
    )


    # ========================================================
    # USAGE
    # ========================================================

    try:

        summary = get_usage_summary(
            user_email
        )

    except Exception as e:

        st.error(
            f"Could not load account usage: {e}"
        )

        return


    plan_name = get_current_plan(
        user_email
    )


    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "💳 Current Plan",
            plan_name
        )


    with col2:

        st.metric(
            "💬 Questions",
            (
                f"{summary.get('questions_used', 0)} / "
                f"{summary.get('questions_limit', 0)}"
            )
        )


    with col3:

        st.metric(
            "📤 Uploads",
            (
                f"{summary.get('uploads_used', 0)} / "
                f"{summary.get('uploads_limit', 0)}"
            )
        )


    st.divider()


    # ========================================================
    # DATASETS
    # ========================================================

    st.markdown(
        "### 📁 Your Datasets"
    )


    try:

        datasets = get_user_dataset_profiles(
            user_email
        )

    except Exception:

        datasets = []


    if datasets:

        for dataset in datasets[:5]:

            dataset_name = dataset.get(
                "dataset_name",
                "Unknown dataset"
            )

            profile = dataset.get(
                "profile",
                {}
            )

            rows = profile.get(
                "rows",
                0
            )

            columns = profile.get(
                "columns",
                0
            )

            st.write(
                f"📊 **{dataset_name}** — "
                f"{rows:,} rows × {columns} columns"
            )

    else:

        st.info(
            "You have not uploaded any datasets yet."
        )


    st.divider()


    # ========================================================
    # UPGRADE
    # ========================================================

    if plan_name.lower() == "free":

        st.markdown(
            "### 🚀 Upgrade Your Plan"
        )

        st.write(
            "Get higher limits and advanced "
            "business analysis features."
        )

        if st.button(
            "🚀 View Plans",
            type="primary"
        ):

            st.info(
                "Subscription plans will be "
                "available here soon."
            )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Usage UI module loaded successfully."
    )
# ============================================================
# AI BUSINESS ANALYST
# UPGRADE UI
#
# Features:
# - Automatic plan recommendation
# - Pro / Business comparison
# - Paystack checkout
# - Payment verification
# - Subscription activation
# ============================================================

import streamlit as st

from plan_manager import get_usage_summary
from payment import initialize_paystack_payment
from payment import verify_paystack_payment


# ============================================================
# PLAN DEFINITIONS
# ============================================================

PLANS = {
    "pro": {
        "name": "Pro",
        "price": 30000,
        "currency": "NGN",
        "questions": 500,
        "uploads": 50,
        "datasets": 20,
        "description": "For individuals and small businesses.",
    },

    "business": {
        "name": "Business",
        "price": 75000,
        "currency": "NGN",
        "questions": 5000,
        "uploads": 500,
        "datasets": 100,
        "description": "For growing businesses and heavier analysis.",
    },
}


# ============================================================
# AUTOMATIC PLAN RECOMMENDATION
# ============================================================

def recommend_plan(user_email):
    """
    Recommend a paid plan based on the user's current usage.
    """

    try:
        usage = get_usage_summary(user_email)

    except Exception:
        return "pro"

    questions_used = usage.get(
        "questions_used",
        0
    )

    questions_limit = usage.get(
        "questions_limit",
        25
    )

    uploads_used = usage.get(
        "uploads_used",
        0
    )

    uploads_limit = usage.get(
        "uploads_limit",
        5
    )

    # --------------------------------------------------------
    # Calculate usage percentages
    # --------------------------------------------------------

    question_usage = (
        questions_used / questions_limit
        if questions_limit > 0
        else 0
    )

    upload_usage = (
        uploads_used / uploads_limit
        if uploads_limit > 0
        else 0
    )

    highest_usage = max(
        question_usage,
        upload_usage
    )

    # --------------------------------------------------------
    # If user is already using a large amount of capacity,
    # recommend Business.
    # --------------------------------------------------------

    if highest_usage >= 0.80:
        return "business"

    return "pro"


# ============================================================
# FORMAT PRICE
# ============================================================

def format_price(amount):
    return f"₦{amount:,.0f}"


# ============================================================
# SHOW PLAN CARD
# ============================================================

def show_plan_card(
    plan_key,
    recommended=False,
):
    """
    Display a single subscription plan.
    """

    plan = PLANS[plan_key]

    if recommended:

        st.success(
            "⭐ Recommended for you"
        )

    st.markdown(
        f"### {plan['name']}"
    )

    st.markdown(
        f"## {format_price(plan['price'])}"
        f" **/ month**"
    )

    st.write(
        plan["description"]
    )

    st.write(
        f"✅ {plan['questions']:,} questions/month"
    )

    st.write(
        f"✅ {plan['uploads']:,} uploads/month"
    )

    st.write(
        f"✅ Up to {plan['datasets']:,} datasets"
    )


# ============================================================
# INITIALIZE CHECKOUT
# ============================================================

def start_checkout(
    user_email,
    plan_key,
):
    """
    Create a Paystack checkout.
    """

    plan = PLANS.get(plan_key)

    if not plan:

        st.error(
            "Invalid subscription plan."
        )

        return

    try:

        with st.spinner(
            "Creating secure Paystack checkout..."
        ):

            result = initialize_paystack_payment(
                user_email=user_email,
                plan=plan_key,
                amount=plan["price"],
                currency=plan["currency"],
            )

        if not result:

            st.error(
                "Could not create payment."
            )

            return

        # ----------------------------------------------------
        # Different payment modules may return different keys.
        # ----------------------------------------------------

        checkout_url = (
            result.get("authorization_url")
            or result.get("checkout_url")
            or result.get("url")
        )

        reference = result.get(
            "reference"
        )

        if not checkout_url:

            st.error(
                "Paystack did not return a checkout URL."
            )

            return

        # ----------------------------------------------------
        # Save checkout information
        # ----------------------------------------------------

        st.session_state.payment_reference = (
            reference
        )

        st.session_state.payment_plan = (
            plan_key
        )

        st.session_state.payment_checkout_url = (
            checkout_url
        )

        st.success(
            "✅ Checkout created successfully."
        )

        st.markdown(
            f"### {plan['name']} — "
            f"{format_price(plan['price'])}/month"
        )

        st.link_button(
            "💳 Continue to Paystack",
            checkout_url,
            use_container_width=True,
        )

        st.info(
            "Complete the payment on Paystack, "
            "then return here and verify the payment."
        )

    except Exception as e:

        st.error(
            f"Could not create checkout: {e}"
        )


# ============================================================
# VERIFY PAYMENT
# ============================================================

def verify_payment(user_email):
    """
    Verify the current Paystack transaction.
    """

    reference = st.session_state.get(
        "payment_reference"
    )

    if not reference:

        st.warning(
            "No payment reference was found."
        )

        return

    try:

        with st.spinner(
            "Verifying your payment..."
        ):

            result = verify_paystack_payment(
                reference=reference,
                user_email=user_email,
            )

        if not result:

            st.error(
                "Payment verification failed."
            )

            return

        success = result.get(
            "success",
            False,
        )

        if success:

            plan = result.get(
                "plan",
                st.session_state.get(
                    "payment_plan",
                    "pro",
                ),
            )

            st.success(
                f"🎉 Payment verified! "
                f"Your {plan.title()} subscription is now active."
            )

            # ------------------------------------------------
            # Clear payment state
            # ------------------------------------------------

            st.session_state.pop(
                "payment_reference",
                None,
            )

            st.session_state.pop(
                "payment_plan",
                None,
            )

            st.session_state.pop(
                "payment_checkout_url",
                None,
            )

            st.rerun()

        else:

            message = result.get(
                "message",
                "Payment has not been completed.",
            )

            st.warning(
                f"❌ Payment not activated.\n\n"
                f"{message}"
            )

    except Exception as e:

        st.error(
            f"Payment verification failed: {e}"
        )


# ============================================================
# MAIN UPGRADE UI
# ============================================================

def show_upgrade_ui(user_email):
    """
    Display subscription upgrade interface.
    """

    st.markdown(
        "## 🚀 Upgrade Your Plan"
    )

    st.write(
        "Choose the plan that best fits your business analysis needs."
    )

    # --------------------------------------------------------
    # Current usage
    # --------------------------------------------------------

    try:

        usage = get_usage_summary(
            user_email
        )

    except Exception:

        usage = {}

    current_plan = usage.get(
        "plan",
        "Free",
    )

    st.info(
        f"Current plan: **{current_plan}**"
    )

    # --------------------------------------------------------
    # Automatic recommendation
    # --------------------------------------------------------

    recommended_plan = recommend_plan(
        user_email
    )

    recommended = PLANS[
        recommended_plan
    ]

    st.markdown(
        f"### ⭐ Recommended: {recommended['name']}"
    )

    st.write(
        recommended["description"]
    )

    st.write(
        f"**{format_price(recommended['price'])}/month**"
    )

    # --------------------------------------------------------
    # Plan comparison
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        show_plan_card(
            "pro",
            recommended=(
                recommended_plan == "pro"
            ),
        )

        if st.button(
            "🚀 Choose Pro",
            key="choose_pro",
            use_container_width=True,
        ):

            start_checkout(
                user_email,
                "pro",
            )

    with col2:

        show_plan_card(
            "business",
            recommended=(
                recommended_plan == "business"
            ),
        )

        if st.button(
            "🚀 Choose Business",
            key="choose_business",
            use_container_width=True,
        ):

            start_checkout(
                user_email,
                "business",
            )

    # --------------------------------------------------------
    # Verification section
    # --------------------------------------------------------

    if st.session_state.get(
        "payment_reference"
    ):

        st.divider()

        st.markdown(
            "### 🔐 Verify Payment"
        )

        st.write(
            "After completing your Paystack payment, "
            "click the button below."
        )

        st.caption(
            f"Reference: "
            f"{st.session_state.payment_reference}"
        )

        if st.button(
            "✅ Verify Payment",
            type="primary",
            use_container_width=True,
        ):

            verify_payment(
                user_email
            )
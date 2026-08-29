# ============================================================
# AI BUSINESS ANALYST - PLAN MANAGER
# ============================================================

from subscription import (
    get_subscription,
    get_user_plan
)

from database import engine

from sqlalchemy import text


# ============================================================
# PLAN DEFINITIONS
# ============================================================

PLANS = {

    "free": {

        "name": "Free",

        "monthly_questions": 25,

        "monthly_uploads": 5,

        "max_datasets": 2,

        "advanced_analysis": False,

        "chat_memory": True,

        "charts": True

    },

    "pro": {

        "name": "Pro",

        "monthly_questions": 500,

        "monthly_uploads": 50,

        "max_datasets": 20,

        "advanced_analysis": True,

        "chat_memory": True,

        "charts": True

    },

    "business": {

        "name": "Business",

        "monthly_questions": 5000,

        "monthly_uploads": 500,

        "max_datasets": 100,

        "advanced_analysis": True,

        "chat_memory": True,

        "charts": True

    }

}


# ============================================================
# CREATE USAGE TABLE
# ============================================================

def create_usage_table():

    sql = text("""
        CREATE TABLE IF NOT EXISTS usage_tracking (

            id SERIAL PRIMARY KEY,

            user_email TEXT NOT NULL,

            usage_month TEXT NOT NULL,

            questions_used INTEGER DEFAULT 0,

            uploads_used INTEGER DEFAULT 0,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(
                user_email,
                usage_month
            )
        )
    """)

    with engine.begin() as conn:

        conn.execute(sql)

    print(
        "✅ usage_tracking table ready."
    )


# ============================================================
# CURRENT MONTH
# ============================================================

def current_month():

    from datetime import datetime

    return datetime.utcnow().strftime(
        "%Y-%m"
    )


# ============================================================
# CREATE MONTHLY USAGE RECORD
# ============================================================

def create_usage_record(user_email):

    create_usage_table()

    month = current_month()

    sql = text("""
        INSERT INTO usage_tracking (

            user_email,

            usage_month,

            questions_used,

            uploads_used

        )

        VALUES (

            :user_email,

            :usage_month,

            0,

            0

        )

        ON CONFLICT (
            user_email,
            usage_month
        )

        DO NOTHING
    """)

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower(),

                "usage_month":
                    month
            }
        )


# ============================================================
# GET USAGE
# ============================================================

def get_usage(user_email):

    create_usage_record(
        user_email
    )

    month = current_month()

    sql = text("""
        SELECT

            questions_used,

            uploads_used

        FROM usage_tracking

        WHERE user_email = :user_email

        AND usage_month = :usage_month

        LIMIT 1
    """)

    with engine.connect() as conn:

        row = conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower(),

                "usage_month":
                    month
            }
        ).fetchone()

    if row is None:

        return {

            "questions_used": 0,

            "uploads_used": 0

        }

    return {

        "questions_used":
            int(row.questions_used),

        "uploads_used":
            int(row.uploads_used)

    }


# ============================================================
# GET PLAN LIMITS
# ============================================================

def get_plan_limits(user_email):

    plan_name = get_user_plan(
        user_email
    )

    return PLANS.get(
        plan_name,
        PLANS["free"]
    )


# ============================================================
# CHECK QUESTION LIMIT
# ============================================================

def can_ask_question(user_email):

    limits = get_plan_limits(
        user_email
    )

    usage = get_usage(
        user_email
    )

    return (
        usage["questions_used"]
        <
        limits["monthly_questions"]
    )


# ============================================================
# CHECK UPLOAD LIMIT
# ============================================================

def can_upload(user_email):

    limits = get_plan_limits(
        user_email
    )

    usage = get_usage(
        user_email
    )

    return (
        usage["uploads_used"]
        <
        limits["monthly_uploads"]
    )


# ============================================================
# RECORD QUESTION
# ============================================================

def record_question(user_email):

    create_usage_record(
        user_email
    )

    month = current_month()

    sql = text("""
        UPDATE usage_tracking

        SET

            questions_used =
                questions_used + 1,

            updated_at =
                CURRENT_TIMESTAMP

        WHERE user_email = :user_email

        AND usage_month = :usage_month
    """)

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower(),

                "usage_month":
                    month
            }
        )


# ============================================================
# RECORD UPLOAD
# ============================================================

def record_upload(user_email):

    create_usage_record(
        user_email
    )

    month = current_month()

    sql = text("""
        UPDATE usage_tracking

        SET

            uploads_used =
                uploads_used + 1,

            updated_at =
                CURRENT_TIMESTAMP

        WHERE user_email = :user_email

        AND usage_month = :usage_month
    """)

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower(),

                "usage_month":
                    month
            }
        )


# ============================================================
# GET USAGE SUMMARY
# ============================================================

def get_usage_summary(user_email):

    limits = get_plan_limits(
        user_email
    )

    usage = get_usage(
        user_email
    )

    return {

        "plan":
            limits["name"],

        "questions_used":
            usage["questions_used"],

        "questions_limit":
            limits["monthly_questions"],

        "uploads_used":
            usage["uploads_used"],

        "uploads_limit":
            limits["monthly_uploads"],

        "max_datasets":
            limits["max_datasets"],

        "advanced_analysis":
            limits["advanced_analysis"],

        "chat_memory":
            limits["chat_memory"],

        "charts":
            limits["charts"]

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================================"
    )

    print(
        "PLAN MANAGER TEST"
    )

    print(
        "============================================================"
    )

    test_email = "test@example.com"

    create_usage_table()

    print()

    print(
        "📋 Plan limits:"
    )

    print(
        get_plan_limits(
            test_email
        )
    )

    print()

    print(
        "📊 Current usage:"
    )

    print(
        get_usage(
            test_email
        )
    )

    print()

    print(
        "📈 Usage summary:"
    )

    print(
        get_usage_summary(
            test_email
        )
    )

    print()

    print(
        "❓ Can ask question:",
        can_ask_question(
            test_email
        )
    )

    print()

    print(
        "📤 Can upload:",
        can_upload(
            test_email
        )
    )

    print()

    print(
        "============================================================"
    )

    print(
        "✅ Plan manager test completed."
    )
    # ============================================================
# QUESTION LIMIT CHECK
# ============================================================

def question_allowed(user_email):
    """
    Check whether the user can ask another question.
    """

    summary = get_usage_summary(user_email)

    if not summary:
        return False

    questions_used = summary.get(
        "questions_used",
        0
    )

    questions_limit = summary.get(
        "questions_limit",
        0
    )

    return questions_used < questions_limit


# ============================================================
# UPLOAD LIMIT CHECK
# ============================================================

def upload_allowed(user_email):
    """
    Check whether the user can upload another dataset.
    """

    summary = get_usage_summary(user_email)

    if not summary:
        return False

    uploads_used = summary.get(
        "uploads_used",
        0
    )

    uploads_limit = summary.get(
        "uploads_limit",
        0
    )

    return uploads_used < uploads_limit


# ============================================================
# INCREMENT QUESTION USAGE
# ============================================================

def increment_question_usage(user_email):
    """
    Record one business question.
    """

    create_usage_tracking_table()

    month = get_current_month()

    sql = text(
        """
        INSERT INTO usage_tracking
        (
            user_email,
            month,
            questions_used,
            uploads_used
        )
        VALUES
        (
            :user_email,
            :month,
            1,
            0
        )
        ON CONFLICT
        (
            user_email,
            month
        )
        DO UPDATE SET
            questions_used =
                usage_tracking.questions_used + 1
        """
    )

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email": user_email.strip().lower(),
                "month": month
            }
        )


# ============================================================
# INCREMENT UPLOAD USAGE
# ============================================================

def increment_upload_usage(user_email):
    """
    Record one dataset upload.
    """

    create_usage_tracking_table()

    month = get_current_month()

    sql = text(
        """
        INSERT INTO usage_tracking
        (
            user_email,
            month,
            questions_used,
            uploads_used
        )
        VALUES
        (
            :user_email,
            :month,
            0,
            1
        )
        ON CONFLICT
        (
            user_email,
            month
        )
        DO UPDATE SET
            uploads_used =
                usage_tracking.uploads_used + 1
        """
    )

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email": user_email.strip().lower(),
                "month": month
            }
        )
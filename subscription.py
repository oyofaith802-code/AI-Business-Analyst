# ============================================================
# AI BUSINESS ANALYST
# SUBSCRIPTION MANAGEMENT
# ============================================================

from datetime import datetime, timedelta

from sqlalchemy import text

from database import engine


# ============================================================
# PLAN DEFINITIONS
# ============================================================

PLANS = {

    "free": {
        "name": "Free",
        "price_usd": 0.00,
        "billing_period": "monthly",

        "monthly_questions": 25,
        "monthly_uploads": 5,
        "max_datasets": 2,

        "advanced_analysis": False,
        "chat_memory": True,
        "charts": True,
        "sql_auto_repair": True,
    },

    "pro": {
        "name": "Pro",
        "price_usd": 19.00,
        "billing_period": "monthly",

        "monthly_questions": 500,
        "monthly_uploads": 50,
        "max_datasets": 20,

        "advanced_analysis": True,
        "chat_memory": True,
        "charts": True,
        "sql_auto_repair": True,
    },

    "business": {
        "name": "Business",
        "price_usd": 49.00,
        "billing_period": "monthly",

        "monthly_questions": 5000,
        "monthly_uploads": 500,
        "max_datasets": 100,

        "advanced_analysis": True,
        "chat_memory": True,
        "charts": True,
        "sql_auto_repair": True,
    },

    "enterprise": {
        "name": "Enterprise",
        "price_usd": None,
        "billing_period": "custom",

        "monthly_questions": None,
        "monthly_uploads": None,
        "max_datasets": None,

        "advanced_analysis": True,
        "chat_memory": True,
        "charts": True,
        "sql_auto_repair": True,
    }
}


# ============================================================
# DEFAULT TRIAL
# ============================================================

TRIAL_DAYS = 7


# ============================================================
# CREATE SUBSCRIPTION TABLE
# ============================================================

def create_subscription_table():

    sql = text(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (

            id SERIAL PRIMARY KEY,

            user_email TEXT NOT NULL UNIQUE,

            plan TEXT NOT NULL DEFAULT 'free',

            status TEXT NOT NULL DEFAULT 'trial',

            trial_started_at TIMESTAMP,

            trial_ends_at TIMESTAMP,

            current_period_start TIMESTAMP,

            current_period_end TIMESTAMP,

            payment_reference TEXT,

            payment_provider TEXT,

            currency TEXT DEFAULT 'USD',

            amount NUMERIC(12, 2),

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    with engine.begin() as conn:
        conn.execute(sql)


# ============================================================
# REPAIR SUBSCRIPTION TABLE
# ============================================================

def repair_subscription_table():

    create_subscription_table()

    required_columns = {

        "plan":
            "TEXT NOT NULL DEFAULT 'free'",

        "status":
            "TEXT NOT NULL DEFAULT 'trial'",

        "trial_started_at":
            "TIMESTAMP",

        "trial_ends_at":
            "TIMESTAMP",

        "current_period_start":
            "TIMESTAMP",

        "current_period_end":
            "TIMESTAMP",

        "payment_reference":
            "TEXT",

        "payment_provider":
            "TEXT",

        "currency":
            "TEXT DEFAULT 'USD'",

        "amount":
            "NUMERIC(12,2)",

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

        "updated_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }

    with engine.begin() as conn:

        rows = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'subscriptions'
                """
            )
        ).fetchall()

        existing_columns = {
            row[0]
            for row in rows
        }

        for column, data_type in required_columns.items():

            if column not in existing_columns:

                conn.execute(
                    text(
                        f"""
                        ALTER TABLE subscriptions
                        ADD COLUMN {column} {data_type}
                        """
                    )
                )

                print(
                    f"Added missing subscription column: {column}"
                )


# ============================================================
# CREATE FREE TRIAL
# ============================================================

def create_free_subscription(user_email):

    if not user_email:
        return False

    user_email = user_email.strip().lower()

    repair_subscription_table()

    now = datetime.utcnow()

    trial_end = (
        now +
        timedelta(days=TRIAL_DAYS)
    )

    sql = text(
        """
        INSERT INTO subscriptions (

            user_email,
            plan,
            status,
            trial_started_at,
            trial_ends_at,
            current_period_start,
            current_period_end,
            currency,
            amount

        )

        VALUES (

            :user_email,
            'free',
            'trial',
            :trial_started_at,
            :trial_ends_at,
            :current_period_start,
            :current_period_end,
            'USD',
            0

        )

        ON CONFLICT (user_email)
        DO NOTHING
        """
    )

    try:

        with engine.begin() as conn:

            conn.execute(
                sql,
                {
                    "user_email":
                        user_email,

                    "trial_started_at":
                        now,

                    "trial_ends_at":
                        trial_end,

                    "current_period_start":
                        now,

                    "current_period_end":
                        trial_end
                }
            )

        return True

    except Exception as e:

        print(
            f"Could not create subscription: {e}"
        )

        return False


# ============================================================
# GET SUBSCRIPTION
# ============================================================

def get_subscription(user_email):

    if not user_email:
        return None

    user_email = user_email.strip().lower()

    repair_subscription_table()

    try:

        sql = text(
            """
            SELECT

                id,
                user_email,
                plan,
                status,
                trial_started_at,
                trial_ends_at,
                current_period_start,
                current_period_end,
                payment_reference,
                payment_provider,
                currency,
                amount,
                created_at,
                updated_at

            FROM subscriptions

            WHERE user_email = :user_email

            LIMIT 1
            """
        )

        with engine.connect() as conn:

            row = conn.execute(
                sql,
                {
                    "user_email":
                        user_email
                }
            ).mappings().first()

        if row is None:

            create_free_subscription(
                user_email
            )

            return get_subscription(
                user_email
            )

        return dict(row)

    except Exception as e:

        print(
            f"Could not load subscription: {e}"
        )

        return None


# ============================================================
# GET USER PLAN
# ============================================================

def get_user_plan(user_email):

    subscription = get_subscription(
        user_email
    )

    if not subscription:

        return "free"

    plan = subscription.get(
        "plan",
        "free"
    )

    if plan not in PLANS:

        return "free"

    return plan


# ============================================================
# GET PLAN DETAILS
# ============================================================

def get_plan_details(user_email):

    plan = get_user_plan(
        user_email
    )

    details = PLANS.get(
        plan,
        PLANS["free"]
    ).copy()

    details["plan"] = plan

    return details


# ============================================================
# CHECK WHETHER TRIAL IS ACTIVE
# ============================================================

def is_trial_active(user_email):

    subscription = get_subscription(
        user_email
    )

    if not subscription:

        return False

    if subscription.get(
        "status"
    ) != "trial":

        return False

    trial_end = subscription.get(
        "trial_ends_at"
    )

    if not trial_end:

        return False

    return datetime.utcnow() < trial_end


# ============================================================
# CHECK WHETHER SUBSCRIPTION IS ACTIVE
# ============================================================

def is_subscription_active(user_email):

    subscription = get_subscription(
        user_email
    )

    if not subscription:

        return False

    status = subscription.get(
        "status"
    )

    if status == "trial":

        return is_trial_active(
            user_email
        )

    if status == "active":

        period_end = subscription.get(
            "current_period_end"
        )

        if period_end:

            return (
                datetime.utcnow()
                < period_end
            )

        return True

    return False


# ============================================================
# GET SUBSCRIPTION STATUS
# ============================================================

def get_subscription_status(user_email):

    subscription = get_subscription(
        user_email
    )

    if not subscription:

        return {
            "active": False,
            "status": "inactive",
            "plan": "free"
        }

    status = subscription.get(
        "status",
        "inactive"
    )

    if status == "trial":

        active = is_trial_active(
            user_email
        )

    elif status == "active":

        active = is_subscription_active(
            user_email
        )

    else:

        active = False

    return {

        "active":
            active,

        "status":
            status,

        "plan":
            subscription.get(
                "plan",
                "free"
            ),

        "trial_ends_at":
            subscription.get(
                "trial_ends_at"
            ),

        "current_period_end":
            subscription.get(
                "current_period_end"
            )
    }


# ============================================================
# UPGRADE SUBSCRIPTION
# ============================================================

def upgrade_subscription(
    user_email,
    plan,
    payment_reference=None,
    payment_provider="paystack",
    currency="USD",
    amount=None
):

    if not user_email:
        return False

    user_email = user_email.strip().lower()

    plan = plan.strip().lower()

    if plan not in PLANS:

        raise ValueError(
            f"Unknown subscription plan: {plan}"
        )

    if plan == "free":

        raise ValueError(
            "Use downgrade_subscription() for the free plan."
        )

    if amount is None:

        amount = PLANS[
            plan
        ]["price_usd"]

    now = datetime.utcnow()

    period_end = (
        now +
        timedelta(days=30)
    )

    repair_subscription_table()

    sql = text(
        """
        INSERT INTO subscriptions (

            user_email,
            plan,
            status,
            current_period_start,
            current_period_end,
            payment_reference,
            payment_provider,
            currency,
            amount,
            updated_at

        )

        VALUES (

            :user_email,
            :plan,
            'active',
            :period_start,
            :period_end,
            :payment_reference,
            :payment_provider,
            :currency,
            :amount,
            CURRENT_TIMESTAMP

        )

        ON CONFLICT (user_email)

        DO UPDATE SET

            plan =
                EXCLUDED.plan,

            status =
                'active',

            current_period_start =
                EXCLUDED.current_period_start,

            current_period_end =
                EXCLUDED.current_period_end,

            payment_reference =
                EXCLUDED.payment_reference,

            payment_provider =
                EXCLUDED.payment_provider,

            currency =
                EXCLUDED.currency,

            amount =
                EXCLUDED.amount,

            updated_at =
                CURRENT_TIMESTAMP
        """
    )

    try:

        with engine.begin() as conn:

            conn.execute(
                sql,
                {
                    "user_email":
                        user_email,

                    "plan":
                        plan,

                    "period_start":
                        now,

                    "period_end":
                        period_end,

                    "payment_reference":
                        payment_reference,

                    "payment_provider":
                        payment_provider,

                    "currency":
                        currency,

                    "amount":
                        amount
                }
            )

        print(
            f"Subscription upgraded to {plan}."
        )

        return True

    except Exception as e:

        print(
            f"Could not upgrade subscription: {e}"
        )

        return False


# ============================================================
# DOWNGRADE TO FREE
# ============================================================

def downgrade_subscription(user_email):

    if not user_email:

        return False

    user_email = user_email.strip().lower()

    repair_subscription_table()

    now = datetime.utcnow()

    trial_end = (
        now +
        timedelta(days=0)
    )

    sql = text(
        """
        UPDATE subscriptions

        SET

            plan = 'free',

            status = 'active',

            current_period_start = :start,

            current_period_end = :end,

            payment_reference = NULL,

            payment_provider = NULL,

            amount = 0,

            updated_at = CURRENT_TIMESTAMP

        WHERE user_email = :user_email
        """
    )

    try:

        with engine.begin() as conn:

            result = conn.execute(
                sql,
                {
                    "user_email":
                        user_email,

                    "start":
                        now,

                    "end":
                        trial_end
                }
            )

        return result.rowcount > 0

    except Exception as e:

        print(
            f"Could not downgrade subscription: {e}"
        )

        return False


# ============================================================
# CANCEL SUBSCRIPTION
# ============================================================

def cancel_subscription(user_email):

    if not user_email:

        return False

    user_email = user_email.strip().lower()

    repair_subscription_table()

    sql = text(
        """
        UPDATE subscriptions

        SET

            status = 'cancelled',

            updated_at =
                CURRENT_TIMESTAMP

        WHERE user_email = :user_email
        """
    )

    try:

        with engine.begin() as conn:

            result = conn.execute(
                sql,
                {
                    "user_email":
                        user_email
                }
            )

        return result.rowcount > 0

    except Exception as e:

        print(
            f"Could not cancel subscription: {e}"
        )

        return False


# ============================================================
# RENEW SUBSCRIPTION
# ============================================================

def renew_subscription(
    user_email,
    payment_reference=None,
    currency="USD",
    amount=None
):

    subscription = get_subscription(
        user_email
    )

    if not subscription:

        return False

    plan = subscription.get(
        "plan",
        "free"
    )

    if plan == "free":

        return False

    if amount is None:

        amount = PLANS[
            plan
        ]["price_usd"]

    now = datetime.utcnow()

    current_end = subscription.get(
        "current_period_end"
    )

    if current_end and current_end > now:

        period_start = current_end

    else:

        period_start = now

    period_end = (
        period_start +
        timedelta(days=30)
    )

    sql = text(
        """
        UPDATE subscriptions

        SET

            status = 'active',

            current_period_start =
                :period_start,

            current_period_end =
                :period_end,

            payment_reference =
                :payment_reference,

            currency =
                :currency,

            amount =
                :amount,

            updated_at =
                CURRENT_TIMESTAMP

        WHERE user_email =
            :user_email
        """
    )

    try:

        with engine.begin() as conn:

            result = conn.execute(
                sql,
                {
                    "user_email":
                        user_email.strip().lower(),

                    "period_start":
                        period_start,

                    "period_end":
                        period_end,

                    "payment_reference":
                        payment_reference,

                    "currency":
                        currency,

                    "amount":
                        amount
                }
            )

        return result.rowcount > 0

    except Exception as e:

        print(
            f"Could not renew subscription: {e}"
        )

        return False


# ============================================================
# EXPIRE OLD TRIALS
# ============================================================

def expire_trials():

    repair_subscription_table()

    now = datetime.utcnow()

    sql = text(
        """
        UPDATE subscriptions

        SET

            status = 'expired',

            updated_at =
                CURRENT_TIMESTAMP

        WHERE status = 'trial'

        AND trial_ends_at < :now
        """
    )

    try:

        with engine.begin() as conn:

            result = conn.execute(
                sql,
                {
                    "now":
                        now
                }
            )

        print(
            f"Expired {result.rowcount} trial subscriptions."
        )

        return result.rowcount

    except Exception as e:

        print(
            f"Could not expire trials: {e}"
        )

        return 0


# ============================================================
# GET PRICING
# ============================================================

def get_pricing():

    return {

        "free": PLANS["free"].copy(),

        "pro": PLANS["pro"].copy(),

        "business":
            PLANS["business"].copy(),

        "enterprise":
            PLANS["enterprise"].copy()
    }


# ============================================================
# TEST
# ============================================================

def main():

    print("=" * 60)
    print("AI BUSINESS ANALYST - SUBSCRIPTION TEST")
    print("=" * 60)

    email = input(
        "Enter test email: "
    ).strip().lower()

    # --------------------------------------------------------
    # Create tables
    # --------------------------------------------------------

    print("\nCreating subscription table...")

    repair_subscription_table()

    print("Subscription table ready.")

    # --------------------------------------------------------
    # Create free trial
    # --------------------------------------------------------

    print("\nCreating free trial...")

    create_free_subscription(
        email
    )

    # --------------------------------------------------------
    # Display subscription
    # --------------------------------------------------------

    print("\nCurrent subscription:")

    print(
        get_subscription(
            email
        )
    )

    # --------------------------------------------------------
    # Display plan
    # --------------------------------------------------------

    print("\nCurrent plan:")

    print(
        get_user_plan(
            email
        )
    )

    # --------------------------------------------------------
    # Display status
    # --------------------------------------------------------

    print("\nSubscription status:")

    print(
        get_subscription_status(
            email
        )
    )

    # --------------------------------------------------------
    # Pricing
    # --------------------------------------------------------

    print("\nPricing:")

    for plan_name, details in PLANS.items():

        print(
            f"{plan_name}: "
            f"${details['price_usd']}"
        )

    print("\n" + "=" * 60)
    print("SUBSCRIPTION TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":

    main()

# ============================================================
# AI BUSINESS ANALYST
# SUBSCRIPTION MANAGEMENT
# ============================================================

from datetime import datetime, timedelta

from sqlalchemy import text

from database import engine


# ============================================================
# CREATE SUBSCRIPTIONS TABLE
# ============================================================

def create_subscriptions_table():

    sql = text("""
        CREATE TABLE IF NOT EXISTS subscriptions (

            id SERIAL PRIMARY KEY,

            user_email TEXT NOT NULL,

            plan TEXT NOT NULL DEFAULT 'free',

            status TEXT NOT NULL DEFAULT 'active',

            currency TEXT NOT NULL DEFAULT 'NGN',

            amount NUMERIC(12, 2) NOT NULL DEFAULT 0,

            payment_provider TEXT,

            transaction_id TEXT,

            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            expires_at TIMESTAMP,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_email)
        )
    """)

    with engine.begin() as conn:
        conn.execute(sql)


# ============================================================
# CREATE FREE SUBSCRIPTION
# ============================================================

def create_free_subscription(user_email):

    if not user_email:
        raise ValueError("User email is required.")

    create_subscriptions_table()

    sql = text("""
        INSERT INTO subscriptions (
            user_email,
            plan,
            status,
            currency,
            amount
        )

        VALUES (
            :user_email,
            'free',
            'active',
            'NGN',
            0
        )

        ON CONFLICT (user_email)
        DO NOTHING
    """)

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower()
            }
        )


# ============================================================
# GET SUBSCRIPTION
# ============================================================

def get_subscription(user_email):

    if not user_email:
        return None

    create_subscriptions_table()

    sql = text("""
        SELECT
            id,
            user_email,
            plan,
            status,
            currency,
            amount,
            payment_provider,
            transaction_id,
            started_at,
            expires_at,
            created_at,
            updated_at

        FROM subscriptions

        WHERE user_email = :user_email

        LIMIT 1
    """)

    with engine.connect() as conn:

        row = conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower()
            }
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row.id,
        "user_email": row.user_email,
        "plan": row.plan,
        "status": row.status,
        "currency": row.currency,
        "amount": float(row.amount or 0),
        "payment_provider": row.payment_provider,
        "transaction_id": row.transaction_id,
        "started_at": row.started_at,
        "expires_at": row.expires_at,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


# ============================================================
# UPDATE SUBSCRIPTION
# ============================================================

def update_subscription(
    user_email,
    plan,
    status="active",
    currency="NGN",
    amount=0,
    payment_provider=None,
    transaction_id=None,
    days=30,
):

    if not user_email:
        raise ValueError("User email is required.")

    if not plan:
        raise ValueError("Plan is required.")

    create_subscriptions_table()

    now = datetime.utcnow()

    expires_at = (
        now +
        timedelta(days=days)
    )

    sql = text("""
        INSERT INTO subscriptions (

            user_email,
            plan,
            status,
            currency,
            amount,
            payment_provider,
            transaction_id,
            started_at,
            expires_at,
            updated_at

        )

        VALUES (

            :user_email,
            :plan,
            :status,
            :currency,
            :amount,
            :payment_provider,
            :transaction_id,
            :started_at,
            :expires_at,
            CURRENT_TIMESTAMP

        )

        ON CONFLICT (user_email)

        DO UPDATE SET

            plan = EXCLUDED.plan,

            status = EXCLUDED.status,

            currency = EXCLUDED.currency,

            amount = EXCLUDED.amount,

            payment_provider =
                EXCLUDED.payment_provider,

            transaction_id =
                EXCLUDED.transaction_id,

            started_at =
                EXCLUDED.started_at,

            expires_at =
                EXCLUDED.expires_at,

            updated_at =
                CURRENT_TIMESTAMP
    """)

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower(),

                "plan":
                    plan.strip().lower(),

                "status":
                    status.strip().lower(),

                "currency":
                    currency.strip().upper(),

                "amount":
                    amount,

                "payment_provider":
                    payment_provider,

                "transaction_id":
                    transaction_id,

                "started_at":
                    now,

                "expires_at":
                    expires_at,
            }
        )


# ============================================================
# CANCEL SUBSCRIPTION
# ============================================================

def cancel_subscription(user_email):

    if not user_email:
        return False

    create_subscriptions_table()

    sql = text("""
        UPDATE subscriptions

        SET
            status = 'cancelled',
            updated_at = CURRENT_TIMESTAMP

        WHERE user_email = :user_email
    """)

    with engine.begin() as conn:

        result = conn.execute(
            sql,
            {
                "user_email":
                    user_email.strip().lower()
            }
        )

    return result.rowcount > 0


# ============================================================
# CHECK ACTIVE SUBSCRIPTION
# ============================================================

def has_active_subscription(user_email):

    subscription = get_subscription(
        user_email
    )

    if subscription is None:
        return False

    if subscription["status"] != "active":
        return False

    expires_at = subscription["expires_at"]

    if expires_at is not None:

        if expires_at < datetime.utcnow():
            return False

    return True


# ============================================================
# GET USER PLAN
# ============================================================

def get_user_plan(user_email):

    subscription = get_subscription(
        user_email
    )

    if subscription is None:
        return "free"

    if subscription["status"] != "active":
        return "free"

    expires_at = subscription["expires_at"]

    if expires_at is not None:

        if expires_at < datetime.utcnow():
            return "free"

    return subscription["plan"]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SUBSCRIPTION SYSTEM TEST")
    print("=" * 60)

    create_subscriptions_table()

    test_email = "test@example.com"

    create_free_subscription(
        test_email
    )

    subscription = get_subscription(
        test_email
    )

    print()
    print("Current subscription:")
    print(subscription)

    print()
    print(
        "Current plan:",
        get_user_plan(test_email)
    )

    print()
    print(
        "Active:",
        has_active_subscription(
            test_email
        )
    )

    print()
    print("Subscription test completed.")
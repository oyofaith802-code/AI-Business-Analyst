# ============================================================
# AI BUSINESS ANALYST
# PAYSTACK PAYMENT MODULE
#
# Supports:
# - Paystack Test Mode
# - Paystack Live Mode
# - Pro / Business plans
# - Transaction initialization
# - Transaction verification
# - Payment database storage
# - Subscription activation
# ============================================================

import os
import re
import uuid
from datetime import datetime

import requests
from dotenv import load_dotenv
from sqlalchemy import text

from database import engine


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY",
    ""
).strip()


PAYSTACK_BASE_URL = (
    "https://api.paystack.co"
)


# ============================================================
# PLAN DEFINITIONS
# ============================================================

PLANS = {
    "pro": {
        "name": "Pro",
        "amount": 30000,
        "currency": "NGN",
    },

    "business": {
        "name": "Business",
        "amount": 75000,
        "currency": "NGN",
    },
}


# ============================================================
# VALIDATE PAYSTACK KEY
# ============================================================

def paystack_configured():

    return bool(
        PAYSTACK_SECRET_KEY
        and PAYSTACK_SECRET_KEY.startswith("sk_")
    )


# ============================================================
# PAYSTACK HEADERS
# ============================================================

def paystack_headers():

    if not paystack_configured():

        raise ValueError(
            "PAYSTACK_SECRET_KEY is missing from .env"
        )

    return {
        "Authorization":
            f"Bearer {PAYSTACK_SECRET_KEY}",

        "Content-Type":
            "application/json",
    }


# ============================================================
# CREATE PAYMENTS TABLE
# ============================================================

def create_payments_table():

    sql = text(
        """
        CREATE TABLE IF NOT EXISTS payments (

            reference TEXT PRIMARY KEY,

            user_email TEXT NOT NULL,

            plan TEXT NOT NULL,

            amount NUMERIC NOT NULL,

            currency TEXT NOT NULL,

            status TEXT DEFAULT 'pending',

            provider TEXT DEFAULT 'paystack',

            transaction_id BIGINT,

            gateway_response TEXT,

            channel TEXT,

            paid_at TIMESTAMP,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    with engine.begin() as conn:

        conn.execute(sql)


# ============================================================
# ADD MISSING COLUMNS TO OLD PAYMENTS TABLE
# ============================================================

def ensure_payment_columns():

    create_payments_table()

    columns = {

        "user_email":
            "TEXT",

        "plan":
            "TEXT",

        "amount":
            "NUMERIC",

        "currency":
            "TEXT",

        "status":
            "TEXT",

        "provider":
            "TEXT",

        "transaction_id":
            "BIGINT",

        "gateway_response":
            "TEXT",

        "channel":
            "TEXT",

        "paid_at":
            "TIMESTAMP",

        "created_at":
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",

    }

    with engine.begin() as conn:

        for column, definition in columns.items():

            try:

                conn.execute(
                    text(
                        f"""
                        ALTER TABLE payments
                        ADD COLUMN IF NOT EXISTS
                        "{column}"
                        {definition}
                        """
                    )
                )

            except Exception:

                pass


# ============================================================
# GENERATE REFERENCE
# ============================================================

def generate_reference():

    token = uuid.uuid4().hex.upper()

    return (
        f"AIBA_{token}"
    )


# ============================================================
# VALIDATE EMAIL
# ============================================================

def valid_email(email):

    if not email:
        return False

    pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    return bool(
        re.match(
            pattern,
            email.strip()
        )
    )


# ============================================================
# SAVE PENDING PAYMENT
# ============================================================

def save_pending_payment(
    user_email,
    reference,
    plan,
    amount,
    currency,
):

    ensure_payment_columns()

    sql = text(
        """
        INSERT INTO payments
        (
            reference,
            user_email,
            plan,
            amount,
            currency,
            status,
            provider
        )

        VALUES
        (
            :reference,
            :user_email,
            :plan,
            :amount,
            :currency,
            'pending',
            'paystack'
        )

        ON CONFLICT (reference)

        DO UPDATE SET

            user_email =
                EXCLUDED.user_email,

            plan =
                EXCLUDED.plan,

            amount =
                EXCLUDED.amount,

            currency =
                EXCLUDED.currency,

            provider =
                'paystack'
        """
    )

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "reference":
                    reference,

                "user_email":
                    user_email.strip().lower(),

                "plan":
                    plan,

                "amount":
                    amount,

                "currency":
                    currency,
            }
        )


# ============================================================
# INITIALIZE PAYSTACK PAYMENT
# ============================================================

def initialize_paystack_payment(
    user_email,
    plan,
    amount=None,
    currency=None,
):

    if not paystack_configured():

        raise ValueError(
            "Paystack is not configured. "
            "Add PAYSTACK_SECRET_KEY to .env."
        )

    user_email = (
        user_email
        .strip()
        .lower()
    )

    if not valid_email(user_email):

        raise ValueError(
            "Invalid customer email."
        )

    plan = plan.lower().strip()

    if plan not in PLANS:

        raise ValueError(
            "Invalid subscription plan."
        )

    plan_data = PLANS[plan]

    if amount is None:

        amount = plan_data["amount"]

    if currency is None:

        currency = plan_data["currency"]

    # --------------------------------------------------------
    # Paystack expects amount in the currency subunit.
    #
    # NGN 30,000 becomes 3,000,000 kobo.
    # --------------------------------------------------------

    amount_subunit = int(
        round(
            float(amount) * 100
        )
    )

    reference = generate_reference()

    payload = {

        "email":
            user_email,

        "amount":
            amount_subunit,

        "currency":
            currency,

        "reference":
            reference,

        "metadata": {

            "product":
                "AI Business Analyst",

            "plan":
                plan,

            "user_email":
                user_email,

        },
    }

    url = (
        PAYSTACK_BASE_URL
        + "/transaction/initialize"
    )

    response = requests.post(
        url,
        headers=paystack_headers(),
        json=payload,
        timeout=30,
    )

    try:

        data = response.json()

    except Exception:

        raise RuntimeError(
            "Paystack returned an invalid response."
        )

    if not response.ok or not data.get(
        "status",
        False,
    ):

        message = data.get(
            "message",
            "Paystack transaction initialization failed."
        )

        raise RuntimeError(
            message
        )

    transaction = data.get(
        "data",
        {}
    )

    authorization_url = transaction.get(
        "authorization_url"
    )

    returned_reference = transaction.get(
        "reference"
    )

    access_code = transaction.get(
        "access_code"
    )

    if not authorization_url:

        raise RuntimeError(
            "Paystack did not return an authorization URL."
        )

    if returned_reference:

        reference = returned_reference

    # --------------------------------------------------------
    # Save payment BEFORE returning checkout.
    # --------------------------------------------------------

    try:

        save_pending_payment(
            user_email=user_email,
            reference=reference,
            plan=plan,
            amount=amount,
            currency=currency,
        )

    except Exception as e:

        # Payment exists on Paystack, but database save failed.
        # Do not pretend the payment is unavailable.

        print(
            "⚠️ Paystack checkout created, "
            f"but database save failed: {e}"
        )

    return {

        "success":
            True,

        "authorization_url":
            authorization_url,

        "checkout_url":
            authorization_url,

        "access_code":
            access_code,

        "reference":
            reference,

        "plan":
            plan,

        "amount":
            amount,

        "currency":
            currency,
    }


# ============================================================
# GET LOCAL PAYMENT
# ============================================================

def get_payment(reference):

    ensure_payment_columns()

    sql = text(
        """
        SELECT

            reference,
            user_email,
            plan,
            amount,
            currency,
            status,
            provider,
            transaction_id,
            gateway_response,
            channel,
            paid_at,
            created_at

        FROM payments

        WHERE reference =
            :reference

        LIMIT 1
        """
    )

    with engine.connect() as conn:

        row = conn.execute(
            sql,
            {
                "reference":
                    reference
            }
        ).mappings().first()

    if not row:

        return None

    return dict(row)


# ============================================================
# UPDATE PAYMENT
# ============================================================

def update_payment(
    reference,
    status,
    transaction_id=None,
    gateway_response=None,
    channel=None,
    paid_at=None,
):

    ensure_payment_columns()

    sql = text(
        """
        UPDATE payments

        SET

            status =
                :status,

            transaction_id =
                :transaction_id,

            gateway_response =
                :gateway_response,

            channel =
                :channel,

            paid_at =
                :paid_at

        WHERE reference =
            :reference
        """
    )

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "reference":
                    reference,

                "status":
                    status,

                "transaction_id":
                    transaction_id,

                "gateway_response":
                    gateway_response,

                "channel":
                    channel,

                "paid_at":
                    paid_at,
            }
        )


# ============================================================
# ACTIVATE SUBSCRIPTION
# ============================================================

def activate_subscription(
    user_email,
    plan,
    reference,
):

    from subscription import (
        upgrade_subscription
    )

    return upgrade_subscription(
        user_email=user_email,
        plan=plan,
        payment_reference=reference,
    )


# ============================================================
# VERIFY PAYSTACK PAYMENT
# ============================================================

def verify_paystack_payment(
    reference,
    user_email=None,
):

    reference = (
        reference
        .strip()
    )

    if not reference:

        return {
            "success":
                False,

            "message":
                "Payment reference is required.",
        }

    if not paystack_configured():

        return {
            "success":
                False,

            "message":
                "Paystack secret key is not configured.",
        }

    # --------------------------------------------------------
    # Get local payment first.
    # --------------------------------------------------------

    local_payment = get_payment(
        reference
    )

    # --------------------------------------------------------
    # If the payment isn't in our DB, we cannot safely
    # activate it because we don't know which user/plan
    # should receive the subscription.
    # --------------------------------------------------------

    if not local_payment:

        return {
            "success":
                False,

            "message":
                "Payment record was not found in the database.",
        }

    if user_email:

        if (
            local_payment["user_email"]
            != user_email.strip().lower()
        ):

            return {
                "success":
                    False,

                "message":
                    "Payment does not belong to this account.",
            }

    # --------------------------------------------------------
    # Call Paystack verification endpoint.
    # --------------------------------------------------------

    url = (
        PAYSTACK_BASE_URL
        + "/transaction/verify/"
        + reference
    )

    try:

        response = requests.get(
            url,
            headers=paystack_headers(),
            timeout=30,
        )

    except requests.RequestException as e:

        return {
            "success":
                False,

            "message":
                f"Could not connect to Paystack: {e}",
        }

    try:

        data = response.json()

    except Exception:

        return {
            "success":
                False,

            "message":
                "Paystack returned an invalid verification response.",
        }

    if not response.ok or not data.get(
        "status",
        False,
    ):

        return {
            "success":
                False,

            "message":
                data.get(
                    "message",
                    "Paystack verification failed."
                ),
        }

    transaction = data.get(
        "data",
        {}
    )

    transaction_status = transaction.get(
        "status"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Paystack API response status != transaction status.
    #
    # We use transaction["status"].
    # --------------------------------------------------------

    if transaction_status != "success":

        update_payment(
            reference=reference,
            status=transaction_status or "unknown",
            transaction_id=transaction.get(
                "id"
            ),
            gateway_response=transaction.get(
                "gateway_response"
            ),
            channel=transaction.get(
                "channel"
            ),
        )

        return {

            "success":
                False,

            "message":
                "Payment has not been completed.",

            "status":
                transaction_status,

            "reference":
                reference,
        }

    # --------------------------------------------------------
    # Verify amount and currency.
    # --------------------------------------------------------

    expected_amount = int(
        round(
            float(
                local_payment["amount"]
            ) * 100
        )
    )

    actual_amount = int(
        transaction.get(
            "amount",
            0
        )
    )

    actual_currency = (
        transaction.get(
            "currency"
        )
        or ""
    ).upper()

    expected_currency = (
        local_payment["currency"]
        or ""
    ).upper()

    if actual_amount != expected_amount:

        return {
            "success":
                False,

            "message":
                "Payment amount does not match the subscription price.",
        }

    if actual_currency != expected_currency:

        return {
            "success":
                False,

            "message":
                "Payment currency does not match the subscription currency.",
        }

    # --------------------------------------------------------
    # Payment is verified.
    # --------------------------------------------------------

    paid_at = None

    paid_at_value = transaction.get(
        "paid_at"
    )

    if paid_at_value:

        try:

            paid_at = datetime.fromisoformat(
                paid_at_value.replace(
                    "Z",
                    "+00:00"
                )
            )

        except Exception:

            paid_at = None

    update_payment(
        reference=reference,
        status="success",
        transaction_id=transaction.get(
            "id"
        ),
        gateway_response=transaction.get(
            "gateway_response"
        ),
        channel=transaction.get(
            "channel"
        ),
        paid_at=paid_at,
    )

    # --------------------------------------------------------
    # Activate subscription.
    # --------------------------------------------------------

    try:

        activation = activate_subscription(
            user_email=local_payment["user_email"],
            plan=local_payment["plan"],
            reference=reference,
        )

    except Exception as e:

        return {

            "success":
                False,

            "message":
                "Payment was verified, but subscription activation failed.",

            "error":
                str(e),

            "reference":
                reference,
        }

    return {

        "success":
            True,

        "message":
            "Payment verified and subscription activated.",

        "plan":
            local_payment["plan"],

        "amount":
            local_payment["amount"],

        "currency":
            local_payment["currency"],

        "reference":
            reference,

        "transaction_id":
            transaction.get(
                "id"
            ),

        "activation":
            activation,
    }


# ============================================================
# COMMAND LINE TEST
# ============================================================

def main():

    print("=" * 60)
    print("AI BUSINESS ANALYST - PAYSTACK TEST")
    print("=" * 60)

    if not paystack_configured():

        print(
            "\n❌ PAYSTACK_SECRET_KEY not found."
        )

        print(
            "Add your Paystack test secret key to .env:"
        )

        print(
            "PAYSTACK_SECRET_KEY=sk_test_xxxxx"
        )

        return

    print(
        "\n1. Initialize Paystack test payment"
    )

    print(
        "2. Verify completed test payment"
    )

    choice = input(
        "\nChoose (1/2): "
    ).strip()

    create_payments_table()

    # ========================================================
    # INITIALIZE
    # ========================================================

    if choice == "1":

        email = input(
            "\nEnter test customer email: "
        ).strip()

        print(
            "\nAvailable paid plans:"
        )

        print(
            "1. Pro - ₦30,000/month"
        )

        print(
            "2. Business - ₦75,000/month"
        )

        plan_choice = input(
            "\nChoose plan (1/2): "
        ).strip()

        if plan_choice == "1":

            plan = "pro"

        elif plan_choice == "2":

            plan = "business"

        else:

            print(
                "❌ Invalid plan."
            )

            return

        print(
            "\nCreating Paystack test checkout..."
        )

        try:

            result = initialize_paystack_payment(
                user_email=email,
                plan=plan,
            )

            print(
                "\n✅ Checkout created successfully."
            )

            print(
                f"Plan: "
                f"{result['plan'].title()}"
            )

            print(
                f"Amount: "
                f"{result['currency']} "
                f"{result['amount']:,.2f}"
            )

            print(
                f"Reference: "
                f"{result['reference']}"
            )

            print(
                "\nOpen this URL in your browser:"
            )

            print(
                result["authorization_url"]
            )

            print(
                "\nAfter completing the TEST payment,"
            )

            print(
                "run this program again and choose option 2."
            )

            print(
                f"Use reference: "
                f"{result['reference']}"
            )

        except Exception as e:

            print(
                f"\n❌ Checkout creation failed: {e}"
            )

    # ========================================================
    # VERIFY
    # ========================================================

    elif choice == "2":

        reference = input(
            "\nEnter Paystack reference: "
        ).strip()

        print(
            "\nVerifying payment..."
        )

        result = verify_paystack_payment(
            reference
        )

        if result.get(
            "success",
            False,
        ):

            print(
                "\n✅ PAYMENT VERIFIED"
            )

            print(
                f"Plan: "
                f"{result.get('plan', '').title()}"
            )

            print(
                f"Amount: "
                f"{result.get('currency')} "
                f"{result.get('amount', 0):,.2f}"
            )

            print(
                f"Reference: "
                f"{result.get('reference')}"
            )

            print(
                "\n✅ Subscription activated."
            )

        else:

            print(
                "\n❌ PAYMENT NOT ACTIVATED"
            )

            print(
                result.get(
                    "message",
                    "Payment verification failed."
                )
            )

    else:

        print(
            "❌ Invalid choice."
        )


if __name__ == "__main__":
    main()
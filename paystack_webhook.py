# ============================================================
# AI BUSINESS ANALYST
# PAYSTACK WEBHOOK
# ============================================================

import os
import hmac
import hashlib
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from sqlalchemy import text

from database import engine


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Business Analyst Paystack Webhook",
    version="1.0.0"
)


# ============================================================
# PAYSTACK SECRET KEY
# ============================================================

PAYSTACK_SECRET_KEY = os.getenv(
    "PAYSTACK_SECRET_KEY"
)


# ============================================================
# VERIFY PAYSTACK SIGNATURE
# ============================================================

def verify_paystack_signature(
    payload: bytes,
    signature: str
) -> bool:

    if not PAYSTACK_SECRET_KEY:
        return False

    expected_signature = hmac.new(
        PAYSTACK_SECRET_KEY.encode("utf-8"),
        payload,
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():

    return {
        "status": "ok",
        "service": "AI Business Analyst Paystack Webhook"
    }


# ============================================================
# PAYSTACK WEBHOOK
# ============================================================

@app.post("/paystack/webhook")
async def paystack_webhook(
    request: Request
):

    # --------------------------------------------------------
    # READ RAW REQUEST
    # --------------------------------------------------------

    payload = await request.body()

    signature = request.headers.get(
        "x-paystack-signature"
    )

    if not signature:

        raise HTTPException(
            status_code=401,
            detail="Missing Paystack signature."
        )

    # --------------------------------------------------------
    # VERIFY SIGNATURE
    # --------------------------------------------------------

    if not verify_paystack_signature(
        payload,
        signature
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Paystack signature."
        )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        data = await request.json()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload."
        )

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    event = data.get(
        "event"
    )

    event_data = data.get(
        "data",
        {}
    )

    # --------------------------------------------------------
    # ONLY PROCESS SUCCESSFUL PAYMENTS
    # --------------------------------------------------------

    if event != "charge.success":

        return {
            "status": "ignored",
            "event": event
        }

    # --------------------------------------------------------
    # PAYMENT INFORMATION
    # --------------------------------------------------------

    reference = event_data.get(
        "reference"
    )

    status = event_data.get(
        "status"
    )

    amount = event_data.get(
        "amount",
        0
    )

    currency = event_data.get(
        "currency",
        "NGN"
    )

    gateway_response = event_data.get(
        "gateway_response"
    )

    channel = event_data.get(
        "channel"
    )

    transaction_id = event_data.get(
        "id"
    )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer = event_data.get(
        "customer",
        {}
    )

    user_email = customer.get(
        "email"
    )

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not reference:

        raise HTTPException(
            status_code=400,
            detail="Payment reference missing."
        )

    if status != "success":

        return {
            "status": "ignored",
            "payment_status": status
        }

    if not user_email:

        raise HTTPException(
            status_code=400,
            detail="Customer email missing."
        )

    # --------------------------------------------------------
    # FIND PAYMENT
    # --------------------------------------------------------

    try:

        with engine.begin() as conn:

            payment = conn.execute(
                text(
                    """
                    SELECT
                        reference,
                        user_email,
                        plan,
                        amount,
                        currency,
                        status
                    FROM payments
                    WHERE reference = :reference
                    LIMIT 1
                    """
                ),
                {
                    "reference": reference
                }
            ).fetchone()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {e}"
        )

    # --------------------------------------------------------
    # PAYMENT NOT FOUND
    # --------------------------------------------------------

    if payment is None:

        raise HTTPException(
            status_code=404,
            detail="Payment record not found."
        )

    plan = payment.plan

    # --------------------------------------------------------
    # UPDATE PAYMENT
    # --------------------------------------------------------

    try:

        with engine.begin() as conn:

            conn.execute(
                text(
                    """
                    UPDATE payments

                    SET
                        status = 'success',
                        transaction_id = :transaction_id,
                        gateway_response = :gateway_response,
                        channel = :channel,
                        paid_at = CURRENT_TIMESTAMP

                    WHERE reference = :reference
                    """
                ),
                {
                    "reference": reference,
                    "transaction_id": str(transaction_id)
                    if transaction_id
                    else None,
                    "gateway_response":
                        gateway_response,
                    "channel": channel
                }
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not update payment: {e}"
        )

    # --------------------------------------------------------
    # ACTIVATE SUBSCRIPTION
    # --------------------------------------------------------

    try:

        from subscription import activate_subscription

        activate_subscription(
            user_email=user_email,
            plan=plan,
            payment_reference=reference
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not activate subscription: {e}"
        )

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    print(
        "============================================================"
    )

    print(
        "✅ PAYSTACK PAYMENT VERIFIED"
    )

    print(
        f"User: {user_email}"
    )

    print(
        f"Plan: {plan}"
    )

    print(
        f"Reference: {reference}"
    )

    print(
        f"Amount: {currency} {amount / 100:,.2f}"
    )

    print(
        "✅ SUBSCRIPTION ACTIVATED"
    )

    print(
        "============================================================"
    )

    return {
        "status": "success",
        "message": "Payment processed successfully.",
        "reference": reference,
        "plan": plan,
        "user_email": user_email
    }
# ============================================================
# AI BUSINESS ANALYST - AUTHENTICATION
# ============================================================

import uuid
import bcrypt

from sqlalchemy import text

from database import engine
from email_service import send_verification_email


# ============================================================
# CREATE USERS TABLE
# ============================================================

def create_users_table():

    query = text(
        """
        CREATE TABLE IF NOT EXISTS users (

            id SERIAL PRIMARY KEY,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            verified BOOLEAN DEFAULT FALSE,

            verification_token TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
        """
    )

    with engine.begin() as conn:

        conn.execute(query)

    print("✅ Users table ready.")


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_password(password):

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


# ============================================================
# CHECK PASSWORD
# ============================================================

def check_password(
    password,
    hashed_password
):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# ============================================================
# REGISTER USER
# ============================================================

def register_user(
    email,
    password
):

    email = email.strip().lower()

    if not email:
        return {
            "success": False,
            "error": "Email is required."
        }

    if not password:
        return {
            "success": False,
            "error": "Password is required."
        }

    if len(password) < 8:
        return {
            "success": False,
            "error": "Password must be at least 8 characters."
        }

    create_users_table()

    token = str(
        uuid.uuid4()
    )

    hashed_password = hash_password(
        password
    )

    query = text(
        """
        INSERT INTO users
        (
            email,
            password,
            verification_token
        )
        VALUES
        (
            :email,
            :password,
            :token
        )
        """
    )

    try:

        with engine.begin() as conn:

            conn.execute(
                query,
                {
                    "email": email,
                    "password": hashed_password,
                    "token": token
                }
            )

    except Exception as e:

        error_text = str(e).lower()

        if "duplicate" in error_text:
            return {
                "success": False,
                "error": "An account with this email already exists."
            }

        return {
            "success": False,
            "error": "Registration failed."
        }

    # --------------------------------------------------------
    # SEND VERIFICATION EMAIL
    # --------------------------------------------------------

    try:

        send_verification_email(
            email,
            token
        )

    except Exception as e:

        print(
            f"⚠️ Verification email failed: {e}"
        )

        return {
            "success": True,
            "email": email,
            "verification_sent": False,
            "message": (
                "Account created, but the verification email "
                "could not be sent."
            )
        }

    return {
        "success": True,
        "email": email,
        "verification_sent": True,
        "message": (
            "Account created. "
            "Please check your email to verify your account."
        )
    }


# ============================================================
# VERIFY EMAIL
# ============================================================

def verify_email(token):

    if not token:
        return False

    query = text(
        """
        UPDATE users

        SET
            verified = TRUE,
            verification_token = NULL

        WHERE verification_token = :token
        """
    )

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {
                "token": token
            }
        )

    return result.rowcount > 0


# ============================================================
# GET USER
# ============================================================

def get_user_by_email(email):

    if not email:
        return None

    email = email.strip().lower()

    query = text(
        """
        SELECT
            id,
            email,
            password,
            verified,
            created_at

        FROM users

        WHERE email = :email

        LIMIT 1
        """
    )

    with engine.connect() as conn:

        return conn.execute(
            query,
            {
                "email": email
            }
        ).fetchone()


# ============================================================
# LOGIN USER
# ============================================================

def login_user(
    email,
    password
):

    email = email.strip().lower()

    user = get_user_by_email(
        email
    )

    if user is None:

        return {
            "success": False,
            "error": "Invalid email or password."
        }

    # --------------------------------------------------------
    # CHECK VERIFICATION
    # --------------------------------------------------------

    if not user.verified:

        return {
            "success": False,
            "error": "NOT_VERIFIED"
        }

    # --------------------------------------------------------
    # CHECK PASSWORD
    # --------------------------------------------------------

    try:

        password_valid = check_password(
            password,
            user.password
        )

    except Exception:

        password_valid = False

    if not password_valid:

        return {
            "success": False,
            "error": "Invalid email or password."
        }

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {
        "success": True,
        "user_id": user.id,
        "email": user.email,
        "verified": user.verified
    }


# ============================================================
# DELETE USER
# ============================================================

def delete_user(email):

    email = email.strip().lower()

    query = text(
        """
        DELETE FROM users
        WHERE email = :email
        """
    )

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {
                "email": email
            }
        )

    return result.rowcount > 0


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI BUSINESS ANALYST - AUTHENTICATION")
    print("=" * 60)

    create_users_table()

    print()
    print("✅ Authentication module loaded successfully.")
    print()
    print("Available functions:")
    print("• create_users_table()")
    print("• hash_password()")
    print("• check_password()")
    print("• register_user()")
    print("• verify_email()")
    print("• get_user_by_email()")
    print("• login_user()")
    print("• delete_user()")
import os
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")



def send_verification_email(email, token):


    verification_link = (
        f"http://localhost:8501/?verify={token}"
    )


    message = f"""
Welcome to AI Business Analyst.


Please verify your account by clicking the link below:


{verification_link}


If you did not create this account, ignore this email.

"""


    msg = MIMEText(
        message
    )


    msg["Subject"] = (
        "Verify your AI Business Analyst account"
    )

    msg["From"] = EMAIL_ADDRESS

    msg["To"] = email



    try:


        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as server:


            server.login(

                EMAIL_ADDRESS,

                EMAIL_PASSWORD

            )


            server.send_message(
                msg
            )


        print(
            "Verification email sent successfully"
        )


        return True



    except Exception as e:


        print(
            "Email sending failed:"
        )


        print(
            e
        )


        return False
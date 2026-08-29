import streamlit as st

from email_service import send_verification_email

from auth import (
    register_user,
    login_user
)


def login_screen():

    st.title("🔐 AI Business Analyst")


    menu = st.radio(
        "Select",
        [
            "Login",
            "Register"
        ]
    )


    email = st.text_input(
        "Email"
    )


    password = st.text_input(
        "Password",
        type="password"
    )


    # ---------------------------------------
    # Register
    # ---------------------------------------

    if menu == "Register":


        if st.button(
            "Create Account",
            key="register_button"
        ):


            try:

                token = register_user(
                    email,
                    password
                )


                send_verification_email(
                    email,
                    token
                )


                st.success(
                    "Account created successfully."
                )


                st.info(
                    "A verification link has been sent to your email. Please verify before login."
                )


            except Exception as e:

                st.error(
                    "Email already exists."
                )

                st.write(e)



    # ---------------------------------------
    # Login
    # ---------------------------------------

    else:


        if st.button(
            "Login",
            key="login_button"
        ):


            user = login_user(
                email,
                password
            )


            if user is None:


                st.error(
                    "Invalid email or password."
                )


            elif user == "NOT_VERIFIED":


                st.warning(
                    "Please verify your email before logging in."
                )


            else:


                st.session_state.logged_in = True


                st.session_state.user = user.email


                st.success(
                    "Login successful."
                )


                st.rerun()
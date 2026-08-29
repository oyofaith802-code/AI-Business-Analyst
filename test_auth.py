from auth import (
    create_users_table,
    register_user,
    login_user
)

create_users_table()

register_user(
    "jeremiah2",
    "MyStrongPassword123!"
)

user = login_user(
    "jeremiah2",
    "MyStrongPassword123!"
)

print(user)
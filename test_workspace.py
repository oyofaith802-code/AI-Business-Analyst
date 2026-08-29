from workspace import (
    create_workspace_table,
    save_workspace,
    get_user_tables
)

create_workspace_table()

save_workspace(
    "test@gmail.com",
    "sales.csv",
    "sales_dataset"
)

print(get_user_tables("test@gmail.com"))
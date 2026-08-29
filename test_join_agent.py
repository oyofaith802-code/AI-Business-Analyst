import pandas as pd

from join_agent import build_join_context


dataframes = {

    "orders": pd.read_csv("olist_orders_dataset.csv"),

    "customers": pd.read_csv("olist_customers_dataset.csv"),

    "payments": pd.read_csv("olist_order_payments_dataset.csv")

}


print(
    build_join_context(dataframes)
)
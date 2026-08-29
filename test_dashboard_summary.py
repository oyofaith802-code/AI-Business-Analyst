import pandas as pd

from dashboard_summary import generate_dashboard

df = pd.read_csv("olist_orders_dataset.csv")

print(generate_dashboard(df))
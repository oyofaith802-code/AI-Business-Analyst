import pandas as pd

from data_profiler import profile_dataset


df = pd.read_csv(
    "olist_orders_dataset.csv"
)


profile = profile_dataset(df)


print(profile)
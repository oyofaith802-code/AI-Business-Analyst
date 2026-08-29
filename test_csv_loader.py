from csv_loader import load_csv_to_database

file = r"C:\Users\USER\Desktop\business_ai\olist_orders_dataset.csv"

table, df = load_csv_to_database(file, "test@example.com")

print("Created table:", table)
print("\nFirst 5 rows:")
print(df.head())
print("\nShape:")
print(df.shape)

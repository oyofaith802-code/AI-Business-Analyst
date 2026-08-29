from csv_loader import load_csv_to_database


# Put the real location of your CSV file here
file = r"C:\Users\USER\Desktop\business_ai\olist_orders_dataset.csv"


# Load CSV into PostgreSQL
table, df = load_csv_to_database(file)


print("Created table:", table)

print("\nFirst 5 rows:")
print(df.head())

print("\nShape:")
print(df.shape)
from data_preview import get_table_preview


table = "olist_orders_dataset"


preview = get_table_preview(table)


print("Sample Data:")
print(preview)
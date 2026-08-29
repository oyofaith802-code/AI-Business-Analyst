from database import run_query


schema = run_query("""
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema='public'
ORDER BY table_name;
""")


for row in schema:
    print(row)
from database import run_query


result = run_query("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public';
""")


print("Tables:")
for table in result:
    print(table)
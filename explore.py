import pandas as pd
from database import engine


queries = {

"Customers":
"""
SELECT COUNT(*) AS total_customers
FROM customers;
""",

"Products":
"""
SELECT COUNT(*) AS total_products
FROM products;
""",

"Payments":
"""
SELECT COUNT(*) AS total_payments
FROM payments;
""",

"Average Payment":
"""
SELECT AVG(payment_value) AS average_payment
FROM payments;
""",

"Highest Payments":
"""
SELECT payment_value
FROM payments
ORDER BY payment_value DESC
LIMIT 10;
"""

}


for name, query in queries.items():

    print("\n====================")
    print(name)
    print("====================")

    result = pd.read_sql(
        query,
        engine
    )

    print(result)
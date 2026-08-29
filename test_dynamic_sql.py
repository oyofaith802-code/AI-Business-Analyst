from sql_agent import generate_sql


def test_generate_sql():
    sql = generate_sql(
        question="How many orders were delivered?",
        tables=["olist_orders_dataset"],
        user_email="solomonenamudu@gmail.com"
    )

    assert isinstance(sql, str)
    assert sql.strip()
    assert sql.strip().upper().startswith(("SELECT", "WITH"))
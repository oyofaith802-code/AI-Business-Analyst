from database import run_query


def get_dashboard_metrics(table):

    metrics = {}

    try:
        metrics["Rows"] = run_query(
            f"SELECT COUNT(*) FROM {table};"
        )[0][0]
    except:
        metrics["Rows"] = "N/A"

    return metrics
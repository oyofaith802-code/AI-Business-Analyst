import pandas as pd


def choose_chart(result):

    if not result:
        return "none"

    df = pd.DataFrame(result)

    if df.shape[1] < 2:
        return "none"

    first = str(df.columns[0]).lower()

    second = str(df.columns[1]).lower()

    time_words = [
        "date",
        "day",
        "week",
        "month",
        "year",
        "time"
    ]

    money_words = [
        "sales",
        "revenue",
        "price",
        "amount",
        "profit"
    ]

    if any(word in first for word in time_words):
        return "line"

    if any(word in second for word in money_words):
        return "bar"

    if len(df) <= 8:
        return "pie"

    return "bar"
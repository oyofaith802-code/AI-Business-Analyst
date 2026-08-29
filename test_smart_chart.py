from smart_chart_agent import choose_chart


result = [
    {
        "month": "January",
        "sales": 100
    },
    {
        "month": "February",
        "sales": 150
    }
]


chart = choose_chart(result)

print(chart)
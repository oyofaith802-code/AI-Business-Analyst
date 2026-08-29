from datetime import datetime


def generate_report(
    dataset_name,
    metrics,
    insights,
    question_history=None
):

    report = f"""
# AI Business Analysis Report


## Dataset

{dataset_name}


## Generated Date

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}



## Dataset Summary

Total Rows:

{metrics.get("Rows", "N/A")}



## AI Business Insights

{insights}



## Recent Business Questions

"""


    if question_history:

        for item in question_history:

            report += f"""

Question:
{item[0]}


Answer:
{item[1]}


"""

    else:

        report += """

No previous questions available.

"""


    report += """

## Recommendations

Based on the dataset analysis:

- Monitor important business trends.
- Identify areas with strong performance.
- Investigate areas needing improvement.
- Use data-driven decisions.


"""


    return report
import json
import pandas as pd

from llm import client, OLLAMA_MODEL


# ============================================================
# AI NATURAL LANGUAGE BUSINESS DATA PARSER
# ============================================================

def parse_business_text(text):

    if not text or not text.strip():
        raise ValueError(
            "Please enter some business information."
        )

    prompt = f"""
You are Aloko, an AI Business Assistant.

Convert the user's business information into structured
business records.

USER INPUT:
{text}

Extract only information explicitly provided.

Possible fields include:
product, item, quantity, price, sales, revenue,
expense, customer, date, category, payment_method,
profit, cost.

Rules:

1. Do not invent information.
2. If a value is unknown, use null.
3. Preserve numerical values accurately.
4. Create one row for each business record.
5. Use clear column names.
6. Return a JSON object with exactly two keys:
   "columns" and "rows".

Example:

{{
  "columns": ["product", "quantity", "price"],
  "rows": [
    {{
      "product": "Rice",
      "quantity": 20,
      "price": 45000
    }}
  ]
}}
"""

    try:

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

    except Exception as e:

        raise RuntimeError(
            f"Aloko AI request failed: {e}"
        )

    content = response["message"]["content"].strip()

    if not content:

        raise ValueError(
            "Aloko did not return any structured data."
        )

    # --------------------------------------------------------
    # PARSE JSON
    # --------------------------------------------------------

    try:

        data = json.loads(content)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Aloko returned invalid structured data: {e}"
        )

    # --------------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------------

    if not isinstance(data, dict):

        raise ValueError(
            "Invalid AI response format."
        )

    columns = data.get("columns")
    rows = data.get("rows")

    if not isinstance(columns, list) or not columns:

        raise ValueError(
            "No business columns were detected."
        )

    if not isinstance(rows, list) or not rows:

        raise ValueError(
            "No business records were detected."
        )

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    dataframe = pd.DataFrame(
        rows,
        columns=columns
    )

    # --------------------------------------------------------
    # REMOVE COMPLETELY EMPTY ROWS
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        how="all"
    )

    if dataframe.empty:

        raise ValueError(
            "No usable business records were detected."
        )

    user_text_lower = text.lower()

    revenue_terms = [
        "revenue",
        "revenues",
        "income",
        "total income"
    ]

    revenue_was_explicitly_provided = any(
        term in user_text_lower
        for term in revenue_terms
    )

    if (
        "revenue" in dataframe.columns
        and not revenue_was_explicitly_provided
    ):
        dataframe = dataframe.drop(
            columns=["revenue"]
        )

    return dataframe
# business_intent.py

import re


# ============================================================
# BUSINESS INTENT DEFINITIONS
# ============================================================

INTENTS = {

    "TOTAL_REVENUE": [
        "total revenue",
        "revenue",
        "total sales",
        "sales revenue",
        "income",
        "total income",
        "gross revenue",
        "how much did i make",
        "how much have i made",
        "money made",
        "sales amount"
    ],

    "AVERAGE_ORDER_VALUE": [
        "average order value",
        "average order",
        "aov",
        "average amount per order",
        "average sales per order",
        "average revenue per order"
    ],

    "TOTAL_ORDERS": [
        "how many orders",
        "number of orders",
        "total orders",
        "orders do i have",
        "orders did i receive",
        "orders received",
        "order count"
    ],

    "TOTAL_CUSTOMERS": [
        "how many customers",
        "number of customers",
        "total customers",
        "customers do i have",
        "customer count",
        "unique customers"
    ],

    "CUSTOMERS_WITH_ORDERS": [
        "customers placed orders",
        "customers who placed orders",
        "customers that placed orders",
        "customers with orders",
        "customers who ordered",
        "customers that ordered"
    ],

    "TOP_PRODUCTS": [
        "top products",
        "best products",
        "best selling products",
        "top selling products",
        "products by sales",
        "products by revenue",
        "highest selling products",
        "best performing products"
    ],

    "TOP_CUSTOMERS": [
        "top customers",
        "best customers",
        "customers by revenue",
        "customers by sales",
        "highest spending customers",
        "biggest customers"
    ],

    "MONTHLY_REVENUE": [
        "monthly revenue",
        "revenue by month",
        "sales by month",
        "monthly sales",
        "revenue each month",
        "sales each month"
    ],

    "MONTHLY_ORDERS": [
        "monthly orders",
        "orders by month",
        "orders each month",
        "orders per month"
    ],

    "DAILY_REVENUE": [
        "daily revenue",
        "revenue by day",
        "sales by day",
        "daily sales"
    ],

    "YEARLY_REVENUE": [
        "yearly revenue",
        "annual revenue",
        "revenue by year",
        "sales by year",
        "yearly sales"
    ],

    "ORDER_STATUS": [
        "order status",
        "orders by status",
        "status of orders",
        "order statuses",
        "how many delivered",
        "how many cancelled",
        "how many canceled"
    ],

    "PAYMENT_METHODS": [
        "payment methods",
        "payment types",
        "how do customers pay",
        "popular payment method",
        "most popular payment",
        "payments by type"
    ],

    "CUSTOMERS_BY_LOCATION": [
        "customers by state",
        "customers by city",
        "customers by country",
        "customers by location",
        "customers location",
        "where are my customers",
        "customer distribution"
    ],

    "PRODUCT_CATEGORIES": [
        "product categories",
        "categories by sales",
        "sales by category",
        "revenue by category",
        "top categories",
        "best categories"
    ],

    "REVIEW_SCORE": [
        "average review",
        "average rating",
        "review score",
        "customer rating",
        "customer reviews",
        "ratings"
    ]
}


# ============================================================
# NORMALIZE QUESTION
# ============================================================

def normalize_question(question):
    """
    Normalize the user's question so intent matching
    is more reliable.
    """

    if not question:
        return ""

    question = str(question).lower().strip()

    # Remove punctuation
    question = re.sub(r"[^a-z0-9\s]", " ", question)

    # Normalize spaces
    question = re.sub(r"\s+", " ", question)

    return question


# ============================================================
# EXTRACT LIMIT
# ============================================================

def extract_limit(question, default=10):
    """
    Extract numbers such as:

    top 5
    top 10
    first 20
    best 3
    """

    question = normalize_question(question)

    patterns = [
        r"\btop\s+(\d+)",
        r"\bfirst\s+(\d+)",
        r"\bbest\s+(\d+)",
        r"\b(\d+)\s+best",
        r"\b(\d+)\s+top"
    ]

    for pattern in patterns:

        match = re.search(pattern, question)

        if match:

            try:
                value = int(match.group(1))

                if value > 0:
                    return min(value, 100)

            except Exception:
                pass

    return default


# ============================================================
# DETECT TIME GRAIN
# ============================================================

def detect_time_grain(question):
    """
    Detect whether the user wants daily, weekly,
    monthly, quarterly or yearly analysis.
    """

    question = normalize_question(question)

    if any(
        phrase in question
        for phrase in [
            "daily",
            "by day",
            "each day",
            "per day"
        ]
    ):
        return "day"

    if any(
        phrase in question
        for phrase in [
            "weekly",
            "by week",
            "each week",
            "per week"
        ]
    ):
        return "week"

    if any(
        phrase in question
        for phrase in [
            "monthly",
            "by month",
            "each month",
            "per month"
        ]
    ):
        return "month"

    if any(
        phrase in question
        for phrase in [
            "quarterly",
            "by quarter",
            "each quarter",
            "per quarter"
        ]
    ):
        return "quarter"

    if any(
        phrase in question
        for phrase in [
            "yearly",
            "annual",
            "by year",
            "each year",
            "per year"
        ]
    ):
        return "year"

    return None


# ============================================================
# SCORE INTENT
# ============================================================

def score_intent(question, phrases):
    """
    Score an intent based on matching phrases.
    """

    score = 0

    for phrase in phrases:

        if phrase in question:

            # Longer phrases are more specific,
            # therefore they receive more weight.
            score += len(phrase.split()) * 2

    return score


# ============================================================
# DETECT BUSINESS INTENT
# ============================================================

def detect_intent(question):
    """
    Detect the main business intent.
    """

    normalized = normalize_question(question)

    if not normalized:
        return {
            "intent": "UNKNOWN",
            "confidence": 0,
            "limit": None,
            "time_grain": None
        }

    scores = {}

    for intent, phrases in INTENTS.items():

        scores[intent] = score_intent(
            normalized,
            phrases
        )

    best_intent = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_intent]

    # No meaningful match
    if best_score == 0:

        return {
            "intent": "UNKNOWN",
            "confidence": 0,
            "limit": extract_limit(normalized),
            "time_grain": detect_time_grain(normalized)
        }

    # Convert score into a simple confidence score
    confidence = min(
        round(best_score / 10, 2),
        1.0
    )

    return {
        "intent": best_intent,
        "confidence": confidence,
        "limit": extract_limit(normalized),
        "time_grain": detect_time_grain(normalized)
    }


# ============================================================
# GET INTENT INSTRUCTIONS
# ============================================================

def get_intent_instructions(intent):
    """
    Give SQL agent specific instructions based on
    detected business intent.
    """

    instructions = {

        "TOTAL_REVENUE": """
The user wants TOTAL REVENUE.

Use SUM() on the detected revenue/payment/sales
measure.

Do NOT divide by number of orders.

Example:

SELECT SUM("payment_value") AS total_revenue
FROM "payments"
""",

        "AVERAGE_ORDER_VALUE": """
The user wants AVERAGE ORDER VALUE.

Calculate:

total revenue / distinct orders

Use NULLIF to prevent division by zero.

Example:

SUM("payment_value")
/
NULLIF(COUNT(DISTINCT "order_id"), 0)
""",

        "TOTAL_ORDERS": """
The user wants the number of orders.

Prefer COUNT(DISTINCT order identifier)
when an order identifier exists.
""",

        "TOTAL_CUSTOMERS": """
The user wants the number of customers.

Use COUNT(DISTINCT customer identifier).
""",

        "CUSTOMERS_WITH_ORDERS": """
The user wants customers who actually placed orders.

Use the appropriate customer/order relationship.

Prefer COUNT(DISTINCT customer_id).
""",

        "TOP_PRODUCTS": """
The user wants products ranked by sales/revenue.

Find the product identifier or product name and
the appropriate numeric sales/revenue measure.

GROUP BY the product.

ORDER BY the sales measure DESC.

Apply the requested LIMIT.
""",

        "TOP_CUSTOMERS": """
The user wants customers ranked by spending/revenue.

Find the customer identifier and appropriate
revenue/payment measure.

GROUP BY customer.

ORDER BY revenue DESC.

Apply the requested LIMIT.
""",

        "MONTHLY_REVENUE": """
The user wants revenue grouped by month.

Use:

DATE_TRUNC('month', date_column)

GROUP BY the month expression.

ORDER BY month.
""",

        "MONTHLY_ORDERS": """
The user wants orders grouped by month.

Use:

DATE_TRUNC('month', order/date column)

COUNT(DISTINCT order_id)

GROUP BY month.

ORDER BY month.
""",

        "DAILY_REVENUE": """
The user wants revenue grouped by day.

Use:

DATE_TRUNC('day', date_column)

GROUP BY day.

ORDER BY day.
""",

        "YEARLY_REVENUE": """
The user wants revenue grouped by year.

Use:

DATE_TRUNC('year', date_column)

GROUP BY year.

ORDER BY year.
""",

        "ORDER_STATUS": """
The user wants order counts grouped by status.

GROUP BY the detected order status/category column.
""",

        "PAYMENT_METHODS": """
The user wants payment methods/types.

GROUP BY the detected payment type/category column
and count orders or payments appropriately.
""",

        "CUSTOMERS_BY_LOCATION": """
The user wants customer distribution by location.

Find an appropriate location field such as
city, state, country or region.

GROUP BY that field and count customers.
""",

        "PRODUCT_CATEGORIES": """
The user wants product category performance.

Find the category column and appropriate
sales/revenue measure.

GROUP BY category.
""",

        "REVIEW_SCORE": """
The user wants customer review/rating information.

Use the review score/rating field if available.
"""
    }

    return instructions.get(
        intent,
        """
Determine the correct business calculation from
the available schema and business metadata.
"""
    )


# ============================================================
# ANALYZE QUESTION
# ============================================================

def analyze_question(question):
    """
    Return complete business intent information.
    """

    detected = detect_intent(question)

    intent = detected["intent"]

    return {
        **detected,
        "instructions": get_intent_instructions(intent)
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    questions = [
        "What is my total revenue?",
        "What is my average order value?",
        "How many orders do I have?",
        "How many customers do I have?",
        "How many customers placed orders?",
        "What are my top 5 products by sales?",
        "Show me my monthly revenue",
        "Show me my monthly orders",
        "Which payment method is most popular?",
        "Which state has the most customers?"
    ]

    for question in questions:

        print("\n" + "=" * 70)
        print(question)
        print("=" * 70)

        print(analyze_question(question))
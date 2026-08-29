from database import engine
from sqlalchemy import text


# ============================================================
# AI BUSINESS ANALYST
# ADVANCED BUSINESS INSIGHTS ENGINE
# ============================================================


def run_query(query, params=None):
    """
    Execute SQL query and return results.
    """

    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            params or {}
        )

        return result.fetchall()


# ============================================================
# TOTAL PRODUCT SALES
# ============================================================

def get_total_sales():

    query = """
        SELECT
            COALESCE(SUM(price), 0)
        FROM order_items
    """

    result = run_query(query)

    return float(result[0][0] or 0)


# ============================================================
# TOTAL PAYMENT REVENUE
# ============================================================

def get_total_payment_value():

    query = """
        SELECT
            COALESCE(SUM(payment_value), 0)
        FROM payments
    """

    result = run_query(query)

    return float(result[0][0] or 0)


# ============================================================
# TOTAL ORDERS
# ============================================================

def get_total_orders():

    query = """
        SELECT
            COUNT(DISTINCT order_id)
        FROM orders
    """

    result = run_query(query)

    return int(result[0][0] or 0)


# ============================================================
# TOTAL CUSTOMERS
# ============================================================

def get_total_customers():

    query = """
        SELECT
            COUNT(DISTINCT customer_id)
        FROM orders
        WHERE customer_id IS NOT NULL
    """

    result = run_query(query)

    return int(result[0][0] or 0)


# ============================================================
# TOTAL PRODUCTS
# ============================================================

def get_total_products():

    query = """
        SELECT
            COUNT(DISTINCT product_id)
        FROM products
    """

    result = run_query(query)

    return int(result[0][0] or 0)


# ============================================================
# AVERAGE ORDER VALUE
# ============================================================

def get_average_order_value():

    query = """
        SELECT
            COALESCE(
                SUM(price) /
                NULLIF(COUNT(DISTINCT order_id), 0),
                0
            )
        FROM order_items
    """

    result = run_query(query)

    return float(result[0][0] or 0)


# ============================================================
# AVERAGE PAYMENT PER ORDER
# ============================================================

def get_average_payment_per_order():

    query = """
        SELECT
            COALESCE(
                SUM(payment_value) /
                NULLIF(COUNT(DISTINCT order_id), 0),
                0
            )
        FROM payments
    """

    result = run_query(query)

    return float(result[0][0] or 0)


# ============================================================
# TOP PRODUCTS
# ============================================================

def get_top_products(limit=10):

    query = """
        SELECT
            oi.product_id,

            COALESCE(
                p.product_category_name,
                'Unknown'
            ) AS category,

            SUM(oi.price) AS total_sales,

            COUNT(*) AS items_sold

        FROM order_items oi

        LEFT JOIN products p
            ON oi.product_id = p.product_id

        GROUP BY
            oi.product_id,
            p.product_category_name

        ORDER BY
            total_sales DESC

        LIMIT :limit
    """

    result = run_query(
        query,
        {
            "limit": limit
        }
    )

    return [
        {
            "product_id": row[0],
            "category": row[1],
            "total_sales": float(row[2] or 0),
            "items_sold": int(row[3] or 0)
        }

        for row in result
    ]


# ============================================================
# TOP CATEGORIES
# ============================================================

def get_top_categories(limit=10):

    query = """
        SELECT

            COALESCE(
                p.product_category_name,
                'Unknown'
            ) AS category,

            SUM(oi.price) AS total_sales,

            COUNT(*) AS items_sold

        FROM order_items oi

        LEFT JOIN products p
            ON oi.product_id = p.product_id

        GROUP BY
            p.product_category_name

        ORDER BY
            total_sales DESC

        LIMIT :limit
    """

    result = run_query(
        query,
        {
            "limit": limit
        }
    )

    return [
        {
            "category": row[0],
            "total_sales": float(row[1] or 0),
            "items_sold": int(row[2] or 0)
        }

        for row in result
    ]


# ============================================================
# AVERAGE REVIEW SCORE
# ============================================================

def get_average_review_score():

    query = """
        SELECT
            COALESCE(
                AVG(review_score),
                0
            )

        FROM reviews

        WHERE review_score IS NOT NULL
    """

    result = run_query(query)

    return float(result[0][0] or 0)


# ============================================================
# REVIEW DISTRIBUTION
# ============================================================

def get_review_distribution():

    query = """
        SELECT
            review_score,
            COUNT(*) AS review_count

        FROM reviews

        WHERE review_score IS NOT NULL

        GROUP BY review_score

        ORDER BY review_score
    """

    result = run_query(query)

    return [
        {
            "score": int(row[0]),
            "count": int(row[1])
        }

        for row in result
    ]


# ============================================================
# ORDER STATUS
# ============================================================

def get_order_status_breakdown():

    query = """
        SELECT

            order_status,

            COUNT(*) AS order_count

        FROM orders

        GROUP BY order_status

        ORDER BY order_count DESC
    """

    result = run_query(query)

    total = sum(
        int(row[1])
        for row in result
    )

    return [
        {
            "status": row[0],

            "count": int(row[1]),

            "percentage": (
                float(row[1]) / total * 100
                if total
                else 0
            )
        }

        for row in result
    ]


# ============================================================
# MONTHLY SALES
# ============================================================

def get_monthly_sales():

    query = """
        SELECT

            DATE_TRUNC(
                'month',
                CAST(
                    o.order_purchase_timestamp
                    AS TIMESTAMP
                )
            ) AS month,

            SUM(oi.price) AS total_sales

        FROM order_items oi

        JOIN orders o

            ON oi.order_id = o.order_id

        WHERE
            o.order_purchase_timestamp IS NOT NULL

        GROUP BY month

        ORDER BY month
    """

    result = run_query(query)

    return [
        {
            "month": str(row[0]),
            "total_sales": float(row[1] or 0)
        }

        for row in result
    ]


# ============================================================
# MONTHLY ORDERS
# ============================================================

def get_monthly_orders():

    query = """
        SELECT

            DATE_TRUNC(
                'month',
                CAST(
                    order_purchase_timestamp
                    AS TIMESTAMP
                )
            ) AS month,

            COUNT(DISTINCT order_id) AS order_count

        FROM orders

        WHERE
            order_purchase_timestamp IS NOT NULL

        GROUP BY month

        ORDER BY month
    """

    result = run_query(query)

    return [
        {
            "month": str(row[0]),
            "orders": int(row[1])
        }

        for row in result
    ]


# ============================================================
# TOP SELLING SELLERS
# ============================================================

def get_top_sellers(limit=10):

    query = """
        SELECT

            seller_id,

            SUM(price) AS total_sales,

            COUNT(*) AS items_sold

        FROM order_items

        GROUP BY seller_id

        ORDER BY total_sales DESC

        LIMIT :limit
    """

    result = run_query(
        query,
        {
            "limit": limit
        }
    )

    return [
        {
            "seller_id": row[0],
            "total_sales": float(row[1] or 0),
            "items_sold": int(row[2] or 0)
        }

        for row in result
    ]


# ============================================================
# DELIVERY PERFORMANCE
# ============================================================

def get_delivery_performance():

    query = """
        SELECT

            COUNT(*) FILTER (
                WHERE
                    order_delivered_customer_date IS NOT NULL
            ) AS delivered,

            COUNT(*) FILTER (
                WHERE
                    order_delivered_customer_date IS NULL
                    AND order_status NOT IN (
                        'canceled',
                        'unavailable'
                    )
            ) AS pending

        FROM orders
    """

    result = run_query(query)

    return {
        "delivered": int(result[0][0] or 0),
        "pending": int(result[0][1] or 0)
    }


# ============================================================
# GENERATE BUSINESS RECOMMENDATIONS
# ============================================================

def generate_recommendations(insights):

    recommendations = []


    # --------------------------------------------------------
    # REVIEW SCORE
    # --------------------------------------------------------

    review_score = insights[
        "average_review_score"
    ]

    if review_score >= 4.5:

        recommendations.append(
            "Customer satisfaction is excellent. "
            "Maintain current service quality."
        )

    elif review_score >= 4.0:

        recommendations.append(
            "Customer satisfaction is good, "
            "but there is room to improve toward "
            "a 4.5+ average rating."
        )

    else:

        recommendations.append(
            "Customer satisfaction requires attention. "
            "Investigate negative reviews and service issues."
        )


    # --------------------------------------------------------
    # CANCELED ORDERS
    # --------------------------------------------------------

    for status in insights[
        "order_status"
    ]:

        if status["status"] == "canceled":

            percentage = status[
                "percentage"
            ]

            if percentage > 2:

                recommendations.append(
                    f"Canceled orders represent "
                    f"{percentage:.1f}% of orders. "
                    "Investigate the main causes of cancellations."
                )


    # --------------------------------------------------------
    # TOP CATEGORY
    # --------------------------------------------------------

    categories = insights[
        "top_categories"
    ]

    if categories:

        top_category = categories[0]

        recommendations.append(
            f"{top_category['category']} is the "
            "highest-revenue category. "
            "Consider increasing inventory and "
            "marketing investment in this category."
        )


    # --------------------------------------------------------
    # TOP PRODUCT
    # --------------------------------------------------------

    products = insights[
        "top_products"
    ]

    if products:

        top_product = products[0]

        recommendations.append(
            f"Product {top_product['product_id']} "
            "is the highest-revenue product. "
            "Consider ensuring strong availability "
            "and monitoring its performance."
        )


    return recommendations


# ============================================================
# GENERATE EVERYTHING
# ============================================================

def generate_insights():

    insights = {}


    # --------------------------------------------------------
    # CORE METRICS
    # --------------------------------------------------------

    insights["total_sales"] = (
        get_total_sales()
    )

    insights["total_payment_value"] = (
        get_total_payment_value()
    )

    insights["total_orders"] = (
        get_total_orders()
    )

    insights["total_customers"] = (
        get_total_customers()
    )

    insights["total_products"] = (
        get_total_products()
    )

    insights["average_order_value"] = (
        get_average_order_value()
    )

    insights["average_payment_per_order"] = (
        get_average_payment_per_order()
    )


    # --------------------------------------------------------
    # PRODUCT ANALYSIS
    # --------------------------------------------------------

    insights["top_products"] = (
        get_top_products()
    )

    insights["top_categories"] = (
        get_top_categories()
    )

    insights["top_sellers"] = (
        get_top_sellers()
    )


    # --------------------------------------------------------
    # CUSTOMER EXPERIENCE
    # --------------------------------------------------------

    insights["average_review_score"] = (
        get_average_review_score()
    )

    insights["review_distribution"] = (
        get_review_distribution()
    )


    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    insights["order_status"] = (
        get_order_status_breakdown()
    )


    # --------------------------------------------------------
    # TRENDS
    # --------------------------------------------------------

    insights["monthly_sales"] = (
        get_monthly_sales()
    )

    insights["monthly_orders"] = (
        get_monthly_orders()
    )


    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    insights["delivery"] = (
        get_delivery_performance()
    )


    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    insights["recommendations"] = (
        generate_recommendations(
            insights
        )
    )


    return insights


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("📊 AI BUSINESS ANALYST")
    print("ADVANCED BUSINESS INSIGHTS")
    print("=" * 65)
    print()


    try:

        insights = generate_insights()


        # ====================================================
        # CORE METRICS
        # ====================================================

        print("💰 PRODUCT SALES")

        print(
            f"₦{insights['total_sales']:,.2f}"
        )

        print()

        print("💳 TOTAL PAYMENT VALUE")

        print(
            f"₦{insights['total_payment_value']:,.2f}"
        )

        print()

        print("🛒 TOTAL ORDERS")

        print(
            f"{insights['total_orders']:,}"
        )

        print()

        print("👥 TOTAL CUSTOMERS")

        print(
            f"{insights['total_customers']:,}"
        )

        print()

        print("📦 TOTAL PRODUCTS")

        print(
            f"{insights['total_products']:,}"
        )

        print()

        print("💵 AVERAGE ORDER VALUE")

        print(
            f"₦{insights['average_order_value']:,.2f}"
        )

        print()

        print("💳 AVERAGE PAYMENT PER ORDER")

        print(
            f"₦{insights['average_payment_per_order']:,.2f}"
        )

        print()

        print("⭐ AVERAGE REVIEW SCORE")

        print(
            f"{insights['average_review_score']:.2f} / 5"
        )

        print()


        # ====================================================
        # TOP PRODUCTS
        # ====================================================

        print("=" * 65)

        print("🏆 TOP 10 PRODUCTS")

        print("=" * 65)


        for index, product in enumerate(
            insights["top_products"],
            start=1
        ):

            print(
                f"{index}. "
                f"{product['product_id']} | "
                f"{product['category']} | "
                f"₦{product['total_sales']:,.2f} | "
                f"{product['items_sold']} items"
            )


        print()


        # ====================================================
        # TOP CATEGORIES
        # ====================================================

        print("=" * 65)

        print("🏷️ TOP 10 CATEGORIES")

        print("=" * 65)


        for index, category in enumerate(
            insights["top_categories"],
            start=1
        ):

            print(
                f"{index}. "
                f"{category['category']} | "
                f"₦{category['total_sales']:,.2f} | "
                f"{category['items_sold']} items"
            )


        print()


        # ====================================================
        # ORDER STATUS
        # ====================================================

        print("=" * 65)

        print("📦 ORDER STATUS")

        print("=" * 65)


        for status in insights[
            "order_status"
        ]:

            print(
                f"{status['status']}: "
                f"{status['count']:,} "
                f"({status['percentage']:.2f}%)"
            )


        print()


        # ====================================================
        # DELIVERY
        # ====================================================

        print("=" * 65)

        print("🚚 DELIVERY PERFORMANCE")

        print("=" * 65)


        print(
            f"Delivered: "
            f"{insights['delivery']['delivered']:,}"
        )

        print(
            f"Pending: "
            f"{insights['delivery']['pending']:,}"
        )


        print()


        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        print("=" * 65)

        print("🤖 BUSINESS RECOMMENDATIONS")

        print("=" * 65)


        for index, recommendation in enumerate(
            insights["recommendations"],
            start=1
        ):

            print(
                f"{index}. {recommendation}"
            )


        print()

        print("=" * 65)

        print("✅ ADVANCED INSIGHTS GENERATED")

        print("=" * 65)

    except Exception as e:

        print()

        print("❌ ERROR")

        print(e)
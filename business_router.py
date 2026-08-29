from kpi import calculate_kpis
from business_metrics import detect_business_metrics


# ============================================================
# BUSINESS ROUTER
# ============================================================

def business_router(question, tables=None):
    """
    Route a business question through the existing KPI and
    business-metrics system.
    """

    if not question:
        return "Please provide a business question."


    # --------------------------------------------------------
    # Detect required metrics
    # --------------------------------------------------------

    try:

        metrics = detect_business_metrics(
            question
        )

    except TypeError:

        if tables is not None:

            try:

                metrics = detect_business_metrics(
                    question,
                    tables
                )

            except Exception as e:

                return f"Business metrics error: {e}"

        else:

            metrics = []

    except Exception as e:

        return f"Business metrics error: {e}"


    # --------------------------------------------------------
    # Calculate KPIs
    # --------------------------------------------------------

    try:

        kpis = calculate_kpis(
            question,
            tables
        )

    except Exception as e:

        kpis = {
            "error": str(e)
        }


    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {
        "question": question,
        "metrics": metrics,
        "kpis": kpis
    }
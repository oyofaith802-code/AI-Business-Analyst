from business_metrics import detect_business_metrics


# ============================================================
# KPI CALCULATOR
# ============================================================

def calculate_kpis(question, tables=None):
    """
    Detect the business metrics needed for a question.
    """

    if not question:
        return []


    # --------------------------------------------------------
    # Call detect_business_metrics()
    # --------------------------------------------------------

    try:

        result = detect_business_metrics(question)

        return result

    except TypeError:

        # Some versions may expect tables as well.
        if tables is not None:

            try:

                result = detect_business_metrics(
                    question,
                    tables
                )

                return result

            except Exception as e:

                return {
                    "error": str(e)
                }

        return []


    except Exception as e:

        return {
            "error": str(e)
        }
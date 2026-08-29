# ============================================================
# AI BUSINESS ANALYST - ANALYSIS ENGINE
# ============================================================

import pandas as pd

from table_selector import (
    select_relevant_tables,
)

from dataset_reasoning import (
    analyze_question,
)

from sql_agent import (
    generate_sql,
)

from sql_validator import (
    validate_sql,
)

from sql_error_agent import (
    fix_sql_error,
)

from answer_agent import (
    generate_business_answer,
)

from chat_memory import (
    save_chat,
)

from database import engine

from sqlalchemy import text


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    if not sql:

        return {
            "success": False,
            "error": "SQL query is empty.",
        }


    try:

        with engine.connect() as conn:

            result = conn.execute(
                text(sql)
            )

            rows = result.fetchall()

            columns = result.keys()


        dataframe = pd.DataFrame(
            rows,
            columns=columns,
        )


        return {
            "success": True,
            "data": dataframe,
            "error": None,
        }


    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_generated_sql(sql):

    try:

        validation = validate_sql(
            sql
        )

    except Exception as e:

        return {
            "valid": False,
            "errors": [
                str(e)
            ],
        }


    if not isinstance(
        validation,
        dict,
    ):

        return {
            "valid": False,
            "errors": [
                "SQL validator returned an invalid response."
            ],
        }


    return validation


# ============================================================
# REPAIR SQL
# ============================================================

def repair_sql(
    question,
    sql,
    error,
    user_email,
):

    try:

        repaired_sql = fix_sql_error(
            question=question,
            sql=sql,
            error=error,
            user_email=user_email,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


    if not repaired_sql:

        return {
            "success": False,
            "error": "SQL repair returned an empty query.",
        }


    return {
        "success": True,
        "sql": repaired_sql,
    }


# ============================================================
# SELECT RELEVANT TABLES
# ============================================================

def find_relevant_tables(
    question,
    user_email,
):

    try:

        tables = select_relevant_tables(
            question,
            user_email,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "tables": [],
        }


    if not tables:

        return {
            "success": False,
            "error": "No relevant datasets were found.",
            "tables": [],
        }


    return {
        "success": True,
        "error": None,
        "tables": tables,
    }


# ============================================================
# CHECK QUESTION ANSWERABILITY
# ============================================================

def check_question(
    question,
    tables,
    user_email,
):

    try:

        analysis = analyze_question(
            question,
            tables,
            user_email,
        )

    except Exception as e:

        return {
            "success": False,
            "answerable": False,
            "reason": str(e),
        }


    if isinstance(
        analysis,
        dict,
    ):

        answerable = analysis.get(
            "answerable",
            False,
        )

        reason = analysis.get(
            "reason",
            "",
        )

    else:

        text_result = str(
            analysis
        )

        answerable = (
            "UNSUPPORTED"
            not in text_result.upper()
        )

        reason = text_result


    return {
        "success": True,
        "answerable": answerable,
        "reason": reason,
    }


# ============================================================
# GENERATE SQL
# ============================================================

def create_sql(
    question,
    tables,
    user_email,
):

    try:

        sql = generate_sql(
            question,
            tables,
            user_email,
        )

    except Exception as e:

        return {
            "success": False,
            "sql": None,
            "error": str(e),
        }


    if not sql:

        return {
            "success": False,
            "sql": None,
            "error": "SQL agent returned an empty query.",
        }


    return {
        "success": True,
        "sql": sql,
        "error": None,
    }


# ============================================================
# GENERATE BUSINESS ANSWER
# ============================================================

def create_business_answer(
    question,
    result,
    user_email,
    dataset_name,
):

    try:

        answer = generate_business_answer(
            question=question,
            result=result,
            user_email=user_email,
            dataset_name=dataset_name,
        )

    except Exception as e:

        return {
            "success": False,
            "answer": None,
            "error": str(e),
        }


    return {
        "success": True,
        "answer": answer,
        "error": None,
    }


# ============================================================
# SAVE CONVERSATION
# ============================================================

def save_analysis_chat(
    user_email,
    dataset_name,
    question,
    answer,
    sql,
):

    try:

        saved = save_chat(
            user_email=user_email,
            dataset_name=dataset_name,
            question=question,
            answer=answer,
            sql_query=sql,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


    if not saved:

        return {
            "success": False,
            "error": "Chat could not be saved.",
        }


    return {
        "success": True,
        "error": None,
    }


# ============================================================
# MAIN ANALYSIS PIPELINE
# ============================================================

def analyze_business_question(
    question,
    user_email,
    dataset_name=None,
):

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not user_email:

        return {
            "success": False,
            "stage": "input",
            "error": "User email is required.",
        }


    if not question:

        return {
            "success": False,
            "stage": "input",
            "error": "Business question is required.",
        }


    question = question.strip()


    if not question:

        return {
            "success": False,
            "stage": "input",
            "error": "Business question is empty.",
        }


    # --------------------------------------------------------
    # STAGE 1 - FIND TABLES
    # --------------------------------------------------------

    tables_result = find_relevant_tables(
        question,
        user_email,
    )


    if not tables_result["success"]:

        return {
            "success": False,
            "stage": "table_selection",
            "error": tables_result["error"],
        }


    tables = tables_result[
        "tables"
    ]


    # --------------------------------------------------------
    # DATASET NAME
    # --------------------------------------------------------

    if dataset_name:

        active_dataset = dataset_name

    elif len(tables) == 1:

        active_dataset = tables[0]

    else:

        active_dataset = ", ".join(
            tables
        )


    # --------------------------------------------------------
    # STAGE 2 - QUESTION REASONING
    # --------------------------------------------------------

    reasoning_result = check_question(
        question,
        tables,
        user_email,
    )


    if not reasoning_result["success"]:

        return {
            "success": False,
            "stage": "reasoning",
            "error": reasoning_result["reason"],
        }


    if not reasoning_result["answerable"]:

        return {
            "success": False,
            "stage": "reasoning",
            "error": reasoning_result["reason"],
        }


    # --------------------------------------------------------
    # STAGE 3 - SQL GENERATION
    # --------------------------------------------------------

    sql_result = create_sql(
        question,
        tables,
        user_email,
    )


    if not sql_result["success"]:

        return {
            "success": False,
            "stage": "sql_generation",
            "error": sql_result["error"],
        }


    sql = sql_result[
        "sql"
    ]


    # --------------------------------------------------------
    # STAGE 4 - SQL VALIDATION
    # --------------------------------------------------------

    validation = validate_generated_sql(
        sql
    )


    if not validation.get(
        "valid",
        False,
    ):

        errors = validation.get(
            "errors",
            [],
        )


        return {
            "success": False,
            "stage": "sql_validation",
            "error": (
                "Generated SQL failed validation."
            ),
            "validation_errors": errors,
            "sql": sql,
        }


    # --------------------------------------------------------
    # STAGE 5 - SQL EXECUTION
    # --------------------------------------------------------

    execution = execute_sql(
        sql
    )


    # --------------------------------------------------------
    # STAGE 6 - AUTOMATIC SQL REPAIR
    # --------------------------------------------------------

    if not execution["success"]:

        original_error = execution[
            "error"
        ]


        repair_result = repair_sql(
            question=question,
            sql=sql,
            error=original_error,
            user_email=user_email,
        )


        if not repair_result["success"]:

            return {
                "success": False,
                "stage": "sql_repair",
                "error": repair_result["error"],
                "original_sql": sql,
                "database_error": original_error,
            }


        repaired_sql = repair_result[
            "sql"
        ]


        # ----------------------------------------------------
        # VALIDATE REPAIRED SQL
        # ----------------------------------------------------

        repaired_validation = (
            validate_generated_sql(
                repaired_sql
            )
        )


        if not repaired_validation.get(
            "valid",
            False,
        ):

            return {
                "success": False,
                "stage": "repaired_sql_validation",
                "error": "Repaired SQL failed validation.",
                "sql": repaired_sql,
                "validation_errors":
                    repaired_validation.get(
                        "errors",
                        [],
                    ),
            }


        # ----------------------------------------------------
        # EXECUTE REPAIRED SQL
        # ----------------------------------------------------

        repaired_execution = execute_sql(
            repaired_sql
        )


        if not repaired_execution["success"]:

            return {
                "success": False,
                "stage": "repaired_sql_execution",
                "error": repaired_execution["error"],
                "sql": repaired_sql,
            }


        sql = repaired_sql

        execution = repaired_execution


    # --------------------------------------------------------
    # GET FINAL RESULT
    # --------------------------------------------------------

    result = execution[
        "data"
    ]


    if result is None:

        return {
            "success": False,
            "stage": "result",
            "error": "No result returned.",
            "sql": sql,
        }


    if result.empty:

        return {
            "success": False,
            "stage": "result",
            "error": "The query returned no results.",
            "sql": sql,
        }


    # --------------------------------------------------------
    # STAGE 7 - BUSINESS ANSWER
    # --------------------------------------------------------

    answer_result = create_business_answer(
        question=question,
        result=result,
        user_email=user_email,
        dataset_name=active_dataset,
    )


    if not answer_result["success"]:

        return {
            "success": False,
            "stage": "answer_generation",
            "error": answer_result["error"],
            "sql": sql,
            "data": result,
        }


    answer = answer_result[
        "answer"
    ]


    # --------------------------------------------------------
    # STAGE 8 - SAVE CHAT MEMORY
    # --------------------------------------------------------

    memory_result = save_analysis_chat(
        user_email=user_email,
        dataset_name=active_dataset,
        question=question,
        answer=answer,
        sql=sql,
    )


    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {
        "success": True,

        "question":
            question,

        "dataset":
            active_dataset,

        "tables":
            tables,

        "sql":
            sql,

        "data":
            result,

        "answer":
            answer,

        "memory_saved":
            memory_result["success"],

        "memory_error":
            memory_result.get(
                "error"
            ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================================"
    )

    print(
        "AI BUSINESS ANALYST - ANALYSIS ENGINE TEST"
    )

    print(
        "============================================================"
    )


    email = input(
        "Enter user email: "
    ).strip()


    dataset = input(
        "Enter dataset name: "
    ).strip()


    question = input(
        "Ask a business question: "
    ).strip()


    print()
    print(
        "🔍 Starting analysis..."
    )


    try:

        response = analyze_business_question(
            question=question,
            user_email=email,
            dataset_name=dataset,
        )


        print()
        print(
            "============================================================"
        )

        print(
            "ANALYSIS RESULT"
        )

        print(
            "============================================================"
        )


        if not response.get(
            "success",
            False,
        ):

            print(
                "❌ Analysis failed."
            )

            print()

            print(
                "Stage:",
                response.get(
                    "stage"
                )
            )

            print()

            print(
                "Error:",
                response.get(
                    "error"
                )
            )


        else:

            print(
                "✅ Analysis completed."
            )

            print()

            print(
                "Dataset:",
                response.get(
                    "dataset"
                )
            )

            print()

            print(
                "Generated SQL:"
            )

            print(
                response.get(
                    "sql"
                )
            )

            print()

            print(
                "Database result:"
            )

            print(
                response.get(
                    "data"
                )
            )

            print()

            print(
                "Business answer:"
            )

            print(
                response.get(
                    "answer"
                )
            )

            print()

            print(
                "Chat memory saved:",
                response.get(
                    "memory_saved"
                )
            )


    except Exception as e:

        print()
        print(
            "❌ Analysis engine failed:"
        )

        print(
            e
        )

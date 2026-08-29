from database import engine
from sqlalchemy import text


def create_memory_table():

    query = """
    CREATE TABLE IF NOT EXISTS chat_memory (

        id SERIAL PRIMARY KEY,

        session_id TEXT,

        user_question TEXT,

        generated_sql TEXT,

        answer TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()



def save_chat(session_id, question, sql, answer):

    query = """
    INSERT INTO chat_memory
    (
        session_id,
        user_question,
        generated_sql,
        answer
    )

    VALUES
    (
        :session_id,
        :question,
        :sql,
        :answer
    );
    """


    with engine.connect() as conn:

        conn.execute(
            text(query),
            {
                "session_id": session_id,
                "question": question,
                "sql": sql,
                "answer": answer
            }
        )

        conn.commit()



def get_previous_chats(session_id):

    query = """
    SELECT 
        user_question,
        answer

    FROM chat_memory

    WHERE session_id = :session_id

    ORDER BY id DESC
    LIMIT 10;
    """


    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            {
                "session_id": session_id
            }
        )

        return result.fetchall()
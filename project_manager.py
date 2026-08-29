from database import engine
from sqlalchemy import text


# ---------------------------------------
# Create Projects Table
# ---------------------------------------

def create_projects_table():

    query = """
    CREATE TABLE IF NOT EXISTS projects (

        id SERIAL PRIMARY KEY,

        username TEXT,

        project_name TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """

    with engine.connect() as conn:

        conn.execute(text(query))
        conn.commit()


# ---------------------------------------
# Create Project
# ---------------------------------------

def create_project(username, project_name):

    query = """
    INSERT INTO projects
    (
        username,
        project_name
    )

    VALUES
    (
        :username,
        :project_name
    );
    """

    with engine.connect() as conn:

        conn.execute(
            text(query),
            {
                "username": username,
                "project_name": project_name
            }
        )

        conn.commit()


# ---------------------------------------
# Get User Projects
# ---------------------------------------

def get_projects(username):

    query = """
    SELECT
        id,
        project_name,
        created_at

    FROM projects

    WHERE username = :username

    ORDER BY id DESC;
    """

    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            {
                "username": username
            }
        )

        return result.fetchall()
from database import engine
from sqlalchemy import text
import hashlib
import re


# ============================================================
# CREATE DOCUMENT MEMORY TABLE
# ============================================================

def create_document_memory_table():

    query = """
    CREATE TABLE IF NOT EXISTS document_memory (
        id SERIAL PRIMARY KEY,
        user_email TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        chunk_text TEXT NOT NULL,
        content_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    with engine.begin() as connection:
        connection.execute(text(query))


# ============================================================
# CREATE CONTENT HASH
# ============================================================

def create_content_hash(chunk_text):

    return hashlib.sha256(
        chunk_text.encode("utf-8")
    ).hexdigest()


# ============================================================
# SAVE DOCUMENT
# ============================================================

def save_document(
    user_email,
    filename,
    file_type,
    chunks
):

    create_document_memory_table()

    # Remove known temporary prefixes
    if filename.startswith("_temp_"):
        filename = filename.replace(
            "_temp_",
            "",
            1
        )

    saved_count = 0

    with engine.begin() as connection:

        for index, chunk in enumerate(chunks):

            chunk = str(chunk).strip()

            if not chunk:
                continue

            content_hash = create_content_hash(
                chunk
            )

            check_query = """
            SELECT id
            FROM document_memory
            WHERE user_email = :user_email
            AND filename = :filename
            AND chunk_index = :chunk_index
            AND content_hash = :content_hash
            LIMIT 1
            """

            existing = connection.execute(
                text(check_query),
                {
                    "user_email": user_email,
                    "filename": filename,
                    "chunk_index": index,
                    "content_hash": content_hash,
                }
            ).fetchone()

            if existing:
                continue

            insert_query = """
            INSERT INTO document_memory
            (
                user_email,
                filename,
                file_type,
                chunk_index,
                chunk_text,
                content_hash
            )
            VALUES
            (
                :user_email,
                :filename,
                :file_type,
                :chunk_index,
                :chunk_text,
                :content_hash
            )
            """

            connection.execute(
                text(insert_query),
                {
                    "user_email": user_email,
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": index,
                    "chunk_text": chunk,
                    "content_hash": content_hash,
                }
            )

            saved_count += 1

    return saved_count


# ============================================================
# EXTRACT IMPORTANT SEARCH WORDS
# ============================================================

def extract_search_words(search_text):

    # Convert to lowercase
    search_text = search_text.lower()

    # Extract words
    words = re.findall(
        r"[a-zA-Z0-9]+",
        search_text
    )

    # Common words that don't help document search
    stop_words = {
        "what",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "from",
        "with",
        "about",
        "this",
        "that",
        "these",
        "those",
        "do",
        "does",
        "did",
        "how",
        "why",
        "when",
        "where",
        "which",
        "who",
        "can",
        "could",
        "would",
        "should",
        "mentioned",
        "report",
        "document",
        "please",
        "tell",
        "me",
    }

    important_words = []

    for word in words:

        if word in stop_words:
            continue

        if len(word) < 2:
            continue

        if word not in important_words:

            important_words.append(
                word
            )

    return important_words


# ============================================================
# SEARCH DOCUMENTS
# ============================================================

def search_documents(
    user_email,
    search_text,
    limit=5
):

    create_document_memory_table()

    words = extract_search_words(
        search_text
    )

    if not words:
        return []

    # --------------------------------------------------------
    # Build OR search
    # --------------------------------------------------------

    conditions = []

    params = {
        "user_email": user_email,
        "limit": limit,
    }

    for index, word in enumerate(words):

        parameter = f"word_{index}"

        conditions.append(
            f"LOWER(chunk_text) LIKE :{parameter}"
        )

        params[parameter] = (
            f"%{word}%"
        )

    where_clause = " OR ".join(
        conditions
    )

    # --------------------------------------------------------
    # Give each matching word a score
    # --------------------------------------------------------

    score_parts = []

    for index, word in enumerate(words):

        parameter = f"word_{index}"

        score_parts.append(
            f"""
            CASE
                WHEN LOWER(chunk_text)
                LIKE :{parameter}
                THEN 1
                ELSE 0
            END
            """
        )

    score_expression = " + ".join(
        score_parts
    )

    query = f"""
    SELECT
        id,
        filename,
        file_type,
        chunk_index,
        chunk_text,
        ({score_expression}) AS relevance_score
    FROM document_memory
    WHERE user_email = :user_email
    AND ({where_clause})
    AND filename NOT LIKE 'tmp%%'
    AND filename NOT LIKE '_temp_%%'
    ORDER BY
        relevance_score DESC,
        filename,
        chunk_index,
        id DESC
    LIMIT :limit
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            params
        )

        rows = result.fetchall()

    documents = []

    seen = set()

    for row in rows:

        filename = row[1]

        chunk_index = row[3]

        key = (
            filename,
            chunk_index
        )

        if key in seen:
            continue

        seen.add(key)

        documents.append(
            {
                "id": row[0],
                "filename": filename,
                "file_type": row[2],
                "chunk_index": chunk_index,
                "chunk_text": row[4],
                "relevance_score": row[5],
            }
        )

    return documents


# ============================================================
# GET PAGE NUMBER
# ============================================================

def get_page_number(
    chunk_text,
    chunk_index
):

    page = chunk_index + 1

    if "[Page " in chunk_text:

        try:

            start = chunk_text.index(
                "[Page "
            ) + 6

            end = chunk_text.index(
                "]",
                start
            )

            page = int(
                chunk_text[start:end]
            )

        except Exception:

            pass

    return page


# ============================================================
# GET DOCUMENT CONTEXT
# ============================================================

def get_document_context(
    user_email,
    question,
    limit=5
):

    documents = search_documents(
        user_email,
        question,
        limit
    )

    if not documents:
        return ""

    context_parts = []

    for document in documents:

        filename = document[
            "filename"
        ]

        chunk_text = document[
            "chunk_text"
        ]

        chunk_index = document[
            "chunk_index"
        ]

        page = get_page_number(
            chunk_text,
            chunk_index
        )

        context_parts.append(
            f"""SOURCE:
{filename} — Page {page}

CONTENT:
{chunk_text}
"""
        )

    return "\n---\n".join(
        context_parts
    )


# ============================================================
# GET DOCUMENT SOURCES
# ============================================================

def get_document_sources(
    user_email,
    question,
    limit=5
):

    documents = search_documents(
        user_email,
        question,
        limit
    )

    sources = []

    seen = set()

    for document in documents:

        filename = document[
            "filename"
        ]

        chunk_text = document[
            "chunk_text"
        ]

        chunk_index = document[
            "chunk_index"
        ]

        if filename.startswith(
            "tmp"
        ):
            continue

        if filename.startswith(
            "_temp_"
        ):
            continue

        key = (
            filename,
            chunk_index
        )

        if key in seen:
            continue

        seen.add(key)

        page = get_page_number(
            chunk_text,
            chunk_index
        )

        sources.append(
            {
                "filename": filename,
                "page": page,
                "chunk_index": chunk_index,
                "text": chunk_text,
            }
        )

    return sources
# ============================================================
# DOCUMENT MANAGEMENT
# ============================================================

def get_user_documents(user_email):
    """
    Return all documents uploaded by a user.
    Each filename appears only once.
    """

    query = """
    SELECT
        filename,
        file_type,
        COUNT(*) AS chunk_count,
        MIN(created_at) AS uploaded_at
    FROM document_memory
    WHERE user_email = :user_email
    GROUP BY filename, file_type
    ORDER BY MIN(created_at) DESC;
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            {
                "user_email": user_email
            }
        )

        rows = result.fetchall()

    documents = []

    for row in rows:

        documents.append(
            {
                "filename": row[0],
                "file_type": row[1],
                "chunk_count": row[2],
                "uploaded_at": row[3]
            }
        )

    return documents


# ============================================================
# CHECK IF DOCUMENT EXISTS
# ============================================================

def document_exists(user_email, filename):
    """
    Check whether a user already has a document.
    """

    query = """
    SELECT EXISTS(
        SELECT 1
        FROM document_memory
        WHERE user_email = :user_email
        AND filename = :filename
    );
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            {
                "user_email": user_email,
                "filename": filename
            }
        )

        return bool(
            result.scalar()
        )


# ============================================================
# DELETE DOCUMENT
# ============================================================

def delete_document(user_email, filename):
    """
    Delete all chunks belonging to one document.
    """

    query = """
    DELETE FROM document_memory
    WHERE user_email = :user_email
    AND filename = :filename;
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            {
                "user_email": user_email,
                "filename": filename
            }
        )

        connection.commit()

    return result.rowcount


# ============================================================
# GET DOCUMENT STATISTICS
# ============================================================

def get_document_stats(
    user_email,
    filename
):
    """
    Return statistics for one document.
    """

    query = """
    SELECT
        COUNT(*) AS chunk_count,
        MIN(created_at) AS uploaded_at
    FROM document_memory
    WHERE user_email = :user_email
    AND filename = :filename;
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            {
                "user_email": user_email,
                "filename": filename
            }
        )

        row = result.fetchone()

    if row is None:

        return None

    return {
        "chunk_count": row[0],
        "uploaded_at": row[1]
    }

from models.db import get_db_connection

def search_students(query):
    if not query:
        return []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # normalize input
    query = query.strip().lower()

    sql = """
    SELECT * FROM students
    WHERE LOWER(first_name) LIKE %s
    OR LOWER(last_name) LIKE %s
    OR LOWER(father_name) LIKE %s
    OR CAST(sr_no AS CHAR) = %s
    """

    # ✅ PREFIX SEARCH (starts with)
    cursor.execute(sql, (
        query + '%',
        query + '%',
        query + '%',
        query
    ))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # ✅ format data for UI
    results = []
    for row in rows:
        results.append({
            "roll_no": row.get('sr_no'),
            "name": f"{row.get('last_name','')} {row.get('first_name','')} {row.get('father_name','')}".strip(),
            "dob": row.get('dob'),
            "category": row.get('category'),
            "percentage": row.get('percentage')
        })

    return results

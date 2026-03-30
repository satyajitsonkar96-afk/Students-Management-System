from models.db import get_db_connection   # Import the database connection function from the db module

def search_students(query):               # Define function that takes a search query string and returns a list of matching student records
    if not query:                         # Check if query is empty or None
        return []                         # Return empty list immediately if no query provided

    conn = get_db_connection()            # Establish a database connection using the imported helper function
    cursor = conn.cursor(dictionary=True) # Create a cursor that returns rows as dictionaries (column name -> value)

    # normalize input
    query = query.strip().lower()         # Remove leading/trailing spaces and convert query to lowercase for case-insensitive search

    sql = """                             # Define SQL query template with placeholders for partial matching
    SELECT * FROM students
    WHERE LOWER(first_name) LIKE %s
    OR LOWER(last_name) LIKE %s
    OR LOWER(father_name) LIKE %s
    OR CAST(sr_no AS CHAR) = %s
    """

    # ✅ PREFIX SEARCH (starts with)
    cursor.execute(sql, (                 # Execute the SQL query with the following parameters:
        query + '%',                      # For first_name: match any value starting with the query
        query + '%',                      # For last_name: same prefix matching
        query + '%',                      # For father_name: same prefix matching
        query                             # For sr_no: exact match (converted to string)
    ))

    rows = cursor.fetchall()              # Fetch all matching rows from the executed query

    cursor.close()                        # Close the cursor to free database resources
    conn.close()                          # Close the database connection

    # ✅ format data for UI
    results = []                          # Initialize an empty list to hold formatted student records
    for row in rows:                      # Iterate over each row returned from the database
        results.append({                  # Append a formatted dictionary to the results list
            "roll_no": row.get('sr_no'),  # Map database field 'sr_no' to 'roll_no'
            "name": f"{row.get('last_name','')} {row.get('first_name','')} {row.get('father_name','')}".strip(),  # Combine last, first, father names, strip extra spaces
            "dob": row.get('dob'),        # Keep date of birth as is
            "category": row.get('category'),  # Keep category field
            "percentage": row.get('percentage')  # Keep percentage field
        })

    return results                        # Return the list of formatted student records
import pyodbc

def clear_stored_procedures():
    """Clear all stored procedures in the database."""
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=DBProject;'
        'UID=sa;'
        'PWD=rs9190678_'
    )

    try:
        # Connect to the database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Query to fetch all stored procedure names
        fetch_procedures_query = """
        SELECT name 
        FROM sys.objects 
        WHERE type = 'P' AND is_ms_shipped = 0;
        """

        cursor.execute(fetch_procedures_query)
        procedures = cursor.fetchall()

        if not procedures:
            print("No stored procedures found to delete.")
        else:
            # Drop each stored procedure
            for proc in procedures:
                proc_name = proc[0]
                drop_query = f"DROP PROCEDURE {proc_name};"
                cursor.execute(drop_query)
                print(f"Deleted procedure: {proc_name}")

            # Commit the changes
            conn.commit()
            print("All stored procedures have been cleared successfully.")

    except Exception as e:
        print(f"Error clearing stored procedures: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clear_stored_procedures()

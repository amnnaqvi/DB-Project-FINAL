import pyodbc

def clear_db():
    # Connect to the database
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=DBProject;'
        'UID=sa;'
        'PWD=rs9190678_')
    cursor = conn.cursor()

    try:
        # Step 1: Drop all foreign key constraints
        cursor.execute("""
            DECLARE @sql NVARCHAR(MAX) = N'';
            SELECT @sql += 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) 
                        + '.' + QUOTENAME(OBJECT_NAME(parent_object_id))
                        + ' DROP CONSTRAINT ' + QUOTENAME(name) + ';'
            FROM sys.foreign_keys;
            EXEC sp_executesql @sql;
        """)
        conn.commit()
        
        # Step 2: Drop all tables
        cursor.execute("EXEC sp_MSforeachtable 'DROP TABLE ?'")
        conn.commit()

        print("All tables and constraints have been dropped successfully.")

    except Exception as e:
        print("An error occurred:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    clear_db()

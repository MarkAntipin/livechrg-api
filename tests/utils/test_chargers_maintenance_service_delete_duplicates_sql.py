import sqlite3


def test_delete_duplicates_sql() -> None:
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    # Create a chargers table
    cursor.execute('''
        CREATE TABLE chargers (
            id INTEGER PRIMARY KEY,
            station_id TEXT,
            ocpi_ids TEXT
        );
    ''')

    # Insert duplicate records
    cursor.executemany('INSERT INTO chargers (station_id, ocpi_ids) VALUES (?, ?)',
                       [("A", "X"), ("A", "X"), ("B", "Y"), ("B", "Y"), ("B", "Y")])

    delete_query = '''
    DELETE FROM chargers
        WHERE id IN (
        SELECT c.id
        FROM chargers c
        INNER JOIN (
            SELECT station_id, ocpi_ids, MIN(id) as MinId
            FROM chargers
            GROUP BY station_id, ocpi_ids
            HAVING COUNT(*) > 1
        ) AS dg ON c.station_id = dg.station_id AND c.ocpi_ids = dg.ocpi_ids
        WHERE c.id > dg.MinId
    );
    '''
    cursor.execute(delete_query)

    # Fetch remaining records to verify that duplicates were removed
    cursor.execute('SELECT * FROM chargers')
    remaining_records = cursor.fetchall()

    assert len(remaining_records) == 2  # Expecting 2 unique records, one for each group

    connection.close()

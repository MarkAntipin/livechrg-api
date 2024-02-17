import sqlite3


def test_identify_duplicates_sql() -> None:
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    # Set up the schema and test data
    cursor.execute('CREATE TABLE chargers (id INTEGER, station_id TEXT, ocpi_ids TEXT)')
    cursor.execute('INSERT INTO chargers VALUES (1, "A", "X"), (2, "A", "X"), (3, "B", "Y")')

    cursor.execute('''
                    SELECT station_id, ocpi_ids, COUNT(*)
                    FROM chargers
                    GROUP BY station_id, ocpi_ids
                    HAVING COUNT(*) > 1;
                    ''')
    results = cursor.fetchall()

    assert len(results) == 1  # Check the number of duplicate groups

    connection.close()

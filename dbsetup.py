import sqlite3

# Create a connection to the database file
conn = sqlite3.connect('example.db')

# Create a table in the database
conn.execute('''
CREATE TABLE IF NOT EXISTS mytable (
    id TEXT PRIMARY KEY,
    fund TEXT,
    description TEXT,
    grantee TEXT,
    amount INTEGER,
    round TEXT,
    highlighted INTEGER,
    elo INTEGER
)
''')

# Insert data into the table
data = [
    ('rec8DZqNuADkWb0xS', 'EA Infrastructure Fund', '2 Month Exit Grant of 2.5 FTE salary split across 5 people to transition the EA Philippines Community', 'Nastassja Quijano', 15100, '2023 Q4', None, 1500),
    ('rec3IKjrIhTA49TrM', 'Animal Welfare Fund', 'To Fund a trilogy of reports which highlight the economic benefits of Farm Animal Welfare across Government departments', 'Conservative Animal Welfare Foundation', 50000, '2023 Q4', None, 1500),
    ('recveSY9EDd3L6ccw', 'Animal Welfare Fund', 'Funding for a full-time economist, a part-time content developer, and a part-time public relations specialist, along with quarterly surveys to support legislative efforts and corporate engagements benefiting farm animals in Peru.', 'Asociacion para el rescate y bienestar de losanimales - ARBA', 22000, '2023 Q4', None, 1500),
    ('rectdSxsSA70PD6I9', 'Animal Welfare Fund', 'Top-up fund to convert alternative protein culminating event from a virtual info session to an in-person symposium', 'Pierce Manlangit', 1000, '2023 Q4', None, 1500),
    ('recQQhUD7oNcG6WQG', 'EA Infrastructure Fund', 'A 6-month top-up salary to build the EA community in Barcelona through regular meetings and outreach events', 'Melanie Brennan', 5622, '2023 Q3', None, 1500)
]
conn.executemany('INSERT INTO mytable (id, fund, description, grantee, amount, round, highlighted, elo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data)

# Commit the changes and close the connection
conn.commit()
conn.close()
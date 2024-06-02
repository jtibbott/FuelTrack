import sqlite3
from flask import Flask, render_template
app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def dashboard():
    return render_template('index.html')

try:

    # Connect to DB and create a cursor
    sqliteConnection = sqlite3.connect('data.db')
    cursor = sqliteConnection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        date TEXT,
        litre REAL,
        "p/l" REAL,
        mileage INTEGER
    )
    ''')

    sqliteConnection.commit()

# Handle errors
except sqlite3.Error as error:
    print('Error occured - ', error)

# Close DB connection irrespective of success
# or failure
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print('SQLlite Connection closed')

if __name__ == '__main__':
    app.run(debug=True)
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def dashboard():
    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('data.db')
        sqliteConnection.row_factory = sqlite3.Row  # This enables accessing columns by name
        cursor = sqliteConnection.cursor()

        cursor.execute('SELECT * FROM data')
        rows = cursor.fetchall()

        # Close the connection
        sqliteConnection.close()

        if rows:
            most_recent_row = rows[0]  # The most recent entry

            # Access the data from the most recent row
            last_litre = most_recent_row['litre']
            last_pl = most_recent_row['p/l']
            last_mileage = most_recent_row['mileage']
            last_date = most_recent_row['date']

            # Calculate the cost and MPG for the most recent entry
            last_cost = last_litre * last_pl
            last_gallons = last_litre / 3.78541
            last_mpg = last_mileage / last_gallons
        else:
            # Provide default values if there are no rows in the database
            last_cost = 0
            last_mpg = 0

    except sqlite3.Error as error:
        print('Error occurred - ', error)
        # Provide default values in case of error
        last_cost = 0
        last_mpg = 0

    return render_template('index.html', last_mpg=last_mpg, last_cost=last_cost)

if __name__ == '__main__':
    app.run(debug=True)

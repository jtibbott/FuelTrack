import sqlite3
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def dashboard():
    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('data.db')
        sqliteConnection.row_factory = sqlite3.Row  # This enables accessing columns by name
        cursor = sqliteConnection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            litre REAL,
            "p/l" REAL,
            mileage INTEGER
            )
            ''') 

        sqliteConnection.commit()       

        cursor.execute('SELECT * FROM data')
        rows = cursor.fetchall()

        # Close the connection
        sqliteConnection.close()

        # Initialize variables
        avg_mpg = 0
        avg_cost = 0
        avg_mileage = 0
        avg_pl = 0
        all_time_fuel_cost = 0
        refuel_frequency = 0
        prev_mileage = None
        mileage_diffs = []
        mileage_diff = 0

        if rows:
            # Calculate averages
            total_litre = 0
            total_pl = 0
            total_mileage = 0
            total_cost = 0
            total_mpg = 0
            num_rows = len(rows)

            for row in rows:
                litre = row['litre']
                pl = row['p/l'] / 100
                mileage = row['mileage']

                # Calculate the difference in mileage if there is a previous mileage
                if prev_mileage is not None:
                    mileage_diff = mileage - prev_mileage
                    mileage_diffs.append(mileage_diff)
                
                # Update prev_mileage for the next iteration
                prev_mileage = mileage

                cost = litre * pl
                gallons = litre / 3.78541
                mpg = mileage_diff / gallons

                total_litre += litre
                total_pl += pl
                total_mileage += mileage
                total_cost += cost
                total_mpg += mpg

            avg_litre = total_litre / num_rows
            avg_pl = round(total_pl / num_rows, 3)
            avg_mileage = total_mileage / num_rows
            avg_cost = round(total_cost / num_rows,2)
            avg_mpg = total_mpg / num_rows

            # Access the data from the most recent row
            most_recent_row = rows[0]
            last_litre = most_recent_row['litre']
            last_pl = most_recent_row['p/l'] / 100
            last_mileage = most_recent_row['mileage']
            last_date = most_recent_row['date']

            # Calculate all-time fuel cost
            all_time_fuel_cost = round(sum(row['litre'] * (row['p/l'] / 100) for row in rows), 2)

            # Calculate the cost and MPG for the most recent entry
            last_cost = round(last_litre * last_pl, 2)
            last_gallons = last_litre / 3.78541
            last_mpg = last_mileage / last_gallons

            # Calculate the average mileage difference
            if mileage_diffs:
                avg_mileage = sum(mileage_diffs) / len(mileage_diffs)
            else:
                avg_mileage = 0            

        else:
            # Provide default values if there are no rows in the database
            avg_mpg=0
            last_mpg=0
            avg_cost=0
            last_cost=0
            avg_mileage=0
            avg_pl=0
            all_time_fuel_cost=0
            refuel_frequency = 0

    except sqlite3.Error as error:
        print('Error occurred - ', error)
        # Provide default values in case of error
        avg_mpg=0
        last_mpg=0
        avg_cost=0
        last_cost=0
        avg_mileage=0
        avg_pl=0
        all_time_fuel_cost=0
        refuel_frequency = 0

    return render_template('index.html', avg_mpg=avg_mpg, last_mpg=last_mpg, avg_cost=avg_cost, last_cost=last_cost, avg_mileage=avg_mileage, avg_pl=avg_pl, all_time_fuel_cost=all_time_fuel_cost, refuel_frequency=refuel_frequency)

@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        date = request.form['date']
        litre = float(request.form['litre'])
        pl = float(request.form['pl'])
        mileage = int(request.form['mileage'])

        try:
            sqliteConnection = sqlite3.connect('data.db')
            cursor = sqliteConnection.cursor()

            cursor.execute('''
                INSERT INTO data (date, litre, "p/l", mileage)
                VALUES (?, ?, ?, ?)
                ''', (date, litre, pl, mileage))

            sqliteConnection.commit()
            sqliteConnection.close()

            return redirect(url_for('dashboard'))

        except sqlite3.Error as error:
            print('Error occurred - ', error)

    return render_template('add_entry.html')

if __name__ == '__main__':
    app.run(debug=True)

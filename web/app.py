from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import datetime
import matplotlib.pyplot as plt
import mplcursors
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('daily_events.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        datetime TEXT NOT NULL,
        value INTEGER NOT NULL,
        description TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Route to display the form and handle submissions
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        hour_minute = request.form['hour']
        ampm = request.form['ampm']
        value = request.form['value']
        description = request.form['description']

        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            datetime.datetime.strptime(hour_minute, '%I:%M')  # Check hour_minute format
        except ValueError:
            flash("Invalid date or time format.")
            return redirect(url_for('index'))

        hour, minute = map(int, hour_minute.split(':'))
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0

        try:
            value = int(value)
        except ValueError:
            flash("Invalid value. Please enter an integer value.")
            return redirect(url_for('index'))

        datetime_str = f"{date} {hour:02}:{minute:02}"
        conn = sqlite3.connect('daily_events.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO events (datetime, value, description) VALUES (?, ?, ?)', (datetime_str, value, description))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    
    # Fetch data for the graph and event list
    conn = sqlite3.connect('daily_events.db')
    cursor = conn.cursor()
    cursor.execute('SELECT datetime, value, description FROM events ORDER BY datetime ASC')  # Order by datetime in ascending order
    data = cursor.fetchall()

    # Calculate summary statistics
    total_events = len(data)
    total_value = sum([row[1] for row in data])
    average_value = round(total_value / total_events, 2) if total_events > 0 else 0

    conn.close()

    if data:
        datetimes = [datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M') for row in data]
        values = [row[1] for row in data]
        descriptions = [row[2] for row in data]

        cumulative_values = []
        current_value = 0

        # Calculate cumulative values without adjusting for decreases
        for value in values:
            current_value += value
            cumulative_values.append(current_value)

        # Generate the graph
        fig, ax = plt.subplots()
        ax.plot(datetimes, cumulative_values, marker='o', linestyle='-', color='blue')
        scatter = ax.scatter(datetimes, cumulative_values, color='blue')

        ax.set_title('Cumulative Daily Values')
        ax.set_xlabel('Datetime')
        ax.set_ylabel('Cumulative Value')
        ax.grid(True)

        # Set y-axis limits
        ax.set_ylim(-10, 10)

        # Highlight horizontal line at y=0
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1)

        fig.autofmt_xdate()

        cursor = mplcursors.cursor(scatter, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(text=f"{descriptions[sel.index]} (Cumulative: {cumulative_values[sel.index]})",
                            anncoords="offset points",
                            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))

        # Save the graph temporarily
        graph_path = 'static/graph.png'
        fig.savefig(graph_path)
        plt.close(fig)

        # Pass graph path, event data, and statistics to the template
        graph_filename = os.path.basename(graph_path)

        return render_template('index.html', data=data, graph_filename=graph_filename,
                               total_events=total_events, total_value=total_value,
                               average_value=average_value)

    # If no data, just render the form
    return render_template('index.html', data=[], graph_filename=None,
                           total_events=0, total_value=0, average_value=0)




if __name__ == '__main__':
    init_db()
    app.run(debug=True)

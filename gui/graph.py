# plot_graph.py

import sqlite3
import datetime
import matplotlib.pyplot as plt
import mplcursors

# Retrieve data from the database
conn = sqlite3.connect('daily_events.db')
cursor = conn.cursor()
cursor.execute('SELECT date, value, description FROM events ORDER BY date')
data = cursor.fetchall()
conn.close()

# Step 4: Calculate Cumulative Values
dates = [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in data]
values = [row[1] for row in data]
descriptions = [row[2] for row in data]

cumulative_values = []
current_value = 0
for value in values:
    current_value += value
    cumulative_values.append(current_value)

# Step 5: Plot the Data
fig, ax = plt.subplots()
ax.plot(dates, cumulative_values, marker='o', linestyle='-', color='blue')
scatter = ax.scatter(dates, cumulative_values, color='blue')

# Adding titles and labels
ax.set_title('Cumulative Daily Values')
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Value')
ax.grid(True)  # Add grid

# Formatting the x-axis to show dates properly
fig.autofmt_xdate()

# Step 6: Add Tooltips
cursor = mplcursors.cursor(scatter, hover=True)

@cursor.connect("add")
def on_add(sel):
    sel.annotation.set(text=f"{descriptions[sel.index]} (Cumulative: {cumulative_values[sel.index]})",
                       anncoords="offset points",
                       bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))

# Show the plot
plt.show()

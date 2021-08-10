from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from csv import writer, reader
import os.path
from datetime import date, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "python"
Bootstrap(app)

hours          = [(0, 8), (1, 9), (2, 10), (3, 11), (4, 12),
                  (5, 1), (6, 2), (7, 3), (8, 4), (9, 5),
                  (10, 6), (11, 7), (12, 8), (13, 9), (14, 10)]  # 12-hour notations
military_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]  # 24-hour notation
quarters       = [(0, 0), (1, 15), (2, 30), (3, 45)]                         # 15-minute quarter-hours
durations      = [(1, "15 minutes"), (2, "30 minutes"), (3, "45 minutes"),
                  (4, "1 hour"), (8, "2 hours"), (12, "3 hours"), (16, "4 hours")]
priorities     = [(0, "Low"), (1, "Medium"), (2, "High")]                                  # Task priorities

end_time_index = 0  # Index of previous task end time
task_number    = 0  # Number of task: 1-9


# Define input task form
class TaskForm(FlaskForm):
    name          = StringField('Task Name',     validators=[DataRequired()])
    start_hour    = SelectField("Start Hour",    choices=hours)
    start_quarter = SelectField("Start Quarter", choices=quarters)
    duration      = SelectField("Duration",      choices=durations)
    priority      = SelectField("Priority",      choices=priorities)
    submit        = SubmitField("Submit Task")


# Flask routes
@app.route("/")
def home():
    """Main home page"""

    iso_date = str(date.today())
    filename = "etp_tasks_" + iso_date + ".csv"

    # Check to see if csv file exists
    is_file_present = os.path.exists(filename)

    return render_template("index.html", exists=is_file_present)


def standard_time(hour, quarter):
    """Converts 24-hour military time to AM/PM standard time

    Keyword arguments:
       hour    -- zero-indexed 24-hour value 0-14 (8:00 AM = 10:00 PM)
       quarter -- zero-indexed quarter-hour 0, 1, 2, 3
    """

    print(f"\nstandard_time(hour={hour}, quarter={quarter})")

    period = "AM" if hour < 12 else "PM"  # Morning or afternoon
    print(f"period={period}")

    standard_hour = hour if hour < 13 else hour - 12  # 8-12 AM or 1-9 PM
    print(f"standard_hour={standard_hour}")

    quarter_hour = quarter * 15  # 0, 15, 30, 45
    print(f"quarter_hour={quarter_hour}")

    time_string = "{:2}:{:02} {}".format(standard_hour, quarter_hour, period)  # HH:MM AM/PM
    print(f"time_string={time_string}")

    return time_string


def get_standard_time(time):
    """Convert time index value to standard time string

    Keyword arguments:
    time -- time in 0-indexed quarter hours 0-57 (8:00 AM - 10:00 PM)

    """

    print(f"\nget_standard_time({time})")

    hour_index = int(time / 4)  # Extract hour 0-14
    hour       = 8 + hour_index
    quarter    = int(time % 4)  # Extract quarter 0-3

    print(f"hour_index={hour_index}, hour={hour}, quarter={quarter}")

    time_string = standard_time(hour, quarter)
    print(f"time_string={time_string}")

    return time_string  # HH:MM AM/PM


@app.route('/add', methods=["GET", "POST"])
def add_task():
    """Add Task Form page"""

    print("\nAdding new task")

    task_form = TaskForm()

    # If task form has validated
    if task_form.validate_on_submit():

        print("Task Form validated")

        # Get form fields
        print("Extracting form fields\n")

        task_name = task_form.name.data                                 # String

        start_hour_index = int(task_form.start_hour.data)               # 0-22 or 8 AM - 10 PM?
        print(f"start_hour_index = {start_hour_index}")

        start_quarter_index = int(task_form.start_quarter.data)         # 0-3 or 0, 15, 30, 45 minutes?
        print(f"start_quarter_index = {start_quarter_index}")

        # Calculate start time index from start hour and start quarter
        start_time_index = start_hour_index * 4 + start_quarter_index   # Calculated as 0-57
        print(f"start_time_index = {start_time_index}")

        start_time_string = get_standard_time(start_time_index)         # Convert to 12-hour format

        # 0, 1, 2, 3, 4, 8, 12, 16 quarter hours
        duration_index = int(task_form.duration.data)                   # 0-16 quarter hours
        print(f"duration_index = {duration_index}")

        duration_string = dict(durations).get(duration_index)            # string duration
        print(f"duration_string = {duration_string}")
        
        current_task_end_time_index = start_time_index + duration_index       # 0-57
        print(f"current_task_end_time_index = {current_task_end_time_index}")

        current_task_end_time_string = get_standard_time(current_task_end_time_index)
        print(f"current_task_end_time_string = {current_task_end_time_string}")

        priority_index = int(task_form.priority.data)                    # 0-2 or string?
        print(f"priority_index = {priority_index}")

        priority_string = priorities[priority_index][1]
        print(f"priority_string = {priority_string}")

        # Check for this task start time index does not overlap end time index of previous task
        global end_time_index

        today = str(date.today())
        filename = "etp_tasks_" + today + ".csv"

        global task_number  # Number of task: 1-9

        # If previous task end time index is zero;
        # No previous task defined
        if end_time_index == 0:

            print(f"\nNo previous task defined")

            # ETP Tasks CSV file for today exists
            # Open and get last task information
            # Update last task end_time_index
            if os.path.isfile(filename):

                print(f"\nExternal CSV file {filename} exists")

                task_number = 0
                with open(filename, mode='r') as task_file:
                    tasks_csv_data = reader(task_file)
                    for task in tasks_csv_data:
                        task_number += 1  # Count tasks
                    task_file.close()
                print(f"Previous task_number = {task_number}")

                # Get end time for this task
                print("\nGet end time for this task")

                end_time_index = current_task_end_time_index  # Save current end index
                print(f"end_time_index = {end_time_index}")

                end_time_string = get_standard_time(end_time_index)
                print(f"end_time_string = {end_time_string}")

                task_number += 1  # Count new task from form
                task_data = [task_number, task_name, 
                             start_time_index, start_time_string,
                             duration_index, duration_string,
                             end_time_index, end_time_string, 
                             priority_string]

                # Now append new task form data
                print("\nAppending new task to existing file")

                with open(filename, mode="a") as task_file:
                    writer_object = writer(task_file)
                    writer_object.writerow(task_data)
                    task_file.close()

            # ETP Tasks CSV file for today does NOT exist
            # Create and write task information
            # Update last task end_time_index
            else:

                print(f"\nExternal CSV file {filename} does NOT exist")

                # Update end_time for this task
                # end_time_index = start_time_index + quarter_hours[duration_index]
                # end_time_string = times[end_time_index][1]
                # Get end time for this task
                print("Get end time for this task")

                end_time_index = current_task_end_time_index
                print(f"end_time_index = {end_time_index}")

                end_time_string = get_standard_time(end_time_index)
                print(f"end_time_string = {end_time_string}")

                task_number = 1  # First task info
                task_data = [task_number, task_name, 
                             start_time_index, start_time_string,
                             duration_index, duration_string,
                             end_time_index, end_time_string, 
                             priority_string]

                # Now write first task information
                print("\nWriting new task to new file")

                with open(filename, mode="w") as task_file:
                    writer_object = writer(task_file)
                    writer_object.writerow(task_data)
                    task_file.close()

            print("\nShowing today's task(s)")
            return redirect(url_for('tasks'))

        # Previous task exists
        # Check for task time overlap
        else:

            print("\nPrevious task exists")
            print(f"start_time_index = {start_time_index}, end_time_index = {end_time_index}")

            # Check for current task start time overlap with previous task end time
            if start_time_index < end_time_index:

                print("\nERROR: Task times overlap")

                # ERROR: This task start time overlaps the previous task end time
                previous_task_end_time = get_standard_time(end_time_index)  # HH:MM AM/PM
                print(f"previous_task_end_time = {previous_task_end_time}")

                current_task_start_time = get_standard_time(start_time_index)  # HH:MM AM/PM
                print(f"current_task_start_time = {current_task_start_time}")

                error_message = "{} start time of current task can not be before " + \
                                "{} end time of previous task." \
                                   .format(current_task_start_time, previous_task_end_time)
                return render_template("error.html", message=error_message)

            # No overlap - write current task info
            else:

                print("\nTask times do NOT overlap")

                # ETP Tasks CSV file exists; append data
                if os.path.isfile(filename):

                    print(f"\nExternal CSV file {filename} exists")

                    # Update end_time for this task
                    end_time_index = current_task_end_time_index
                    print(f"end_time_index = {end_time_index}")

                    end_time_string = get_standard_time(end_time_index)
                    print(f"end_time_string = {end_time_string}")

                    task_number += 1
                    task_data = [task_number, task_name, 
                                 start_time_index, start_time_string,
                                 duration_index, duration_string,
                                 end_time_index, end_time_string, 
                                 priority_string]

                    # Append this task data to existing file
                    print("\nAppending new task to existing file")

                    with open(filename, mode="a") as task_file:
                        writer_object = writer(task_file)
                        writer_object.writerow(task_data)
                        task_file.close()

                # ETP Tasks CSV file for today DOES NOT exists;
                # create and write new task data
                else:

                    print(f"\nExternal CSV file {filename} does NOT exists")

                    # ETP Tasks CSV file for today does NOT exist; create it

                    # Update end_time for this task
                    end_time_index = current_task_end_time_index
                    print(f"end_time_index = {end_time_index}")

                    end_time_string = get_standard_time(end_time_index)
                    print(f"end_time_string = {end_time_string}")

                    task_number += 1
                    task_data = [task_number, task_name, 
                                 start_time_index, start_time_string,
                                 duration_index, duration_string,
                                 end_time_index, end_time_string, 
                                 priority_string]

                    # Write new file with this task data
                    print("\nWriting new task to new file")

                    with open(filename, mode="w") as task_file:
                        writer_object = writer(task_file)
                        writer_object.writerow(task_data)
                        task_file.close()

                print("\nShowing today's task(s)")
                return redirect(url_for('tasks'))

    return render_template('add.html', form=task_form)


@app.route('/tasks')
def tasks():
    """Loads CSV task data file and lists task data"""

    print("tasks")
    iso_date = str(date.today())
    filename = "etp_tasks_" + iso_date + ".csv"

    global end_time_index

    # Check to see if csv file exists
    if os.path.exists(filename):

        print(f"{filename} file exists")

        # Comma-separated value file for today's tasks exists. Open in read mode
        with open(filename, mode='r') as task_file:
            tasks_csv_data = reader(task_file)
            tasks_list = []
            for task in tasks_csv_data:
                tasks_list.append(task)
                end_time_index = int(task[6])
            task_file.close()

        task_count = len(tasks_list)
        print(f"task_count = {task_count}")
        print(f"end_time_index = {end_time_index}")

        today = datetime.now()
        formatted_date = today.strftime("%A, %B %d, %Y")  # Day name, Month day, year

        # Now go show users what tasks have been defined for today
        return render_template('tasks.html', today=formatted_date, tasks=tasks_list, count=task_count)

    else:

        # File does NOT exist. Display error message
        error_message = "Missing external CSV file {}".format(filename)
        return render_template('error.html', message=error_message)


@app.route('/etp')
def etp():
    """Loads CSV task data file and displays Emergent Task Planner with tasks"""

    print(f"\nEmergent Task Planner (ETP) Form Page")

    iso_date = str(date.today())
    filename = "etp_tasks_" + iso_date + ".csv"

    # Check to see if csv file exists
    if os.path.exists(filename):

        print(f"External CSV file {filename} exists.")

        today = datetime.now()
        formatted_date = today.strftime("%A, %B %d, %Y")    # Day name, Month day, year
        print(f"formatted_date = {formatted_date}")

        # Comma-separated value file for today's tasks exists. Open in read mode
        with open(filename, mode='r') as task_file:
            tasks_csv_data = reader(task_file)
            tasks_list = []
            for task in tasks_csv_data:

                print(task)

                # Format for class names in etp.html web page entries
                task_number = task[0]  # 1-9
                task_name = task[1]  # string
                # quarter hour start block number qblock00-qblock57
                task_start_time_index = "qblock{:02d}".format(int(task[2]))
                task_start_time_string = task[3]  # HH:MM AM/PM
                # duration block vertical size
                task_duration = "quarter{:02d}".format(int(task[4]))
                task_duration_string = task[5]  # 15, 30, 45, 60, 120, 180, 240 minutes
                # quarter hour block number qblock00-qblock57
                task_end_time_index = "qblock{:02d}".format(int(task[6]))
                task_end_time_string = task[7]  # HH:MM AM/PM
                task_priority_value = "task-{}".format(task[8].lower())
                task_data = [task_number, task_name,
                             task_start_time_index, task_start_time_string,
                             task_duration, task_duration_string,
                             task_end_time_index, task_end_time_string,
                             task_priority_value]
                tasks_list.append(task_data)

            task_file.close()

        # Now go show users what tasks have been defined for today
        return render_template('etp.html', date=formatted_date, tasks=tasks_list)

    else:

        # File does NOT exist. Display error message
        error_message = "Missing external CSV file {}".format(filename)
        return render_template('error.html', message=error_message)


if __name__ == '__main__':
    app.run(debug=True)

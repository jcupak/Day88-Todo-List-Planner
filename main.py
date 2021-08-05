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

times            = []                                        # Quarter hour times from 8:00AM to 9:45PM
durations        = [(0, 15), (1, 30), (2, 45), (3, 60), (4, 120), (5, 180), (6, 240)]  # (value, label)
quarter_hours    = [1, 2, 3, 4, 8, 12, 16]
priorities       = [(0, "Low"), (1, "Medium"), (2, "High")]  # Task priorities
end_time_index   = 0                                         # Index of previous task end time
task_number      = 0                                         # Number of task: 1-9


def create_times():
    """Fill times list with times from 8:00 AM to 9:45 PM"""

    print("Creating times")

    # Set start time to 8:00 AM
    hour = 8
    minutes = 0
    period = "AM"  # Morning or afternoon

    # Create 56 time items from 8:00 AM to 10:00 PM in 15 minute increments
    global times
    for quarter in range(57):
        time_str = f"{hour:2}:{minutes:02} {period}"
        time_item = (quarter, time_str)
        times.append(time_item)  # (0-55 'HH:MM AM/PM')
        # Set up next time item
        minutes += 15  # Increment by quarter hour
        # Check if minutes equal to next hour
        if minutes == 60:
            hour += 1  # Increment hour
            minutes = 0  # Reset minutes
        # Check if 12 noon and change period designation
        if hour == 12:
            period = "PM"  # Change to afternoon
        # Check if 24 hour time rolled over to afternoon
        if hour == 13:  # Afternoon
            hour = 1  # 1:00 PM


# Define input task form
class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    start_time = SelectField("Start Time", choices=times)
    duration = SelectField("Duration (minutes)", choices=durations)
    priority = SelectField("Priority", choices=priorities)
    submit = SubmitField("Submit Task")


# Flask routes
@app.route("/")
def home():
    """Main home page"""

    iso_date = str(date.today())
    filename = "etp_tasks_" + iso_date + ".csv"

    # Check to see if csv file exists
    file_is_present = os.path.exists(filename)

    return render_template("index.html", exists=file_is_present)


@app.route('/add', methods=["GET", "POST"])
def add_task():
    """Add Task Form page"""

    print("Adding new task")

    global times
    if len(times) == 0:
        create_times()

    task_form = TaskForm()

    # If task form has validated
    if task_form.validate_on_submit():

        print("Task Form validated")

        # Get form fields
        print("Extracting form fields")

        task_name = task_form.name.data

        start_time = task_form.start_time.data
        start_time_index = int(start_time)
        start_time_value = times[start_time_index][1]

        duration = task_form.duration.data
        duration_index = int(duration)
        duration_value = durations[duration_index][1]

        priority = task_form.priority.data
        priority_index = int(priority)
        priority_value = priorities[priority_index][1]

        # Check for this task start time index does not overlap end time index of previous task
        global end_time_index  # times

        today = str(date.today())
        filename = "etp_tasks_" + today + ".csv"

        global task_number  # Number of task: 1-9

        # If previous task end time index is zero;
        # No previous task defined
        if end_time_index == 0:

            print("end_time_index == 0")

            # ETP Tasks CSV file for today exists
            # Open and get last task information
            # Update last task end_time_index
            if os.path.isfile(filename):

                print(f"{filename} exists")

                task_number = 0
                with open(filename, mode='r') as task_file:
                    tasks_csv_data = reader(task_file)
                    for task in tasks_csv_data:
                        task_number += 1  # Count tasks
                    task_file.close()

                end_time_index = start_time_index + quarter_hours[duration_index]  # Index of times
                end_time_value = times[end_time_index][1]

                task_number += 1  # Count new task from form
                task_data = [task_number, task_name, start_time_index, start_time_value,
                             duration_index, duration_value,
                             end_time_index, end_time_value, priority_value]

                # Now append new task form data
                print("Appending new task to existing file")

                with open(filename, mode="a") as task_file:
                    writer_object = writer(task_file)
                    writer_object.writerow(task_data)
                    task_file.close()

            # ETP Tasks CSV file for today does NOT exist
            # Create and write task information
            # Update last task end_time_index
            else:

                print(f"{filename} does NOT exist")

                # Update end_time for this task
                end_time_index = start_time_index + quarter_hours[duration_index]  # Index of times
                end_time_value = times[end_time_index][1]

                task_number = 1  # First task info
                task_data = [task_number, task_name, start_time_index, start_time_value,
                             duration_index, duration_value,
                             end_time_index, end_time_value, priority_value]

                # Now write first task information
                print("Writing new task to new file")

                with open(filename, mode="w") as task_file:
                    writer_object = writer(task_file)
                    writer_object.writerow(task_data)
                    task_file.close()

            print("Showing today's task(s)")
            return redirect(url_for('tasks'))

        # Previous task exists
        # Check for task time overlap
        else:

            print("Previous task exists")
            print(f"start_time_index = {start_time_index}, end_time_index = {end_time_index}")

            # Check for task time overlap
            if start_time_index < end_time_index:

                print("ERROR: Task times overlap")

                # ERROR: This task start time overlaps the previous task end time

                previous_task_end_time = times[end_time_index][1]     # HH:MM AM/PM
                current_task_start_time = times[start_time_index][1]  # HH:MM AM/PM
                error_message = f"{current_task_start_time} start time of current task "\
                                f"can not be before {previous_task_end_time} end time of previous task."
                return render_template("error.html", message=error_message)

            # No overlap - write current task info
            else:

                print("Task times do NOT overlap")

                # ETP Tasks CSV file exists; append data
                if os.path.isfile(filename):

                    print(f"{filename} exists")

                    # Update end_time for this task
                    end_time_index = start_time_index + quarter_hours[duration_index]  # Index of times
                    end_time_value = times[end_time_index][1]

                    task_number += 1
                    task_data = [task_number, task_name, start_time_index, start_time_value,
                                 duration_index, duration_value,
                                 end_time_index, end_time_value, priority_value]

                    # Append this task data to existing file
                    with open(filename, mode="a") as task_file:
                        writer_object = writer(task_file)
                        writer_object.writerow(task_data)
                        task_file.close()

                # ETP Tasks CSV file for today DOES NOT exists;
                # create and write new task data
                else:

                    print(f"{filename} does NOT exists")

                    # ETP Tasks CSV file for today does NOT exist; create it

                    # Update end_time for this task
                    end_time_index = start_time_index + quarter_hours[duration_index]  # Index of times
                    end_time_value = times[end_time_index][1]

                    task_number += 1
                    task_data = [task_number, task_name, start_time_index, start_time_value,
                                 duration_index, duration_value,
                                 end_time_index, end_time_value, priority_value]

                    # Write new file with this task data
                    with open(filename, mode="w") as task_file:
                        writer_object = writer(task_file)
                        writer_object.writerow(task_data)
                        task_file.close()

                print("Showing today's task(s)")
                return redirect(url_for('tasks'))

            # Update end_time_index and end_time_value for this new task
            # end_time_index = start_time_index + quarter_hours[duration_index]  # Index of times
            # end_time_value = times[end_time_index][1]
            #
            # print(f"start_time_index = {start_time_index}")
            # print(f"start_time_value = {start_time_value}")
            # print(f"duration_index   = {duration_index}")
            # print(f"quarter_hours    = {quarter_hours[duration_index]}")
            # print(f"len(times)       = {len(times)}")
            # print(f"end_time_index   = {end_time_index}")
            # print(f"end_time_value]  = {end_time_value}")
            #
            # end_time_index = start_time_index + quarter_hours[duration_index]  # Index of times
            # end_time_value = times[end_time_index][1]
            #
            # task_number += 1
            # task_data = [task_number, task_name, start_time_index, start_time_value,
            #              duration_index, duration_value,
            #              end_time_index, end_time_value, priority_value]
            #
            # # ETP Tasks CSV file for today does NOT exist; create it
            # with open(filename, mode="w") as task_file:
            #     writer_object = writer(task_file)
            #     writer_object.writerow(task_data)
            #     task_file.close()
            #
            # return redirect(url_for('tasks'))

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
        formatted_date = today.strftime("%A, %B %d, %Y")

        # Now go show users what tasks have been defined for today
        return render_template('tasks.html', today=formatted_date, tasks=tasks_list, count=task_count)

    else:

        # File does NOT exist. Display error message
        error_message = f"Missing {filename} file"
        return render_template('error.html', message=error_message)


@app.route('/etp')
def etp():
    """Loads CSV task data file and displays Emergent Task Planner with tasks"""

    if len(times) == 0:
        create_times()

    iso_date = str(date.today())
    filename = "etp_tasks_" + iso_date + ".csv"

    # Check to see if csv file exists
    if os.path.exists(filename):

        today = datetime.now()
        formatted_date = today.strftime("%A, %B %d, %Y")

        # Comma-separated value file for today's tasks exists. Open in read mode
        with open(filename, mode='r') as task_file:
            tasks_csv_data = reader(task_file)
            tasks_list = []
            for task in tasks_csv_data:
                # Format for class names in etp.html web page entries
                task_number           = task[0]                       # 1-9
                task_name             = task[1]                       # string
                task_start_time_index = f"qblock{int(task[2]):02d}"   # quarter hour start block number qblock00-qblock57
                task_start_time_value = task[3]                       # HH:MM AM/PM
                task_duration         = f"quarter{quarter_hours[int(task[4])]:02d}"  # duration block vertical size
                task_duration_value   = task[5]                       # 15, 30, 45, 60, 120, 180, 240 minutes
                task_end_time_index   = f"qblock{int(task[6]):02d}"   # quarter hour block number qblock00-qblock57
                task_end_time_value   = task[7]                       # HH:MM AM/PM
                task_priority_value   = f"task-{task[8].lower()}"     # "task-low", "task-medium", "task-high"
                task_data = [task_number, task_name,
                             task_start_time_index, task_start_time_value,
                             task_duration, task_duration_value,
                             task_end_time_index, task_end_time_value,
                             task_priority_value]
                tasks_list.append(task_data)
            task_file.close()

        # Now go show users what tasks have been defined for today
        return render_template('etp.html', date=formatted_date, tasks=tasks_list)

    else:

        # File does NOT exist. Display error message
        error_message = f"Missing {filename} file"
        return render_template('error.html', message=error_message)


if __name__ == '__main__':
    app.run(debug=True)

###########################################################################################
# Course:            100 Days of Code - The Complete Python Pro Bootcamp for 2021         #
# Exercise:          Day 88 TODO List Planner                                             #
# Description:       Collects daily task planner information and prints an ETP worksheet  #
# Course Instructor: Angela Yu                                                            #
# Author:            John Cupak                                                           #
# History:           2021-06-28 Started                                                   #
#                    2021-06-29 Completed create_widgets                                  #
#                    2021-07-13 Created get_tasks                                         #
###########################################################################################

# Imports
from tkinter import Tk, Frame, Label, Entry, Listbox, Button

class Tasks(Frame):

    def __init__(root, master):
        Frame.__init__(root, master)
        root.grid()
        root.create_widgets()


    def get_tasks(root):
        """Callback extracts to do list task entries and passes data to etp.html web page"""

        # TODO: Create and write todo.csv file

        task_number = 0
        for task in root.tasks:

            todo = []  # Single to do task

            # Exit task loop if current task name is blank
            if len(task[0].get()) == 0:
                break

            task_number += 1
            task_name = task[0].get()
            start_index = task[1].curselection()[0]     # start_index number 0-95
            start_time = task[1].get(start_index)       # start_time text 8:00 AM - 9:45 PM
            duration_index = task[2].curselection()[0]  # duration index number 0-6
            duration = task[2].get(duration_index)      # duration text 15-240 minutes
            priority_index = task[3].curselection()[0]  # priority index number 0-2
            priority = task[3].get(priority_index)      # priority text "low", "medium", or "high"

            todo.append(task_number)
            todo.append(task_name)
            todo.append(start_index)
            todo.append(start_time)
            todo.append(duration_index)
            todo.append(duration)
            todo.append(priority_index)
            todo.append(priority)

            print(todo)  # Each to do task number, name, start_time, duration, priority

        root.quit()  # All tasks extracted


    def create_widgets(root):
        """Creates to do task Label, Entry, Listbox, and Button widgets"""

        root.tasks = []  # All task widgets

        # Create and display column header labels
        task_name_label = Label(root, text="Task Description", font=("Arial", 12, "bold"), fg="black")
        task_name_label.grid(row=0, column=0, padx=50, sticky='w' + 'e' + 'n' + 's')

        task_start_label = Label(root, text="Start", font=("Arial", 12, "bold"), fg="black")
        task_start_label.grid(row=0, column=1, padx=3, sticky='w' + 'e' + 'n' + 's')

        task_duration_label = Label(root, text="Duration", font=("Arial", 12, "bold"), fg="black")
        task_duration_label.grid(row=0, column=2, padx=5, sticky='w' + 'e' + 'n' + 's')

        task_priority_label = Label(root, text="Priority", font=("Arial", 12, "bold"), fg="black")
        task_priority_label.grid(row=0, column=3, padx=5, sticky='w' + 'e' + 'n' + 's')

        # Create time list_items
        times = []
        # Set start time to 8:00 AM
        hour = 8
        minutes = 0
        period = "AM"  # Morning or afternoon
        # Create list items from 8:00 AM start time to 9:45 PM in 15 minute increments
        for quarter in range(56):
            times.append(f"{hour:2}:{minutes:02} {period}")  # HH:MM AM/PM
            # Set up next time item
            minutes += 15  # Increment by quarter hour
            # Check if minutes equal to next hour
            if minutes == 60:
                hour += 1    # Increment hour
                minutes = 0  # Reset minutes
            # Check if 12 noon and change period designation
            if hour == 12:
                period = "PM"  # Change to afternoon
            # Check if 24 hour rolled over to afternoon
            if hour > 12:  # Afternoon
                hour = 1  # 1:00 PM

        durations = [15, 30, 45, 60, 120, 180, 240]  # minutes
        priorities = [" Low", " Medium", " High"]

        # Create nine task to do list entries
        for task_number in range(9):

            task = []  # Single task of name, start time, duration, and priority entries

            # Create task name/description entry
            name_entry = Entry(root, width=30)
            name_entry.grid(row=task_number + 2, column=0, padx=2, pady=2)
            task.append(name_entry)

            # Create task start times listbox
            # NOTE: exportselection=0 important to allow multiple listbox selections
            start_time = Listbox(root, height=3, selectmode='SINGLE', width=8, exportselection=0)
            index = 0
            for item in times:
                index += 1
                start_time.insert(index, item)
            start_time.grid(row=task_number + 2, column=1, padx=2, pady=2)
            task.append(start_time)

            # Create task duration listbox
            duration = Listbox(root, height=3, selectmode='SINGLE', width=3, exportselection=0)
            index = 0
            for minutes in durations:
                index += 1
                duration.insert(index, minutes)
            duration.grid(row=task_number + 2, column=2, padx=2, pady=2)
            task.append(duration)

            # Create task priority listbox
            priority = Listbox(root, height=3, selectmode='SINGLE', width=6, exportselection=0)
            index = 0
            for task_priority in priorities:
                index += 1
                priority.insert(index, task_priority)
            priority.grid(row=task_number + 2, column=3, padx=2, pady=2)
            task.append(priority)

            #  Append task widgets to main root
            root.tasks.append(task)

        task_button = Button(root, text="Submit Tasks", command=root.get_tasks)
        task_button.grid(row=14, column=0)


    # def create_instructions(root):
    #     instructions_frame = Frame(root, width=600, height=400)
    #     instructions_text = """This is the TODO list dialog for the Emergent Task Planner (ETP).
    #     Enter the name/description, select the start time, select the duration in minutes,
    #     and select the priority of each task (up to nine), and click on the SUBMIT button.
    #     NOTE: Please ensure that the start time of a task does not overlap any prior task."""
    #
    #     Label(root)

    def run(root):
        root.mainloop()

root = Tk()
root.title('To Do Task Lists')

app = Tasks(root)
app.run()

print("Time to pass to do data to web page")

# @app.route("/todo", methods=["POST"])


# TODO 5: Pass today's tasks data to ETP web page
# TODO 6: Print ETP web page with ETP background

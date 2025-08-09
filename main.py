import re
import zmq
import time


#helper function for redundant conditionals
def conditional_hlp(prompt):
    "return yes or no"
    while True:
        answer = input(f"{prompt} (y, n): ").strip().lower()
        if answer in ('y', 'n'):
            return answer == 'y'
        print("Answer not recognized.")

def MainMenu():
    """This will be the home screen in CLI app"""
    tasks = []
    while True:
        print("---------------------------------\n"
            "   Welcome to the Task Planner\n"
            "---------------------------------\n\n\n\n"
            "### Main Menu ###\n\n"
            " 1. Task list\n"
            " 2. Available Time\n"
            " 3. Optimized Plan\n"
            " 4. About Program\n"
            " 5. Exit Program\n"
            )
        
            
        selection = input("Select Menu Option (1 - 5): ").strip()


        if selection == "1":
            if taskList(tasks):
                tasks = AddTasks(tasks)
            else:
                pass
        elif selection == "2":
            avl_time = int(available_Time())
        elif selection == "3":
            planName, plan, planTime = CreatePlan(tasks, avl_time)
            if not plan or not planTime:
                continue
             
            print("Plan succesfully created!")
            if conditional_hlp("View plan?"):
                view_Plan(planName, plan, planTime, avl_time)
                if conditional_hlp("Manage plan?"):
                    after_plan_menu(plan, planTime, avl_time, planName, tasks)                
        elif selection == '4':
            About()
        elif selection == '5':
            print("Have nice day!")
            break
        else:      
            print("Invalid Input, please enter a digit between 1 and 4.")

def after_plan_menu(plan, plan_time, avl_time, planName, tasks):
    """View screen post plan"""
    while True:
        print("---------------------------------\n"
            "         Task Planner\n"
            "---------------------------------\n\n\n\n")
        print("\nPost-Plan Menus:")
        print("1. Sort Plan")
        print("2. Add Breaks")
        print("3. Export to CSV")
        print("4. Edit Plan")
        print("5. Return to Main Menu")
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            print("Sorting plan")
            sort_type = input("Sort by 'id' or 'duration'?: ").strip().lower()
            data = {"sort_key": sort_type, "plan": plan}
            plan = call_server(5557, data)
        elif choice == "2":
            print("Adding breaks")
            data = {"plan": plan, "plan_time": plan_time, "allocated_time": avl_time}
            plan = call_server(5559, data)
        elif choice == "3":
            print("creating CSV file")
            data = {"plan_name": planName, "plan": plan, "plan_time": plan_time, "allocated_time": avl_time}
            call_server(5564, data)
        elif choice == "4":
            data =  updatePlan(plan, tasks ,plan_time)
            updated_plan = call_server(5555, data)
            plan = updated_plan['plan']
        elif choice == "5":
            break
        else:
            print("Input not recognized.")

def taskList(tasks):
    """Allows user to view and prompts to add tasks that will be stored in a task list"""
    
    print("---------------------------------\n"
          "   Task list\n"
          "---------------------------------\n\n\n\n"
          "### Current tasks:"
    )

    for i, key in enumerate(tasks, start = 1):
        print(f"{i}. {key['id']}: {key['duration']}")
    
    return conditional_hlp("Add more tasks?")
        
        



def AddTasks(tasks):
    """Allows user to Add tasks"""
    print("---------------------------------\n"
          "   Add Tasks\n"
          "---------------------------------\n\n\n\n"
          "Enter tasks following the format below:\n"
          "(Task name, task length in minutes)\n"
          "Example: (Laundry, 120)\n\n"
          "## Enter [done] when finished adding tasks.\n"
          "***Entering [done] will navigate back to Main Menu\n")
    
    if conditional_hlp("Need help converting hours to minutes?"):
        while True:
            convert = input("Enter hours value (EX: 2.5): ")
            try:
                inMin = float(convert)*60
                print(f"{convert} hours is {inMin} minutes" )
                break
            except ValueError:
                print("Invalid input. Please enter a number")

    taskFormat = r'^\s*([A-Za-z ]+),\s*(\d+)'
    while True:
        newTask = input("Enter task: ").strip().lower()
        if newTask == "done":
            if conditional_hlp("Are you sure you're done adding tasks? "):
                return tasks
            else:
                pass
        validFormat = re.match(taskFormat, newTask)
        if  validFormat:
            name = validFormat.group(1).strip()
            duration = int(validFormat.group(2))
            
            newTask = {
                "id": name,
                "duration": duration, 
            }
            tasks.append(newTask)

            print(f"Task Added: {newTask}")
        else:
            print("Invalid Input, please follow format: task name, duration(in digits), unit of time 'h' (hours) or 'm' (minutes).")

def available_Time():
    """Adds available time to an optimized plan"""


    print("---------------------------------\n"
          "   Available Time\n"
          "---------------------------------\n\n\n\n"
          "Enter time in format of minutes\n"
          "Example: 180 \n\n")
    
    while True:
        taskTimes = input("Enter amount of time availble to work on tasks: ")
        if not taskTimes.isdigit():
            print("Please enter a digit variable ")
        else:
            if conditional_hlp(f"You entered {taskTimes} is this correct?"):
                return int(taskTimes)
        
def CreatePlan(tasks, timeAvailable):
    """Returns an optimized plan"""


    print("---------------------------------\n"
          "   Create Plan\n"
          "---------------------------------\n\n\n\n")
    for i, key in enumerate(tasks, start = 1):
        print(f"{i}. {key['id']}: {key['duration']}")

    print(f"[Allocated time: {timeAvailable} minutes \n\n]"      
          "**Caution New plan will need to be generated if time or tasks are not included**\n")
    
    if conditional_hlp("Confirm task and available time are correct?"):
        planName = input("Please provide a plan name: ")
        n = len(tasks)  #tasks in tasks list

        duration = [task['duration'] for task in tasks]  #creates a list of all the times i have available
        vals = [[0 for x in range(n+1)] for t in range(timeAvailable + 1)]


        for t in range(1, timeAvailable +1):
            for x in range (1, n+1):
                taskDuration = duration[x-1]

                if taskDuration <= t:   #confirm the current time available is greater than the time it takes to finish this task
                    vals[t][x] = max( vals[t][x - 1], vals[t-taskDuration][x-1]+ taskDuration)
                else:
                    vals[t][x] = vals[t][x-1]

        plannedTasks = []
        t = timeAvailable
        for x in range(n, 0, -1):
            if vals[t][x] != vals[t][x-1]:
                plannedTasks.append(tasks[x-1])
                t -= tasks[x-1]['duration']
        usedTime = vals[timeAvailable][n]

        return planName, plannedTasks, usedTime
    else:
        print("Add tasks by selecting 1 in main menu")
        return

# Citation: 
# Source: https://www.geeksforgeeks.org/python/enumerate-in-python/
# Accessed: 7/28/2025
# Adopted: Formatting of enumerate loop 
def view_Plan(planName, plannedTasks, usedTime, time):
    "displays the optimal plan to users"

    print("---------------------------------\n"
        f"  {planName}\n"
        "---------------------------------\n\n\n\n"
        "Here's your plan for today!\n")
    
    for i, key in enumerate(plannedTasks, start = 1):
        print(f"{i}. {key['id']}: {key['duration']}")
    
    print(f"This plan uses {usedTime} minutes of {time} minutes available.\n",
          "## This plan is an optimal plan that has leveragred dynamic programming to generate a solution of tasks" \
          "that efficeintly use the majority of available time.")

def updatePlan(plan, tasks,plantime):
    """this function allows the user to select a task to swap"""
    data = {'action': 'update_plan',}
    remove = input("Enter name of task to remove (as show in plan): ")
    data['remove'] = remove
    if conditional_hlp("Would you like to add a task to the plan?"):
        print("Task list \n")
        for i, key in enumerate(tasks, start = 1):
            print(f"{i}. {key['id']}: {key['duration']}")
        add = input("Enter name of task you would like to add to plan\n" \
        "*** Match naming format: ")
        for task in tasks:
            if task["id"].lower() == add.lower():
                data['add'] = task
            else:
                data['add'] = {'id': add, 'duration': 0}
    data['plan'] = plan
    data['allocated_time'] = plantime
    return data

    
def About():
    """Short description about this program"""
    
    print("---------------------------------\n"
        "  About this Program\n"
        "---------------------------------\n\n\n\n"
        "This program helps the user to create an efficient task plan"
        "by maximizing the amount of available time spent on completing tasks.\n"
        "Behind the scenes we leverage a dynamic programming algorithm similiar to the (0/1)KnapSack solution. The algorithm" \
        "ensures that each plan is utilizing the maximum possible time available to complete full tasks!")
        
def call_server(port, data):
    #microservice request
    context = zmq.Context()
    
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{port}")

    
    print("\nSending request")
    socket.send_json(data)  # use send_json since all requests will be in JSON format

        # get the reply from the server
    reply = socket.recv_json()
    print(reply)
    return reply

    
    
    
if __name__ == "__main__":
    MainMenu()
    


    

       

    

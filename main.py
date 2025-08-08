import re
import zmq
import time

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
            )
        
            
        selection = input("Select Menu Option (1 - 4): ").strip()


        if selection == "1":
            moreTasks = TaskList(tasks)
            if moreTasks == 'y':
                tasks = AddTasks(tasks)
            else:
                pass
        elif selection == "2":
            time = int(AvailableTime())
        elif selection == "3":
            planName, plan, planTime = CreatePlan(tasks, time)
            if not plan or not planTime:
                pass
            else: 
                print("Plan succesfully created!")
                viewPlan = input("View plan?(y/n): ").strip().lower()
                if viewPlan == 'y':
                    ViewPlan(planName, plan, planTime, time)
                    taskswap = input("Would you like to swap a task?(y/n)").strip().lower()
                    if taskswap == 'y':
                        data = updatePlan(plan, tasks, planTime)
                        plan = main(5555, data)

                        
                        
                
        elif selection == '4':
            About()
        else:
                    
            print("Invalid Input, please enter a digit between 1 and 4.")

        

def TaskList(tasks):
    """Allows user to view and prompts to add tasks that will be stored in a task list"""
    
    print("---------------------------------\n"
          "   Task list\n"
          "---------------------------------\n\n\n\n"
          "### Current tasks:"
    )

    for i, key in enumerate(tasks, start = 1):
        print(f"{i}. {key['id']}: {key['duration']}")
    
    while True:
        
        moreTasks = input("Add more tasks? (y/n): ").strip().lower()
        valid = ["y", "n"]
        if moreTasks.lower() in valid:
            return moreTasks
        print("Please enter y (yes) or n (no)\n")



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
    conversion = input("Need help converting hours to minutes?(y/n): ").strip().lower()
    if conversion == 'y':
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
            confirmation = input("Are you sure your done adding tasks? (y or (n): )").strip().lower()
            if confirmation == ('y'):
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

def AvailableTime():
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
            checkTime = input(f"You entered {taskTimes} is this correct?(y/n):  ").strip().lower()
            if checkTime == 'y':
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
    
    ready = input("Confirm task and available time are correct (y/n): ")
    if ready.lower() in ('y', 'Y'):

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
def ViewPlan(planName, plannedTasks, usedTime, time):
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
    addTask = input("Would you like to add a task to the plan? (y/n): ").lower().strip()
    if addTask == 'n':
        pass
    else:
        print(f"Task list \n")
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
    print(data)
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
        
def main(port, data):
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
    


    

       

    

from matplotlib.ticker import MaxNLocator
from prettytable import PrettyTable
import matplotlib.pyplot as plt

# create a pretty table to save the processes' data
table = PrettyTable()


# input process data
def inputProcessData(num):
    # list of processes' data
    data = []

    # input information
    for i in range(num):
        process_id = i + 1

        arrival_time = int(input(f"Enter Arrival Time of Process {process_id}: "))

        burst_time = int(input(f"Enter Burst Time of Process {process_id}: "))

        # 0 means not executed and 1 means execution is complete
        data.append([process_id, arrival_time, burst_time, 0, burst_time])

    q = int(input('Enter Time Period: '))

    schedulingProcess(data, q)


# RR Scheduling
def schedulingProcess(data, q):
    start_time = []
    finish_time = []
    executed_process = []  # to save processes' execution sequence
    ready_queue = []  # to stores all the processes that have already arrived
    s_time = 0

    # Sort processes according to the Arrival Time
    data.sort(key=lambda x: x[1])

    # execute processes until all the processes are complete
    while True:
        notArrived_queue = []  # to store all the processes that haven't arrived yet

        # check if the next process is not a part of ready_queue
        for i in range(len(data)):
            if data[i][1] <= s_time and data[i][3] == 0:
                present = 0
                if len(ready_queue) != 0:
                    for k in range(len(ready_queue)):
                        if data[i][0] == ready_queue[k][0]:
                            present = 1

                # add a process to the ready_queue if it is not already present in it
                if present == 0:
                    ready_queue.append([data[i][0], data[i][1], data[i][2], data[i][4]])

                # make sure that the recently executed process is appended at the end of ready_queue
                if len(ready_queue) != 0 and len(executed_process) != 0:
                    for k in range(len(ready_queue)):
                        if ready_queue[k][0] == executed_process[len(executed_process) - 1]:
                            ready_queue.insert((len(ready_queue) - 1), ready_queue.pop(k))

            elif data[i][3] == 0:
                notArrived_queue.append([data[i][0], data[i][1], data[i][2], data[i][4]])

        # end while true loop if both queues are empty
        if len(ready_queue) == 0 and len(notArrived_queue) == 0:
            break

        if len(ready_queue) != 0:

            # If process has remaining burst time greater than the time period,
            # it will execute for a time period equal to time period and then switch
            if ready_queue[0][2] > q:

                start_time.append(s_time)
                s_time = s_time + q
                f_time = s_time
                finish_time.append(f_time)
                executed_process.append(ready_queue[0][0])
                for j in range(len(data)):
                    if data[j][0] == ready_queue[0][0]:
                        break
                data[j][2] = data[j][2] - q
                ready_queue.pop(0)

            # If a process has a remaining burst time less than or equal to time period,
            # it will complete its execution
            elif ready_queue[0][2] <= q:

                start_time.append(s_time)
                s_time = s_time + ready_queue[0][2]
                f_time = s_time
                finish_time.append(f_time)
                executed_process.append(ready_queue[0][0])
                for j in range(len(data)):
                    if data[j][0] == ready_queue[0][0]:
                        break
                data[j][2] = 0
                data[j][3] = 1
                data[j].append(f_time)
                ready_queue.pop(0)

        elif len(ready_queue) == 0:
            if s_time < notArrived_queue[0][1]:
                s_time = notArrived_queue[0][1]

            if notArrived_queue[0][2] > q:

                # If process has remaining burst time greater than the time period,
                # it will execute for a time period equal to time period and then switch
                start_time.append(s_time)
                s_time = s_time + q
                f_time = s_time
                finish_time.append(f_time)
                executed_process.append(notArrived_queue[0][0])
                for j in range(len(data)):
                    if data[j][0] == notArrived_queue[0][0]:
                        break
                data[j][2] = data[j][2] - q

            # If a process has a remaining burst time less than or equal to time period,
            # it will complete its execution
            elif notArrived_queue[0][2] <= q:

                start_time.append(s_time)
                s_time = s_time + notArrived_queue[0][2]
                f_time = s_time
                finish_time.append(f_time)
                executed_process.append(notArrived_queue[0][0])
                for j in range(len(data)):
                    if data[j][0] == notArrived_queue[0][0]:
                        break
                data[j][2] = 0
                data[j][3] = 1
                data[j].append(f_time)

    # calculate turnaround time
    turnaround = calculateTurnaroundTime(data)

    # calculate waiting time
    waiting = calculateWaitingTime(data)

    # print data
    printData(data, turnaround, waiting, executed_process)

    # make plot
    showPlot(executed_process, q, start_time, finish_time)


# make plot
def showPlot(executed_process, q, start_time, finish_time):
    # create a dictionary to save each process execution time to create plot
    dic = {}

    # add process data to dic
    for i in range(len(executed_process)):
        try:
            dic[str(executed_process[i])].extend([(start_time[i], finish_time[i] - start_time[i])])
        except:
            dic[str(executed_process[i])] = [(start_time[i], finish_time[i] - start_time[i])]

    # create a sub plot
    fig, ax = plt.subplots()

    # create plot bars
    i = 0
    color = 1
    for item, item2 in dic.items():
        ax.broken_barh(item2, (10 + i, 10), facecolors=('C' + str(color)))
        color += 1
        i += 10

    # customize axes
    ax.set_xlabel(f'Round Robin Process Scheduling, Q:{q}')

    # set y axis labels
    ax.set_yticks(list(range(10, len(dic) * 10 + 1, 10)))
    ax.set_yticklabels(dic.keys())

    # set x axis tickers with integer values
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.invert_yaxis()
    ax.autoscale()
    plt.grid(True)

    # show plot
    plt.show()


# calculate each process turnaround time and append it at the end of process data list
# return average turnaround time
def calculateTurnaroundTime(data):
    total_turnaround_time = 0

    for i in range(len(data)):

        # turnaround_time = completion_time - arrival_time
        turnaround_time = data[i][5] - data[i][1]

        total_turnaround_time = total_turnaround_time + turnaround_time
        data[i].append(turnaround_time)

    # average_turnaround_time = total_turnaround_time / no_of_processes
    average_turnaround_time = total_turnaround_time / len(data)

    return average_turnaround_time


# calculate each process waiting time and append it at the end of process data list
# return average waiting time
def calculateWaitingTime(data):
    total_waiting_time = 0
    for i in range(len(data)):

        # waiting_time = turnaround_time - burst_time
        waiting_time = data[i][6] - data[i][4]

        total_waiting_time = total_waiting_time + waiting_time
        data[i].append(waiting_time)

    # average_waiting_time = total_waiting_time / no_of_processes
    average_waiting_time = total_waiting_time / len(data)

    return average_waiting_time


# print data
def printData(data, average_turnaround_time, average_waiting_time, executed_process):
    # Sort processes according to the Process ID
    data.sort(key=lambda x: x[0])

    # add fields name to pretty table
    table.field_names = ['ID', 'Arrival', 'Remaining', 'isCompleted', 'BurstTime', 'FinishTime', 'Turnaround', 'Waiting']

    # add data to pretty table
    for i in range(len(data)):
        table.add_row(data[i])

    # print pretty table
    print(table)

    print(f'Average Turnaround Time: {average_turnaround_time}')

    print(f'Average Waiting Time: {average_waiting_time}')

    # print execution sequence of processes
    print(f'Sequence of Processes: {executed_process}')


# main block
if __name__ == "__main__":
    processes = int(input("Enter number of processes: "))
    inputProcessData(processes)

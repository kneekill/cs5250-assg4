'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
from queue import Queue
from heapq import heappop, heappush

input_file = 'input.txt'
INITIAL_EXPECTED_BURST = 5

class PeekableQueue(Queue):
    def peek(self):
        return self.queue[0]

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))
    
    def __lt__(self,other):
        if(self.remaining_time < other.remaining_time):
            return True
        elif self.remaining_time == other.remaining_time:
            return self.arrive_time < other.arrive_time
        else:
            return False

#resetting remaining_time
def cleanup(process):
    process.remaining_time = process.burst_time

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    ready_q = PeekableQueue()
    process_q = PeekableQueue()
    curr_time = 0
    schedule = []
    total_waiting_time = 0
    last_scheduled_process = -1
    list(map(process_q.put, process_list))    
    while not process_q.empty() or not ready_q.empty():
        if ready_q.empty():
            curr_process = process_q.get()
            curr_time = curr_process.arrive_time
            ready_q.put(curr_process)
        # checking if any other processes are within tq
        while(not process_q.empty()):
            process_q_head = process_q.peek()
            if(curr_time+time_quantum >= process_q_head.arrive_time):
                ready_q.put(process_q.get())
            else:
                break
        curr_process = ready_q.get()
        if last_scheduled_process != curr_process.id:
            schedule.append((curr_time, curr_process.id))
            last_scheduled_process = curr_process.id
        time_spent = min(time_quantum, curr_process.remaining_time)
        curr_time += time_spent
        curr_process.remaining_time -= time_spent
        if(curr_process.remaining_time>0):
            ready_q.put(curr_process)
        else:
            total_waiting_time += curr_time - curr_process.arrive_time - curr_process.burst_time
    list(map(cleanup, process_list))
    return schedule, total_waiting_time/float(len(process_list))
    # return (["to be completed, scheduling process_list on round robin policy with time_quantum"], 0.0)

def SRTF_scheduling(process_list):
    curr_time = 0
    ready_q = []
    process_q = PeekableQueue()
    total_waiting_time = 0
    schedule = []
    last_scheduled_process = -1
    list(map(process_q.put, process_list))
    while ready_q or not process_q.empty():
        if not ready_q:
            curr_process = process_q.get()
            curr_time = curr_process.arrive_time
            heappush(ready_q,curr_process)
        while(not process_q.empty()):
            process_q_head = process_q.peek()
            if(curr_time >= process_q_head.arrive_time):
                heappush(ready_q,process_q.get())
            else:
                break
        curr_process = heappop(ready_q)
        if last_scheduled_process != curr_process.id:
            schedule.append((curr_time,curr_process.id))
            last_scheduled_process = curr_process.id
        curr_time += 1
        curr_process.remaining_time -= 1
        if(curr_process.remaining_time>0):
            heappush(ready_q,curr_process)
        else:
            total_waiting_time += curr_time - curr_process.arrive_time - curr_process.burst_time
    list(map(cleanup, process_list))
    return (schedule, total_waiting_time/float(len(process_list)))

def get_new_prediction(tn, tau, alpha):
    return alpha * tn + (1- alpha) * tau

def SJF_scheduling(process_list, alpha):
    schedule = []
    ready_q = []
    process_q = PeekableQueue()
    n = 0
    curr_time = 0
    for process in process_list:
        if(process.id > n):
            n = process.id
        process_q.put(process)
    n += 1
    last_scheduled_process = -1
    # previous_burst = [0] * n
    expected_burst = [INITIAL_EXPECTED_BURST] * n
    ready_q_ids = []
    curr_min_expected_burst = sys.maxsize
    min_ready_q_index = -1
    total_waiting_time = 0
    while ready_q or not process_q.empty():
        if not ready_q:
            curr_process = process_q.get()
            if(curr_time < curr_process.arrive_time):
                curr_time = curr_process.arrive_time
            ready_q.append(curr_process)
            ready_q_ids.append(curr_process.id)
        while(not process_q.empty()):
            process_q_head = process_q.peek()
            if(curr_time >= process_q_head.arrive_time):
                ready_q.append(process_q.get())
            else:
                break
        #getting the lowest minimum expected burst in the ready_q
        for index, process in enumerate(ready_q):
            if(expected_burst[process.id] < curr_min_expected_burst):
                curr_min_expected_burst = expected_burst[process.id]
                min_ready_q_index = index
        curr_min_expected_burst = sys.maxsize
        executing_proc = ready_q[min_ready_q_index]
        process_id = executing_proc.id
        total_waiting_time += curr_time - executing_proc.arrive_time
        if last_scheduled_process != process_id:
            schedule.append((curr_time, process_id))
            last_scheduled_process = process_id
        curr_time += executing_proc.burst_time
        expected_burst[process_id] = get_new_prediction(executing_proc.burst_time,expected_burst[process_id],alpha)
        del ready_q[min_ready_q_index]
    return (schedule,total_waiting_time/float(len(process_list)))


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])


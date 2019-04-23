import sys
from simulator import FCFS_scheduling, RR_scheduling, SJF_scheduling, read_input, write_output

def find_best_tq(process_list):
    best_tq = 0
    best_schedule= []
    best_waiting_time = sys.maxsize
    max_tq = 0
    for process in process_list:
        if process.burst_time > max_tq:
            max_tq = process.burst_time
    for tq in range(1,max_tq+1):
        schedule, ave_waiting_time = RR_scheduling(process_list,tq)
        if ave_waiting_time < best_waiting_time:
            best_schedule = schedule
            best_waiting_time = ave_waiting_time
            best_tq = tq
    write_output('optimum_rr.txt', best_schedule, best_waiting_time)
    with open('optimum_rr.txt','a') as f:
        f.write('optimum time quantum %d \n'%(best_tq))

def find_best_alpha(process_list):
    best_alpha = 0
    best_schedule = 0
    best_waiting_time = sys.maxsize
    for alpha in range(1,101):
        alpha = float(alpha)/100
        schedule, ave_waiting_time = SJF_scheduling(process_list,alpha)
        if(ave_waiting_time < best_waiting_time):
            best_waiting_time = ave_waiting_time
            best_schedule = schedule
            best_alpha = alpha
    write_output('optimum_sjf.txt', best_schedule, best_waiting_time)
    with open('optimum_sjf.txt','a') as f:
        f.write('optimum alpha %.2f \n'%(best_alpha))


def main(argv):
    process_list = read_input()
    find_best_tq(process_list)
    find_best_alpha(process_list)


if __name__ == '__main__':
    main(sys.argv[1:])

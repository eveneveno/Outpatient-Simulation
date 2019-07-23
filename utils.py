import random
import scipy
from scipy import stats
import pdb
import math
import numpy as np
import pandas as pd
import prettytable as pt

# -------------------------------------------------------------------------------------------------------
import argparse
parser = argparse.ArgumentParser(description='Outpatient Simulation')
parser.add_argument('--sim_end',            type = int, default = 720)
parser.add_argument('--p_showup',           type = float, default = 2/5)
parser.add_argument('--walk_in_rate',       type = float, default = 1/10)
parser.add_argument('--arrival_rate_blood', type = float, default = 1/15)
parser.add_argument('--arrival_rate_scan',  type = float, default = 1/25)
parser.add_argument('--num_node',           type = list,  default = [1,2,3])
parser.add_argument('--mute',               type = bool,  default = False)
args = parser.parse_args()

trans_prob = np.array([[0,   0.6, 0.3],
                        [0.5, 0,   0.5],
                        [1,   0,   0  ]])
walk_time = np.zeros(trans_prob.shape)

# ----------------------------------------Global Variable------------------------------------------------
#################################################
# Mode MUTE: print some points
MUTE = args.mute
RECORD = True
#################################################

# Random Seed for Reproducing
RAN_SEED = 2019
random.seed(RAN_SEED)
scipy.random.seed(42)

# Global Variable
DIGITS = 5               # Number of digits of patient ID (eg., '00001')
SIM_END = args.sim_end   # End Time of Simulation (mins)

NUM_CHECK = 2            # number of check service (blood + scan)
NUM_STEP = NUM_CHECK + 2 # temp number (plus doctor and revisit) (for result table)

SLOT = 5.0               # slot duration 
Now_step = 0.0           # Time Stamp

# for print
Name_waiting_place = {0: "Doctor", 1: "Blood", 2: "Scan", 3: "Revisit",
                      2019:"Go Home", 2020:"Go Home", 2000:"Other Doctor"} 

# for colorful hightlight
Clear  = "\033[0m" 
Red    = "\033[1;31m" # bold 
Green  = "\033[32m"
Yellow = "\033[33m" 
Blue   = "\033[34m"

max_id = 0
all_patient = []

def print_update(color, count, type, id):
    print("------------------------------------------------------------")
    print(color+'Event Count: {} Current Time: {:.2f} \nActive Station: {}-{} '.format(
            count, Now_step, Name_waiting_place[type], id)+Clear)

def write_update(count, type, id, file):
    file.write("--------------------------------------------------------\n")
    file.write('Event Count: {} Current Time: {:.2f} \nActive Station: {}-{}\n'.format(
            count, Now_step, Name_waiting_place[type], id))

def print_transit(color, TO, patient, type):
    print(Green+"Patient ID: {}".format(patient.id)+Clear)

    if TO == 1 or TO == 2:
        if Name_waiting_place[type] != 'Doctor':
            print(color+"At {}\tStart: {:.2f}, Finish: {:.2f}, Report: {:.2f}\nTo {}\tArrive: {:.2f}".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2], patient.time[type][3],
                Name_waiting_place[TO], patient.time[TO, 0])+Clear)
        else:
            print(color+"At {}\tStart: {:.2f}, Finish: {:.2f}\nTo {}\tArrive: {:.2f}".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2],
                Name_waiting_place[TO], patient.time[TO, 0])+Clear)           
    elif TO == 0:
        print(color+"At {}\tStart: {:.2f}, Finish: {:.2f}, Report: {:.2f}\nTo {}\tArrive: {:.2f}".format(
            Name_waiting_place[type], patient.time[type][1], patient.time[type][2], patient.time[type][3],
            Name_waiting_place[TO], patient.time[-1, 0])+Clear)    

    elif TO == 2019:
        print(color+"At {}\tStart: {:.2f}, Finish: {:.2f}\nTo{}\tArrive: N/A".format(
            Name_waiting_place[type], patient.time[-1][1], patient.time[-1][2],
            Name_waiting_place[TO])+Clear)
    else: 
        if Name_waiting_place[type] != 'Doctor':
            print(color+"At {}\tStart: {:.2f}, Finish: {:.2f}, Report: {:.2f}\nTo {}\tArrive: N/A".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2], patient.time[type][3],
                Name_waiting_place[TO])+Clear) 
        else:
            print(color+"At {}\tStart: {:.2f}, Finish: {:.2f}\nTo {}\tArrive: N/A".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2],
                Name_waiting_place[TO])+Clear) 

def write_transit(TO, patient, type, file):
    file.write("========== Patient ID: {} ==========\n".format(patient.id))

    if TO == 1 or TO == 2:
        if Name_waiting_place[type] != 'Doctor':
            file.write("At {}\tStart: {:.2f}, Finish: {:.2f}, Report: {:.2f}\nTo {}\tArrive: {:.2f}\n".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2], patient.time[type][3],
                Name_waiting_place[TO], patient.time[TO, 0]))
        else:
            file.write("At {}\tStart: {:.2f}, Finish: {:.2f}\nTo {}\tArrive: {:.2f}\n".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2],
                Name_waiting_place[TO], patient.time[TO, 0]))           
    elif TO == 0:
        file.write("At {}\tStart: {:.2f}, Finish: {:.2f}, Report: {:.2f}\nTo {}\tArrive: {:.2f}\n".format(
            Name_waiting_place[type], patient.time[type][1], patient.time[type][2], patient.time[type][3],
            Name_waiting_place[TO], patient.time[-1, 0]))    

    elif TO == 2019:
        file.write("At {}\tStart: {:.2f}, Finish: {:.2f}\nTo{}\tArrive: N/A\n".format(
            Name_waiting_place[type], patient.time[-1][1], patient.time[-1][2],
            Name_waiting_place[TO]))
    else: 
        if Name_waiting_place[type] != 'Doctor':
            file.write("At {}\tStart: {:.2f}, Finish: {:.2f}, Report: {:.2f}\nTo {}\tArrive: N/A\n".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2], patient.time[type][3],
                Name_waiting_place[TO])) 
        else:
            file.write("At {}\tStart: {:.2f}, Finish: {:.2f}\nTo {}\tArrive: N/A\n".format(
                Name_waiting_place[type], patient.time[type][1], patient.time[type][2],
                Name_waiting_place[TO])) 

def write_info(patient, file):
    s = ""
    for i in range(patient.time.shape[0]):
        s += Name_waiting_place[i]+"\t"
        for j in patient.time[i]:
            if j is not None:
                j = "{:.2f}".format(j)
            s += str(j)+"\t"
        s += "\n"
    file.write(s)

# save patient records
SAVE = [[],[],[]]

# ----------------------------------------Random number generator--------------------------------------------
class Generator(object):
    def Exponential(self, lamda):
        assert lamda > 0
        return stats.expon.rvs(1/lamda, 1)
    # def Exponential(self, lamda):
    #     return random.expovariate(lamda)

    def Bernoulli(self, p):
        assert p >= 0 and p <= 1
        if random.random() <= p:
            return 1
        else:
            return 0
    # def Bernoulli(self, p):
    #     return np.random.binomial(1, p)
Generator = Generator()

# Since doctor must operate in time slot (identify which slot)
def Ceil_Slot(t):
    return math.ceil(t / SLOT) * SLOT

# visualize record
def Visualize(SAVE):
    
    col_names = ["patient_id","arrive_time","begin_time","finish_time","None","doctor_id",
                 "blood_arrive_time","blood_begin_time","blood_finish_time","blood_report_time","blood_id",
                 "scan_arrive_time","scan_begin_time","scan_finish_time","scan_report_time","scan_id",
                 "revisit_arrive_time","revisit_begin_time","revisit_finish_time","None","revisit_id"]
    for i in range(3):
        L = SAVE[i]
        rows_list = []
        for row in L:
            LL = [row.id]
            dict1 = row.time.reshape(-1)
            L1 = dict1.tolist()
            rows_list.append(LL+L1)
        df = pd.DataFrame(rows_list, columns = col_names)

        # save in .csv   
        name = Name_waiting_place[i]
        df.to_csv("./result/"+name+".csv")

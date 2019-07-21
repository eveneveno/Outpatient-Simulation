import utils as H
from Patient import *
from Waiting_Place import *
from Serve_Place import *
import numpy as np
import random
import pdb

import argparse
parser = argparse.ArgumentParser(description='Outpatient Simulation')
parser.add_argument('--p_showup',           type = float, default = 4/5)
parser.add_argument('--walk_in_rate',       type = float, default = 1/5)
parser.add_argument('--arrival_rate_blood', type = float, default = 1/15)
parser.add_argument('--arrival_rate_scan',  type = float, default = 1/25)
parser.add_argument('--num_node',          type = list,  default = [1,2,3])
random.seed(H.RAN_SEED)
args = parser.parse_args()

p_showup           = args.p_showup
walk_in_rate       = args.walk_in_rate
arrival_rate_blood = args.arrival_rate_blood
arrival_rate_scan  = args.arrival_rate_scan
num_node           = args.num_node

# trans_prob
trans_prob = np.array([[0,   0.6, 0.3],
                        [0.5, 0,   0.5],
                        [1,   0,   0  ]])

#################################################
# Mode MUTE: print some points
MUTE = False
RECORD = True
#################################################

class Simulation(object):
    def __init__(self, num_node, trans_prob, walk_time):
        # network design
        self.net = [[Doctor([0.6, 0.8]) for _ in range(num_node[0])], 
                    [Blood_Service() for _ in range(num_node[1])], 
                    [Scan_Service() for _ in range(num_node[2])]]

        self.waiting_place = [Doctor_Place (True, p_showup, walk_in_rate), 
                              Waiting_Place(1, True, arrival_rate_blood), 
                              Waiting_Place(2, True, arrival_rate_scan)]

        self.cusum_prob = np.cumsum(trans_prob, axis=1)
        self.walk_time = walk_time

    def run(self):

        txt_file = open("./result/events.txt", "w")

        count = 0
        while H.Now_step < H.SIM_END:
            # select next time stop
            H.Now_step, type, id = self.next()
            if H.Now_step >= H.SIM_END: 
                break
            patient = self.waiting_place[type].send_patient()
            assert isinstance(patient, Patient)
            
            if not MUTE:
                H.print_update(H.Red, count, type, id)
            if RECORD:
                H.write_update(count, type, id, txt_file)

            # operate next
            before_State = patient.isRevisit() # the state before serve 
            patient = self.net[type][id].work(patient)
            
            # transmit the patient
            TO = None
            if before_State and type == 0: # revisit doctor.
                TO = 2019 # leave hospital
            else:
                if len(patient.checklist) == 0:
                    if len(patient.check_list) == 0:
                        TO = 2020 # leave hospital
                    else:
                        TO = 0
                        if patient.time[0, -1] == 0: 
                            last = self.argmax_report_time(patient)
                            patient.time[-1, 0] = patient.time[last, 3] + self.walk_time[last, 0]
                            self.waiting_place[TO].add_patient(patient, True)
                        else: 
                            TO = 2000 # for extneral arrivals, send to other doctors
                else:
                    TO = patient.checklist.pop(0)
                    patient.time[TO, 0] = patient.time[type, 2] + self.walk_time[type, TO]
                    self.waiting_place[TO].add_patient(patient)

            if not MUTE: 
                H.print_transit(H.Yellow, TO, patient, type)  
            if RECORD:
                H.write_transit(TO, patient, type, txt_file)
            count += 1
            if not MUTE:
                patient.print_info()
            if RECORD:
                H.write_info(patient, txt_file)
            
    # In all service and doctor (including busy servers, find min(all servers' max(finish_time, expected_time))
    def next(self):
        type, id = None, None
        m = H.SIM_END
        for i in range(len(self.net)):
            expected_time = self.waiting_place[i].next_patient()
            for j in range(len(self.net[i])):
                temp = max(expected_time, self.net[i][j].finish_time)
                if temp < m:
                    type, id = i, j
                    m = temp
        return m, type, id    
        
    def argmax_report_time(self, patient):
        idx = None
        M = -1
        for i in range(1, len(patient.time[:-1, 3])):
            if patient.time[i, 3] is not None and patient.time[i, 3] > M:
                M = patient.time[i, 3]
                idx = i
        assert M >= 0
        return idx
        
if __name__ == "__main__":

    # simuation setting
    # sim = Simulation([1,2,3], trans_prob, np.zeros(trans_prob.shape))
    sim = Simulation(num_node, trans_prob, np.zeros(trans_prob.shape))
    
    # run simulatinon 
    sim.run()

    # save .csv records for each station
    H.Visualize(H.SAVE)
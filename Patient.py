import utils as H
import numpy as np
import prettytable as pt

# Patient Class
class Patient(object):
    ID_generate = 0 # to generate unique ID for patients
    def __init__(self, select = 0, arrive_time = None):
        self.id = str(Patient.ID_generate).zfill(H.DIGITS) # to identify patient
        Patient.ID_generate += 1
        
        self.revisit = False # to indentify whether he/she has seen the doctor
        
        # time: record all kinds of time
        # Row: 0-doctor, 1-blood, 2-scan, 3(namely -1)-revisit
        # Col: 0-arrival_time(for queue), 1-begin_time, 2-finish_time, 3-report_time, 4-Doctor/Service ID
        self.time = np.full((H.NUM_STEP, 5), None)
        self.time[select, 0] = arrive_time
        self.check_list = [] # operation list
        self.checklist =  [] # just temp operation list
        
    # to solve when the PriorityQueue have same key
    def __lt__(self, a):
        return True
    
    def isRevisit(self):
        return self.revisit

    def print_info(self):
        tb = pt.PrettyTable()
        tb.field_names = ["Station", "Arrival", "Start", "End", "Report", "ID"]
        for i in range(self.time.shape[0]):
            row = [H.Name_waiting_place[i]]
            for j in self.time[i]:
                if j is not None:
                    row.append("{:.2f}".format(j))
                else: 
                    row.append(str(j)) 
            tb.add_row(row)
        print(tb)
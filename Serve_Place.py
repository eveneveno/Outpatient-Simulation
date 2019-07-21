import utils as H
from copy import deepcopy
import numpy as np
import random

# -------------------------------------------------------------------------------------------------------
# This file is for modeling serving process. 
# Their Constructor is for generating doctors or Service.
# The Serve_Place has only one API:
# 1. work(self, patient):
#    Just serve the patient, and return him/her.

class Serve_Place(object):
    # def __init__(self, service_type, service_id, serve_time, report_time):
    def __init__(self, service_type, service_id):
        self.service_type = service_type
        self.id = service_id
        self.finish_time = 0
        
    def work(self, patient):
        patient.time[self.service_type,1] = H.Now_step # service start time 
        if self.service_type == 1: # blood
            serve_time = np.random.uniform(3,6) # uniform 3-6 mins for blood test 
            report_time = random.sample([30, 30, 45],1)[0]
        elif self.service_type == 2:
            serve_time = np.random.uniform(10,15) # uniform 10-15 mins for blood test 
            report_time = 0

        patient.time[self.service_type,2] = H.Now_step + serve_time # service end time 
        patient.time[self.service_type,3] = H.Now_step + serve_time + report_time # service report time
        patient.time[self.service_type,-1] = self.id

        self.finish_time = H.Now_step + serve_time
        H.SAVE[self.service_type].append(deepcopy(patient))
        return patient
    
class Blood_Service(Serve_Place):
    ID_generate = 0 # to generate unique ID for Blood_Service
    def __init__(self):
        # super().__init__(1, Blood_Service.ID_generate, serve_time = 30, report_time = 60)
        super().__init__(1, Blood_Service.ID_generate)
        Blood_Service.ID_generate += 1
    
class Scan_Service(Serve_Place):
    ID_generate = 0 # to generate unique ID for Scan_Service
    def __init__(self):
        # super().__init__(2, Scan_Service.ID_generate, serve_time = 15, report_time = 0)
        super().__init__(2, Scan_Service.ID_generate)
        Scan_Service.ID_generate += 1

class Doctor(object):
    ID_generate = 0 # to generate unique ID for Doctor_Service
    def __init__(self, trans_prob):
        self.service_type = 0
        self.id = Doctor.ID_generate
        self.finish_time = 0
        self.serve_time = H.SLOT
        Doctor.ID_generate += 1
        
        self.trans_prob = trans_prob
        
    def work(self, patient):
        if not patient.isRevisit():
            patient.time[self.service_type,1]  = H.Now_step
            patient.time[self.service_type,2]  = H.Now_step + self.serve_time
            patient.time[self.service_type,-1] = self.id
            self.finish_time = H.Now_step + self.serve_time
            patient.checklist = self.__check_list().copy()
            patient.check_list = patient.checklist.copy()
            H.SAVE[self.service_type].append(deepcopy(patient))
            patient.revisit = True
        else:
            patient.time[-1,1] = H.Now_step
            patient.time[-1,2] = H.Now_step + self.serve_time
            patient.time[-1,-1] = self.id
            self.finish_time = H.Now_step + self.serve_time
            H.SAVE[self.service_type].append(deepcopy(patient))
        return patient
    
    def __check_list(self):
        L = []
        for i in range(len(self.trans_prob)):
            if H.Generator.Bernoulli(self.trans_prob[i]):
                L.append(i+1)
            
        return L
            

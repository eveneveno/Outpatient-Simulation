import utils as H
import queue
from Patient import Patient

# -------------------------------------------------------------------------------------------------------
# This file is for modeling waiting place. And Doctor Place is also a kind of waiting place.
# Their Constructor is for generating patients or adding patients.
# The Waiting_Place (including Doctor_Place) has 3 main APIs:

# 1. add_patient(self, patient):
#    For blood_place or scan_place which has 1 queue, the API just lets the patient inqueue.
#    For doctor_place, the API can let the patient inqueue scheduled queue (default) or revisited queue. 
#    Since the walk-in is Exponential Distribution (memoryless), we can just generate one.

# 2. next_patient(self):
#    Just to return when the next patient appear. 
#    If there is no person now, return the time when the expected next person appears (max is SIM_END).
#    If available, return now.

# 3. send_patient(self):
#    Just return next patient.

class Waiting_Place(object):
    def __init__(self, PlaceType, GENERATE=False, lamda_or_patients=list()):
        self.WaitingQ = queue.PriorityQueue()
        # 0 is Doctor, 1 is blood, 2 is scan
        self.PlaceType = PlaceType # to identify the type of place, need overwrite s
        # ADD external patients
        # If True, Generate ideal patients with Exponential Distribution (lamda) ; else add input patients
        if GENERATE: 
            patients = self.__generate_external(lamda_or_patients)
        else:
            patients = lamda_or_patients
            
        self.__add_external(patients)
        print("Successfully generate patients in {}_Place!".format(H.Name_waiting_place[self.PlaceType]))

    def __generate_external(self, lamda):
        now = 0
        patients = []
        while now < H.SIM_END:
            now += H.Generator.Exponential(lamda)
            patients.append(Patient(self.PlaceType, arrive_time=now))
        return patients
    
    def add_patient(self, patient):
        self.WaitingQ.put((patient.time[self.PlaceType, 0], patient)) 
        
    def __add_external(self, patients):
        for patient in patients:
            self.add_patient(patient)

    def next_patient(self):
        if self.WaitingQ.empty():
            return H.SIM_END
        else:
            return max(self.WaitingQ.queue[0][0], H.Now_step)
        
    def send_patient(self):
        if self.WaitingQ.empty() or self.WaitingQ.queue[0][0] > H.Now_step:
            return None
        else:
            patient = self.WaitingQ.get()[1]
            return patient
    
class Doctor_Place(object):
    def __init__(self, GENERATE=False, prob_or_patients=list(), walk_in_rate=None):
        if GENERATE:
            patients = self.__generate_schedule(prob_or_patients)
        else:
            patients = prob_or_patients
        # the WaitingQ in superclass is scheduled     
        self.WaitingQ = queue.PriorityQueue()

        # 0 is Doctor, 1 is blood, 2 is scan
        self.PlaceType = 0 # to identify the type of place, need overwrite 
        # ADD external patients
        # add input patients

        for patient in patients:
            self.add_patient(patient)
        
        print("Successfully generate patients in {}_Place!".format(H.Name_waiting_place[self.PlaceType]))
        
        # Add walk-in and revisit
        # walk-in
        self.walk_in_rate = walk_in_rate
        self.walkin = queue.Queue() 
        
        walkin_patients = patients = self.__generate_walkin(walk_in_rate)
        for patient in walkin_patients:
            self.add_walkin(patient)

        # revisit 
        self.revisit = queue.Queue()
        
    def __generate_walkin(self, lamda):
        now = 0
        walkin_patients = []
        while now < H.SIM_END:
            now += H.Generator.Exponential(lamda)
            walkin_patients.append(Patient(self.PlaceType, arrive_time=now))
        return walkin_patients

    def add_walkin(self, patient):
        self.walkin.put(patient)

    # scheduled_patients
    def __generate_schedule(self, p):
        patients = []
        i = 0
        while i < H.SIM_END:
            # Here, each slot is generated with equal probability.
            if H.Generator.Bernoulli(p):
                patients.append(Patient(arrive_time=i))
            i += H.SLOT
        return patients
        
    def add_patient(self, patient, revisit=False):
        if revisit:
            self.revisit.put(patient)
        else:
            self.WaitingQ.put((patient.time[self.PlaceType, 0], patient)) 

    # return time (next time stamp) 
    def next_patient(self):
        revisit = self.revisit.queue[0].time[-1, 0] if not self.revisit.empty() else H.SIM_END
        scheduled = self.WaitingQ.queue[0][0] if not self.WaitingQ.empty() else H.SIM_END
        return max(H.Now_step, min(scheduled, H.Ceil_Slot(self.walkin.queue[0].time[0,0]), H.Ceil_Slot(revisit)))

    # return type (which queue) 
    def send_patient(self):
        # Scheduled patient has the highest priority, so ask scheduled queue first.
        if (not self.WaitingQ.empty()) and self.WaitingQ.queue[0][0] <= H.Now_step:
            assert self.WaitingQ.queue[0][0] == H.Now_step # Must serve the scheduled patient at the scheduled time
            patient = self.WaitingQ.get()[1]
            return patient

        else:
            if (not self.revisit.empty()) and H.Ceil_Slot(self.revisit.queue[0].time[-1,0]) <= H.Now_step:
                return self.revisit.get()
            elif H.Ceil_Slot(self.walkin.queue[0].time[0,0]) <= H.Now_step:
                patient = self.walkin.get()
                return patient
            else:
                assert False
                return None, None   
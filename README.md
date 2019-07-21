# Simulation Platform for Hospital #

## 1. Source Code ##

### 1) utils.py ###

- This file includes all global variables and functions.
- Also some extra functions, such as formatted print out with colors

#### Global Variable: ####

- **RAN_SEED**: random seed, to reproduce
- **MUTE**: Mode setting, to print all events
- **Name_waiting_place**, **Red**, **Clear** etc: Lookup table or string
- **SAVE**: list of list to save patient, 0-doctor 1-blood 2-scan

#### Global Function / Class: ####

- **Generator**: class for generate some distribution
  It have 2 methods / functions, **Exponential** and **Bernoulli**.
  And **Generator = Generator()** is to get an instance to call.

- **Ceil_Slot**: Since doctor must operate in a SLOT.

- **Visualize**: to visualize the element of SAVE.
  call (when your main environment is the Simulation.py) or you can call this code in “\_\_main\_\_” of Simulation.py:

  ```python
  >>H.Visualize(H.SAVE).to_csv("请输入文件名.csv")
  ```

### 2) Patient.py ###

- This file determines the class, Patient.

#### Class Variable: ####

- **id**: string, to identify patient
- **revisit**: bool, to identify whether he/she has seen the doctor
- **time**: numpy.narray, Record all kids of Time
  Row: 0-doctor, 1-blood, 2-scan, 3(namely -1)-revisit
  Col: 0-arrival_time(for queue), 1-begin_time, 2-finish_time, 3-report_time, 4-Doctor/Service ID
- **check_list**: list, operation list
- **checklist**: list, just temp operation list to program easily *(can be optimized)*

#### Global Function: ####

- **\_\_lt\_\_**: to solve when the Priorityqueue have same key.
- **isRevisit**: return self.revisit
- **\_\_str\_\_**: to print patient's info

### 3) Waiting_Place.py ###

- This file is for modeling waiting place and doctor place (triage). And waiting place including blood place and scan place.
- Their Constructor is for generating patients or adding patients.
- The Waiting_Place and Doctor_Place has 3 main API:
  - add_patient(self, patient):
    For blood_place or scan_place which has 1 queue, the API just lets the patient inqueue.
    For doctor_place, the API can let the patient inqueue scheduled queue (default) or revisited queue. 
    Since the walk-in is Exponential Distribution (memoryless), we can just generate one.
  - next_patient(self):
    Just to return when the next patient appear. 
    If there is no person now, return the time when the expected next person appears (max is SIM_END).
    If available, return now.
  - send_patient(self):
    Just return next patient.

### 4) Serve_Place.py ###

-  This file is for modeling serving process. 

- Their Constructor is for generating doctors or Service.
- The Serve_Place has only one API:
  - work(self, patient): Just serve the patient, and return him/her.

### 5) Simulation.py ###

- This file is main file to simulate the whole process.
- It has 2 strategies.
  - Strategy 1: in all idle service and doctor (finish_time <= Now_step), find whose expected patient's time is minimum, and update Now_step = the time. However, there is a bug, when a busy server is idle at that time. So use itself for skip this period.
  - Strategy 2: in all service and doctor (including busy servers), find min(all servers' max(finish_time, expected_time))
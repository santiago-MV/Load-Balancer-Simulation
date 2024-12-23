import math


import random as r


import matplotlib.pyplot as plt
import math as m

respuestaValorNominal = 50
maxPowerConsumption = 575
maxSpeed = 3.1 # In Ghz
perturbationChance = 0.1
maxPerturbation = 100
perturbationTTL = 3
CPUAmount = 5
iterationAmount = 500
minCPUAmount = 1
maxCPUAmount = 8
maxRequestPerCPU = 3100
maxRPS = 0.25*maxRequestPerCPU # In Mips
t=0
error = 0
transitionaryState = True
usage = []
requests = []
time = []
lengths = []
requestsList = []
perturbations = []

class Perturbation:
    def __init__(self,requests,TTL):
        self.requests = requests
        self.TTL = TTL

class CPU:
    # We used an INTEL Xeon 6960P as reference
    # 72 Cores -> 144 Threats
    # At a maximum 3.1 GHz speed
    # Assuming a IPC=1.0 (Average for Intel Server CPUs) => maxIPS = 3.1GIPS = 3,100 MIPS
    def __init__(self,usage,activeRequests,powerConsumption):
        self.usage = usage
        self.activeRequests = activeRequests #IPS in M (10^6)
        self.speed = 0 #In GHz (10^9 cicles per second)
        self.powerConsumption = powerConsumption
        self.perturbations = []

CPUs = [CPU(0,0,0)]*CPUAmount

# Controllers (Sacamos el derivativo?)
kd = 0.0003
kp = 1

def totalRequests():
    return sum(C.activeRequests + sum(p.requests for p in C.perturbations) for C in CPUs) # Perturbations stay constant on the CPUs that are handling them

def requestForCPU(requestAmount):
    return m.ceil(requestAmount/len(CPUs))

def GenerateRequests():
    requestAmount = round(r.random()*maxRPS)
    return requestForCPU(requestAmount)

def CalculateUsage(cpu:CPU):
    cpu.usage = (cpu.activeRequests+(sum(p.requests for p in cpu.perturbations)))/maxRequestPerCPU #
    cpu.powerConsumption = maxPowerConsumption * cpu.usage
    cpu.speed = maxSpeed * cpu.usage

def refreshCPUs(requests,perturbations:Perturbation):
    for C in CPUs:  # Assign the requests and refresh the usage
        C.activeRequests = requests
        # Reduce TTL and delete perturbations
        for p in C.perturbations:
            p.TTL -= 1
            if p.TTL <= 0:
                C.perturbations.remove(p)
        # Add new perturbation
        if perturbations.TTL != 0:
            C.perturbations.append(perturbations)
        CalculateUsage(C)


def loadbalancer(error): #If a Heavy query is executed it will stay on the CPU that's managing it
    global transitionaryState
    if abs(error) <= 15 & transitionaryState:
        transitionaryState = False
    if abs(error) > 25:
        if not transitionaryState:
            print("The system has reached failure! Aborting...")
            return 1
    if 15 <= abs(error) <= 25:# Need to add or delete a CPU
        totalError = error * len(CPUs) # Total excess
        CPUdifference = m.ceil(abs(totalError)/input)# The amount of CPUs to add or delete
        ActiveRequests = totalRequests() # The total amount of active requests
        if error>0: # Need to delete a CPU
            for x in range(abs(CPUdifference)):
                if len(CPUs) > minCPUAmount:
                    CPUs.pop()
                else: print("Minimum CPU amount of  ("+ str(minCPUAmount) +") reached! no more CPUs will be deactivated");
                    break
        else:
            for x in range(abs(CPUdifference)):
                if len(CPUs) < maxCPUAmount:
                    newCPU = CPU(0,0,0)
                    CPUs.append(newCPU)
                else: print("Maximum CPU amount of  ("+ str(maxCPUAmount) +") reached! no more CPUs will be activated");
                    break
        CPURequest = requestForCPU(ActiveRequests) # Divide the request between the new amount of CPUs
        refreshCPUs(CPURequest,Perturbation(0,0))
    return 0

while t<iterationAmount:
    print('Tiempo: ' + str(t))
    # 30% of the time a random amount of requests is deleted
    deletedRequest=0
    if (not transitionaryState) & (r.random()< 0.5):
        deletedRequest = round(CPUs[0].activeRequests*r.random()*0.1)# Delete a random amount of requests up to 60% of the active requests
        for C in CPUs:
            C.activeRequests = max(C.activeRequests - deletedRequest, 0)

    # Perturbations that occur because of a spike in the need of CPU usage by  are randomly generated

    if (not transitionaryState) & (r.random() < perturbationChance):
        perturbation = Perturbation(math.ceil(r.random()*maxPerturbation),math.ceil(r.random()*perturbationTTL))
        print('A perturbation has occurred, TTL: '+str(perturbation.TTL)+' Value: '+str(perturbation.requests) +' Mips')
    else:
        perturbation = Perturbation(0,0)
    # Generate the incoming requests in this t
    if transitionaryState:
        req = 0.25*maxRequestPerCPU
    else:
        req = GenerateRequests()
    requestPerCPU = min(req + requestForCPU(totalRequests()),maxRequestPerCPU)
    #Refresh the CPUs
    refreshCPUs(requestPerCPU,perturbation)



    # Error signal
    previousError = error
    error = (input) - (CPUs[0].usage*100) # All CPUs Have the same usage, this represents the excess of usage in each CPU
    proportionalError = kp*error

    derivativeError = kd*(error-previousError)
    calculatedError = proportionalError+derivativeError

    #Balance the charge
    balanceResult = loadbalancer(calculatedError)
    usage.append(round(CPUs[0].usage*100,2))
    lengths.append(len(CPUs))
    requestsList.append(CPUs[0].activeRequests)
    perturbations.append(sum(p.requests for p in CPUs[0].perturbations))

    time.append(t)
    if (not transitionaryState) & balanceResult == 1 :
        break



    print('Server amount: ' + str(len(CPUs)) + ' - Usage percentage: ' + str(round(CPUs[0].usage*100,2)) + '% - Error signal: ' + str(round(calculatedError,2)))
    print('New requests: ' + str(req) + ' Mips per Server - Deleted request: ' + str(deletedRequest)+' Mips per Server')

    print('=======================================================================================')
    t += 1
# CPU Usage
custom_ticks = [0,25,35,50,65,75,100]
plt.figure(figsize=(20, 6))
plt.plot(time, usage, label="CPU usage [%]", color="blue", linewidth=0.5)
plt.axhline(y=50, color='green', linestyle='-', linewidth=0.75)
plt.axhline(y=65, color='blue', linestyle='--', linewidth=0.75)
plt.axhline(y=35, color='blue', linestyle='--', linewidth=0.75)
plt.axhline(y=75, color='red', linestyle=':', linewidth=0.75)
plt.axhline(y=25, color='red', linestyle=':', linewidth=0.75)
plt.title("CPU usage through time")
plt.xlabel("Time [seg]")
plt.ylim(0, 1)
plt.yticks(custom_ticks)
plt.ylabel("CPU usage [%]")
plt.grid(True)
plt.legend()
plt.show()
# CPU amount
plt.figure(figsize=(20, 6))
plt.plot(time, lengths, label="CPUs amount", color="green")
plt.xlabel("Tiempo [seg]")
plt.ylim(0, maxCPUAmount + 2)
plt.ylabel("Active CPU [Units]")
plt.title("CPU amount through time")
plt.grid(True)
plt.legend()
plt.show()
# Requests and perturbations
plt.figure(figsize=(20, 6))
plt.plot(time, requestsList, label="Request amount", color="blue")
plt.xlabel("Tiempo [seg]")
plt.ylim(0, maxRequestPerCPU+1)
plt.ylabel("Amount")
plt.title("Requests through time")
plt.grid(True)
plt.legend()
plt.show()
# Perturbations
plt.figure(figsize=(20, 6))
plt.plot(time, perturbations, label="Perturbation amount", color="red")
plt.xlabel("Time [seg]")
plt.ylabel("Value of the perturbations")
plt.title("Perturbaciones through time")
plt.grid(True)
plt.legend()
plt.show()
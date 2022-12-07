import gurobipy as gp
import numpy as np
from gurobipy import*
mdl = Model("VRP")

'''Sets and parameters'''
K = [1,2,3]                     # Types of aircraft
V = {1:550,2:820,3:850}         # Speed of the aircraft [km/h]
C = {1:45,2:70,3:150}           # Number of seats
R = {1:1500,2:3300,3:6300}      # Range [km]
L = {1:1400,2:1600,3:1800}      # Runway length required [m]
LC = {1:15000/7,2:34000/7,3:80000/7}  # Lease cost per day
FC = {1:300,2:600,3:1250}       # Fixed cost
TC = {1:750,2:775,3:1400}       # Time cost
KC = {1:1,2:2,3:3.75}           # Fuel cost
TAT = {1:25,2:35,3:45}          # Turnaround time [min]
TATmult = [1.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
Re = 6371                       # Earth radius [km]
g = [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1] # 0 for hub airport
LF = 0.8                        # Average load Factor
BT = 10
Airports = ['Lira','LIRQ','LICJ','LIPZ','LIMF','LIBD','LIPX','LIEO','LICA','LICC','LIPE','LIMJ','LIRN','LIPY','LIPQ']
Runway_length = [2208,1750,3326,3300,3300,3068,2745,2745,2414,2435,2800,3066,2012,2962,3000]
Latitudes = [41.802425,43.808653,38.1824,45.5032,45.2004992,41.1366,45.395699,40.916668,38.906585,37.4673,44.535442,44.414165,40.884,43.616943,45.823]
Longitudes = [12.602139,11.201225,13.100582,12.3512,7.643164094,16.7564,10.8885,9.5,16.243402,15.0658,11.288667,8.942184,14.2878,13.516667,13.485]
Airport_number = 15
demand = [
	[0, 361.9511544, 206.9770217, 328.2983508, 124.749693, 245.7205615, 318.9248941, 138.8433101, 173.1423016, 231.1699322, 377.4290116, 235.4077403, 404.6287226, 237.3324213, 234.197101],
	[361.9511544, 0, 168.5477475, 360.0999954, 131.8855381, 202.0544303, 367.1792454, 120.0728087, 142.1955422, 192.0776711, 496.8611059, 264.4324591, 297.1698798, 226.248177, 242.3709704],
	[206.9770217, 168.5477475, 0, 163.6736059, 65.33564906, 137.2136604, 159.7432005, 73.61692975, 115.8853068, 179.4892986, 182.1877589, 119.2215111, 206.1164119, 108.0061412, 118.396308],
	[328.2983508, 360.0999954, 163.6736059, 0, 131.3404447, 203.1163314, 425.0571154, 109.736744, 141.140857, 189.6410532, 448.1682212, 244.4229446, 286.3791021, 221.6080457, 333.7235545],
	[124.749693, 131.8855381, 65.33564906, 131.3404447, 0, 75.71032266, 141.4840907, 46.3060526, 54.62094697, 74.93025856, 149.934919, 122.7126493, 108.6216159, 74.15891456, 90.67002004],
	[245.7205615, 202.0544303, 137.2136604, 203.1163314, 75.71032266, 0, 193.1494586, 77.23693458, 137.1996552, 166.0615399, 220.7284162, 138.6153892, 263.3895616, 139.4671153, 149.6695858],
	[318.9248941, 367.1792454, 159.7432005, 425.0571154, 141.4840907, 193.1494586, 0, 109.9169609, 136.0691448, 184.1211675, 474.125151, 268.5344322, 275.4574535, 204.3349338, 266.3326943],
	[138.8433101, 120.0728087, 73.61692975, 109.736744, 46.3060526, 77.23693458, 109.9169609, 0, 57.60408764, 80.3936096, 126.8798346, 86.54262835, 117.7474904, 71.0535639, 77.68631175],
	[173.1423016, 142.1955422, 115.8853068, 141.140857, 54.62094697, 137.1996552, 136.0691448, 57.60408764, 0, 153.9272332, 154.8503177, 99.50059262, 183.3383016, 94.06681587, 103.1343528],
	[231.1699322, 192.0776711, 179.4892986, 189.6410532, 74.93025856, 166.0615399, 184.1211675, 80.3936096, 153.9272332, 0, 209.0040778, 136.0488079, 234.2233072, 124.5338717, 137.9886408],
	[377.4290116, 496.8611059, 182.1877589, 448.1682212, 149.934919, 220.7284162, 474.125151, 126.8798346, 154.8503177, 209.0040778, 0, 296.6913799, 318.9556735, 245.9148144, 287.8840708],
	[235.4077403, 264.4324591, 119.2215111, 244.4229446, 122.7126493, 138.6153892, 268.5344322, 86.54262835, 99.50059262, 136.0488079, 296.6913799, 0, 201.0492427, 139.9566898, 166.1349956],
	[404.6287226, 297.1698798, 206.1164119, 286.3791021, 108.6216159, 263.3895616, 275.4574535, 117.7474904, 183.3383016, 234.2233072, 318.9556735, 201.0492427, 0, 201.6257448, 207.766325],
	[237.3324213, 226.248177, 108.0061412, 221.6080457, 74.15891456, 139.4671153, 204.3349338, 71.0535639, 94.06681587, 124.5338717, 245.9148144, 139.9566898, 201.6257448, 0, 159.1588704],
	[234.197101, 242.3709704, 118.396308, 333.7235545, 90.67002004, 149.6695858, 266.3326943, 77.68631175, 103.1343528, 137.9886408, 287.8840708, 166.1349956, 207.766325, 159.1588704, 0]
]

def greatcircle(airport1,airport2):
    """
    Calculate the great circle distance between airport 1 and airport 2
    :param airport1: Index number of airport 1 for Lat lon lists
    :param airport2: Index number of airport 2 for Lat lon lists
    :return: distance: Great circle distance between airports
    """
    arclength = 2*np.arcsin(np.sqrt(np.sin((np.radians(Latitudes[airport1]-Latitudes[airport2]))/2)**2
                                    +np.cos(np.radians(Latitudes[airport1]))
                                    *np.cos(np.radians(Latitudes[airport2]))
                                    *np.sin((np.radians(Longitudes[airport1]
                                    -Longitudes[airport2]))/2)**2))
    distance = Re * arclength
    return distance

def route_cost(airport1,airport2,aircraft_type):
    fixed_cost = FC[aircraft_type]
    time_cost = TC[aircraft_type]*greatcircle(airport1,airport2)/V[aircraft_type]
    fuel_cost = KC[aircraft_type]*1.42/1.5*greatcircle(airport1,airport2)
    cost = fixed_cost + time_cost + fuel_cost
    if airport1 == 0 or airport2 == 0:
        cost = 0.7*cost
    return cost

def yields(airport1,airport2):
    money = 5.9*greatcircle(airport1,airport2)**(-0.76)+0.043
    return money

'''Decision Variable'''
Hubflow = [(i,j) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j]
Directflow = [(i,j) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j]
Aircraftflow = [(i,j,k) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j for k in range(1,len(K)+1)]
Aircraft_number = [i for i in range (1,len(K)+1)]


w = mdl.addVars(Hubflow, vtype=GRB.INTEGER, name="Hubflow")
x = mdl.addVars(Directflow, vtype=GRB.INTEGER, name="Directflow")
y = mdl.addVars(Aircraftflow, vtype=GRB.INTEGER, name="Aircraftflow")
z = mdl.addVars(Aircraft_number, vtype=GRB.INTEGER, name="Aircraft number")

mdl.modelSense = GRB.MAXIMIZE


# '''Constraints'''
# All flow from each airport leave the airport, either through a hub or not
mdl.addConstrs(x[i,j]+w[i,j] <= demand[i][j] for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j)
# There are only transfer passengers if neither of the two airports is the hub-airport.
mdl.addConstrs(w[i,j] <= demand[i][j]*g[i]*g[j] for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j)
# Capacity verification in each flight leg
mdl.addConstrs(x[i,j]+quicksum(w[i,m]*(1-g[j]) for m in range(0,Airport_number) if i!=m) + quicksum(w[m,j]*(1-g[i]) for m in range(0,Airport_number) if j!=m) <= quicksum(y[i,j,k]*C[k]*LF for k in K) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j)
# Balance between incoming and outgoing flight
mdl.addConstrs(y[i,j,k] == y[j,i,k] for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j for k in K)
# Limit aircraft usage
mdl.addConstrs(quicksum((greatcircle(i,j)/V[k]+TAT[k]*TATmult[i]*TATmult[j]/60)*y[i,j,k] for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j) <= BT*z[k] for k in K)
# Ensure the aircraft has the range to fly the route
for i in range(0,Airport_number):
    for j in range(0,Airport_number):
        if i!=j:
            for k in K:
                if R[k] >= greatcircle(i,j):
                    a = 10000
                else:
                    a = 0
                mdl.addConstr(y[i,j,k] <= a)
# Minimum required runway length
for i in range(0,Airport_number):
    for j in range(0,Airport_number):
        if i!=j:
            for k in K:
                if L[k] > Runway_length[i] or L[k] > Runway_length[j]:
                    a = 0
                else:
                    a = 10000
                mdl.addConstr(y[i,j,k] <= a)

'''Objective Function'''

mdl.setObjective(quicksum(yields(i,j)*greatcircle(i,j)*(x[i,j]+0.9*w[i,j])-quicksum(route_cost(i,j,k)*y[i,j,k] for k in K) for i in range(0,Airport_number) for j in range(0,Airport_number) if i!=j)-quicksum(z[k]*LC[k] for k in K))

# Flight departing or arriving at the hub have 30% lower cost
# Yield on connecting flights is 10% less
# Average load factor is not higher than 80%
# Aircraft can be used 10 hours per day
# TAT for flight to the hub are 50% longer

'''Solve'''
mdl.write("myLP.lp")
mdl.Params.MIPGap = 0.1
mdl.Params.TimeLimit = 30  # seconds
mdl.optimize()
solution = {}

for i in mdl.getVars():
    if i.x > 0 or i.x < 0:
        print (i)
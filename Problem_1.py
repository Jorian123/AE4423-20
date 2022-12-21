import gurobipy as gp
import numpy as np
from gurobipy import*
mdl = Model("VRP")
import pandas as pd

'''Sets and parameters'''
K = [1,2,3]                                     # Types of aircraft
V = {1:550,2:820,3:850}                         # Speed of the aircraft [km/h]
C = {1:45,2:70,3:150}                           # Number of seats
Ra = {1:1500, 2:3300, 3:6300}                      # Range [km]
L = {1:1400,2:1600,3:1800}                      # Runway length required [m]
LC = {1:15000,2:34000,3:80000}                  # Lease cost per week
FC = {1:300,2:600,3:1250}                       # Fixed cost
TC = {1:750,2:775,3:1400}                       # Time cost
KC = {1:1,2:2,3:3.75}                           # Fuel cost
TAT = {1:25/60,2:35/60,3:45/60}                 # Turnaround time [hour]
TATmult = [1.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1]     # Turn around time multiplier. 1.5 for the hub airports.
Re = 6371                                       # Earth radius [km]
g = [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1]             # 0 for hub airport
LF = 0.8                                        # Average load Factor
BT = 70                                         # Block Time
Airports = ['Lira','LIRQ','LICJ','LIPZ','LIMF','LIBD','LIPX','LIEO','LICA','LICC','LIPE','LIMJ','LIRN','LIPY','LIPQ']
Runway_length = [2208,1750,3326,3300,3300,3068,2745,2745,2414,2435,2800,3066,2012,2962,3000]
Latitudes = [41.802425,43.808653,38.1824,45.5032,45.2004992,41.1366,45.395699,40.916668,38.906585,37.4673,44.535442,44.414165,40.884,43.616943,45.823]
Longitudes = [12.602139,11.201225,13.100582,12.3512,7.643164094,16.7564,10.8885,9.5,16.243402,15.0658,11.288667,8.942184,14.2878,13.516667,13.485]
Airport_number = 15
q = [
	[0, 402.2347489, 230.012667, 364.8365341, 138.6337931, 273.0681948, 354.4198523, 154.2959686, 192.4122892, 256.8981435, 419.4352245, 261.6076013, 449.6621454, 263.746491, 260.2622231],
	[402.2347489, 0, 187.3063812, 400.1775639, 146.5638268, 224.5422125, 408.0447038, 133.4363918, 158.0212897, 213.4550833, 552.1595932, 293.8626455, 330.2435992, 251.4286183, 269.3458087],
	[230.012667, 187.3063812, 0, 181.8897687, 72.60722357, 152.484946, 177.5219262, 81.81017491, 128.7828391, 199.4656794, 202.4644667, 132.4903484, 229.056275, 120.0267566, 131.5733038],
	[364.8365341, 400.1775639, 181.8897687, 0, 145.9580668, 225.7222986, 472.3641298, 121.949968, 156.8492225, 210.7472803, 498.0474014, 271.6261588, 318.2518547, 246.2720605, 370.8655394],
	[138.6337931, 146.5638268, 72.60722357, 145.9580668, 0, 84.13655338, 157.2306567, 51.45971552, 60.70002159, 83.26967152, 166.6220255, 136.3700352, 120.7107308, 82.41248028, 100.7612002],
	[273.0681948, 224.5422125, 152.484946, 225.7222986, 84.13655338, 0, 214.6461561, 85.83307058, 152.4693821, 184.5434694, 245.2945321, 154.0426811, 292.7036781, 154.9892006, 166.3271619],
	[354.4198523, 408.0447038, 177.5219262, 472.3641298, 157.2306567, 214.6461561, 0, 122.1502422, 151.2130508, 204.6130553, 526.893225, 298.4211504, 306.114674, 227.0765262, 295.9743686],
	[154.2959686, 133.4363918, 81.81017491, 121.949968, 51.45971552, 85.83307058, 122.1502422, 0, 64.01517288, 89.34106984, 141.0010102, 96.17444773, 130.8522756, 78.96151755, 86.33246148],
	[192.4122892, 158.0212897, 128.7828391, 156.8492225, 60.70002159, 152.4693821, 151.2130508, 64.01517288, 0, 171.058667, 172.0844868, 110.5745773, 203.7430598, 104.5360447, 114.6127592],
	[256.8981435, 213.4550833, 199.4656794, 210.7472803, 83.26967152, 184.5434694, 204.6130553, 89.34106984, 171.058667, 0, 232.2653256, 151.1904505, 260.2913459, 138.3939518, 153.3461784],
	[419.4352245, 552.1595932, 202.4644667, 498.0474014, 166.6220255, 245.2945321, 526.893225, 141.0010102, 172.0844868, 232.2653256, 0, 329.7118443, 354.4540573, 273.2840672, 319.9243199],
	[261.6076013, 293.8626455, 132.4903484, 271.6261588, 136.3700352, 154.0426811, 298.4211504, 96.17444773, 110.5745773, 151.1904505, 329.7118443, 0, 223.4251519, 155.5332627, 184.6251005],
	[449.6621454, 330.2435992, 229.056275, 318.2518547, 120.7107308, 292.7036781, 306.114674, 130.8522756, 203.7430598, 260.2913459, 354.4540573, 223.4251519, 0, 224.0658161, 230.8898164],
	[263.746491, 251.4286183, 120.0267566, 246.2720605, 82.41248028, 154.9892006, 227.0765262, 78.96151755, 104.5360447, 138.3939518, 273.2840672, 155.5332627, 224.0658161, 0, 176.8725627],
	[260.2622231, 269.3458087, 131.5733038, 370.8655394, 100.7612002, 166.3271619, 295.9743686, 86.33246148, 114.6127592, 153.3461784, 319.9243199, 184.6251005, 230.8898164, 176.8725627, 0]
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
    """
    Calculate the cost of a route, including the fixed cost, the time cost and the fuel cost.
    :param airport1: The departure airport.
    :param airport2: The arrival airport.
    :param aircraft_type: The type of aircraft used to fly the route.
    :return: The total cost for the route between the two airports.
    """
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

'''Decision Variables'''
# Flow between airports via the hub in number of passengers
Hubflow = [(i,j) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j]
# Flow between airports in number of passengers
Directflow = [(i,j) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j]
# Flow between airports in number of flights
Aircraftflow = [(i,j,k) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j for k in range(1,len(K)+1)]
# Total amount of aircraft between all types
Aircraft_number = [i for i in range (1,len(K)+1)]

if __name__ == "__main__":
    w = mdl.addVars(Hubflow, vtype=GRB.INTEGER, name="Hubflow")
    x = mdl.addVars(Directflow, vtype=GRB.INTEGER, name="Directflow")
    y = mdl.addVars(Aircraftflow, vtype=GRB.INTEGER, name="Aircraftflow")
    z = mdl.addVars(Aircraft_number, vtype=GRB.INTEGER, name="Aircraft number")

    mdl.modelSense = GRB.MAXIMIZE


    # '''Constraints'''
    # All flow from each airport leaves the airport, either through a hub or directly to another airport.
    mdl.addConstrs((x[i,j] + w[i,j] <= q[i][j] for i in range(0, Airport_number) for j in range(0, Airport_number) if i != j), name="FC")
    # There are only transfer passengers if neither of the two airports is the hub-airport.
    mdl.addConstrs(w[i,j] <= q[i][j] * g[i] * g[j] for i in range(0, Airport_number) for j in range(0, Airport_number) if i != j)
    # Capacity verification in each flight leg.
    mdl.addConstrs(x[i,j]+quicksum(w[i,m]*(1-g[j]) for m in range(0,Airport_number) if i!=m) + quicksum(w[m,j]*(1-g[i]) for m in range(0,Airport_number) if j!=m) <= quicksum(y[i,j,k]*C[k]*LF for k in K) for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j)
    # Balance between incoming and outgoing flight for each airport.
    mdl.addConstrs(quicksum(y[i,j,k] for j in range(0,Airport_number) if i != j)  == quicksum(y[j,i,k]for j in range(0,Airport_number) if i != j) for i in range(0,Airport_number) for k in K )
    # Limit aircraft usage to the assigned block time.
    mdl.addConstrs(quicksum((greatcircle(i,j)/V[k]+TAT[k]*TATmult[i]*TATmult[j])*y[i,j,k] for i in range(0,Airport_number) for j in range(0,Airport_number) if i != j) <= BT*z[k] for k in K)
    # Ensure the aircraft has the range to fly the route.
    for i in range(0,Airport_number):
        for j in range(0,Airport_number):
            if i!=j:
                for k in K:
                    if Ra[k] >= greatcircle(i, j):
                        a = 10000
                    else:
                        a = 0
                    mdl.addConstr(y[i,j,k] <= a)
    # Minimum required runway length for the aircraft type used on the route.
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

    '''Solve'''
    mdl.write("LP_Formulation_Problem_1.lp")
    mdl.Params.MIPGap = 0.001
    mdl.Params.TimeLimit = 300  # seconds
    mdl.optimize()
    mdl.write("Solution_Problem_1.JSON")
    solution = {}

    # Print all non-zero variables
    for i in mdl.getVars():
        if i.x > 0 or i.x < 0:
            print("{} : {}".format(i.Varname, i.x))

    Aircraftflowresult = np.zeros((15,15), dtype=tuple)

    for i,j,p in Aircraftflow:

        for k in K:
            if k == 1:
                a = mdl.getVarByName("Aircraftflow[{},{},{}]".format(i,j,k)).x
            if k == 2:
                b = mdl.getVarByName("Aircraftflow[{},{},{}]".format(i,j,k)).x
            if k == 3:
                c = mdl.getVarByName("Aircraftflow[{},{},{}]".format(i,j,k)).x
        value = int(a),int(b),int(c)
        Aircraftflowresult[i,j]= value
    print(Aircraftflowresult)
    pd.DataFrame(Aircraftflowresult).to_csv('sample.csv')



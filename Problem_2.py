import gurobipy as gp
import numpy as np
from gurobipy import*
mdl = Model("VRP")
import pandas as pd

'''Sets and parameters'''
K = [1,2,3,4,5]                                # Types of aircraft
V = {1:550,2:820,3:850,4:350,5:480}                         # Speed of the aircraft [km/h]
C = {1:45,2:70,3:150,4:20,5:48}                           # Number of seats
Ra = {1:1500, 2:3300, 3:6300, 4:400, 5:1000}                      # Range [km]
L = {1:1400,2:1600,3:1800,4:750,5:950}                      # Runway length required [m]
G = {4:2130, 5:8216}                                               #Charge capacity
LC = {1:15000,2:34000,3:80000,4:12000,5:22000}                  # Lease cost per week
FC = {1:300,2:600,3:1250,4:90,5:120}                       # Fixed cost
TC = {1:750,2:775,3:1400,4:750,5:750}                       # Time cost
KC = {1:1,2:2,3:3.75,4:0.07,5:0.07}                           # Fuel cost
BE = {1:0,2:0,3:0,4:2130,5:8216}
TAT = {1:25/60,2:35/60,3:45/60,4:20/60,5:25/60}                 # Turnaround time [hour]
TATadd = {1:0,2:0,3:0,4:20/60,5:45/60}
TATmult = [
            [1.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1.5,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ]     # Turn around time multiplier. 1.5 for the hub airports.
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
    if airport1 == airport2:
        return 0
    arclength = 2*np.arcsin(np.sqrt(np.sin((np.radians(Latitudes[airport1]-Latitudes[airport2]))/2)**2
                                    +np.cos(np.radians(Latitudes[airport1]))
                                    *np.cos(np.radians(Latitudes[airport2]))
                                    *np.sin((np.radians(Longitudes[airport1]
                                    -Longitudes[airport2]))/2)**2))
    distance = Re * arclength
    return distance
def route_distance(route):
    """
    Calculate the total great circle distance for a route
    :param route: The route for which the distance is to be calculated.
    :return: The total distance
    """
    distance = 0
    for i in range(0,len(route)-1):
        distance += greatcircle(route[i],route[i+1])
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
    if aircraft_type in [1,2,3]:
        fuel_cost = KC[aircraft_type]*1.42/1.5*greatcircle(airport1,airport2)
    else:
        fuel_cost = KC[aircraft_type] * G[aircraft_type] * greatcircle(airport1, airport2) / Ra[aircraft_type]
    if airport1 == 0 or airport2 == 0 and aircraft_type in [1,2,3]:
        cost = 0.7*(fixed_cost + time_cost + fuel_cost)
    elif airport1 == 0 or airport2 == 0:
        cost = 0.7 * (fixed_cost + time_cost) + fuel_cost
    else:
        cost = fixed_cost + time_cost + fuel_cost
    return cost

def total_route_cost(route,aircraft_type):
    """
    Calculate the total route cost.
    :param route: The route for which to calculate this cost.
    :param aircraft_type: The aircraft type flown on this route.
    :return: The total cost.
    """
    cost = 0
    for i in range(0,len(route)-1):
        cost += route_cost(route[i],route[i+1],aircraft_type)
    return cost


def yields(airport1,airport2):
    if airport1 == airport2:
        return 0
    money = 5.9*greatcircle(airport1,airport2)**(-0.76)+0.043
    return money

def turn_time(route,aircraft_type):
    """
    Calculate the total turnaround time for a route.
    :param route: The route for which to calculate the turnaround time.
    :param aircraft_type: The type of aircraft to calculate the turnaround time.
    :return: The total turnaround time.
    """
    length = len(route)
    if aircraft_type == 1 or aircraft_type == 2 or aircraft_type == 3:
        time = 1.5*TAT[aircraft_type]+(length-2)*TAT[aircraft_type]
    if aircraft_type == 4 or aircraft_type == 5:
        time = (length-1)*TAT[aircraft_type]+TATadd[aircraft_type]
    return time

"Generate possible routes"
R1 = []
R2 = []
for i in range(Airport_number):
    for j in range(Airport_number):
        if i!=j and i!=0 and j!=0:
            ori = (0, i, j, 0)
            R2.append(ori)
        elif i==j and i!=0:
            ori = (0, i, 0)
            R1.append(ori)

R = R1 + R2

"generate subsequent and precedent nodes"
route_sub_1 = []
route_pre_1 = []
route_sub_2 = []
route_pre_2 = []

for route in R1:
    dic1 = {}
    dic2 = {}
    dic1[route[0]] = [route[1],route[2]]
    dic1[route[1]] = [route[2]]
    dic2[route[0]] = [route[0]]
    dic2[route[1]] = [route[1],route[0]]
    route_sub_1.append(dic1)
    route_pre_1.append(dic2)

for route in R2:
    dic1 = {}
    dic2 = {}
    dic1[route[0]] = [route[1],route[2],route[3]]
    dic1[route[1]] = [route[2],route[3]]
    dic1[route[2]] = [route[3]]
    dic2[route[0]] = [route[0]]
    dic2[route[1]] = [route[1], route[0]]
    dic2[route[2]] = [route[2],route[1], route[0]]
    route_sub_2.append(dic1)
    route_pre_2.append(dic2)
route_sub = route_sub_1 + route_sub_2
route_pre = route_pre_1 + route_pre_2


route_index = range(len(R))
'''Decision Variables'''
# Flow between routes via the hub in number of passengers
Transfer_flow = [(i,j,r,n) for r in range(len(R)) for n in range(len(R)) for i in range(Airport_number) for j in range(Airport_number)]

# Flow between airports in number of passengers
Direct_flow = [(i,j,r) for r in range(len(R)) for i in range(Airport_number) for j in range(Airport_number)]

# Flow between airports in number of flights
Aircraft_flow = [(r,k) for k in range (1,len(K)+1) for r in range(len(R))]

# Total amount of aircraft between all types
Aircraft_number = [i for i in range (1,len(K)+1)]


"Generate Auxiliary parameters"
delta = {}
for flow in Direct_flow:
    delta[flow]=0
for r in route_index:
    for i in set(R[r]):
        for j in route_sub[r][i]:
            if i!=j:
                delta[i, j, r] = 1

if __name__ == "__main__":
    w = mdl.addVars(Transfer_flow, vtype=GRB.INTEGER, name="Hubflow")
    x = mdl.addVars(Direct_flow, vtype=GRB.INTEGER, name="Directflow")
    z = mdl.addVars(Aircraft_flow, vtype=GRB.INTEGER, name="Aircraftflow")
    AC = mdl.addVars(Aircraft_number, vtype=GRB.INTEGER, name="Aircraftnumber")

    mdl.modelSense = GRB.MAXIMIZE


    ''' Demand constraints'''
    # Limit the direct flows to actual flows in routes
    mdl.addConstrs((quicksum(x[i,j,r] + quicksum(w[i,j,r,n] for n in route_index) for r in route_index) <= q[i][j] for i in range(Airport_number) for j in range(Airport_number)), name="DFC")
    # Eliminate direct flow paths not in the route
    mdl.addConstrs(x[i,j,r] <= q[i][j] * delta[i, j, r] for i in range(Airport_number) for j in range(Airport_number) for r in route_index)
    # Eliminate indirect flow paths not in the routes
    mdl.addConstrs(w[i,j,r,n] <= q[i][j] * delta[i, 0, r] * delta[0, j, n] for i in range(Airport_number) for j in range(Airport_number) for r in route_index for n in route_index)


    """Aircraft utilization constraints"""
    # Limit aircraft usage to the assigned block time.
    mdl.addConstrs((quicksum((route_distance(R[r]) / V[k] + turn_time(R[r], k)) * z[r, k] for r in route_index) <= BT * AC[k] for k in K), name="AUC")

    """Aircraft allocation constraints"""
    # Ensure the aircraft has the range to fly the route.
    for r in route_index:
        route = R[r]
        length=route_distance(route)
        for k in K:
            if Ra[k] >= length:
                a = 10000
            else:
                a = 0
            mdl.addConstr(z[r,k] <= a, name="RC{}{}".format(r,k))


    """Aircraft Flow constraints"""
    # From the hub node
    mdl.addConstrs(((quicksum(x[0,m,r] for m in route_sub[r][0]) + quicksum(w[p,m,n,r] for n in route_index for p in range(Airport_number) for m in route_sub[r][0])) <= quicksum(z[r,k] * C[k] * LF for k in K) for r in route_index), name="FCH-")
    # To the hub node
    mdl.addConstrs(((quicksum(x[m,0,r] for m in route_pre[r][R[r][-2]]) + quicksum(w[m, p, r, n] for n in route_index for p in range(Airport_number) for m in route_pre[r][R[r][-2]])) <= quicksum(z[r, k] * C[k] * LF for k in K) for r in route_index), name="FC-H")
    # Between the spokes

    mdl.addConstrs(((quicksum(x[route_sub[r][0][0],m,r] for m in route_sub[r][R[r][-2]])
                     +quicksum(x[m,route_sub[r][0][1],r] for m in route_pre[r][R[r][1]])
                     +quicksum(w[p,route_sub[r][0][1],n,r] for n in route_index for p in range(Airport_number))
                     +quicksum(w[route_sub[r][0][0], p, r, n] for n in route_index for p in range(Airport_number))
                     )
                    <= quicksum(z[r,k] * C[k] * LF for k in K) for r in route_index if len(R[r]) > 3), name="FCS")

    # Minimum required runway length for the aircraft type used on the route.
    for r in range(len(R)):
        for k in K:
            for airport in R[r]:
                if L[k] > Runway_length[airport]:
                    mdl.addConstr(z[r,k] <= 0, name="Runway")


    '''Objective Function'''
    # Parts that generate revenue
    Revenue = quicksum(yields(i,j)*greatcircle(i,j)*(x[i,j,r]+0.9*quicksum(w[i,j,r,n] for n in route_index)) for i in range(Airport_number) for j in range(Airport_number) for r in route_index)
    # Parts that cost money
    Lease_cost = quicksum(AC[k] * LC[k] for k in K)
    Travel_cost = quicksum(total_route_cost(R[r], k) * z[r, k] for k in K for r in route_index)
    mdl.setObjective(Revenue-Lease_cost-Travel_cost)

    '''Solve'''
    mdl.write("LP_Formulation_Problem_2.lp")
    mdl.Params.MIPGap = 0.001
    mdl.Params.TimeLimit = 1800  # seconds
    mdl.optimize()
    mdl.write("Solution_Problem_2.JSON")
    solution = {}

    # Print all non-zero variables
    for i in mdl.getVars():
        if i.x > 0:
            print("{} : {}".format(i.Varname,i.x))


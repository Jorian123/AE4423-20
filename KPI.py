import importlib
import json
from Problem_1 import greatcircle

# Define which problem you want to be solved. Expects pre-generated solution
problem_number = [1,2]

#Distance between 2 airports in a route
def legdistance(airport1,airport2,route):
    start=route.index(airport1)
    dis = greatcircle(airport1, route[start+1])
    if route[start+1] == airport2:
        return dis
    else:
        dis += greatcircle(route[start+1],route[start+2])
        return dis


for p in problem_number:
    problem = importlib.import_module("Problem_{}".format(p))
    with open("Solution_Problem_{}.JSON".format(p)) as file:
        solution = json.load(file)

    Vars = {}
    for sol in solution['Vars']:
        Vars[sol["VarName"]] = sol['X']

    "Calculate available seat kilometers"
    ASK = 0
    RPK = 0
    CASK = 0
    if p == 1:
        for i in range(problem.Airport_number):
            for j in range(problem.Airport_number):
                if 'Directflow[{},{}]'.format(i,j) in Vars.keys():
                    RPK += Vars['Directflow[{},{}]'.format(i, j)]*problem.greatcircle(i,j)
                if 'Hubflow[{},{}]'.format(i,j) in Vars.keys():
                    RPK += Vars['Hubflow[{},{}]'.format(i, j)] * (problem.greatcircle(i, 0)+problem.greatcircle(0, j))
                for k in problem.K:
                    if 'Aircraftflow[{},{},{}]'.format(i,j,k) in Vars.keys():
                        ASK += Vars['Aircraftflow[{},{},{}]'.format(i,j,k)]*problem.C[k]*problem.greatcircle(i,j)
                        CASK += Vars['Aircraftflow[{},{},{}]'.format(i,j,k)]*problem.route_cost(i,j,k)
        for k in problem.K:
            if "Aircraft number[{}]".format(k) in Vars.keys():
                CASK += Vars["Aircraft number[{}]".format(k)]*problem.LC[k]
    else:
        for r in problem.route_index:
            for i in set(problem.R[r]):
                for j in set(problem.R[r]):
                    if "Directflow[{},{},{}]".format(i,j,r) in Vars.keys():
                        RPK += legdistance(i,j,problem.R[r])*Vars["Directflow[{},{},{}]".format(i,j,r)]
                    for n in problem.route_index:
                        if "Hubflow[{},{},{},{}]".format(i,j,n,r) in Vars.keys():
                            RPK += (legdistance(i,0,problem.R[n])+legdistance(0,j,problem.R[r]))*Vars["Hubflow[{},{},{},{}]".format(i,j,n,r)]
            for k in problem.K:
                if 'Aircraftflow[{},{}]'.format(r,k) in Vars.keys():
                    ASK+= Vars['Aircraftflow[{},{}]'.format(r,k)]*problem.C[k]*problem.route_distance(problem.R[r])
                    CASK += Vars['Aircraftflow[{},{}]'.format(r,k)]*problem.total_route_cost(problem.R[r],k)
        for k in problem.K:
            if "Aircraftnumber[{}]".format(k) in Vars.keys():
                CASK += Vars["Aircraftnumber[{}]".format(k)]*problem.LC[k]
    Profit = int(solution["SolutionInfo"]["ObjVal"])
    print("Problem {}:".format(p))
    print("ASK: {} [KM]".format(int(ASK)))
    print("RPK: {} [KM]".format(int(RPK)))
    print("Load factor: {}".format(RPK/ASK))
    print("CASK: {}".format(int(CASK)))
    print("CASK/ASK: {}".format(CASK/ASK))
    print("Revenue-ASK: {}".format((Profit+CASK)/ASK))
    print("Revenue-RPK: {}".format((Profit+CASK)/RPK))
    print("Profit {}".format(Profit))
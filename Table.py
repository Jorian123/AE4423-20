import importlib
import re
import pandas as pd
import json
from texttable import Texttable
import latextable

group = 8  # Fill in your group number here
airport_data = pd.read_csv('Group_' + str(group) + '_Airport_info.csv', encoding='unicode_escape', index_col=1)
# demand_data = pd.read_csv('Group_'+str(group)+'_Demand.csv', encoding = 'unicode_escape',index_col=0)
distance_data = pd.read_csv('Group_' + str(group) + '_Distances.csv', encoding='unicode_escape', index_col=0)
aircraft_data = pd.read_csv('Aircraft_info.csv', encoding='unicode_escape')
annual_growth_csv = pd.read_csv('Group_' + str(group) + '_Annual_growth.csv', encoding='unicode_escape', header=None)
annual_growth = annual_growth_csv[0][0]
airports = airport_data.index
hub = airports[0]
min_line_thick = 0.5
scale_factor = 5
Table_create = True

# Define which problem you want to be solved. Expects pre-generated solution
problem_number = 2
problem = importlib.import_module("Problem_{}".format(problem_number))
# Destination airport to print
Destination = 12
print('The hub of your network is', hub)

if __name__ == "__main__":
    with open("Solution_Problem_{}.JSON".format(problem_number)) as file:
        solution = json.load(file)
        Vars = {}
        for sol in solution['Vars']:
            Vars[sol["VarName"]] = sol['X']


        if problem_number == 1:
            table_vars = [["Airports"]]
            for airport in airports[7:15]:
                table_vars[0].append(airport)
            for i in range(len(airports)):
                ap1 = [airports[i]]
                for j in range(7,15):
                    ap2 = []
                    for k in problem.K:
                        if "Aircraftflow[{},{},{}]".format(i,j,k) in Vars.keys():
                            ap2.append(Vars["Aircraftflow[{},{},{}]".format(i,j,k)])
                        else:
                            ap2.append(0)
                    ap1.append(",".join(str(i) for i in ap2))
                table_vars.append(ap1)
        if problem_number == 2:
            table_vars=[["Route", "Path","Aircraft type", "Number"]]
            for var in Vars:
                if "Aircraftflow" in var:
                    digits = re.findall(r'\d+', var)
                    digits = list(map(int, digits))
                    route = []
                    for i in problem.R[digits[0]]:
                        route.append(airports[i])
                    route = " to ".join(route)
                    table_vars.append([digits[0],
                                       route,
                                      digits[1],
                                       Vars[var]])
        if problem_number == 10:
            for var in Vars:
                if "Aircraftflow" in var:
                    digits = re.findall(r'\d+', var)
                    digits = list(map(int, digits))
                    table_vars.append([var,
                                       "Amount of flights from {} to {} with aircraft type {}".format(airports[digits[0]] ,
                                                                                                 airports[digits[1]],
                                                                                                 digits[2]),
                                       Vars[var]])
                if "number" in var:
                    digits = re.findall(r'\d+', var)
                    digits = list(map(int, digits))
                    table_vars.append([var,
                                       "Amount of aircraft type {} ".format(digits[0]),
                                       Vars[var]])

        if Table_create:
            table = Texttable()
            table.set_cols_align(["c"] * len(table_vars[0]))
            table.set_deco(Texttable.HEADER | Texttable.VLINES | Texttable.HLINES)
            table.add_rows(table_vars)
            # print('\nTabulate Latex:')
            # print(tabulate(table_vars, headers='firstrow', tablefmt='latex'))
            print('\nTexttable Latex:')
            print(latextable.draw_latex(table, caption="All non-zero variables"))
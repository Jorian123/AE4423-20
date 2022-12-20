import importlib

from gurobipy import *
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
import json


group = 8 # Fill in your group number here
airport_data = pd.read_csv('Group_'+str(group)+'_Airport_info.csv',  encoding = 'unicode_escape',index_col=1)
# demand_data = pd.read_csv('Group_'+str(group)+'_Demand.csv', encoding = 'unicode_escape',index_col=0)
distance_data = pd.read_csv('Group_'+str(group)+'_Distances.csv', encoding = 'unicode_escape',index_col=0)
aircraft_data = pd.read_csv('Aircraft_info.csv', encoding = 'unicode_escape')
annual_growth_csv = pd.read_csv('Group_'+str(group)+'_Annual_growth.csv', encoding = 'unicode_escape', header=None)
annual_growth = annual_growth_csv[0][0]
airports = airport_data.index
hub = airports[0]

# Define which problem you want to be solved. Expects pre-generated solution
problem_number = 1
problem = importlib.import_module("Problem_{}".format(problem_number))
# Destination airport to print
Destination = airports[1]
print('The hub of your network is', hub)


if __name__ == "__main__":
    with open("Solution_Problem_{}.JSON".format(problem_number)) as file:
        solution = json.load(file)

    fig = go.Figure(data=go.Scattergeo())
    fig.add_trace(go.Scattergeo(lat =(airport_data['Latitude (deg)']), lon= (airport_data['Longitude (deg)']), text =airports,  line = dict( color = "blue")))
    fig.add_trace(go.Scattergeo(lat =([airport_data.loc[hub]['Latitude (deg)']]), lon= ([airport_data.loc[hub]['Longitude (deg)']]), text =airports, line = dict( color = "red")))
    fig.update_layout(showlegend=False, geo=dict(resolution=50, lataxis=dict(range=[36, 48], showgrid=True, dtick=3), lonaxis=dict(range=[6, 20], showgrid=True, dtick=3)))
    # fig.add_trace(
    #     go.Scattergeo(
    #         lat = [airport_data['Latitude (deg)'][hub],airport_data['Latitude (deg)']["LIRQ"]],
    #         lon = [airport_data['Longitude (deg)'][hub],airport_data['Longitude (deg)']["LIRQ"]],
    #         mode = 'lines',
    #         line = dict(width = 1,color = 'red')
    #     )
    # )

    for i in range(len(airports)):
        for j in solution['Vars']:
            print(j["VarName"])
            if j['VarName'] == "Hubflow[{},{}]".format(i,Destination):
                flow = j["X"]
                print(flow)
            else:
                flow = 0
            fig.add_trace(
                go.Scattergeo(
                    lat=[airport_data['Latitude (deg)'][i], airport_data['Latitude (deg)'][Destination]],
                    lon=[airport_data['Longitude (deg)'][i], airport_data['Longitude (deg)'][Destination]],
                    mode='lines',
                    line=dict(width=flow, color='red')
                )
            )
    fig.show()
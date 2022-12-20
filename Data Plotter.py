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
min_line_thick = 0.5
scale_factor = 5

# Define which problem you want to be solved. Expects pre-generated solution
problem_number = 2
problem = importlib.import_module("Problem_{}".format(problem_number))
# Destination airport to print
Destination = 3
print('The hub of your network is', hub)


if __name__ == "__main__":
    with open("Solution_Problem_{}.JSON".format(problem_number)) as file:
        solution = json.load(file)

    fig = go.Figure(data=go.Scattergeo())
    fig.add_trace(go.Scattergeo(lat =(airport_data['Latitude (deg)']), lon= (airport_data['Longitude (deg)']), text =airports,  line = dict( color = "blue")))
    fig.add_trace(go.Scattergeo(lat =([airport_data.loc[airports[Destination]]['Latitude (deg)']]), lon= ([airport_data.loc[airports[Destination]]['Longitude (deg)']]), text =airports, line = dict( color = "red")))
    fig.add_trace(go.Scattergeo(lat=([airport_data.loc[hub]['Latitude (deg)']]),
                                lon=([airport_data.loc[hub]['Longitude (deg)']]), text=airports,
                                line=dict(color="green")))
    fig.update_layout(showlegend=False, geo=dict(resolution=50, lataxis=dict(range=[36, 48], showgrid=True, dtick=3), lonaxis=dict(range=[6, 20], showgrid=True, dtick=3)))
    # fig.add_trace(
    #     go.Scattergeo(
    #         lat = [airport_data['Latitude (deg)'][hub],airport_data['Latitude (deg)']["LIRQ"]],
    #         lon = [airport_data['Longitude (deg)'][hub],airport_data['Longitude (deg)']["LIRQ"]],
    #         mode = 'lines',
    #         line = dict(width = 1,color = 'red')
    #     )
    # )
    if problem_number == 1:
        Vars = {}
        for sol in solution['Vars']:
            Vars[sol["VarName"]] = sol['X']
        total_flow = 0
        flow = 0
        hubflow = 0
        for i in range(len(airports)):
            if 'Directflow[{},{}]'.format(i,Destination) in Vars.keys():
                total_flow += Vars['Directflow[{},{}]'.format(i,Destination)]
            if 'Hubflow[{},{}]'.format(i,Destination) in Vars.keys():
                total_flow += Vars['Hubflow[{},{}]'.format(i, Destination)]
        for i in range(len(airports)):
            if i == 0:
                for j in range(len(airports)):
                    if 'Hubflow[{},{}]'.format(j,Destination) in Vars.keys():
                        flow += Vars['Hubflow[{},{}]'.format(j, Destination)]
                        hubflow += Vars['Hubflow[{},{}]'.format(j, Destination)]
                        if flow != 0:
                            fig.add_trace(
                                go.Scattergeo(
                                    lat=[airport_data['Latitude (deg)'][j],
                                         airport_data['Latitude (deg)'][airports[i]]],
                                    lon=[airport_data['Longitude (deg)'][j],
                                         airport_data['Longitude (deg)'][airports[i]]],
                                    mode='lines',
                                    text=airports,
                                    line=dict(width=max(flow/total_flow*scale_factor,min_line_thick), color='green')
                                )
                            )
                            flow=0
                if 'Directflow[{},{}]'.format(i, Destination) in Vars.keys():
                    flow += Vars['Directflow[{},{}]'.format(i, Destination)]
                if flow+hubflow != 0:
                    fig.add_trace(
                        go.Scattergeo(
                            lat=[airport_data['Latitude (deg)'][i],
                                 airport_data['Latitude (deg)'][airports[Destination]]],
                            lon=[airport_data['Longitude (deg)'][i],
                                 airport_data['Longitude (deg)'][airports[Destination]]],
                            mode='lines',
                            text=airports,
                            line=dict(width=max((flow+hubflow) / total_flow * scale_factor, min_line_thick), color='red')
                        )
                    )
                    flow=0
                    hubflow=0
            elif 'Directflow[{},{}]'.format(i, Destination) in Vars.keys():
                flow+= Vars['Directflow[{},{}]'.format(i,Destination)]
                if flow != 0:
                    fig.add_trace(
                        go.Scattergeo(
                            lat=[airport_data['Latitude (deg)'][i], airport_data['Latitude (deg)'][airports[Destination]]],
                            lon=[airport_data['Longitude (deg)'][i], airport_data['Longitude (deg)'][airports[Destination]]],
                            mode='lines',
                            text=airports,
                            line=dict(width=max(flow/total_flow*scale_factor,min_line_thick), color='red')
                        )
                    )
                    flow=0

    if problem_number == 2:
        Vars = {}
        for sol in solution['Vars']:
            Vars[sol["VarName"]] = sol['X']
        total_flow = 0
        flow = 0
        hubflow = 0
        for i in range(len(airports)):
            for r in problem.route_index:
                if 'Directflow[{},{},{}]'.format(i, Destination, r) in Vars.keys():
                    total_flow += Vars['Directflow[{},{},{}]'.format(i, Destination, r)]
                for n in problem.route_index:
                    if 'Hubflow[{},{},{},{}]'.format(i,Destination,r,n) in Vars.keys():
                        total_flow += Vars['Hubflow[{},{},{},{}]'.format(i,Destination,r,n)]
        print(total_flow)
        for i in range(len(airports)):
            if i == 0:
                for j in range(len(airports)):
                    for r in problem.route_index:
                        for n in problem.route_index:
                            if 'Hubflow[{},{},{},{}]'.format(j,Destination,r,n) in Vars.keys():
                                flow += Vars['Hubflow[{},{},{},{}]'.format(j,Destination,r,n)]
                                hubflow += Vars['Hubflow[{},{},{},{}]'.format(j,Destination,r,n)]
                    print(i,Destination,flow,hubflow)
                    if flow != 0:
                        fig.add_trace(
                            go.Scattergeo(
                                lat=[airport_data['Latitude (deg)'][j],
                                     airport_data['Latitude (deg)'][airports[i]]],
                                lon=[airport_data['Longitude (deg)'][j],
                                     airport_data['Longitude (deg)'][airports[i]]],
                                mode='lines',
                                text=airports,
                                line=dict(width=max(flow/total_flow*scale_factor,min_line_thick), color='green')
                            )
                        )
                        flow=0
                for r in problem.route_index:
                    if 'Directflow[{},{},{}]'.format(i, Destination, r) in Vars.keys():
                        flow += Vars['Directflow[{},{},{}]'.format(i, Destination, r)]
                        print(flow)
                fig.add_trace(
                    go.Scattergeo(
                        lat=[airport_data['Latitude (deg)'][i],
                             airport_data['Latitude (deg)'][airports[Destination]]],
                        lon=[airport_data['Longitude (deg)'][i],
                             airport_data['Longitude (deg)'][airports[Destination]]],
                        mode='lines',
                        text=airports,
                        line=dict(width=max((flow+hubflow) / total_flow * scale_factor, min_line_thick), color='red')
                    )
                )
                flow=0
                hubflow=0
            else:
                for r in problem.route_index:
                    if 'Directflow[{},{},{}]'.format(i, Destination, r) in Vars.keys():
                        flow+= Vars['Directflow[{},{},{}]'.format(i, Destination, r)]
                if flow != 0:
                    fig.add_trace(
                        go.Scattergeo(
                            lat=[airport_data['Latitude (deg)'][i], airport_data['Latitude (deg)'][airports[Destination]]],
                            lon=[airport_data['Longitude (deg)'][i], airport_data['Longitude (deg)'][airports[Destination]]],
                            mode='lines',
                            text=airports,
                            line=dict(width=max(flow/total_flow*scale_factor,min_line_thick), color='red')
                        )
                    )
                    flow=0
    fig.show()
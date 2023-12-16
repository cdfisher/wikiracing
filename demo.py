"""demo.py
Chris Fisher, 2023

Demo for my implementation of a wikiracing solver for COMP 545.
"""

import json
from pathfinder import bfs
from datetime import datetime

input_file = 'osrs_7dec2023_noredir.json'
remove_redirects = True

with open(input_file, 'r') as infile:
    graph_data = json.load(infile)

redirects = dict()
for key in graph_data["redirects"]:
    redirects[int(key)] = int(graph_data["redirects"][key])

graph = dict()
for key in graph_data["graph"]:
    try:
        if not remove_redirects:
            graph[int(key)] = set(graph_data["graph"][key])
        else:
            adj = set(graph_data["graph"][key])
            for _ in set(graph_data["graph"][key]):
                if _ in redirects.keys():
                    adj.remove(_)
            if key in adj:
                adj.remove(key)
            graph[int(key)] = adj

    # Handle case where pages do not link anywhere
    except TypeError:
        continue

# Fetch a saved ID map so that there aren't any MediaWiki API calls needed in order to translate
# page IDs to titles.
id_map = dict()
name_map = dict()
for key in graph_data["mapping"]:
    id_map[int(key)] = graph_data["mapping"][key]
    name_map[graph_data["mapping"][key]] = int(key)

run = True

while run:
    try:
        try:
            start = input("Starting page: ")
            end = input("Ending page: ")
            start = name_map[start]
            end = name_map[end]
        except KeyError:
            print('Invalid page name')
            continue

        search_start = datetime.now()

        if remove_redirects:
            if start in redirects.keys():
                start = int(redirects[start])
            if end in redirects.keys():
                end = int(redirects[end])

        path_ids = bfs(graph, start, end)

        print(f'Pathfinding took {datetime.now() - search_start}.')

        if path_ids != -1:
            print(f'Going from {id_map[start]} to {id_map[end]} takes '
                  f'{len(path_ids) - 1} steps.\nSolution:')

            for i in range(len(path_ids)):
                print(f'{i}) {id_map[path_ids[i]]}')

        else:
            print(f'There is no path from {id_map[start]} to {id_map[end]}.')

    except KeyboardInterrupt:
        run = False

"""find_shortest_path.py
Chris Fisher, 2023

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
for key in graph_data["mapping"]:
    id_map[int(key)] = graph_data["mapping"][key]



# TODO remove this and/or add some stuff for inputs on CLI or __name == __main__
start = 351816
end = 340102

# Longest path from old data: 236128 -> 105596
#try 71383, 105596

#print(f'Finding a path between {id_map[start]} and {id_map[end]}.')

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

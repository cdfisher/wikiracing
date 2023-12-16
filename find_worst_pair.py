"""find_worst_pair.py
Chris Fisher, 2023

Script for using the BFS traversal implemented in traversal.py to find
the starting and ending points in an unweighted, directed graph for which
the length of the shortest path between those two points is the diameter
of the graph.
"""
import json
from datetime import datetime
from traversal import bfs_traversal

graph_file = 'osrs_7dec2023_noredir.json'
# graph_file = 'rsc_7dec2023.json'

remove_redirects = False

start_time = datetime.now()
print(f'Starting at {start_time}')


with open(graph_file, 'r') as infile:
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

id_map = dict()
for key in graph_data["mapping"]:
    id_map[int(key)] = graph_data["mapping"][key]

search_start = datetime.now()
print(f'Starting search at {search_start}')

n_vertices = len(graph)
start_nodes_searched = 0


longest_path = []
longest_path_length = 0
for key in graph:
    try:
        current_path = bfs_traversal(graph, key)
        if len(current_path) > longest_path_length:
            longest_path = current_path
            longest_path_length = len(current_path)
        start_nodes_searched += 1
        if start_nodes_searched % 100 == 0:
            print(f'Searched {start_nodes_searched} of {n_vertices} starting nodes.')
    except Exception as e:
        print(f'longest_path: {longest_path}\n'
              f'length: {longest_path_length}\n'
              f'Current key: {key}')
        raise e


print(f'The longest path starts at {id_map[longest_path[0]]} and '
      f'ends at {id_map[longest_path[-1]]}.'
      f'\nIt takes {longest_path_length - 1} steps from start to end.')

path_names = []
for i in range(longest_path_length):
    path_names.append(id_map[longest_path[i]])

print('Solution:\n')

for i in range(longest_path_length):
    print(f'{i}) {path_names[i]}')

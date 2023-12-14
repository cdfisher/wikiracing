"""preprocess_sql_data.py
Chris Fisher, 2023

Script to process data from raw SQL output into an adjacency-list-based graph,
a dictionary to translate wiki page IDs into page names, and a dictionary to
resolve redirect pages to their targets.

Implements some additional processing such as filtering based on page
namespace, and lookup of redirect targets in order to improve the quality of
the resulting graph.
"""
import json
from datetime import datetime
from time import sleep
from get_redirect_target import parse

#edges_file_name = 'rsc.txt'
#titles_file_name = 'rsc_pages.txt'
edges_file_name = 'osrs.txt'
titles_file_name = 'osrs_pages.txt'

#output_name = 'rsc_7dec2023_noredir.json'
output_name = 'osrs_7dec2023_noredir.json'

# Required in order to prevent some odd behavior caused by inclusion of some technical namespaces
# OSRS
allowable_namespaces = {0, 14, 110, 112, 118, 122, 3002}
# RSC
#allowable_namespaces = {0, 14, 110, 122}

remove_redirects = True

# List of namespaces can be seen at
# {oldschool, classic}.runescape.wiki/api.php?action=query&meta=siteinfo&siprop=namespaces

data_path = './data'

edges_file = f'{data_path}/{edges_file_name}'
titles_file = f'{data_path}/{titles_file_name}'

start_time = datetime.now()

with open(edges_file, 'r', encoding='utf8') as infile:
    # Skip the first 4 lines of the file as those contain the SQL query and table
    # headers
    for i in range(4):
        infile.readline()

    # Initialize dictionary to use as adjacency list
    adj_dict = dict()

    all_pages = set()

    i = 0
    for line in infile:
        if line:    # Ignore empty lines
            if line.startswith('|'):    # Ignores some SQL info at end of file
                split_line = line.strip(' \n').split('|')
                source = int(split_line[1])
                destination = int(split_line[2])
                all_pages.add(source)
                all_pages.add(destination)
                if source not in adj_dict.keys():
                    adj_dict[source] = {destination}
                else:
                    adj_dict[source].add(destination)
                i += 1
                if i % 50000 == 0:
                    print(f'Parsed {i} edges.')

missing_keys = all_pages.difference(set(adj_dict.keys()))

# Add adjacency lists for vertices that are linked to but don't link to anything
for key in missing_keys:
    adj_dict[key] = []

with open(titles_file, 'r', encoding='utf8') as infile:
    # Skip the first 4 lines of the file as those contain the SQL query and table
    # headers
    redirects = dict()
    id_map = dict()
    namespaces = dict()
    for i in range(4):
        infile.readline()

    i = 0
    for line in infile:
        if line:    # Ignore empty lines
            if line.startswith('|'):    # Ignores some SQL info at end of file
                split_line = line.strip(' \n').split('|')
                page_id = int(split_line[1].strip())
                namespace = int(split_line[2].strip())
                title = split_line[3].strip().replace('_', ' ')
                is_redirect = int(split_line[4].strip())

                if page_id in all_pages:
                    if namespace in allowable_namespaces:
                        id_map[page_id] = title
                    namespaces[page_id] = namespace
                    if is_redirect:
                        try:
                            if len(adj_dict[page_id]) > 0:
                                redirects[page_id] = int(next(iter(adj_dict[page_id])))
                        except KeyError:
                            try:
                                print(f'KeyError: {page_id}, namespace = {namespace}')
                                adj_dict[page_id] = {int(parse(page_id))}
                            except TypeError:
                                print(f'Interwiki link from {page_id} in namespace {namespace}')
                            sleep(0.25)

                i += 1
                if i % 5000 == 0:
                    print(f'Parsed {i} pages.')

keys_to_remove = set()
# Sets are not JSON serializable, so we'll have to re-cast these lists to sets when running the graph alg itself
# While doing so, remove any nodes from the graph that aren't in an allowable namespace.
for key in adj_dict:
    if namespaces[key] in allowable_namespaces:
        try:
            destinations = []
            for element in adj_dict[key]:
                if namespaces[element] in allowable_namespaces:
                    destinations.append(element)
            adj_dict[key] = destinations
        except TypeError:
            print(f'Key {key} giving TypeError for value {adj_dict[key]}')
            adj_dict[key] = []
    else:
        keys_to_remove.add(key)

for key in keys_to_remove:
    adj_dict.pop(key, None)

if remove_redirects:
    normalized_graph = dict()
    for k in adj_dict.keys():
        redir_set = set()
        dest_set = set()
        for value in adj_dict[k]:
            if value in redirects.keys():
                redir_set.add(value)
                dest_set.add(redirects[value])
        if k in redirects.keys():
            if redirects[k] in normalized_graph.keys():
                try:
                    adj = set(adj_dict[k]).union(dest_set)
                    normalized_graph[redirects[k]] = list(adj.difference(redir_set).union(set(adj_dict[redirects[k]])))
                except KeyError:
                    adj = set(adj_dict[k]).union(dest_set)
                    normalized_graph[redirects[k]] = list(adj.difference(redir_set))
            else:
                normalized_graph[redirects[k]] = list(set(adj_dict[k]).union(dest_set).difference(redir_set))
        else:
            if k in normalized_graph.keys():
                normalized_graph[k] = list(set(adj_dict[k]).union(dest_set, set(normalized_graph[k])).difference(redir_set))
            else:
                normalized_graph[k] = list(set(adj_dict[k]).union(dest_set).difference(redir_set))

    adj_dict = normalized_graph



graph_json = {
    "graph": adj_dict,
    "mapping": id_map,
    "redirects": redirects
}

parsing_end_time = datetime.now()

with open(output_name, 'w') as outfile:
    json.dump(graph_json, outfile)

    finished_time = datetime.now()

    print(
        f'Started at {start_time}. Finished parsing at {parsing_end_time}. Finished writing at {finished_time}.\n'
        f'Time spent parsing: {parsing_end_time - start_time}. Time spent '
        f'writing: {finished_time - parsing_end_time}')

print(f'{len(adj_dict)} pages, {len(id_map)} titles, {len(redirects)} redirects')

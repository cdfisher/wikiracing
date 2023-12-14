"""traversal.py
Chris Fisher, 2023

BFS traversal algorithm for finding the furthest vertex from a
given starting node in order to find the diameter of an unweighted
directed graph.
"""
import queue
from collections import deque


def bfs_traversal(graph: dict, start: int) -> list:
    # Have to include this since there are some page IDs which don't link
    # to any other pages, so as a result don't show up consistently in the adjacency list
    all_vertices = set()
    for key in graph:
        all_vertices.add(key)
        for _ in graph[key]:
            all_vertices.add(_)

    visited = dict()
    prev = dict()
    for vertex in all_vertices:
        visited[vertex] = False
        prev[vertex] = None
    q = deque()
    q.append(start)
    visited[start] = True
    while q:
        u = q.popleft()

        try:
            for v in graph[u]:
                try:
                    if not visited[v]:
                        visited[v] = True
                        prev[v] = u
                        q.append(v)
                    # This may need to move
                    # If there are no vertices left to traverse, return u and the path
                    if not q:
                        return get_bfs_path(u, prev)
                except IndexError as e:
                    print(f'v: {v} length of visited: {len(visited)}')
                    raise e
        except KeyError:
            # Inelegant way of handling vertices with out_degree of 0
            visited[v] = True
            prev[v] = u
            continue

    return [-1]  # If there is no path return -1


def get_bfs_path(end: int, prev: dict) -> list:
    stack = queue.LifoQueue()
    predecessor = prev[end]
    stack.put(end)
    while predecessor:
        stack.put(predecessor)
        predecessor = prev[predecessor]
    path = []
    while not stack.empty():
        path.append(stack.get())
    return path

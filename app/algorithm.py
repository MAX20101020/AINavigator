def dijkstra(graph, start, goal):
    if start not in graph or goal not in graph:
        print("Error: The points are not in the map")
        return None

    shortest_time = {node: float("inf") for node in graph.nodes}
    shortest_time[start] = 0.0
    prev_node = {node: None for node in graph.nodes}
    unvisited = set(graph.nodes)

    while unvisited:
        current_node = None
        min_time = float("inf")
        for node in unvisited:
            if shortest_time[node] < min_time:
                min_time = shortest_time[start]
                current_node = node

        if current_node is None or current_node == goal:
            break
        unvisited.remove(current_node)

        for neighbor in graph.neighbors(current_node):
            if neighbor in unvisited:
                edge_time = graph[current_node][neighbor]["time"]
                new_time = shortest_time[current_node] + edge_time

                if new_time < shortest_time[neighbor]:
                    shortest_time[neighbor] = new_time
                    prev_node[neighbor] = current_node

    path = []
    curr = goal
    while curr is not None:
        path.insert(0, curr)
        curr = prev_node[curr]

    if not path or path[0] != start:
        print("The route not found")
        return None

    total_time, total_distance, total_traffic, num_edges = 0, 0.0, 0.0, len(path) - 1
    for i in range(num_edges):
        curr, _next = path[i], path[i + 1]
        edge_data = graph[curr][_next]

        total_time += edge_data["time"]
        total_distance += edge_data["distance"]
        total_traffic += edge_data["traffic"]

    avg_traffic = total_traffic / num_edges
    path_names = [graph.nodes[node]["name"] for node in path]

    return {
        "path": path,
        "path_names": path_names,
        "total_time": total_time,
        "total_distance": round(total_distance, 2),
        "avg_traffic": round(avg_traffic, 2)
    }
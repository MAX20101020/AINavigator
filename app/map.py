import networkx as nx

LOCATIONS = {
        'A': 'Центр',
        'B': 'Університет',
        'C': 'Лікарня',
        'D': 'Парк',
        'E': 'Вокзал',
        'F': 'Торговий центр',
        'G': 'Аеропорт'
    }

EDGES = [
        ('A', 'B', {'distance': 3.5, 'time': 10, 'traffic': 3, 'difficulty': 1}),
        ('A', 'C', {'distance': 2.0, 'time': 8, 'traffic': 4, 'difficulty': 2}),
        ('A', 'D', {'distance': 4.0, 'time': 12, 'traffic': 2, 'difficulty': 1}),
        ('B', 'F', {'distance': 5.0, 'time': 15, 'traffic': 2, 'difficulty': 2}),
        ('C', 'E', {'distance': 6.5, 'time': 20, 'traffic': 3, 'difficulty': 3}),
        ('D', 'F', {'distance': 3.0, 'time': 9, 'traffic': 1, 'difficulty': 1}),
        ('E', 'G', {'distance': 12.0, 'time': 25, 'traffic': 2, 'difficulty': 1}),
        ('F', 'G', {'distance': 15.0, 'time': 30, 'traffic': 4, 'difficulty': 2}),
        ('B', 'C', {'distance': 2.5, 'time': 7, 'traffic': 2, 'difficulty': 1}),
        ('D', 'E', {'distance': 8.0, 'time': 18, 'traffic': 1, 'difficulty': 4})
    ]

def generate_map():
    city_map = nx.Graph()

    for code, name in LOCATIONS.items():
        city_map.add_node(code, name=name)

    for src, dst, attrs in EDGES:
        city_map.add_edge(src, dst, **attrs)

    return city_map
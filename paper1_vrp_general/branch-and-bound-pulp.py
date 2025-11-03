import pulp
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

node_counter = 0
edges = []
best_solution = ((None, None), float('-inf'))
node_values = {}


def branch_and_bound(x1_range=(0, None), x2_range=(0, None)):
    global node_counter, best_solution, edges, node_values

    # Create the PuLP problem
    U34 = pulp.LpProblem("U34", pulp.LpMaximize)

    # Define variables with bounds
    x1 = pulp.LpVariable('x1', lowBound=x1_range[0],
                         upBound=x1_range[1] if x1_range[1] is not None else None)
    x2 = pulp.LpVariable('x2', lowBound=x2_range[0],
                         upBound=x2_range[1] if x2_range[1] is not None else None)

    # Constraints
    U34 += 50 * x1 + 31 * x2 <= 250
    U34 += 3 * x1 - 2 * x2 >= -4

    # Objective function
    U34 += x1 + 0.64 * x2

    # Solve using the default CBC solver
    U34.solve(pulp.PULP_CBC_CMD(msg=0))

    node_id = node_counter
    node_counter += 1

    if pulp.LpStatus[U34.status] == "Optimal":
        x1_val = pulp.value(x1)
        x2_val = pulp.value(x2)
        objective = pulp.value(U34.objective)

        node_values[node_id] = (round(x1_val, 2), round(x2_val, 2), round(objective, 2))

        if float(x1_val).is_integer() and float(x2_val).is_integer() and objective > best_solution[1]:
            best_solution = ((x1_val, x2_val), objective)

        # Branch on non-integer variables
        if not float(x1_val).is_integer():
            x1_floor = int(np.floor(x1_val))
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=(x1_range[0], x1_floor), x2_range=x2_range)
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=(x1_floor + 1, x1_range[1]), x2_range=x2_range)

        if not float(x2_val).is_integer():
            x2_floor = int(np.floor(x2_val))
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=x1_range, x2_range=(x2_range[0], x2_floor))
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=x1_range, x2_range=(x2_floor + 1, x2_range[1]))


def visualize_tree(edges, node_values):
    G = nx.DiGraph()
    G.add_edges_from(edges)

    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')

    nx.draw_networkx_nodes(G, pos, node_color='white', node_size=1)
    nx.draw_networkx_edges(G, pos)

    labels = {}
    for node, values in node_values.items():
        labels[node] = f"x={values[0]}, y={values[1]}, z={values[2]}"

    nx.draw_networkx_labels(G, pos, labels, bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='white'))

    plt.show()


# Run the Branch-and-Bound algorithm
branch_and_bound()

print(f"Best integer result: x={best_solution[0][0]}, y={best_solution[0][1]}")

# Visualize the tree
visualize_tree(edges, node_values)

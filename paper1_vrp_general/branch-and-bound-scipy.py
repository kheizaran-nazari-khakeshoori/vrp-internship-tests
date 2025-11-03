import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches

node_counter = 0
edges = []
best_solution = ((None, None), float('-inf')) 
node_values = {}


def branch_and_bound(x1_range=(0, None), x2_range=(0, None)):
    global node_counter, best_solution, edges, node_values

    c = [-1, -0.64]
    A_ub = [[50, 31], [-3, 2]]
    b_ub = [250, 4]

    bounds = [x1_range, x2_range]

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

    node_id = node_counter
    node_counter += 1

    if res.success:
        x1_val, x2_val = res.x
        objective = -res.fun  

        
        node_values[node_id] = (round(x1_val, 2), round(x2_val, 2), round(objective, 2))

       
        if x1_val.is_integer() and x2_val.is_integer() and objective > best_solution[1]:
            best_solution = ((x1_val, x2_val), objective)

   
        if not x1_val.is_integer():
            x1_floor = int(np.floor(x1_val))
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=(0, x1_floor), x2_range=x2_range)
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=(x1_floor+1, None), x2_range=x2_range)

        
        if not x2_val.is_integer():
            x2_floor = int(np.floor(x2_val))
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=x1_range, x2_range=(0, x2_floor))
            edges.append((node_id, node_counter))
            branch_and_bound(x1_range=x1_range, x2_range=(x2_floor+1, None))


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


# Execute the Branch-and-Bound algorithm and then print and visualize the result
branch_and_bound()

print(f"Best integer result: x={best_solution[0][0]}, y={best_solution[0][1]}")


visualize_tree(edges, node_values)
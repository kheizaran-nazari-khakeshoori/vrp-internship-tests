import pulp
from itertools import permutations, combinations

# ===========================
# Problem instance (small VRPTW)
# ===========================
customers = [0, 1, 2, 3]  # 0 = depot
demand = {0: 0, 1: 1, 2: 1, 3: 2}
vehicle_capacity = 3

# distance matrix
distance = {
    (0, 1): 10, (0, 2): 15, (0, 3): 20,
    (1, 0): 10, (1, 2): 35, (1, 3): 25,
    (2, 0): 15, (2, 1): 35, (2, 3): 30,
    (3, 0): 20, (3, 1): 25, (3, 2): 30
}

# time windows: [ready_time, due_date]
time_window = {
    0: (0, 100),  # depot
    1: (0, 50),
    2: (10, 60),
    3: (20, 80)
}

service_time = {0:0, 1:5, 2:5, 3:5}  # service duration at each customer

# ===========================
# Step 1: Generate all feasible routes (small example)
# Include time windows and capacity
# ===========================
def all_feasible_routes(customers, demand, capacity, distance, time_window, service_time):
    routes = []
    cust_list = customers[1:]
    for r_size in range(1, len(cust_list)+1):
        for subset in combinations(cust_list, r_size):
            for perm in permutations(subset):
                route = [0] + list(perm) + [0]
                load = sum(demand[c] for c in perm)
                if load > capacity:
                    continue
                # check time windows
                time = 0
                feasible = True
                for i in range(len(route)-1):
                    from_c, to_c = route[i], route[i+1]
                    time += distance[(from_c, to_c)]
                    time = max(time, time_window[to_c][0])
                    if time > time_window[to_c][1]:
                        feasible = False
                        break
                    time += service_time[to_c]
                if feasible:
                    routes.append(route)
    return routes

feasible_routes = all_feasible_routes(customers, demand, vehicle_capacity, distance, time_window, service_time)
print(f"Number of feasible routes: {len(feasible_routes)}")
for r in feasible_routes:
    print(r)

# Compute route costs
route_costs = {tuple(r): sum(distance[(r[i], r[i+1])] for i in range(len(r)-1)) for r in feasible_routes}

# ===========================
# Step 2: Master problem (Set Partitioning)
# ===========================
master_prob = pulp.LpProblem("VRPTW_Master", pulp.LpMinimize)
x_vars = {tuple(r): pulp.LpVariable(f"x_{i}", cat='Binary') for i,r in enumerate(feasible_routes)}

# Objective
master_prob += pulp.lpSum([route_costs[tuple(r)] * x_vars[tuple(r)] for r in feasible_routes])

# Each customer visited exactly once
for c in customers[1:]:
    master_prob += pulp.lpSum([x_vars[tuple(r)] for r in feasible_routes if c in r]) == 1

# Solve
master_prob.solve(pulp.PULP_CBC_CMD(msg=1))

# ===========================
# Step 3: Output
# ===========================
print("\nSelected routes in solution:")
for r in feasible_routes:
    if pulp.value(x_vars[tuple(r)]) > 0.5:
        print(tuple(r), "cost:", route_costs[tuple(r)])

print("\nTotal cost:", pulp.value(master_prob.objective))

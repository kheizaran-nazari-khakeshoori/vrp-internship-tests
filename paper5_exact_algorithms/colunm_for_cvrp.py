import pulp
from itertools import permutations, combinations

# ===========================
# Problem instance (small CVRP)
# ===========================
customers = [0, 1, 2, 3]  # 0 = depot
demand = {0: 0, 1: 1, 2: 1, 3: 2}
vehicle_capacity = 3

distance = {
    (0, 1): 10, (0, 2): 15, (0, 3): 20,
    (1, 0): 10, (1, 2): 35, (1, 3): 25,
    (2, 0): 15, (2, 1): 35, (2, 3): 30,
    (3, 0): 20, (3, 1): 25, (3, 2): 30
}

# ===========================
# Step 1: Generate all feasible routes (all subsets of customers)
# ===========================
def all_routes(customers, capacity, demand):
    routes = []
    customer_list = customers[1:]  # exclude depot
    # generate all subsets of customers
    for r_size in range(1, len(customer_list)+1):
        for subset in combinations(customer_list, r_size):
            # check all permutations of this subset
            for perm in permutations(subset):
                route = [0] + list(perm) + [0]
                load = sum(demand[c] for c in perm)
                if load <= capacity:
                    routes.append(route)
    return routes

feasible_routes = all_routes(customers, vehicle_capacity, demand)
print(f"Number of feasible routes: {len(feasible_routes)}")
for r in feasible_routes:
    print(r)

# Compute route costs
route_costs = {tuple(r): sum(distance[(r[i], r[i+1])] for i in range(len(r)-1)) for r in feasible_routes}

# ===========================
# Step 2: Master problem (Set Partitioning LP)
# ===========================
master_prob = pulp.LpProblem("CVRP_Master", pulp.LpMinimize)

# Variables: x_r = 1 if route r is selected
x_vars = {tuple(r): pulp.LpVariable(f"x_{i}", cat='Binary') for i, r in enumerate(feasible_routes)}

# Objective: minimize total cost
master_prob += pulp.lpSum([route_costs[tuple(r)] * x_vars[tuple(r)] for r in feasible_routes])

# Constraints: each customer visited exactly once
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

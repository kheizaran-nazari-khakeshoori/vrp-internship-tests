from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus
import itertools

# ===========================
# Problem instance
# ===========================
# Customers: 0 = depot
customers = [0, 1, 2, 3]  
demand = {0: 0, 1: 1, 2: 1, 3: 2}
vehicle_capacity = 3

# Distance matrix (symmetric)
distance = {
    (0,1):10, (0,2):15, (0,3):20,
    (1,0):10, (1,2):35, (1,3):25,
    (2,0):15, (2,1):35, (2,3):30,
    (3,0):20, (3,1):25, (3,2):30
}

# ===========================
# Generate all feasible routes (any subset of customers)
# ===========================
def generate_feasible_routes(customers, demand, capacity):
    routes = []
    cust_list = customers[1:]  # exclude depot
    for L in range(1, len(cust_list)+1):  # subsets of length 1..N
        for subset in itertools.permutations(cust_list, L):
            load = sum(demand[c] for c in subset)
            if load <= capacity:
                route = [0] + list(subset) + [0]
                routes.append(route)
    return routes

feasible_routes = generate_feasible_routes(customers, demand, vehicle_capacity)

# Check if feasible routes exist
if len(feasible_routes) == 0:
    print("Error: No feasible routes generated. Adjust vehicle capacity or customer demands.")
    exit()

print("Feasible routes generated:")
for r in feasible_routes:
    print(r)
print(f"Total feasible routes: {len(feasible_routes)}\n")

# ===========================
# Route cost
# ===========================
def route_cost(route):
    return sum(distance[(route[i], route[i+1])] for i in range(len(route)-1))

# Convert routes to tuple keys
route_costs = {tuple(r): route_cost(r) for r in feasible_routes}

# ===========================
# Master problem
# ===========================
def solve_master(routes, costs):
    model = LpProblem("VRP_Master", LpMinimize)
    # Convert routes to tuples for keys
    x = {tuple(r): LpVariable(f"x_{tuple(r)}", lowBound=0, upBound=1) for r in routes}

    # Objective
    model += lpSum([costs[tuple(r)] * x[tuple(r)] for r in routes])

    # Constraints: each customer visited exactly once
    for cust in customers[1:]:
        customer_in_routes = [x[tuple(r)] for r in routes if cust in r]
        if len(customer_in_routes) == 0:
            print(f"Error: Customer {cust} not in any route. LP infeasible!")
            exit()
        model += lpSum(customer_in_routes) == 1

    model.solve()
    return model, x

# ===========================
# Solve master LP
# ===========================
master_model, x_vars = solve_master(feasible_routes, route_costs)

print("LP Status:", LpStatus[master_model.status])
print("\nSelected routes in LP solution:")
for r, var in x_vars.items():
    if var.varValue > 1e-5:
        print(f"Route {r} -> Fractional assignment: {var.varValue:.2f}, Cost: {route_costs[r]}")

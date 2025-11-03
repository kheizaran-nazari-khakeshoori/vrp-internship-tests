import random
import copy
import math

# ===========================
# Problem instance (small VRP)
# ===========================
customers = [0, 1, 2, 3]  # 0 = depot
demand = {0: 0, 1: 1, 2: 1, 3: 2}
vehicle_capacity = 3

distance = {
    (0,1):10, (0,2):15, (0,3):20,
    (1,0):10, (1,2):35, (1,3):25,
    (2,0):15, (2,1):35, (2,3):30,
    (3,0):20, (3,1):25, (3,2):30
}

# ===========================
# Cost function
# ===========================
def route_cost(route):
    return sum(distance[(route[i], route[i+1])] for i in range(len(route)-1))

def solution_cost(solution):
    total = 0
    for route in solution:
        load = sum(demand[c] for c in route if c != 0)
        if load > vehicle_capacity:
            total += 1000*(load-vehicle_capacity)  # penalty
        total += route_cost(route)
    return total

# ===========================
# Initial solution (simple sequential)
# ===========================
def initial_solution():
    cust_list = customers[1:]
    routes = []
    current_route = [0]
    current_load = 0
    for c in cust_list:
        if current_load + demand[c] <= vehicle_capacity:
            current_route.append(c)
            current_load += demand[c]
        else:
            current_route.append(0)
            routes.append(current_route)
            current_route = [0, c]
            current_load = demand[c]
    current_route.append(0)
    routes.append(current_route)
    return routes

# ===========================
# ALNS operators
# ===========================
def random_removal(solution, n_remove=1):
    new_solution = copy.deepcopy(solution)
    all_customers = [c for route in new_solution for c in route if c != 0]
    removed = random.sample(all_customers, n_remove)
    for route in new_solution:
        route[:] = [c for c in route if c not in removed]
    return new_solution, removed

def greedy_insertion(solution, removed):
    new_solution = copy.deepcopy(solution)
    for c in removed:
        best_cost = math.inf
        best_pos = None
        best_route_idx = None
        for r_idx, route in enumerate(new_solution):
            for i in range(1, len(route)):
                temp_route = route[:i] + [c] + route[i:]
                load = sum(demand[cust] for cust in temp_route if cust != 0)
                if load <= vehicle_capacity:
                    cost = route_cost(temp_route)
                    if cost < best_cost:
                        best_cost = cost
                        best_pos = i
                        best_route_idx = r_idx
        if best_route_idx is not None:
            new_solution[best_route_idx] = new_solution[best_route_idx][:best_pos] + [c] + new_solution[best_route_idx][best_pos:]
        else:
            # if no feasible insertion, start new route
            new_solution.append([0, c, 0])
    return new_solution

# ===========================
# ALNS main loop
# ===========================
def ALNS(max_iterations=100, n_remove=1):
    current_solution = initial_solution()
    best_solution = copy.deepcopy(current_solution)
    best_cost = solution_cost(best_solution)

    for iteration in range(max_iterations):
        # Destroy
        destroyed_solution, removed = random_removal(current_solution, n_remove)
        # Repair
        new_solution = greedy_insertion(destroyed_solution, removed)
        # Evaluate
        new_cost = solution_cost(new_solution)
        delta = new_cost - solution_cost(current_solution)

        # Acceptance criterion (Simulated Annealing style)
        T = max(0.01, 1.0 - iteration/max_iterations)
        if delta < 0 or random.random() < math.exp(-delta/T):
            current_solution = new_solution
            if new_cost < best_cost:
                best_solution = copy.deepcopy(new_solution)
                best_cost = new_cost

        if iteration % 10 == 0:
            print(f"Iteration {iteration}, best cost: {best_cost}")

    return best_solution, best_cost

# ===========================
# Run ALNS
# ===========================
if __name__ == "__main__":
    best_sol, best_cost = ALNS(max_iterations=100, n_remove=1)
    print("\nBest solution routes:")
    for route in best_sol:
        print(route)
    print(f"Total cost: {best_cost}")

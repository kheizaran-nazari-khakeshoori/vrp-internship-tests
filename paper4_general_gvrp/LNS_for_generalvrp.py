import random
import copy

# ===========================
# Problem instance (GVRP)
# ===========================
customers = [0, 1, 2, 3]  # 0 = depot
demand = {0:0, 1:1, 2:1, 3:2}
vehicle_capacity = 3

distance = {
    (0,1):10, (0,2):15, (0,3):20,
    (1,0):10, (1,2):35, (1,3):25,
    (2,0):15, (2,1):35, (2,3):30,
    (3,0):20, (3,1):25, (3,2):30
}

# ===========================
# Cost functions
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
# Initial solution
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
# Destroy operator: remove a large part of customers
# ===========================
def destroy(solution, n_remove):
    new_solution = copy.deepcopy(solution)
    all_customers = [c for route in new_solution for c in route if c != 0]
    if len(all_customers) == 0:
        return new_solution, []
    n_remove = min(n_remove, len(all_customers))
    removed_customers = random.sample(all_customers, n_remove)
    # remove customers from routes
    for route in new_solution:
        route[:] = [c for c in route if c not in removed_customers]
    # remove routes with only depot
    new_solution = [r for r in new_solution if len(r) > 2]
    return new_solution, removed_customers

# ===========================
# Repair operator: greedy insertion
# ===========================
def repair(solution, removed_customers):
    new_solution = copy.deepcopy(solution)
    for c in removed_customers:
        best_cost = float('inf')
        best_pos = None
        best_route_idx = None
        for r_idx, route in enumerate(new_solution):
            for i in range(1, len(route)):
                temp_route = route[:i] + [c] + route[i:]
                load = sum(demand[x] for x in temp_route if x != 0)
                if load <= vehicle_capacity:
                    cost = route_cost(temp_route)
                    if cost < best_cost:
                        best_cost = cost
                        best_pos = i
                        best_route_idx = r_idx
        if best_route_idx is not None:
            new_solution[best_route_idx] = new_solution[best_route_idx][:best_pos] + [c] + new_solution[best_route_idx][best_pos:]
        else:
            # start a new route
            new_solution.append([0, c, 0])
    return new_solution

# ===========================
# LNS main loop
# ===========================
def LNS(max_iterations=100, destroy_fraction=0.5):
    current_solution = initial_solution()
    best_solution = copy.deepcopy(current_solution)
    best_cost = solution_cost(best_solution)

    for iteration in range(max_iterations):
        n_remove = max(1, int(destroy_fraction * sum(len(r)-2 for r in current_solution)))
        # Destroy
        destroyed_solution, removed_customers = destroy(current_solution, n_remove)
        # Repair
        new_solution = repair(destroyed_solution, removed_customers)
        # Evaluate
        new_cost = solution_cost(new_solution)
        if new_cost < solution_cost(current_solution):
            current_solution = new_solution
            if new_cost < best_cost:
                best_solution = copy.deepcopy(new_solution)
                best_cost = new_cost

        if iteration % 10 == 0:
            print(f"Iteration {iteration}, best cost: {best_cost}")

    return best_solution, best_cost

# ===========================
# Run LNS
# ===========================
if __name__ == "__main__":
    best_sol, best_cost = LNS(max_iterations=100, destroy_fraction=0.5)
    print("\nBest solution routes:")
    for route in best_sol:
        print(route)
    print(f"Total cost: {best_cost}")

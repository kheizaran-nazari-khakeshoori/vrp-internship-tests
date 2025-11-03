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
# Neighborhood operators
# ===========================
def swap_customers(solution):
    new_solution = copy.deepcopy(solution)
    all_customers = [c for route in new_solution for c in route if c != 0]
    if len(all_customers) < 2:
        return new_solution
    a, b = random.sample(all_customers, 2)
    for route in new_solution:
        for i in range(1, len(route)-1):
            if route[i] == a:
                route[i] = b
            elif route[i] == b:
                route[i] = a
    # remove routes that have only depots
    new_solution = [r for r in new_solution if len(r) > 2]
    return new_solution

def relocate_customer(solution):
    new_solution = copy.deepcopy(solution)
    # pick a random non-depot customer
    all_customers = [(r_idx, i, c) for r_idx, route in enumerate(new_solution) 
                     for i, c in enumerate(route) if c != 0]
    if not all_customers:
        return new_solution
    r_idx, i, c = random.choice(all_customers)
    new_solution[r_idx].pop(i)
    # remove route if it only has depot left
    if len(new_solution[r_idx]) <= 2:
        new_solution.pop(r_idx)

    # pick a route to insert
    if not new_solution:
        new_solution.append([0, c, 0])
        return new_solution

    r_insert = random.randint(0, len(new_solution)-1)
    route_len = len(new_solution[r_insert])
    # insert between depots
    pos_insert = 1 if route_len <= 2 else random.randint(1, route_len-1)
    new_solution[r_insert].insert(pos_insert, c)
    return new_solution

def two_opt(route):
    if len(route) <= 4:
        return route
    i, j = sorted(random.sample(range(1, len(route)-1), 2))
    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
    return new_route

def two_opt_all(solution):
    new_solution = copy.deepcopy(solution)
    r_idx = random.randint(0, len(new_solution)-1)
    new_solution[r_idx] = two_opt(new_solution[r_idx])
    return new_solution

# ===========================
# Variable Neighborhood Search (VNS)
# ===========================
def VNS(max_iterations=100):
    current_solution = initial_solution()
    best_solution = copy.deepcopy(current_solution)
    best_cost = solution_cost(best_solution)
    
    neighborhoods = [swap_customers, relocate_customer, two_opt_all]
    
    for iteration in range(max_iterations):
        k = 0
        while k < len(neighborhoods):
            # Shake
            neighbor = neighborhoods[k](current_solution)
            # Local search
            improved = True
            while improved:
                new_neighbor = neighborhoods[k](neighbor)
                if solution_cost(new_neighbor) < solution_cost(neighbor):
                    neighbor = new_neighbor
                else:
                    improved = False
            # Acceptance
            if solution_cost(neighbor) < solution_cost(current_solution):
                current_solution = neighbor
                if solution_cost(current_solution) < best_cost:
                    best_solution = copy.deepcopy(current_solution)
                    best_cost = solution_cost(best_solution)
                k = 0  # restart neighborhoods
            else:
                k += 1  # move to next neighborhood

        if iteration % 10 == 0:
            print(f"Iteration {iteration}, best cost: {best_cost}")
    
    return best_solution, best_cost

# ===========================
# Run VNS
# ===========================
if __name__ == "__main__":
    best_sol, best_cost = VNS(max_iterations=100)
    print("\nBest solution routes:")
    for route in best_sol:
        print(route)
    print(f"Total cost: {best_cost}")

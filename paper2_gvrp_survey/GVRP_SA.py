import random
import math
import copy

# ===========================
# Define problem instance
# ===========================

# Example customers: (id, demand, x, y)
customers = [
    (0, 0, 50, 50),  # depot
    (1, 1, 20, 30),
    (2, 1, 40, 70),
    (3, 2, 60, 20),
    (4, 1, 80, 80)
]

vehicle_capacity = 3
num_vehicles = 2

# Fuel/emission factor: fuel cost per distance unit
fuel_factor = 1.5  # can be tuned

# ===========================
# Distance calculation
# ===========================
def euclidean_distance(a, b):
    return math.sqrt((a[2]-b[2])**2 + (a[3]-b[3])**2)

def total_distance(tour):
    dist = 0
    for i in range(len(tour)-1):
        dist += euclidean_distance(customers[tour[i]], customers[tour[i+1]])
    return dist

# ===========================
# Cost function (green VRP)
# ===========================
def compute_cost(solution):
    """
    solution: list of routes, each route is a list of customer ids
    """
    total = 0
    for route in solution:
        dist = 0
        load = 0
        for i in range(len(route)-1):
            dist += euclidean_distance(customers[route[i]], customers[route[i+1]])
            load += customers[route[i]][1]
        # Penalize capacity violation
        penalty = max(0, load - vehicle_capacity) * 1000
        total += dist * fuel_factor + penalty
    return total

# ===========================
# Initial solution (simple split)
# ===========================
def initial_solution():
    customer_ids = [c[0] for c in customers if c[0] != 0]
    random.shuffle(customer_ids)
    # Split customers evenly into vehicles
    solution = []
    per_vehicle = len(customer_ids) // num_vehicles
    for i in range(num_vehicles):
        route = [0] + customer_ids[i*per_vehicle:(i+1)*per_vehicle] + [0]
        solution.append(route)
    # Add remaining customers to last vehicle
    remaining = customer_ids[num_vehicles*per_vehicle:]
    if remaining:
        solution[-1] = solution[-1][:-1] + remaining + [0]
    return solution

# ===========================
# Neighborhood: swap two customers
# ===========================
def neighbor(solution):
    new_solution = copy.deepcopy(solution)
    # pick two routes randomly
    r1, r2 = random.sample(range(len(solution)), 2)
    # pick random customer (not depot)
    if len(new_solution[r1]) <= 2 or len(new_solution[r2]) <= 2:
        return new_solution
    i = random.randint(1, len(new_solution[r1])-2)
    j = random.randint(1, len(new_solution[r2])-2)
    # swap customers
    new_solution[r1][i], new_solution[r2][j] = new_solution[r2][j], new_solution[r1][i]
    return new_solution

# ===========================
# Simulated Annealing
# ===========================
def simulated_annealing(max_iter=500, initial_temp=1000, cooling_rate=0.995):
    current_solution = initial_solution()
    current_cost = compute_cost(current_solution)
    best_solution = copy.deepcopy(current_solution)
    best_cost = current_cost
    T = initial_temp

    for iteration in range(max_iter):
        new_solution = neighbor(current_solution)
        new_cost = compute_cost(new_solution)
        delta = new_cost - current_cost
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_solution = new_solution
            current_cost = new_cost
            if current_cost < best_cost:
                best_solution = copy.deepcopy(current_solution)
                best_cost = current_cost
        T *= cooling_rate

        if iteration % 50 == 0:
            print(f"Iteration {iteration}, best cost: {best_cost:.2f}")

    return best_solution, best_cost

# ===========================
# Main
# ===========================
if __name__ == "__main__":
    best_solution, best_cost = simulated_annealing()
    print("\nBest solution routes:")
    for route in best_solution:
        print(route)
    print(f"\nTotal green cost: {best_cost:.2f}")

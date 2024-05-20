import random
import time
import matplotlib.pyplot as plt

def read_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines]
    
    num_sectors = int(lines[0].split()[-1])
    num_locations = int(lines[1].split()[-1])
    installation_cost = []
    sectors = []
    list_maps_demands = []
    index = 2
    
    for _ in range(num_locations):
        linea = lines[index]
        elements = linea.split()
        for elemento in elements:
            installation_cost.append(int(elemento))
        index += 1
        if len(installation_cost) == num_locations:
            break
    
    for sec in range(num_sectors):
        list_demands = []    
        num_demand_locations = int(lines[index].split()[-1])
        for _ in range(num_demand_locations):
            if index == len(lines) - 1:
                break
            index += 1
            linea = lines[index]
            elements = linea.split()
            for elemento in elements:
                list_demands.append(int(elemento))
            if len(list_demands) == num_demand_locations:
                index += 1
                break
        placesMap = {"demand_places": num_demand_locations, "satisfaction_list": list_demands}
        list_maps_demands.append(placesMap)
        
    return {
        "num_sectors": num_sectors,
        "num_locations": num_locations,
        "installation_cost": installation_cost,
        "sectors": list_maps_demands
    }

def print_data(result):
    print("Número de sectores:", result["num_sectors"])
    print("Número de ubicaciones:", result["num_locations"])
    print("Costo de instalación de cada clínica:", result["installation_cost"])
    
    print("Detalles de los sectores:")
    sectorCount = 1
    for sector in result["sectors"]:
        print(f"Sector {sectorCount} - Número de lugares que satisfacen la demanda:", sector["demand_places"])
        print("Lista de lugares donde se puede instalar una clínica:", sector["satisfaction_list"])
        print()
        sectorCount += 1

def greedy_deterministic(data):
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    sectors = data['sectors']
    
    selected_locations = set()
    covered_sectors = set()
    
    while len(covered_sectors) < data['num_sectors']:
        best_location = None
        best_cost_benefit = float('inf')
        
        for loc in range(num_locations):
            if loc in selected_locations:
                continue
            benefit = sum(1 for i, sector in enumerate(sectors) if loc in sector['satisfaction_list'] and i not in covered_sectors)
            
            if benefit > 0 and loc < len(installation_cost):
                cost_benefit = installation_cost[loc] / benefit

                if cost_benefit < best_cost_benefit:
                    best_cost_benefit = cost_benefit
                    best_location = loc
        
        if best_location is not None:
            selected_locations.add(best_location)
            for i, sector in enumerate(sectors):
                if best_location in sector['satisfaction_list']:
                    covered_sectors.add(i)
        else:
            print("No valid location found to cover remaining sectors.")
            break
    
    return selected_locations

def greedy_stochastic(data, num_iterations=10):
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    sectors = data['sectors']
    
    best_solution = None
    best_solution_cost = float('inf')
    
    for _ in range(num_iterations):
        selected_locations = set()
        covered_sectors = set()
        solution_cost = 0
        
        while len(covered_sectors) < data['num_sectors']:
            available_locations = [loc for loc in range(num_locations) if loc not in selected_locations]
            if not available_locations:
                break
            
            loc = random.choice(available_locations)
            selected_locations.add(loc)
            
            for i, sector in enumerate(sectors):
                if loc in sector['satisfaction_list'] and i not in covered_sectors:
                    covered_sectors.add(i)
                    solution_cost += installation_cost[loc]
        
        if solution_cost < best_solution_cost:
            best_solution = selected_locations
            best_solution_cost = solution_cost
    
    return best_solution, best_solution_cost

def objective_function(solution, installation_cost):
    return sum(installation_cost[loc] for loc in solution)

def generate_neighbor(current_solution, num_locations):
    neighbor = current_solution[:]
    index = random.randint(0, len(neighbor) - 1)
    new_loc = random.randint(0, num_locations - 1)
    neighbor[index] = new_loc
    return neighbor

def hill_climbing(data, max_iterations=1000):
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    initial_solution = greedy_stochastic(data)[0]
    current_solution = list(initial_solution)
    current_fitness = objective_function(current_solution, installation_cost)
    
    iterations = 0
    while iterations < max_iterations:
        neighbor = generate_neighbor(current_solution, num_locations)
        neighbor_fitness = objective_function(neighbor, installation_cost)
        
        if neighbor_fitness < current_fitness:
            current_solution = neighbor
            current_fitness = neighbor_fitness
        else:
            iterations += 1
    
    return current_solution, current_fitness

def brisket_variant(data, remove_count=2):
    initial_solution = greedy_stochastic(data)[0]
    current_solution = list(initial_solution)
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    
    for _ in range(remove_count):
        if current_solution:
            current_solution.pop(random.randint(0, len(current_solution) - 1))
    
    remaining_sectors = set(range(data['num_sectors']))
    while remaining_sectors:
        best_location = None
        best_cost_benefit = float('inf')
        
        for loc in range(num_locations):
            if loc in current_solution:
                continue
            covered_sectors_count = sum(1 for sector_idx in remaining_sectors if loc in data['sectors'][sector_idx]['satisfaction_list'])
            if covered_sectors_count == 0:
                continue
            cost_benefit = installation_cost[loc] / covered_sectors_count

            if cost_benefit < best_cost_benefit:
                best_cost_benefit = cost_benefit
                best_location = loc
        
        if best_location is not None:
            current_solution.append(best_location)
            remaining_sectors -= {sector_idx for sector_idx in remaining_sectors if best_location in data['sectors'][sector_idx]['satisfaction_list']}
    
    return current_solution, objective_function(current_solution, installation_cost)

def greedy_stochastic_benchmark(file_name, num_executions=10):
    execution_times = []
    objective_function_values = []

    for _ in range(num_executions):
        data = read_file(file_name)

        start_time = time.time()
        _, best_solution_cost = greedy_stochastic(data)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        objective_function_values.append(best_solution_cost)

    avg_execution_time = sum(execution_times) / num_executions
    avg_fitness = sum(objective_function_values) / num_executions

    print(f"Avg Execution Time Greedy Stochastic: {avg_execution_time} seconds")
    print(f"Avg Fitness Greedy Stochastic: {avg_fitness}")

    plt.plot(range(num_executions), objective_function_values, marker='o')
    plt.title('Convergence Plot Greedy Stochastic')
    plt.xlabel('Execution')
    plt.ylabel('Objective Function Value')
    plt.show()

def hill_climbing_benchmark(file_name, num_executions=5, max_iterations=1000):
    execution_times = []
    objective_function_values = []

    for _ in range(num_executions):
        data = read_file(file_name)

        start_time = time.time()
        _, best_fitness = hill_climbing(data, max_iterations)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        objective_function_values.append(best_fitness)

    avg_execution_time = sum(execution_times) / num_executions
    avg_fitness = sum(objective_function_values) / num_executions

    print(f"Avg Execution Time Hill Climbing: {avg_execution_time} seconds")
    print(f"Avg Fitness Hill Climbing: {avg_fitness}")

    plt.plot(range(num_executions), objective_function_values, marker='o')
    plt.title('Convergence Plot Hill Climbing')
    plt.xlabel('Execution')
    plt.ylabel('Objective Function Value')
    plt.show()

def brisket_benchmark(file_name, num_executions=5, remove_count=2):
    execution_times = []
    objective_function_values = []

    for _ in range(num_executions):
        data = read_file(file_name)

        start_time = time.time()
        brisket_solution, brisket_fitness = brisket_variant(data, remove_count)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)
        objective_function_values.append(brisket_fitness)

    avg_execution_time = sum(execution_times) / num_executions
    avg_fitness = sum(objective_function_values) / num_executions

    print(f"Avg Execution Time Brisket: {avg_execution_time} seconds")
    print(f"Avg Fitness Brisket: {avg_fitness}")

    plt.plot(range(num_executions), objective_function_values, marker='o')
    plt.title('Convergence Plot Brisket')
    plt.xlabel('Execution')
    plt.ylabel('Objective Function Value')
    plt.show()

file_name = 'C1.txt'
data = read_file(file_name)

print_data(data)
print()

# Greedy Deterministic
deterministic_solution = greedy_deterministic(data)
print("Greedy Deterministic Solution:", deterministic_solution)
print()

# Greedy Stochastic
stochastic_solution, stochastic_cost = greedy_stochastic(data)
print("Greedy Stochastic Solution:", stochastic_solution)
print("Greedy Stochastic Cost:", stochastic_cost)
print()

# Hill Climbing
best_solution, best_fitness = hill_climbing(data)
print("Hill Climbing Best Solution:", best_solution)
print("Hill Climbing Best Fitness:", best_fitness)
print()

# Brisket Variant
brisket_solution, brisket_fitness = brisket_variant(data)
print("Brisket Variant Best Solution:", brisket_solution)
print("Brisket Variant Best Fitness:", brisket_fitness)
print()

# Benchmark
greedy_stochastic_benchmark(file_name)
hill_climbing_benchmark(file_name)
brisket_benchmark(file_name)

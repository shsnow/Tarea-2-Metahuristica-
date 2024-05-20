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
            if index == len(lines)-1:
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
    for sector in result["sectors"]:
        print("Número de lugares que satisfacen la demanda:", sector["demand_places"])
        print("Lista de lugares donde se puede instalar una clínica:", sector["satisfaction_list"])
        print()

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

    print(f"Avg Execution Time: {avg_execution_time} seconds")
    print(f"Avg Fitness: {avg_fitness}")

    plt.plot(range(num_executions), objective_function_values, marker='o')
    plt.title('Convergence Plot')
    plt.xlabel('Execution')
    plt.ylabel('Objective Function Value')
    plt.show()

# Example usage:
file_name = 'C1.txt'
data = read_file(file_name)
stochastic_solution = greedy_stochastic(data)
print("Greedy Stochastic Solution:", stochastic_solution)
print()

greedy_stochastic_benchmark(file_name)

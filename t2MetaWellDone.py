import random
import time
import matplotlib.pyplot as plt

def read_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines]
    
    num_sectors = int(lines[0].split()[-1])
    num_locations = int(lines[1].split()[-1])
    #installation_cost = list(map(int, lines[2].split()))
    installation_cost =[]
    sectors = []
    list_maps_demands = []
    index = 2
    for _ in range(num_locations):
        linea = lines[index] 
        elements = linea.split()  # Dividir la línea en elementos usando split()
        for elemento in elements:
            installation_cost.append(int(elemento))
        index += 1
        if installation_cost.__len__() == num_locations:
            break
    #print(installation_cost)
    #print("largo costo",installation_cost.__len__())
    #print("linea siguiente ",index)
    #print("line ",lines[index].split())
    for sec in range (num_sectors):
        list_demands = []    
        num_demand_locations = int(lines[index].split()[-1])
        #print("num demand: ", num_demand_locations)
        for _ in range(num_demand_locations):
            if index == len(lines)-1:
                break
            index += 1
            linea = lines[index]
            elements = linea.split()  # Dividir la línea en elementos usando split()
            for elemento in elements:
                list_demands.append(int(elemento))
                #print(list_demands)
            if len(list_demands) == num_demand_locations:
                #print("lista demandas",list_demands)
                index+=1
                break
        #print(list_demands)
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
        print("Sector",sectorCount,"Número de lugares que satisfacen la demanda:", sector["demand_places"])
        print("Lista de lugares donde se puede instalar una clínica:", sector["satisfaction_list"])
        print()
        sectorCount+=1

# Llamamos a la función para imprimir los valores
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
            
            if benefit > 0 and loc < len(installation_cost):  # Check if loc is within the range of installation_cost
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
    
    return best_solution

def objective_function(solution, installation_cost):
    total_cost = 0
    for loc in solution:
        total_cost += installation_cost[loc]
    return total_cost

'''
def objective_function(solution, installation_cost):
    # Ensure all locations in solution are within the valid range
    if all(0 <= loc < len(installation_cost) for loc in solution):
        return sum(installation_cost[loc] for loc in solution)
    else:
        # Return a very high cost if the solution is invalid
        return float('inf')
'''

def generate_neighbor(current_solution, num_locations):
    neighbor = current_solution[:]
    index = random.randint(0, len(neighbor) - 1)
    new_loc = random.randint(0, num_locations - 1)
    neighbor[index] = new_loc
    return neighbor

def hill_climbing(data, max_iterations=1000):
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    initial_solution = greedy_stochastic(data)
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
    initial_solution = greedy_stochastic(data)
    current_solution = list(initial_solution)
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    
    for _ in range(remove_count):
        if current_solution:
            current_solution.pop(random.randint(0, len(current_solution) - 1))
    
    remaining_sectors = set(range(data['num_sectors']))  # Inicializar con todos los sectores
    while remaining_sectors:
        best_location = None
        best_cost_benefit = float('inf')
        
        for loc in range(num_locations):
            if loc in current_solution:
                continue
            # Calcular el beneficio/costo de cubrir cada sector restante con esta ubicación
            if sum(1 for sector_idx in remaining_sectors if loc in data['sectors'][sector_idx]['satisfaction_list']) == 0:
                continue
            cost_benefit = installation_cost[loc] / sum(1 for sector_idx in remaining_sectors if loc in data['sectors'][sector_idx]['satisfaction_list'])
            #print("costo/beneficio",cost_benefit)

            if cost_benefit < best_cost_benefit:
                best_cost_benefit = cost_benefit
                best_location = loc
        
        if best_location is not None:
            current_solution.append(best_location)
            # Eliminar los sectores cubiertos por esta ubicación de los sectores restantes
            remaining_sectors -= {sector_idx for sector_idx in remaining_sectors if best_location in data['sectors'][sector_idx]['satisfaction_list']}
    
    return current_solution, objective_function(current_solution, installation_cost)

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

    print(f"Avg Execution Time: {avg_execution_time} seconds")
    print(f"Avg Fitness: {avg_fitness}")

    plt.plot(range(num_executions), objective_function_values, marker='o')
    plt.title('Convergence Plot')
    plt.xlabel('Execution')
    plt.ylabel('Objective Function Value')
    plt.show()



file_name = 'C1.txt'
data = read_file(file_name)


print_data(data)
print()


#greedy dterminista (GOOOOD)
deterministic_solution = greedy_deterministic(data)
print("Greedy Deterministic Solution:", deterministic_solution)
print()
#greedy estocastico (GOOOOD)
stochastic_solution = greedy_stochastic(data)
print("Greedy Stochastic Solution:", stochastic_solution)
print()

#hill climbing (GOOOOOD)
best_solution, best_fitness = hill_climbing(data)
print("Hill Climbing Best Solution:", best_solution)
print("Hill Climbing Best Fitness:", best_fitness)
print()

#Brisket (GOOOOD ?)
brisket_solution, brisket_fitness = brisket_variant(data)
print("Brisket Variant Best Solution:", brisket_solution)
print("Brisket Variant Best Fitness:", brisket_fitness)

# Ejecutar el benchmark
brisket_benchmark(file_name)


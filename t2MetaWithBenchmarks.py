import random
import time
import matplotlib.pyplot as plt
def RandomNumber(initial, final):
    #valores para el generador congruencial lineal
    a = 1664525
    c = 1013904223
    m = 2**32
    #usar la marca de tiempo actual como semilla
    seed = int(time.time() * 1000) % m  # Convertir el tiempo actual en milisegundos y ajustarlo con el módulo m
    #generar un número pseudoaleatorio usando el método LCG
    seed = (a * seed + c) % m
    random_number = seed
    #escalar el número aleatorio a un rango
    rango = final - initial + 1
    result = initial + (random_number % rango)
    return result
def read_file(file_name):
    #leer archivo
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines]
    
    num_sectors = int(lines[0].split()[-1])
    num_locations = int(lines[1].split()[-1])
    installation_cost = []
    sectors = []
    list_maps_demands = []
    index = 2
    #extraer los datos de las ubicaciones
    for _ in range(num_locations):
        linea = lines[index]
        elements = linea.split()
        for elemento in elements:
            installation_cost.append(int(elemento))
        index += 1
        if len(installation_cost) == num_locations:
            break
    #extraer los datos de los sectores
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
    #retornar toda la data
    return {
        "num_sectors": num_sectors,
        "num_locations": num_locations,
        "installation_cost": installation_cost,
        "sectors": list_maps_demands
    }
def print_data(result):
    #imprimir resultados
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
    #extraer el número de ubicaciones, costos de instalación y sectores
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    sectors = data['sectors']
    #inicializar los conjuntos para las ubicaciones seleccionadas y los sectores cubiertos
    selected_locations = set()
    covered_sectors = set()
    #mientras no se cubran todos los sectores
    while len(covered_sectors) < data['num_sectors']:
        best_location = None
        best_cost_benefit = float('inf')
        #iterar sobre todas las ubicaciones
        for loc in range(num_locations):
            #se omiten las ubicaciones ya seleccionadas
            if loc in selected_locations:
                continue
            #se calcula el beneficio de seleccionar la ubicación actual
            benefit = sum(1 for i, sector in enumerate(sectors) if loc in sector['satisfaction_list'] and i not in covered_sectors)
            #si la ubicación ofrece un beneficio, se calcula la relación costo-beneficio
            if benefit > 0 and loc < len(installation_cost):
                cost_benefit = installation_cost[loc] / benefit
                #se actualiza la mejor ubicación si es que encuentra una mejor relación costo-beneficio
                if cost_benefit < best_cost_benefit:
                    best_cost_benefit = cost_benefit
                    best_location = loc
        #si se encontró una mejor ubicación, se agrega a las seleccionadas y se actualizan los sectores cubiertos
        if best_location is not None:
            selected_locations.add(best_location)
            for i, sector in enumerate(sectors):
                if best_location in sector['satisfaction_list']:
                    covered_sectors.add(i)
        else:
            #si no se encuentra una ubicación válida se termina el ciclo
            print("No valid location found to cover remaining sectors.")
            break
    #retorna las ubicaciones seleccionadas
    return selected_locations

def greedy_stochastic(data, num_iterations=10):
    #extraer el número de ubicaciones, costos de instalación y sectores
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    sectors = data['sectors']
    #se nicializa la mejor solución y su costo
    best_solution = None
    best_solution_cost = float('inf')
    #se ejecuta el algoritmo según el numero de iteraciones
    for _ in range(num_iterations):
        selected_locations = set()
        covered_sectors = set()
        solution_cost = 0
        #mientras no se cubran todos los sectores
        while len(covered_sectors) < data['num_sectors']:
            #se genera una lista de ubicaciones disponibles (no seleccionadas)
            available_locations = [loc for loc in range(num_locations) if loc not in selected_locations]
            if not available_locations:
                break
            #se usa RandomNumber para seleccionar una ubicación aleatoria
            random_index = RandomNumber(0, len(available_locations) - 1)
            loc = available_locations[random_index]
            selected_locations.add(loc)
            #se actualizan los sectores cubiertos y el costo de la solución
            for i, sector in enumerate(sectors):
                if loc in sector['satisfaction_list'] and i not in covered_sectors:
                    covered_sectors.add(i)
                    solution_cost += installation_cost[loc]
        #si la solución actual es mejor que la mejor conocida, la actualiza
        if solution_cost < best_solution_cost:
            best_solution = selected_locations
            best_solution_cost = solution_cost
    #retorna la mejor solución encontrada y su costo
    return best_solution, best_solution_cost

def objective_function(solution, installation_cost):
    #se calcula y retorna la suma de los costos de instalación para las ubicaciones seleccionadas en la solución
    return sum(installation_cost[loc] for loc in solution)

def generate_neighbor(current_solution, num_locations):
    #se guarda la solución actual para crear un vecino
    neighbor = current_solution[:]
    #se genera un índice aleatorio usando RandomNumber
    index = RandomNumber(0, len(neighbor) - 1)
    #se genera una nueva ubicación aleatoria usando RandomNumber
    new_loc = RandomNumber(0, num_locations - 1)
    #se reemplaza la ubicación en el índice aleatorio con la nueva ubicación generada
    neighbor[index] = new_loc
    #retorna el vecino
    return neighbor

def hill_climbing(data, max_iterations=1000):
    #extraer el número de ubicaciones y costos de instalación
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    #se genera una solución inicial usando el  greedy estocástico
    initial_solution = greedy_stochastic(data)[0]
    #se establece la solución actual como la inicial y se calcula su fitness
    current_solution = list(initial_solution)
    current_fitness = objective_function(current_solution, installation_cost)

    iterations = 0 #se inicializa el contador de iteraciones
    
    #se itera hasta alcanzar el número máximo de iteraciones
    while iterations < max_iterations:
        #se genera un vecino de la solución actual
        neighbor = generate_neighbor(current_solution, num_locations)
        #se calcula el fitness del vecino generado
        neighbor_fitness = objective_function(neighbor, installation_cost)
        #si el fitness del vecino es mejor (menor), se actualiza la solución actual y su fitness
        if neighbor_fitness < current_fitness:
            current_solution = neighbor
            current_fitness = neighbor_fitness
        else:
            #si no mejora, se incrementa el contador de iteraciones
            iterations += 1
    #retorna la mejor solución encontrada y su fitness
    return current_solution, current_fitness

def brisket_variant(data, remove_count=2):
    #se genera una solución inicial usando el greedy estocástico
    initial_solution = greedy_stochastic(data)[0]
    #se establece la solución actual como la inicial
    current_solution = list(initial_solution)
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    #se eliminan aleatoriamente algunos lugares escogidos
    for _ in range(remove_count):
        if current_solution:
            random_index = RandomNumber(0, len(current_solution) - 1)
            current_solution.pop(random_index)
    #se inicializa el conjunto de sectores restantes por cubrir
    remaining_sectors = set(range(data['num_sectors']))
    while remaining_sectors:
        best_location = None
        best_cost_benefit = float('inf')
        #se evalúa cada ubicación
        for loc in range(num_locations):
            if loc in current_solution:
                continue
            #se cuentan los sectores cubiertos por la ubicación actual
            covered_sectors_count = sum(1 for sector_idx in remaining_sectors if loc in data['sectors'][sector_idx]['satisfaction_list'])
            if covered_sectors_count == 0:
                continue
            #se calcula la relación costo-beneficio
            cost_benefit = installation_cost[loc] / covered_sectors_count
            #se actualiza la mejor ubicación si se encuentra una mejor relación costo-beneficio
            if cost_benefit < best_cost_benefit:
                best_cost_benefit = cost_benefit
                best_location = loc
        #si es que se encuentra una mejor ubicación, se agrega a la solución actual y se actualizan los sectores restantes
        if best_location is not None:
            current_solution.append(best_location)
            remaining_sectors -= {sector_idx for sector_idx in remaining_sectors if best_location in data['sectors'][sector_idx]['satisfaction_list']}
    #se retorna la mejor solución encontrada y su costo total
    return current_solution, objective_function(current_solution, installation_cost)

def convergence_plot(executions, values, algorithm):
    #se genera un gráfico de línea de los valores de la función objetivo a lo largo de las ejecuciones
    plt.plot(range(executions), values, marker='o')
    plt.title('Convergence Plot '+algorithm)
    plt.xlabel('Execution')
    plt.ylabel('Objective Function Value')
    plt.show() #se muestra el gráfico generado
def greedy_stochastic_benchmark(file_name, num_executions=10):
    #se crean listas para guardar los tiempos de ejecución y los valores de la función objetivo
    execution_times = []
    objective_function_values = []
    #se ejecuta el benchmark según num_executions
    for _ in range(num_executions):
        #se leen los datos del archivo
        data = read_file(file_name)
        start_time = time.time() #tiempo de inicio
        #se ejecuta el greedy estocástico y se obtiene el costo de la mejor solución
        _, best_solution_cost = greedy_stochastic(data)
        end_time = time.time() #tiempo final
        #se calcula el tiempo de ejecución para la iteración
        execution_time = end_time - start_time
        #se guarda el tiempo de ejecución y el valor de la función objetivo
        execution_times.append(execution_time)
        objective_function_values.append(best_solution_cost)
    #se calcula el tiempo de ejecución promedio y el valor promedio de la función objetivo
    avg_execution_time = sum(execution_times) / num_executions
    avg_fitness = sum(objective_function_values) / num_executions
    #se imprimen los resultados
    print(f"Avg Execution Time Greedy Stochastic: {avg_execution_time} seconds")
    print(f"Avg Fitness Greedy Stochastic: {avg_fitness}")
    #se grafican los valores de la función objetivo para cada ejecución
    convergence_plot(num_executions,objective_function_values,'Greedy Stochastic')

def hill_climbing_benchmark(file_name, num_executions=5, max_iterations=1000):
    #se crean listas para guardar los tiempos de ejecución y los valores de la función objetivo
    execution_times = []
    objective_function_values = []
    #se ejecuta el benchmark según num_executions
    for _ in range(num_executions):
        #se leen los datos del archivo
        data = read_file(file_name)
        start_time = time.time() #tiempo de inicio
        #se ejecuta el algoritmo de hill climbing y se obtiene el mejor fitness
        _, best_fitness = hill_climbing(data, max_iterations)
        end_time = time.time() #tiempo final
        #se calcula el tiempo de ejecución para esta iteración
        execution_time = end_time - start_time
        #se guarda el tiempo de ejecución y el valor de la función objetivo
        execution_times.append(execution_time)
        objective_function_values.append(best_fitness)
    #se calcula el tiempo de ejecución promedio y el valor promedio de la función objetivo
    avg_execution_time = sum(execution_times) / num_executions
    avg_fitness = sum(objective_function_values) / num_executions
    #se imprimen los resultados
    print(f"Avg Execution Time Hill Climbing: {avg_execution_time} seconds")
    print(f"Avg Fitness Hill Climbing: {avg_fitness}")
    #se grafican los valores de la función objetivo para cada ejecución
    convergence_plot(num_executions,objective_function_values,'Hill Climbing')

def brisket_benchmark(file_name, num_executions=5, remove_count=2):
    #se crean listas para guardar los tiempos de ejecución y los valores de la función objetivo
    execution_times = []
    objective_function_values = []
    #se ejecuta el benchmark según num_executions
    for _ in range(num_executions):
        #se leen los datos del archivo
        data = read_file(file_name)
        start_time = time.time() #tiempo de inicio
        #se ejecuta la variante Brisket y se obtiene la solución y su fitness
        brisket_solution, brisket_fitness = brisket_variant(data, remove_count)
        end_time = time.time() #tiempo final
        #se calcula el tiempo de ejecución para esta iteración
        execution_time = end_time - start_time
        #se guarda el tiempo de ejecución y el valor de la función objetivo
        execution_times.append(execution_time)
        objective_function_values.append(brisket_fitness)
    #se calcula el tiempo de ejecución promedio y el valor promedio de la función objetivo
    avg_execution_time = sum(execution_times) / num_executions
    avg_fitness = sum(objective_function_values) / num_executions
    #se imprimen los resultados
    print(f"Avg Execution Time Brisket: {avg_execution_time} seconds")
    print(f"Avg Fitness Brisket: {avg_fitness}")
    #se grafican los valores de la función objetivo para cada ejecución
    convergence_plot(num_executions,objective_function_values,'Brisket')

def runFiles(file_name):
    print('- - - - - '+file_name+' - - - - -')
    data = read_file(file_name)
    print_data(data)
    print()
    # Greedy Deterministic
    deterministic_solution = greedy_deterministic(data)
    print("Greedy Deterministic Solution "+file_name+":", deterministic_solution)
    print()
    # Greedy Stochastic
    stochastic_solution, stochastic_cost = greedy_stochastic(data)
    print("Greedy Stochastic Solution "+file_name+":", stochastic_solution)
    print("Greedy Stochastic Cost "+file_name+":", stochastic_cost)
    print()
    # Hill Climbing
    best_solution, best_fitness = hill_climbing(data)
    print("Hill Climbing Best Solution "+file_name+":", best_solution)
    print("Hill Climbing Best Fitness "+file_name+":", best_fitness)
    print()
    # Brisket Variant
    brisket_solution, brisket_fitness = brisket_variant(data)
    print("Brisket Variant Best Solution "+file_name+":", brisket_solution)
    print("Brisket Variant Best Fitness "+file_name+":", brisket_fitness)
    print()
    # Benchmark
    greedy_stochastic_benchmark(file_name)
    hill_climbing_benchmark(file_name)
    brisket_benchmark(file_name)

runFiles('C1.txt')
runFiles('C2.txt')


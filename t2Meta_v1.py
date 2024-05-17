import random

#extraer info

def read_file(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines]
    
    num_sectors = int(lines[0].split()[-1])
    num_locations = int(lines[1].split()[-1])
    installation_cost = list(map(int, lines[2].split()))
    
    sectors = []
    index = 3
    for _ in range(num_sectors):
        num_demand_locations = int(lines[index].split()[-1])
        index += 1
        demand_locations = list(map(int, lines[index].split()))
        index += 1
        sectors.append({
            "num_demand_locations": num_demand_locations,
            "demand_locations": demand_locations
        })
    
    return {
        "num_sectors": num_sectors,
        "num_locations": num_locations,
        "installation_cost": installation_cost,
        "sectors": sectors
    }

def print_data(data):
    print(f"Number of sectors (m): {data['num_sectors']}")
    print(f"Number of locations where a clinic can be installed (n): {data['num_locations']}")
    print("Installation cost of each clinic:")
    print(" ".join(map(str, data['installation_cost'])))
    print()

    for i, sector in enumerate(data['sectors'], start=1):
        print(f"Sector {i}:")
        print(f"  Number of locations that satisfy the demand: {sector['num_demand_locations']}")
        print(f"  Locations: {' '.join(map(str, sector['demand_locations']))}")
        print()

#----------------------

# parte del greeedy estocastico y determinista

def greedy_deterministic(data):
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    sectors = data['sectors']
    
    selected_locations = set()
    covered_sectors = set()
    
    print(f"num_locations: {num_locations}")
    print(f"installation_cost: {installation_cost}")
    
    while len(covered_sectors) < data['num_sectors']:
        best_location = None
        best_cost_benefit = float('inf')
        
        for loc in range(num_locations):
            if loc in selected_locations:
                continue
            benefit = sum(1 for i, sector in enumerate(sectors) if loc in sector['demand_locations'] and i not in covered_sectors)
            
            #print(f"Location: {loc}, Benefit: {benefit}")
            
            if benefit > 0 and loc < len(installation_cost):
                cost_benefit = installation_cost[loc] / benefit

                if cost_benefit < best_cost_benefit:
                    best_cost_benefit = cost_benefit
                    best_location = loc
        
        if best_location is not None:
            selected_locations.add(best_location)
            for i, sector in enumerate(sectors):
                if best_location in sector['demand_locations']:
                    covered_sectors.add(i)
        else:
            print("no hay locaciones validas")
            break
    
    return selected_locations


def greedy_stochastic(data):
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    sectors = data['sectors']
    
    selected_locations = set()
    covered_sectors = set()

    print(f"num_locations: {num_locations}")
    print(f"installation_cost: {installation_cost}")
    
    while len(covered_sectors) < len(sectors):
        best_locations = []
        best_cost_benefit = float('inf')
        
        for loc in range(num_locations):
            if loc in selected_locations:
                continue
            benefit = sum(1 for i, sector in enumerate(sectors) if loc in sector['demand_locations'] and i not in covered_sectors)
            #print(f"Location: {loc}, Benefit: {benefit}")
            if benefit > 0 and loc < len(installation_cost): 
                cost_benefit = installation_cost[loc] / benefit

                if cost_benefit < best_cost_benefit:
                    best_cost_benefit = cost_benefit
                    best_locations = [loc]
                elif cost_benefit == best_cost_benefit:
                    best_locations.append(loc)
        
        if best_locations:
            # selecciona una de las mejores locaciones de manera random
            best_location = random.choice(best_locations)
            selected_locations.add(best_location)
            for i, sector in enumerate(sectors):
                if best_location in sector['demand_locations']:
                    covered_sectors.add(i)
        else:
            print("no hay locaciones validas")
            break
    
    return selected_locations

#--------------------------

# parte del hill climning con la funcion objetivo
def objective_function(solution, installation_cost):
    # verifica si las soluciones estan en el rango o se sale del index, le da la maña
    if all(0 <= loc < len(installation_cost) for loc in solution):
        return sum(installation_cost[loc] for loc in solution)
    else:
        # retorna si la solucion es invalida
        return float('inf')

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

#------------------------------------------

# su wea del brisket mas complicada que la chucha


def brisket_variant(data, remove_count=2):
    initial_solution = greedy_stochastic(data)
    current_solution = list(initial_solution)
    num_locations = data['num_locations']
    installation_cost = data['installation_cost']
    
    for _ in range(remove_count):
        if current_solution:
            current_solution.pop(random.randint(0, len(current_solution) - 1))
    
    # Convertir los sectores a tuplas para que sean hashables
    sector_tuples = {tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in sector.items()) for sector in data['sectors']}
    covered_sectors = {tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in sector.items()) for loc in current_solution for sector in data['sectors'] if loc in sector['demand_locations']}
    
    remaining_sectors = sector_tuples - covered_sectors
    
    while remaining_sectors:
        best_location = None
        best_cost_benefit = float('inf')
        
        for loc in range(num_locations):
            if loc in current_solution or loc >= len(installation_cost):
                continue
            sectors_covered_by_loc = [tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in sector.items()) for sector in data['sectors'] if loc in sector['demand_locations']]
            if not sectors_covered_by_loc:
                continue
            cost_benefit = installation_cost[loc] / len(sectors_covered_by_loc)
            
            if cost_benefit < best_cost_benefit:
                best_cost_benefit = cost_benefit
                best_location = loc
        
        if best_location is not None:
            current_solution.append(best_location)
            newly_covered_sectors = {tuple((k, tuple(v) if isinstance(v, list) else v) for k, v in sector.items()) for sector in data['sectors'] if best_location in sector['demand_locations']}
            remaining_sectors -= newly_covered_sectors
    
    return current_solution, objective_function(current_solution, installation_cost)





#------------------------------------------

file_name = 'C1.txt'
data = read_file(file_name)
#print_data(data)

#greedy dterminista (GOOOOD)
#deterministic_solution = greedy_deterministic(data)
#print("Greedy Deterministic Solution:", deterministic_solution)

#greedy estocastico (GOOOOD)
#stochastic_solution = greedy_stochastic(data)
#print("Greedy Stochastic Solution:", stochastic_solution)


#hill climbing (GOOOOOD)
#best_solution, best_fitness = hill_climbing(data)
#print("Hill Climbing Best Solution:", best_solution)
#print("Hill Climbing Best Fitness:", best_fitness)


#Brisket
brisket_solution, brisket_fitness = brisket_variant(data)
print("Brisket Variant Best Solution:", brisket_solution)
print("Brisket Variant Best Fitness:", brisket_fitness)


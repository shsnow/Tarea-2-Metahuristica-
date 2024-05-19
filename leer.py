import random

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


def print_data(file_name):
    result = read_file(file_name)
    
    print("Número de sectores:", result["num_sectors"])
    print("Número de ubicaciones:", result["num_locations"])
    print("Costo de instalación de cada clínica:", result["installation_cost"])
    
    print("Detalles de los sectores:")
    for sector in result["sectors"]:
        print("Número de lugares que satisfacen la demanda:", sector["demand_places"])
        print("Lista de lugares donde se puede instalar una clínica:", sector["satisfaction_list"])
        print()

# Llamamos a la función para imprimir los valores


file_name = 'C1.txt'
data = read_file(file_name)
print_data(file_name)
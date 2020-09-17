from client import create_input
from client import Client
from optimal_model import create_optimal_model
from baseline_algorithms import run_myopic_algorithm

if __name__ == "__main__":
    lifetime = 4
    clientNum = 1
    datacenter = create_input()
    clients = []
    for c in range(clientNum):
        clients.append(Client(lifetime))
    optimal_model = create_optimal_model(datacenter, clients, lifetime)
    optimal_model.optimize()
    print(optimal_model.status)
    print(optimal_model.objVal)
    #
    myopic_cost = run_myopic_algorithm(datacenter, clients, lifetime)
    print(myopic_cost)
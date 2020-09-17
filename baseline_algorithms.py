import numpy as np
from client import VNF


class Server:
    def __init__(self, serverId, coreNum):
        self.serverId = serverId
        self.coreNum = coreNum
        self.usedCores = 0
        self.vnfNum = {0: 0, 1: 0, 2: 0, 3: 0}

    def add_vnf_by_id(self, vnfId):
        if self.usedCores + VNF.CORE_DEMAND[vnfId] <= self.coreNum:
            self.usedCores += VNF.CORE_DEMAND[vnfId]
            self.vnfNum[vnfId] += 1
            return True
        else:
            return False


def calc_deployment_cost(prev_alloc, new_alloc):
    cost = 0.0
    for s1 in new_alloc:
        for s2 in prev_alloc:
            if s1.serverId == s2.serverId:
                for vnfId in s1.vnfNum:
                    if s1.vnfNum[vnfId] > s2.vnfNum[vnfId]:
                        cost += ((s1.vnfNum[vnfId] - s2.vnfNum[vnfId]) * VNF.DP_COST[vnfId])
    return cost


def calc_operational_cost(new_alloc):
    cost = 0.0
    for s in new_alloc:
        for vnfId in s.vnfNum:
            cost += (s.vnfNum[vnfId] * VNF.OP_COST[vnfId])
    return cost


def run_myopic_algorithm(datacenter, clients, lifetime):
    op_cost = 0.0
    dp_cost = 0.0
    vnfs = range(4)
    prev_alloc = []
    new_alloc = []
    for t in range(lifetime):
        for client in clients:
            client.calc_demand_at(t)
        if t != 0:
            prev_alloc = new_alloc
            new_alloc = []
        avail_servers = datacenter.servers
        new_server = Server(avail_servers[0],
                            datacenter.dcTopo.nodes[avail_servers[0]]["coreNum"])
        avail_servers = avail_servers[1:]
        new_alloc.append(new_server)
        for client in clients:
            for vnf in vnfs:
                vnf_demand = client.get_vnf_req_by_id(vnf)
                for _ in range(vnf_demand):
                    if not new_server.add_vnf_by_id(vnf):
                        new_server = Server(avail_servers[0],
                                            datacenter.dcTopo.nodes[avail_servers[0]]["coreNum"])
                        avail_servers = avail_servers[1:]
                        new_alloc.append(new_server)
                        if not new_server.add_vnf_by_id(vnf):
                            print("can not serve request!")
                            return -1
        if t == 0:
            op_cost += calc_operational_cost(new_alloc)
        else:
            op_cost += calc_operational_cost(new_alloc)
            dp_cost += calc_deployment_cost(prev_alloc, new_alloc)
    return op_cost + dp_cost
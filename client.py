from generator import write_fat_tree_to_file
import networkx as nx
import numpy as np


class Datacenter:
    def __init__(self, dcTopo, servers, switches):
        self.dcTopo = dcTopo
        self.servers = servers
        self.switches = switches

class Chain:
    def __init__(self):
        chainLen = np.random.randint(1, 5)
        allVnfs = ["FW", "DPI", "NAT", "LB"]
        np.random.shuffle(allVnfs)
        self.vnfs = []
        for i in range(chainLen):
            self.vnfs.append(VNF(allVnfs[i]))

    def calc_demand(self, trafficRate):
        for vnf in self.vnfs:
            vnf.calc_demand(trafficRate)
            trafficRate = vnf.outputRate

    def set_no_demand(self):
        for vnf in self.vnfs:
            vnf.set_no_demand()

    def __str__(self):
        chainStr = ""
        for i in range(len(self.vnfs)-1):
            chainStr += "{}--".format(str(self.vnfs[i]))
        chainStr += "{}".format(str(self.vnfs[-1]))
        return chainStr


class VNF:
    VNF_ID = {"DPI": 0, "FW": 1, "NAT": 2, "LB": 3}
    OP_COST     = {0: 1, 1: 1, 2: 1, 3: 1}
    DP_COST     = {0: 8, 1: 5, 2: 4, 3: 10}
    CORE_DEMAND = {0: 4, 1: 3, 2: 2, 3: 1}
    PROCESSING_RATE = 10

    def __init__(self, vnfType):
        self.vnfType = vnfType
        self.vnfTypeId = VNF.VNF_ID[vnfType]
        self.inputRate = 0
        self.vnfNum = 0
        self.outputRate = 0

    def calc_demand(self, inputRate):
        self.inputRate = inputRate
        self.vnfNum = int(np.ceil(inputRate / 10))
        self.outputRate = self.calc_out_rate(self.inputRate)

    def calc_out_rate(self, inputRate):
        if self.vnfType == "DPI":
            return inputRate * 0.85
        if self.vnfType == "FW":
            return inputRate * 0.95
        return inputRate

    def set_no_demand(self):
        self.inputRate = 0
        self.vnfNum = 0
        self.outputRate = 0

    def __str__(self):
        vnfStr = "(t:{},in:{:.1f},c:{},ou:{:.1f})".format(self.vnfType, self.inputRate, self.vnfNum, self.outputRate)
        return vnfStr


class Client:
    def __init__(self, lifetime):
        self.traffic = np.random.uniform(10, 100, size=lifetime)
        self.chain = Chain()
        self.lifetime = lifetime

    def calc_demand_at(self, t):
        if t >= self.lifetime or t < 0:
            self.chain.set_no_demand()
        else:
            self.chain.calc_demand(self.traffic[t])

    def get_vnf_req_by_id(self, vnfId):
        for vnf in self.chain.vnfs:
            if vnf.vnfTypeId == vnfId:
                return vnf.vnfNum
        return 0


def create_input():
    podNum = 4
    topoFile = "fattree4"
    write_fat_tree_to_file(podNum, topoFile)
    f = open(topoFile, "r")
    nodeNum = int(f.readline())
    serversStr = f.readline()
    servers = [int(s) for s in serversStr[:-2].split(" ")]
    datacenter = nx.DiGraph()
    for s in servers:
        datacenter.add_node(s, nodeType="server", coreNum=100)
    switches = []
    for linkStr in f:
        if len(linkStr) <= 1:
            continue
        endpoints = [int(e) for e in linkStr.split(" ")]
        for e in [0, 1]:
            if endpoints[e] not in servers and endpoints[e] not in switches:
                switches.append(endpoints[e])
                datacenter.add_node(endpoints[e], nodeType="switch")
        datacenter.add_edge(endpoints[0], endpoints[1], bw=1000)
        datacenter.add_edge(endpoints[1], endpoints[0], bw=1000)
    return Datacenter(datacenter, servers, switches)
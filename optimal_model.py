import gurobipy as gp
from gurobipy import GRB, quicksum
from client import VNF


def create_optimal_model(datacenter, clients, lifetime):
    m = gp.Model("vnf-wf")
    timeslots = list(range(lifetime))
    vnfs = range(4)
    y = m.addVars(datacenter.servers, vnfs, timeslots, vtype=GRB.INTEGER, name="y")
    z = m.addVars(datacenter.servers, vnfs, timeslots, lb=0, vtype=GRB.INTEGER, name="z")

    for t in timeslots:
        for client in clients:
            client.calc_demand_at(t)

        m.addConstrs(
            (
                quicksum(
                    y[s, vnf, t]
                    for s in datacenter.servers
                ) >= quicksum(
                    c.get_vnf_req_by_id(vnf)
                    for c in clients
                )
                for vnf in vnfs
            ), name="demand-at-{}".format(t)
        )

        m.addConstrs(
            (
                quicksum(
                    y[s, vnf, t] * VNF.CORE_DEMAND[vnf]
                    for vnf in vnfs
                ) <= datacenter.dcTopo.nodes[s]["coreNum"]
                for s in datacenter.servers
            ), name="capacity-at-{}".format(t)
        )

        if t > 0:
            m.addConstrs(
                (
                    z[s, vnf, t] >= y[s, vnf, t] - y[s, vnf, t-1]
                    for s in datacenter.servers
                    for vnf in vnfs
                ), name="deploy-at-{}".format(t)
            )

    m.setObjective(
        quicksum(
            y[s, vnf, t] * VNF.OP_COST[vnf]
            for s in datacenter.servers
            for vnf in vnfs
            for t in timeslots
        ) + quicksum(
            z[s, vnf, t] * VNF.DP_COST[vnf]
            for s in datacenter.servers
            for vnf in vnfs
            for t in timeslots[1:]
        ), GRB.MINIMIZE
    )

    return m
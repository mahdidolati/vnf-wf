import gurobipy as gp
from gurobipy import GRB, quicksum
from client import VNF


def run_wf_at(datacenter, clients, cur_time, y_t_1):
    m = gp.Model("vnf-wf")
    timeslots = list(range(cur_time + 1))
    vnfs = range(4)
    y = m.addVars(datacenter.servers, vnfs, timeslots, vtype=GRB.INTEGER, name="y")
    z = m.addVars(datacenter.servers, vnfs, timeslots, lb=0, vtype=GRB.INTEGER, name="z")
    z_t_1 = m.addVars(datacenter.servers, vnfs, lb=0, vtype=GRB.INTEGER, name="z_t_1")

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
                    z[s, vnf, t] >= y[s, vnf, t] - y[s, vnf, t - 1]
                    for s in datacenter.servers
                    for vnf in vnfs
                ), name="deploy-at-{}".format(t)
            )

    if cur_time > 0:
        m.addConstrs(
            (
                z_t_1[s, vnf] >= y[s, vnf, timeslots[-1]] - y_t_1[s][vnf]
                for s in datacenter.servers
                for vnf in vnfs
            ), name="last-change"
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
        ) + quicksum(
            z_t_1[s, vnf] * VNF.DP_COST[vnf]
            for s in datacenter.servers
            for vnf in vnfs
        ), GRB.MINIMIZE
    )

    m.setParam("LogToConsole", 0)
    return m, y


def calc_cost(datacenter, y_t, y_t_1):
    cost = 0.0
    vnfs = range(4)
    for s in datacenter.servers:
        for vnf in vnfs:
            cost += y_t[s][vnf] * VNF.OP_COST[vnf]
            if len(y_t_1) > 0:
                if y_t[s][vnf] - y_t_1[s][vnf] > 0:
                    cost += (y_t[s][vnf] - y_t_1[s][vnf]) * VNF.DP_COST[vnf]
    return cost


def run_wf_algorithm(datacenter, clients, lifetime):
    cost = 0.0
    y_t_1 = {}
    vnfs = range(4)
    for t in range(lifetime):
        m, y = run_wf_at(datacenter, clients, t, y_t_1)
        m.optimize()
        y_t = {}
        for s in datacenter.servers:
            if s not in y_t:
                y_t[s] = {}
            for vnf in vnfs:
                y_t[s][vnf] = y[s, vnf, t].X
        cost += calc_cost(datacenter, y_t, y_t_1)
        y_t_1 = y_t
    print(cost)
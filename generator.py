def write_fat_tree_to_file(pod_num, file_name):
    fw = open(file_name, 'w')
    sw_counter = 1
    links = []
    servers = {}
    edges = {}
    for p in range(pod_num):
        for e in range(pod_num//2):
            edges[(p,e)] = sw_counter
            sw_counter += 1
    aggs = {}
    for p in range(pod_num):
        for a in range(pod_num//2):
            aggs[(p,a)] = sw_counter
            sw_counter += 1
    cores = {}
    for c1 in range(pod_num//2):
        for c2 in range(pod_num//2):
            cores[(c1, c2)] = sw_counter
            sw_counter += 1
    for s in servers:
        p = s[0]
        e = s[1]
        links.append((servers[s], edges[(p,e)]))
    for e in edges:
        pe = e[0]
        for a in aggs:
            pa = a[0]
            if pe == pa:
                links.append((edges[e],aggs[a]))
    for c in cores:
        for p in range(pod_num):
            a = (p, c[1])
            links.append((cores[c], aggs[a]))

    fw.write(str(sw_counter-1) + '\n')
    for e in edges:
        fw.write(str(edges[e]) + ' ')
    fw.write('\n')
    for l in links:
        fw.write('%d %d\n' %(l[0], l[1]))

    fw.close()
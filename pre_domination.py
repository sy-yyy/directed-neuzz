#!/usr/bin/env python3
import argparse
import networkx as nx
import re

# Regular expression to find callee
pattern = re.compile('@.*?\(')


def node_name(name):
    if is_cg:
        return "\"{%s}\"" % name
    else:
        return "\"{%s:" % name


#################################
# Find the graph node for a name
#################################
def find_nodes(name):
    n_name = node_name(name)
    n_list = list(filter(lambda d: 'label' in d[1] and n_name in d[1]['label'], G.nodes(data=True)))
    if len(n_list) > 0:
        print("jsy")
        print(n_list)
        return n_list
    else:
        return []


##################################
# Calculate Distance
##################################

def dominate(name):
    for (n, _) in find_nodes(name):
        lst = dict((nx.immediate_dominators(G, n).items()))
        out.write(str(lst))
        print(len(lst))
        for (t, _) in targets:
            domination = []
            temp = [t]
            while not (temp.__contains__(n)):
                list_p = []
                for tt in temp:
                    shortest = nx.dijkstra_path_length(G, lst[tt], tt)
                    print("shortest:" + str(shortest))
                    if shortest > 3:
                        parent = list(G.predecessors(tt))
                        print(parent)
                        for p in parent:
                            if p in lst.keys():
                                # shortest = nx.dijkstra_path_length(G, lst[p], tt)
                                # print("shortest:" + str(shortest))
                                if nx.dijkstra_path_length(G, lst[p], tt) <= 3:
                                    list_p.append(lst[p])

                    else:
                        list_p.append(lst[tt])
                list_p = list(set(list_p))
                temp = list_p
                list_n = []
                for l in list_p:
                    node = G.nodes[l]['label']
                    node = re.sub(r'[^\w\s]', '', node)
                    print(node)
                    list_n.append(node)
                domination.append(list_n)
                print(domination)


# Main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dot', type=str, required=True, help="Path to dot-file representing the graph.")
    parser.add_argument('-t', '--targets', type=str, required=True, help="Path to file specifying Target nodes.")
    parser.add_argument('-o', '--out', type=str, required=True,
                        help="Path to output file containing distance for each node.")
    parser.add_argument('-n', '--names', type=str, required=True, help="Path to file containing name for each node.")
    parser.add_argument('-c', '--cg_distance', type=str, help="Path to file containing call graph distance.")
    parser.add_argument('-s', '--cg_callsites', type=str,
                        help="Path to file containing mapping between basic blocks and called functions.")

    args = parser.parse_args()

    print("\nParsing %s .." % args.dot)
    G = nx.DiGraph(nx.drawing.nx_pydot.read_dot(args.dot))
    print(nx.info(G))

    is_cg = 1 if "Name: Call graph" in nx.info(G) else 0
    print("\nWorking in %s mode.." % ("CG" if is_cg else "CFG"))

    # Process as ControlFlowGraph
    caller = ""

    if not is_cg:

        caller = args.dot.split(".")
        caller = caller[len(caller) - 2]
        print("Loading cg_distance for function '%s'.." % caller)

        print("determine dominate nodes..")
        with open(args.out, "w") as out:
            labels = nx.get_node_attributes(G, 'label')
            lst = nx.dominating_set(G)
            for l in lst:
                print(l)
                dominate_start = labels[l].split(":")[0:3]
                # print("{0[0]}:{0[1]}".format(dominate_start))
                out.write(":".join(dominate_start))
                succ = nx.dfs_successors(G, l)[l]
                print("succ")
                print(succ)
                count = 0
                for m in succ:
                    print(++count)
                    out.write(",")
                    # dominate_end = labels[m].split(":")[0:3]
                    # out.write(":".join(dominate_end))
                    out.write(labels[m])
                out.write("\n\n")

        # print("Adding target BBs (if any)..")
        # with open(args.targets, "r") as f:
        #     for l in f.readlines():
        #         s = l.strip().split("/")
        #         line = s[len(s) - 1]
        #         nodes = find_nodes(line)
        #         if len(nodes) > 0:
        #             bb_distance[line] = 0
        #             print("Added target BB!")

    # Process as CallGraph
    else:

        print("Loading targets..")
        with open(args.targets, "r") as f:
            targets = []
            for line in f.readlines():
                line = line.strip()
                for target in find_nodes(line):
                    targets.append(target)

        if (len(targets) == 0 and is_cg):
            print("No targets available")
            exit(1)

        print("determine dominate nodes..")
        with open(args.out, "w") as out:
            with open(args.names, "r") as f:
                line = f.readline().strip()
                dominate(line)

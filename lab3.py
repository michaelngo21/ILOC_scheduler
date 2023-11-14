import lab1
import lab2
import sys

# TODO: update help message before submitting
helpMessage = """
COMP 412, Scheduler (lab 3)
Syntax: ./schedule [options] filename

        filename is the pathname (absolute or relative) to the input file

        Options can precede or follow the filename.
        -h prints this message (requires no filename)

        -c : dump value table after constant propagation.
        -e : turns off early release
        -f : toggles fast output
        -g : creates a '.dot' file for graphviz
        -n : disables constant propagation.
        -s : disables dependence trimming for LOAD, STORE, & OUTPUT
        -t : turns on internal timing reports
        -V : verifies dependence graph structure before use.
        -v : prints version number.
        -w : suppresses some warning messages
"""

EDGE_TYPES = ["Data", "Serialization", "Conflict"]
DATA, SERIALIZATION, CONFLICT = 0, 1, 2

LOAD_LATENCY = 5
LOADI_LATENCY = 1
STORE_LATENCY = 5
ADD_LATENCY = 1
SUB_LATENCY = 1
MULT_LATENCY = 3
LSHIFT_LATENCY = 1
RSHIFT_LATENCY = 1
OUTPUT_LATENCY = 1
NOP_LATENCY = 1

class GraphNode:
    def __init__(self, ir_node: lab1.IR_Node):
        self.ir_node =  ir_node   # represents IR_Node
        self.out_edges = [] # note: edges will be tuples: (<destination GraphNode>, <edge type (int)> ) NOTE: there will be an optional 3rd element in tuple to store vr for DATA edges
        self.in_edges = []
        self.prio = 0
        # potentially have a field for self.in (in-edges)
    def add_edge(self, dest, edge_type: int, data_vr=-1):
        if data_vr == -1:
            self.out_edges.append((dest, edge_type))
            dest.in_edges.append((self, edge_type))
        else:
            self.out_edges.append((dest, edge_type, data_vr))
            dest.in_edges.append((self, edge_type, data_vr))

def create_dependence_graph(dummy: lab1.IR_Node):
    def_location = {}
    nodes_arr = []
    prev_stores = []
    prev_outputs = []
    prev_loads = []

    curr = dummy.next
    while curr != dummy:
        # create a node for current operation
        node = GraphNode(curr)
        nodes_arr.append(node)

        # if o defines a virtual register, update the def_location map
        if curr.op3.sr != -1: # check if curr.op3 exists
            def_location[curr.op3.vr] = node

        # temp code
        # if curr.opcode == lab1.STORE_LEX:
        #     print(f"{lab1.LEXEMES[curr.opcode]}\t{curr.op1.printSR()}, {curr.op2.printSR()}, {curr.op3.printSR()}")

        # last_store_idx = len(prev_stores) - 1
        # last_output_idx = len(prev_outputs) - 1
        # last_load_idx = len(prev_loads) - 1

        data_edge_nodes = []
        # set edges for each of this node's uses to their definition locations
        for i in range(1, 3):
            if i == 1:
                o = curr.op1
            elif i == 2:
                o = curr.op2
            if o.sr == -1:  # o.sr == -1 indicates empty operand
                continue    
            if o.isConstant:
                o.vr = o.sr # o.vr is set to o.sr. This may be inefficient, not sure.
                continue
            # add DATA edge
            node.add_edge(def_location[o.vr], DATA, o.vr)
            data_edge_nodes.append(def_location[o.vr])
            
        # sort data_edge_nodes to help with updating last_store, last_output, and last_load
        # print(f"data_edge_nodes before sort: {[node.lineno for node in data_edge_nodes]}")
        # data_edge_nodes.sort(key=node.ir_node.lineno, reverse=True)
        # print(f"data_edge_nodes after sort: {[node.lineno for node in data_edge_nodes]}")

        # update last_store, last_output, and load_load to be the most recent NON-DATA node
        # if len(prev_stores) > last_store_idx and data_edge_nodes[-1] 
        # while len(prev_stores) > last_store_idx and data_edge_node[] == prev_stores[last_store_idx]:
        #     last_store_idx -= 1
        nondata_prev_stores = [node for node in prev_stores if node not in data_edge_nodes]
        if len(nondata_prev_stores) != len(prev_stores):
            print("data store removed!")
        nondata_prev_loads = [node for node in prev_loads if node not in data_edge_nodes]
        if len(nondata_prev_loads) != len(prev_loads):
            print("data load removed!")
        nondata_prev_outputs = [node for node in prev_outputs if node not in data_edge_nodes]
        if len(nondata_prev_outputs) != len(prev_outputs):
            print("data output removed!")

        # set up a list comprehension containing just the GraphNodes at the end of edges to use "in" operation
        # edge_nodes = [edge[0] for edge in node.edges]

        # if o is a load, store, or output, add serial and conflict edges to other memory ops
        if curr.opcode == lab1.LOAD_LEX:                    # load needs conflict edge to most recent store
            if nondata_prev_stores: # add extra check to confirm there isn't already a DATA edge to that node
                node.add_edge(nondata_prev_stores[-1], CONFLICT)  
            prev_loads.append(node)
            if len(prev_loads) > 3:
                prev_loads.pop(0)
        elif curr.opcode == lab1.OUTPUT_LEX:                # output needs conflict edge to recent store + serialization edge to recent output
            if nondata_prev_stores:
                node.add_edge(nondata_prev_stores[-1], CONFLICT)
            if nondata_prev_outputs:
                node.add_edge(nondata_prev_outputs[-1], SERIALIZATION)
            prev_outputs.append(node)
            if len(prev_outputs) > 3:
                prev_outputs.pop(0)
        elif curr.opcode == lab1.STORE_LEX:                 # store needs serialization edge to most recent store, load, & output
            # print(f"entered store for curr={curr.lineno}: last_load={prev_loads.ir_node.lineno}")
            if nondata_prev_loads:
                # temp code
                # print(f"adding serialization edge from {node.ir_node.lineno} to {prev_loads.ir_node.lineno}")
                # print(f"node's edges:")
                # for edge in node.edges:
                #     print(edge[0].ir_node.lineno)
                # print(f"last_load({prev_loads.ir_node.lineno}) in node.edges = {prev_loads in node.edges}")
                # temp code
                node.add_edge(nondata_prev_loads[-1], SERIALIZATION)
            if nondata_prev_outputs:
                node.add_edge(nondata_prev_outputs[-1], SERIALIZATION)
            if nondata_prev_stores:
                node.add_edge(nondata_prev_stores[-1], SERIALIZATION)
            prev_stores.append(node)
            if len(prev_stores) > 3:
                prev_stores.pop(0)
        
        curr = curr.next
    
    return nodes_arr
    
def get_roots(nodes_arr):
    root_set = set()
    for node in nodes_arr:
        if len(node.in_edges) == 0:
            root_set.add(node)
    return root_set

def assign_priorities(nodes_arr, root_set):
    for root in root_set:
        assign_priorities_helper(root)

def assign_priorities_helper(curr):
    for edge in curr.out_edges:
        child = edge[0]
        child_prio = 0
        if child.ir_node.opcode == lab1.LOAD_LEX:
            child_prio += LOAD_LATENCY
        elif child.ir_node.opcode == lab1.LOADI_LEX:
            child_prio += LOADI_LATENCY
        elif child.ir_node.opcode == lab1.STORE_LEX:
            child_prio += STORE_LATENCY
        elif child.ir_node.opcode == lab1.ADD_LEX:
            child_prio += ADD_LATENCY
        elif child.ir_node.opcode == lab1.SUB_LEX:
            child_prio += SUB_LATENCY
        elif child.ir_node.opcode == lab1.MULT_LEX:
            child_prio += MULT_LATENCY
        elif child.ir_node.opcode == lab1.LSHIFT_LEX:
            child_prio += LSHIFT_LATENCY
        elif child.ir_node.opcode == lab1.RSHIFT_LEX:
            child_prio += RSHIFT_LATENCY
        elif child.ir_node.opcode == lab1.OUTPUT_LEX:
            child_prio += OUTPUT_LATENCY
        elif child.ir_node.opcode == lab1.NOP_LEX:
            child_prio += NOP_LATENCY

        child_prio *= 10    # Multiply latency weight by 10
        child_prio += len(child.out_edges)  # Add number of descendants
        child_prio += curr.prio # Add parent weight

        if child_prio > child.prio:
            child.prio = child_prio
            assign_priorities_helper(child)
            return True
        else:
            False

def write_graphviz(nodes_arr):
    filename = "out.dot"
    try:
        with open("out.dot", 'w') as file:
            file.write("digraph testcase1\n{\n")

            for node in nodes_arr:
                file.write(f"{node.ir_node.lineno} [label=\"{node.ir_node.lineno}: {node.ir_node.printWithVRClean()} \n prio: {node.prio}\"];\n")

            for node in nodes_arr:
                tail = node.ir_node.lineno
                for edge in node.out_edges:
                    head = edge[0].ir_node.lineno  # recall that edge is formatted as (dest GraphNode, edge_type int)
                    edge_type = EDGE_TYPES[edge[1]]
                    edge_vr_string = "" # for data edges, there will be a 3rd element in edge which represents the vr
                    if len(edge) == 3:
                        edge_vr_string = f", vr{edge[2]}"
                    # edge_vr = edge[0].ir_node.op
                    file.write(f"{tail} -> {head} [label = \" {edge_type}{edge_vr_string}\"];\n")
            file.write("}")

    except IOError:
        print(f"ERROR: could not open file {filename} as the input file.", file=sys.stderr)
        exit(0)


def main():
    print("entered main")
    # HANDLE COMMAND LINE
    argc = len(sys.argv)
    filename = ""

    if argc < 2 or argc > 4:
        print("ERROR: Invalid number of arguments passed in. Syntax should be ./412alloc k filename [flag]", file=sys.stderr)
        print(helpMessage)
        exit(0)
    if argc == 2:
        if sys.argv[1] == "-h":
            print(helpMessage)
            return
        filename = sys.argv[1]
    if argc == 3:
        # TODO: implement helper flags
        filename = sys.argv[2]

    # PARSE
    # if filename can't be opened, lab1 will print error message and exit cleanly
    dummy, maxSR = lab1.parse(["lab1.py", filename]) # dummy is the head of the linked list 

    # RENAME
    maxLive, maxVR = lab2.rename(dummy, maxSR)

    # CREATE DEPENDENCE GRAPH
    nodes_arr = create_dependence_graph(dummy)

    # Get roots
    root_set = get_roots(nodes_arr)
    
    # ASSIGN PRIORITIES
    assign_priorities(nodes_arr, root_set)

    # Construct .dot file for graphviz
    write_graphviz(nodes_arr)

if __name__ == "__main__": # if called by the command line, execute parse()
    main()
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

class GraphNode:
    def __init__(self, ir_node: lab1.IR_Node):
        self.ir_node =  ir_node   # represents IR_Node
        self.edges = [] # note: edges will be tuples: (<destination GraphNode>, <edge type (int)> ) NOTE: there will be an optional 3rd element in tuple to store vr for DATA edges
        # potentially have a field for self.in (in-edges)
    def add_edge(self, dest, edge_type: int, data_vr=-1):
        if data_vr == -1:
            self.edges.append((dest, edge_type))
        else:
            self.edges.append((dest, edge_type, data_vr))

def create_dependence_graph(dummy: lab1.IR_Node):
    def_location = {}
    nodes_arr = []
    last_store = None
    last_output = None
    last_load = None

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
            node.add_edge(def_location[o.vr], DATA, o.vr)

        # set up a list comprehension containing just the GraphNodes at the end of edges to use "in" operation
        edge_nodes = [edge[0] for edge in node.edges]

        # if o is a load, store, or output, add serial and conflict edges to other memory ops
        if curr.opcode == lab1.LOAD_LEX:                    # load needs conflict edge to most recent store
            if last_store != None and last_store not in edge_nodes: # add extra check to confirm there isn't already a DATA edge to that node
                node.add_edge(last_store, CONFLICT)  
            last_load = node
        elif curr.opcode == lab1.OUTPUT_LEX:                # output needs conflict edge to recent store + serialization edge to recent output
            if last_store != None and last_store not in edge_nodes:
                node.add_edge(last_store, CONFLICT)
            if last_output != None and last_output not in edge_nodes:
                node.add_edge(last_output, SERIALIZATION)
            last_output = node
        elif curr.opcode == lab1.STORE_LEX:                 # store needs serialization edge to most recent store, load, & output
            print(f"entered store for curr={curr.lineno}: last_load={last_load.ir_node.lineno}")
            if last_load != None and last_load not in edge_nodes:
                # temp code
                print(f"adding serialization edge from {node.ir_node.lineno} to {last_load.ir_node.lineno}")
                print(f"node's edges:")
                for edge in node.edges:
                    print(edge[0].ir_node.lineno)
                print(f"last_load({last_load.ir_node.lineno}) in node.edges = {last_load in node.edges}")
                # temp code
                node.add_edge(last_load, SERIALIZATION)
            if last_output != None and last_output not in edge_nodes:
                node.add_edge(last_output, SERIALIZATION)
            if last_store != None and last_store not in edge_nodes:
                node.add_edge(last_store, SERIALIZATION)
            last_store = node
        
        curr = curr.next
    
    return nodes_arr
    
def write_graphviz(nodes_arr):
    filename = "out.dot"
    try:
        with open("out.dot", 'w') as file:
            file.write("digraph testcase1\n{\n")

            for node in nodes_arr:
                file.write(f"{node.ir_node.lineno} [label=\"{node.ir_node.lineno}: {node.ir_node.printWithVRClean()} \"];\n")

            for node in nodes_arr:
                tail = node.ir_node.lineno
                for edge in node.edges:
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
    
    write_graphviz(nodes_arr)

if __name__ == "__main__": # if called by the command line, execute parse()
    main()
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

EDGE_TYPES = ["SERIALIZATION", "CONFLICT"]
SERIALIZATION, CONFLICT = 0, 1

class GraphNode:
    def __init__(self, op: lab1.IR_Node):
        self.op =  op   # represents IR_Node
        self.out = [] # note: edges will be tuples: (<destination GraphNode>, <edge type (int)> ) 
        # potentially have a field for self.in (in-edges)
    def add_edge(self, dest, edge_type: int):
        self.out.append((dest, edge_type))

def create_dependence_graph(dummy: lab1.IR_Node):
    dep_map = {}
    o = dummy.prev
    while o != next:
        node = GraphNode(curr)
        

        curr = curr.next


def main():
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
    create_dependence_graph(dummy)


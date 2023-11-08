import lab1
import lab2
import sys

helpMessage = """
COMP 412, Allocator (lab 2)
Command Syntax:
        ./412alloc k filename <flag>

Required arguments:
        k        specifies the number of registers available to the allocator
        filename  is the pathname (absolute or relative) to the input file

Optional flags:
        -h        prints this message
        -m        reports MaxLive value to stdout
        -x        prints the renamed list before register allocation
"""

def main():
    argc = len(sys.argv)
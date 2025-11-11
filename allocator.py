import random
from optparse import OptionParser

class Allocator:
    def __init__(self, size, start, headerSize, policy, order, coalesce, align):
        # size of space
        self.size = size

        # fake headers
        self.headerSize = headerSize

        # init free list
        self.freelist = [] 
        self.freelist.append((start, size))
        
        # track ptr to size mappings
        self.sizemap = {}
        
        #policy
        self.policy = policy
            # assert checks if statement is true. if false halts program
            #   here it has a list of strings, and compares self.policy to
            #       the strings in the list
        assert(self.policy in ['FIRST', 'BEST', 'WORST'])

        # list ordering
        self.returnPolicy = order
        assert(self.returnPolicy in ['ADDSORT', 'SIZESORT+', 'SIZESORT-', 'INSERT-FRONT', 'INSERT-BACK'])

        # full list coalesce
        self.coalese = coalesce

        # alignment (will be -1 if no alignment)
        self.align = align
        # we do not want 0 or any negative other than -1
        assert(self.align == -1 or self.align > 0)

        def addToMap(self, addr, size):
            assert(addr not in self.sizemap)
            self.sizemap[addr] = size
            #prints "adding", addr, "to map of size", size
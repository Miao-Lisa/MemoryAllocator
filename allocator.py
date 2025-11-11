import random
from optparse import OptionParser

class Allocator:
    def __init__(self, size, start, headerSize, policy):
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
        assert(self.policy in ['FIRST', 'BEST', 'WORST'])
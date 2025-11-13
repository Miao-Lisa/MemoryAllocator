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

    def malloc(self, size):
        if self.align != -1:
            left = size % self.align
            if left != 0:
                diff = self.align - left
            else:
                diff = 0
            size += diff

        size += self.headerSize
        
        bestIdx = -1
        if self.policy == 'BEST':
            bestSize = self.size + 1
        elif self.policy == 'WORST' or self.policy == 'FIRST':
            bestSize = -1

        count = 0

        for i in range(len(self.freelist)):
            eaddr, esize = self.freelist[i][0], self.freelist[i][1]
            count += 1
            if esize >= size and ((self.policy == 'BEST' and esize < bestSize) or
                                  (self.policy == 'WORST' and esize > bestSize) or
                                  (self.policy == 'FIRST')):
                bestAddr = eaddr
                bestSize = esize
                bestIdx = i
                if self.policy == 'FIRST':
                    break

            if bestIdx != -1:
                if bestSize > size:
                    self.freelist[bestIdx] = (bestAddr + size, bestSize - size)
                    self.addToMap(bestAddr, size)
                elif bestSize == size:
                    self.freelist.pop(bestIdx)
                    self.addToMap(bestAddr, size)
                else:
                    abort('should never get here')
                return (bestAddr, count)
            
            return (-1, count)

    def free(self, addr):
        # simple back on end of list, no coalesce
        if addr not in self.sizemap:
            return -1
            
        size = self.sizemap[addr]
        if self.returnPolicy == 'INSERT-BACK':
            self.freelist.append((addr, size))
        elif self.returnPolicy == 'INSERT-FRONT':
            self.freelist.insert(0, (addr, size))
        elif self.returnPolicy == 'ADDRSORT':
            self.freelist.append((addr, size))
            self.freelist = sorted(self.freelist, key=lambda e: e[0])
        elif self.returnPolicy == 'SIZESORT+':
            self.freelist.append((addr, size))
            self.freelist = sorted(self.freelist, key=lambda e: e[1], reverse=False)
        elif self.returnPolicy == 'SIZESORT-':
            self.freelist.append((addr, size))
            self.freelist = sorted(self.freelist, key=lambda e: e[1], reverse=True)

        # not meant to be an efficient or realistic coalescing...
        if self.coalesce == True:
            self.newlist = []
            self.curr    = self.freelist[0]
            for i in range(1, len(self.freelist)):
                eaddr, esize = self.freelist[i]
                if eaddr == (self.curr[0] + self.curr[1]):
                    self.curr = (self.curr[0], self.curr[1] + esize)
                else:
                    self.newlist.append(self.curr)
                    self.curr = eaddr, esize
            self.newlist.append(self.curr)
            self.freelist = self.newlist
            
        del self.sizemap[addr]
        return 0 
    
    # prints free list showing quantity of free blocks, their respective addresses, and sizes.
    def dump(self):
        print('Free List [ Size %d ]: ' % len(self.freelist), end='')
        for e in self.freelist:
            print('[ addr:%d sz:%d ]' % (e[0], e[1]), end='') 
        print('')
"""
allocators.py
Implements the Strategy Pattern for different memory allocation algorithms.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# Constants
HEADER_SIZE = 0  # Set to 0 to simplify math, or 4 to simulate real overhead

class AllocatorStrategy(ABC):
    """Abstract Base Class for all memory allocators."""
    
    def __init__(self, heap_size: int):
        self.heap_size = heap_size
        self.name = "Unknown"

    @abstractmethod
    def malloc(self, size: int) -> Tuple[int, int]:
        """
        Allocates memory.
        Returns: (pointer_address, nodes_searched_count)
        If allocation fails, returns (-1, nodes_searched_count)
        """
        pass

    @abstractmethod
    def free(self, addr: int, size: int) -> bool:
        """
        Frees memory.
        Returns: True if successful.
        """
        pass

    @abstractmethod
    def get_fragmentation(self) -> float:
        """
        Returns external fragmentation metric (0.0 to 1.0).
        1.0 means highly fragmented (free memory exists but in useless chunks).
        """
        pass


class LinkedListAllocator(AllocatorStrategy):
    """
    Base class for First/Best/Worst fit. 
    Manages a free list sorted by address and handles coalescing.
    """
    def __init__(self, heap_size: int):
        super().__init__(heap_size)
        # Free list format: List of (start_address, size_length)
        self.free_list: List[Tuple[int, int]] = [(0, heap_size)]

    def _coalesce(self):
        """Merges adjacent free blocks."""
        if not self.free_list:
            return

        # Sort by address (standard practice for easy coalescing)
        self.free_list.sort(key=lambda x: x[0])

        new_list = []
        if not self.free_list:
            return
            
        curr_addr, curr_size = self.free_list[0]

        for i in range(1, len(self.free_list)):
            next_addr, next_size = self.free_list[i]
            
            # If current block ends exactly where next starts -> Merge
            if curr_addr + curr_size == next_addr:
                curr_size += next_size
            else:
                new_list.append((curr_addr, curr_size))
                curr_addr, curr_size = next_addr, next_size
        
        new_list.append((curr_addr, curr_size))
        self.free_list = new_list

    def free(self, addr: int, size: int) -> bool:
        """Generic free: Add back to list and coalesce."""
        self.free_list.append((addr, size))
        self._coalesce()
        return True

    def get_fragmentation(self) -> float:
        """
        Formula: 1 - (Largest_Free_Block / Total_Free_Bytes)
        If largest block is the ONLY block, fragmentation is 0.
        """
        total_free = sum(block[1] for block in self.free_list)
        if total_free == 0:
            return 0.0
        
        largest_block = max(block[1] for block in self.free_list)
        return 1.0 - (largest_block / total_free)
    
    @abstractmethod
    def _find_block_index(self, size: int) -> Tuple[int, int]:
        """
        Strategy specific search.
        Returns: (index_in_freelist, nodes_searched)
        """
        pass

    def malloc(self, size: int) -> Tuple[int, int]:
        req_size = size + HEADER_SIZE
        
        idx, search_count = self._find_block_index(req_size)

        if idx == -1:
            return -1, search_count

        # Found a block, now allocate
        block_addr, block_size = self.free_list[idx]

        if block_size >= req_size:
            # Remove the current block
            self.free_list.pop(idx)
            
            # If there is leftover space, add it back (Split)
            remaining = block_size - req_size
            if remaining > 0:
                # Insert remaining part back into the list
                # (Simple optimization: insert at same index or resort)
                self.free_list.insert(idx, (block_addr + req_size, remaining))
            
            return block_addr, search_count
        
        return -1, search_count


class FirstFit(LinkedListAllocator):
    def __init__(self, heap_size):
        super().__init__(heap_size)
        self.name = "First Fit"

    def _find_block_index(self, size: int) -> Tuple[int, int]:
        for i, (addr, block_size) in enumerate(self.free_list):
            if block_size >= size:
                return i, i + 1 # +1 because we checked this node
        return -1, len(self.free_list)


class BestFit(LinkedListAllocator):
    def __init__(self, heap_size):
        super().__init__(heap_size)
        self.name = "Best Fit"

    def _find_block_index(self, size: int) -> Tuple[int, int]:
        best_idx = -1
        best_size = float('inf')
        count = 0
        
        for i, (addr, block_size) in enumerate(self.free_list):
            count += 1
            if block_size >= size:
                if block_size < best_size:
                    best_size = block_size
                    best_idx = i
        
        return best_idx, count


class WorstFit(LinkedListAllocator):
    def __init__(self, heap_size):
        super().__init__(heap_size)
        self.name = "Worst Fit"

    def _find_block_index(self, size: int) -> Tuple[int, int]:
        worst_idx = -1
        worst_size = -1
        count = 0
        
        for i, (addr, block_size) in enumerate(self.free_list):
            count += 1
            if block_size >= size:
                if block_size > worst_size:
                    worst_size = block_size
                    worst_idx = i
        
        return worst_idx, count
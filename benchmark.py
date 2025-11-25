"""
benchmark.py
Generates workloads and runs the simulation loop.
"""
import random
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from allocators import AllocatorStrategy

class SimulationResult:
    def __init__(self, name: str):
        self.name = name
        self.total_ops = 0
        self.failed_allocs = 0
        self.total_search_steps = 0
        self.fragmentation_history: List[float] = []

class BenchmarkSuite:
    def __init__(self, heap_size=4096, seed=42):
        self.heap_size = heap_size
        self.seed = seed
        self.ops_script = []  # Stores the generated workload

    def generate_workload(self, num_ops: int, max_alloc_size: int, percent_alloc: float):
        """
        Pre-generates a list of operations:
        ('MALLOC', size, id) or ('FREE', id)
        """
        random.seed(self.seed)
        self.ops_script = []
        active_ptrs = [] # List of IDs currently allocated
        op_id_counter = 0

        for _ in range(num_ops):
            is_alloc = random.random() < (percent_alloc / 100.0)
            
            # If we want to alloc, or if we HAVE to alloc (because nothing to free)
            if is_alloc or not active_ptrs:
                size = random.randint(1, max_alloc_size)
                # Store (Operation, Size, UniqueID)
                self.ops_script.append(('MALLOC', size, op_id_counter))
                active_ptrs.append(op_id_counter)
                op_id_counter += 1
            else:
                # Pick a random pointer to free
                victim_idx = random.randint(0, len(active_ptrs) - 1)
                victim_id = active_ptrs.pop(victim_idx)
                self.ops_script.append(('FREE', 0, victim_id))

    def run(self, allocators: List[AllocatorStrategy]) -> List[SimulationResult]:
        results = []
        
        print(f"Running benchmark on {len(self.ops_script)} operations...")

        for allocator in allocators:
            print(f"  -> Testing {allocator.name}...")
            res = SimulationResult(allocator.name)
            
            # Map unique Op IDs to actual memory addresses (so we know what to free)
            # Format: { op_id: (address, size) }
            ptr_map: Dict[int, tuple] = {}

            for op_type, val, op_id in self.ops_script:
                res.total_ops += 1
                
                if op_type == 'MALLOC':
                    addr, checks = allocator.malloc(val)
                    res.total_search_steps += checks
                    
                    if addr == -1:
                        res.failed_allocs += 1
                    else:
                        ptr_map[op_id] = (addr, val)
                
                elif op_type == 'FREE':
                    if op_id in ptr_map:
                        addr, size = ptr_map[op_id]
                        allocator.free(addr, size)
                        del ptr_map[op_id]
                
                # Record health stats periodically (every 100 ops to save memory)
                if res.total_ops % 50 == 0:
                    res.fragmentation_history.append(allocator.get_fragmentation())

            results.append(res)
        
        return results

    def plot_results(self, results: List[SimulationResult]):
        """Visualizes the data using Matplotlib"""
        if not results:
            print("No results to plot.")
            return

        # 1. Performance (Search Efficiency)
        names = [r.name for r in results]
        avg_checks = [r.total_search_steps / r.total_ops for r in results]
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        bars = plt.bar(names, avg_checks, color=['#3498db', '#e74c3c', '#f1c40f'])
        plt.title('Search Efficiency (Lower is Better)')
        plt.ylabel('Avg List Nodes Checked per Op')
        
        # 2. Fragmentation over Time
        plt.subplot(1, 2, 2)
        for r in results:
            plt.plot(r.fragmentation_history, label=r.name)
        
        plt.title('External Fragmentation Over Time')
        plt.ylabel('Fragmentation Score (0-1)')
        plt.xlabel('Time (x50 ops)')
        plt.legend()
        
        plt.tight_layout()
        plt.show()

        # Text Summary
        print("\n--- Final Scoreboard ---")
        print(f"{'Algorithm':<15} | {'Failures':<10} | {'Avg Search Depth':<20}")
        print("-" * 50)
        for r, checks in zip(results, avg_checks):
            print(f"{r.name:<15} | {r.failed_allocs:<10} | {checks:.2f}")
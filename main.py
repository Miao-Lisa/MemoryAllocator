"""
main.py
CLI Entry point for the Allocator Olympics.
"""
import argparse
from allocators import FirstFit, BestFit, WorstFit
from benchmark import BenchmarkSuite

def main():
    parser = argparse.ArgumentParser(description="Memory Allocator Olympics Simulator")
    
    parser.add_argument('-S', '--size', type=int, default=1000, 
                        help='Total size of the heap (bytes)')
    parser.add_argument('-n', '--num_ops', type=int, default=1000, 
                        help='Number of operations to simulate')
    parser.add_argument('-r', '--range', type=int, default=100, 
                        help='Max size of a single allocation')
    parser.add_argument('-P', '--percent_alloc', type=int, default=70, 
                        help='Percent of operations that are MALLOCs (balance are FREEs)')
    parser.add_argument('-s', '--seed', type=int, default=42, 
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()

    # 1. Initialize the Arena
    suite = BenchmarkSuite(heap_size=args.size, seed=args.seed)

    # 2. Generate the Workload
    # A high percent_alloc (e.g. 70%) ensures the heap gets full, stressing the algorithms.
    suite.generate_workload(
        num_ops=args.num_ops, 
        max_alloc_size=args.range, 
        percent_alloc=args.percent_alloc
    )

    # 3. Select Contestants
    # We create fresh instances for every run inside the suite, but here we define the roster.
    contestants = [
        FirstFit(args.size),
        BestFit(args.size),
        WorstFit(args.size)
    ]

    # 4. Start the Games
    results = suite.run(contestants)

    # 5. Ceremony (Visualize)
    suite.plot_results(results)

if __name__ == "__main__":
    main()
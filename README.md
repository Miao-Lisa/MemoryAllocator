# **Allocator Olympics 🥇**

A high-performance simulation and benchmarking suite for Operating System memory allocation strategies.

## **📖 Overview**

**Allocator Olympics** is a simulation engine designed to visualize and quantify the trade-offs between different memory allocation algorithms. Unlike simple visualization scripts, this tool runs rigorous, randomized workloads against multiple "contestants" (First Fit, Best Fit, Worst Fit) to empirically measure:

1. **External Fragmentation:** How much free memory is wasted in small, unusable gaps.  
2. **Search Efficiency:** The computational cost (nodes visited) of finding a free block.  
3. **Allocation Failures:** How often the allocator fails despite having enough total free bytes.

This project was built from the ground up using **Object-Oriented Design** principles (Strategy Pattern) to ensure extensibility and clean separation of concerns.

## **🚀 Key Features**

* **Modular Architecture:** Algorithms are decoupled from the simulation loop using the Strategy Pattern.  
* **Real-time Visualization:** Uses matplotlib to plot fragmentation over time and search depth efficiency.  
* **Configurable Workloads:** Customize heap size, operation count, max allocation size, and allocation/free ratios.  
* **Reproducible Results:** Seed-based random generation ensures all algorithms face the exact same sequence of requests.

## **🛠 Installation**

1. **Clone the repository:**  
   ```sh
   git clone https://github.com/Miao-Lisa/MemoryAllocator.git && cd MemoryAllocator
   ```

2. Install dependencies:  
   This project requires matplotlib for graph generation.  
   ```sh
   pip install matplotlib
   ```

## **💻 Usage**

Run the simulation using the command line interface. The default settings provide a balanced workload.  
python main.py

### **Customizing the Benchmark**

You can stress-test the algorithms by adjusting the flags:

| Flag | Description | Default |
| :---- | :---- | :---- |
| \-S, \--size | Total size of the heap (bytes) | 1000 |
| \-n, \--num\_ops | Number of operations to simulate | 1000 |
| \-r, \--range | Max size of a single allocation | 100 |
| \-P, \--percent\_alloc | Probability of an operation being malloc vs free | 70% |
| \-s, \--seed | Random seed for reproducibility | 42 |

Example: High Fragmentation Stress Test  
Run a simulation with a small heap and high allocation pressure to force fragmentation:  
```sh
python main.py --size 500 --num_ops 2000 --range 50 --percent_alloc 60
```

## **🏗 Architecture**

The project follows strict **Separation of Concerns**:  
```py
classDiagram  
    class AllocatorStrategy {  
        <<Abstract>>  
        +malloc(size)  
        +free(addr)  
        +get_fragmentation()  
    }  
    class LinkedListAllocator {  
        #free_list  
        #coalesce()  
    }  
    class FirstFit  
    class BestFit  
    class WorstFit  
      
    AllocatorStrategy <|-- LinkedListAllocator  
    LinkedListAllocator <|-- FirstFit  
    LinkedListAllocator <|-- BestFit  
    LinkedListAllocator <|-- WorstFit  
      
    class BenchmarkSuite {  
        +generate_workload()  
        +run(strategies)  
    }
```

* **allocators.py**: Contains the logic. LinkedListAllocator handles the low-level pointer arithmetic and coalescing, while subclasses implement the specific search logic.  
* **benchmark.py**: The "Referee". Generates a workload script (List of Tuples) *before* the race begins to ensure every algorithm processes the exact same malloc and free requests.  
* **main.py**: Handles CLI parsing and orchestration.

## **📊 Results Explanation**

When you run the tool, two charts are generated:

1. **Search Efficiency (Bar Chart):**  
   * **Lower is better.**  
   * Shows the average number of list nodes checked per malloc.  
   * *Expectation:* First Fit is usually O(1) to O(k), while Best/Worst fit are O(N) as they must scan the whole list.  
2. **Fragmentation Over Time (Line Chart):**  
   * **Lower is better.**  
   * Measures 1 \- (Largest\_Free\_Block / Total\_Free\_Memory).  
   * *Expectation:* Best Fit usually minimizes fragmentation (green line stays low). Worst Fit often creates high fragmentation quickly (Swiss cheese effect).

## **🔮 Future Work**

* **Buddy Allocator:** Implement binary-tree based allocation for O(log N) coalescing.  
* **Slab Allocator:** Simulate cache-based allocation for fixed-size objects.  
* **Heatmap Visualization:** Add a pixel-map view of the heap memory state.

## Authors

Francisco Duran, Lisa Miao, Stefin Racho

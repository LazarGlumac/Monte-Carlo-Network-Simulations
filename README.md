# Monte-Carlo-Network-Simulations

## Instructions On How To Run Program
To run the simulation, first run in your console, ‘pip install -r requirements.txt’ to install the required libraries.

Then, import the simulation classes from simulation.py into your python script as follows:
```
from simulation import (FullyConnectedTopologySimulation, ConstantTopologySimulation, ClusteredTopologySimulation)
```

Next, create a simulation object with the desired topology as follows:

In all topology simulations,
NUM_SIMS is the number of simulations you would like to run.
NUM_NODES is the number of nodes in the graph.

To simulate a fully connected topology:
```
Simulation_Object = FullyConnectedTopologySimulation(NUM_SIMS, NUM_NODES)
```

 To simulate a constant topology.
 ```
Simulation_Object = ConstantTopologySimulation(NUM_SIMS, NUM_NODES, NUM_LINKS_PER_NODE)
```

NUM_LINKS_PER_NODE is the maximum number of links each node can have.

To simulate a clustered topology.
```
Simulation_Object = ClusteredTopologySimulation(NUM_SIMS, NUM_NODES, NUM_CLUSTERS)
```

NUM_CLUSTERS is the number of clusters in the graph.

To randomize the graph in each iteration of the simulation, put a value of -1 for the NUM_NODES field. The program will then pick a random number of nodes for the graph from a range of 25 to 150 inclusive. For a constant topology, the program will pick a random number of links per node from a range of 25 to one less than the number of nodes. And for a clustered topology, the program will pick a random number of clusters from a range of 5 to 15 inclusive.

To run the simulation with the simulation object, do the following:
```
Simulation_Object.simulate()
```

The program will run simulations for finding the maximum flow, shortest path, and number of disconnected components on the chosen topology

To see the output of the simulation results as a scatterplot / 3D mesh map, do the following:
```
Simulation_Object.visualize_simulation()
```

The program will generate an html file which contains an interactable graph of the results of the simulation (seen in the figures below in the analysis section of this report). This html file can be found in the results folder.

Finally, now that the simulation is set up, simply run ‘python <FILE_NAME>.py’ in your console to run the simulations and generate graphs of the results.

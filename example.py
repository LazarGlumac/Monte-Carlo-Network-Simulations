from simulation import (FullyConnectedTopologySimulation, ConstantTopologySimulation, ClusteredTopologySimulation)

NUM_SIMS = 500
NUM_NODES = -1
NUM_CLUSTERS = 10
NUM_LINKS_PER_NODE = 10

FullyConnectedTopologySimulation = FullyConnectedTopologySimulation(NUM_SIMS, NUM_NODES)
FullyConnectedTopologySimulation.simulate()
FullyConnectedTopologySimulation.visualize_simulation()

ConstantTopologySimulation = ConstantTopologySimulation(NUM_SIMS, NUM_NODES, NUM_LINKS_PER_NODE)
ConstantTopologySimulation.simulate()
ConstantTopologySimulation.visualize_simulation()

ClusteredTopologySimulation = ClusteredTopologySimulation(NUM_SIMS, NUM_NODES, NUM_CLUSTERS)
ClusteredTopologySimulation.simulate()
ClusteredTopologySimulation.visualize_simulation()
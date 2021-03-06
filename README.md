# Quantitative Interval Stream Mining

## Abstract

## Algorithms 

### Pairwise stream dependenices mining

#### ITLD (Interval Time Lag Discovery)
Amine El Ouassouli, Lionel Robinault, Vasile-Marian Scuturici:
**Mining Quantitative Temporal Dependencies Between Interval-Based Streams**. DaWaK 2019: 151-165

#### TEDDY  
Marc Plantevit, Céline Robardet, Vasile-Marian Scuturici: 
**Graph dependency construction based on interval-event dependencies detection in data streams**. Intell. Data Anal. 20(2): 223-256 (2016)

#### PIVOTMiner  
Marwan Hassani, Yifeng Lu, Jens Wischnewsky, Thomas Seidl: 
**A geometric approach for mining sequential patterns in interval-based data streams**. FUZZ-IEEE 2016: 2128-2135

NB: We added a temporal constraint <img src="https://latex.codecogs.com/gif.latex?$\Delta&space;=&space;[min,&space;max]$"/> to this algorithm permitting to keep Delta vectors with time lags in <img src="https://latex.codecogs.com/gif.latex?$\Delta$"/> for the clusturing step. 

### Complex Temporal Dependencies Mining

#### CTDMiner (Complex Temporal Dependency Miner)
Amine El Ouassouli, Lionel Robinault, Vasile-Marian Scuturici:
**Mining complex temporal dependencies from heterogeneous sensor data streams**. IDEAS 2019: 23:1-23:10


## Data sets
### Real world datasets
#### Fox

### Synthetic Data
#### Simulation Tool 
<p align="center"> 
    <img  src="resources/img/generator_screenshot.PNG" width="70%">
    <br>
    Fig 1. Screenshot of the motion simulation tool. Green squares are moving object instances. Lines refer to trajectories. Red squares are "motion sensors"
</p>

Synthetic data sets are generated using a motion simulation tool permitting to define motion scenarios. A scenario is built as follows:

- Generate a test bed of a given size
- Draw Nodes, Segments and define trajectories
- Place motion sensors in the testbed
- Define trajectories occurrrences by specifying the following parameters:
    - Occurrence number: Number of moving objects (green squares) to be generated 
    - Duration (<img src="https://latex.codecogs.com/gif.latex?$T_{observation}$" title="$T_{observation}$" />): Duration of the simulation
    - Speed <img src="https://latex.codecogs.com/gif.latex?\sim&space;\mathcal{N}(v,&space;\sigma^2)" title="\sim \mathcal{N}(v, \sigma^2)" />: v in pixels/time unit, <img src="https://latex.codecogs.com/gif.latex?$\sigma^2$"/> is the variance of the speed normal distribution.
- Add trajectories occurrences by choosing a trajectory in the list and clicking on "Add to scenario".

A moving object (green squares) per trajectory occurrence is generated. The starting timestamp of each occurrence is chosen randomly in <img src="https://latex.codecogs.com/gif.latex?$T_{observation}$" title="$T_{observation}$" />. The simulation process computes at each time unit in <img src="https://latex.codecogs.com/gif.latex?$T_{observation}$" title="$T_{observation}$" /> the position of each instance. If motion is detected in a sensor's area (presence of a moving object) an event *Motion Begin* is added to the corresponding stream. Similarly, a event *Motion End* is triggered when motion ends.

The simulation process can be vizualized by playing the scenario. 

#### Datasets specification

- **syn_delta**: Linear trajectory with 10 equidistant sensors. <img src="https://latex.codecogs.com/gif.latex?$T_{observation}&space;=&space;10000$"/>, <img src="https://latex.codecogs.com/gif.latex?$v&space;=&space;10$"/>, <img src="https://latex.codecogs.com/gif.latex?$\sigma^2&space;=&space;0$"/>, <img src="https://latex.codecogs.com/gif.latex?$occurrences&space;=&space;1000$"/> (1 datasets)

- **syn_density**: Linear trajectory with 10 equidistant sensors. <img src="https://latex.codecogs.com/gif.latex?$T_{observation}&space;=&space;10000$"/>, <img src="https://latex.codecogs.com/gif.latex?$v&space;=&space;10$"/>, <img src="https://latex.codecogs.com/gif.latex?$\sigma^2&space;=&space;0$"/>, <img src="https://latex.codecogs.com/gif.latex?$occurrences&space;\in&space;[100,&space;9000]$"/>. (11 datasets)

- **syn_temporal_variability**: Linear trajectory with 10 equidistant sensors.  <img src="https://latex.codecogs.com/gif.latex?$T_{observation}&space;=&space;10000$"/>, <img src="https://latex.codecogs.com/gif.latex?$v&space;=&space;5$"/>, <img src="https://latex.codecogs.com/gif.latex?$\sigma^2&space;\in&space;[0,2]$"/>, <img src="https://latex.codecogs.com/gif.latex?$occurrences&space;=&space;1000$"/>. (17 datasets)



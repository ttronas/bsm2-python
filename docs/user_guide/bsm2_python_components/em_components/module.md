---
hide:
  - toc
---

### Introduction

The module class serves as a base (parent) class for other energy management classes, providing a standardized set of methods that can be inherited.

Energy management instances that inherit from the module class then can use these methods to output useful information or update their attributes to a different state in a simulation with the energy management system (`bsm2_olem.py`). For example if you want to save the load of chp1 for every simulation step in a readable .csv file (add highlighted lines):

``` py title="example in bsm2_olem.py", hl_lines="10 17 18 21"
# Initialization of chp1 and chp2
chp1 = CHP(...)
chp2 = CHP(...)

# Creates a list of the two chp objects
self.chps = [chp1, chp2]

# Add this before the step function
# Creates an empty numpy array with 2 rows (simulation step i, load) for the whole simulation
    self.load_chp1_all = np.zeros((len(self.simtime), 2))

# Step function with simulation step i
def step(i=int, ...):
    
    # Add this in the step function
    # Saves the current sim step i and the current load of CHP1 in the numpy array
    self.load_chp1_all[i][0] = i
    self.load_chp1_all[i][1] = self.chps[0].load

    # Saves the numpy array as .csv file
    np.savetxt('load_chp1_all.csv', self.load_chp1_all, delimiter=',', fmt='%.2f')
```

The module class contains the following methods:

| Method | Description |
| ------ | ----------- |
| runtime() | Return the runtime of the module [h] |
| load() | Return the load of the module [-] |
| load(value) | Sets the load of the module to 'value' (0-1) |
| total_maintenance_time() | Return the total maintenance time of the module [h] |
| total_maintenance_time(value) | Sets the total maintenance time of the module to 'value' [h] |
| remaining_maintenance_time() | Return the remaining maintenance time of the module [h] |
| remaining_maintenance_time(value) | Sets the remaining maintenance time of the module to 'value' [h] and changes the maintenance status |
| time_since_last_maintenance() | Return the time since the last maintenance of the module [h] |
| under_maintenance() | Return the maintenance status of the module (bool) |
| under_maintenance(value) | Sets the maintenance status of the module to 'value' (bool) |
| ready_to_change_load() | Return weather the module is ready to change load (bool) |
| products() | Returns the products of the module |
| consumption() | Returns the consumption of the module |
| check_failure() | Checks if the module has failed |
| check_load_change() | Checks if the module has changed its load in the previous timestep |
| reduce_remaining_load_change_time(time_delta) | Reduces the remaining load change time to the value 'time delta' |
| check_ready_for_load_change() | Checks if the module is ready to change load |
| produce() | Produces energy based on the load and time delta |
| consume() | Consumes energy based on the load and time delta |
| maintain(time_delta) | Sets the maintenance time of the module to the given 'time_delta' [h] |
| calculate_maintenance_time() | Calculates the maintenance time of the module |
| report_status() | Reports the status of the module |
| step(time_delta) | Updates the module for a time step based on the load and the given 'time delta' |

The following energy management classes inherit from the module class:

- Boiler

- CHP

- Compressor

- Cooler

- Flare

Children classes have to implement the following methods, to inherit from the module class:

- check_failure()

- produce()

- consume()

- calculate_maintenance_time()


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [module](/reference/bsm2_python/energy_management/module)

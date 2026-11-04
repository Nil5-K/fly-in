*This project has been created as part of the 42 curriculum by nkerstin.*

# fly-in

## Description

**fly-in** is a drone routing simulator. It reads a map that describes a network of zones (hubs) and the connections between them, then routes a whole fleet of drones from a single start hub to a single end hub in **as few simulation turns as possible**.

Every drone has to respect these rules:

- **Zone capacity** (`max_drones`). A zone can hold only a limited number of drones in the same turn. The start and end hubs can hold the whole fleet.
- **Connection capacity** (`max_link_capacity`). Only a limited number of drones can be on a connection in the same turn, counting both directions.
- **Zone types**
  - `normal`: entering it costs 1 turn
  - `restricted`: entering it costs 2 turns. The drone stays on the connection during the extra turn and must arrive on the following turn.
  - `priority`: entering it costs 1 turn, and the pathfinder prefers it when two routes are equally fast
  - `blocked`: drones can never enter it

The program prints the turn-by-turn movement in the format required by the subject. It then opens a **pygame window** that animates the simulation.

### Results on the provided maps

| Map | Drones | Target | **fly-in** |
|---|---:|---:|---:|
| easy/01_linear_path | 2 | ≤ 6 | **4** |
| easy/02_simple_fork | 3 | ≤ 6 | **5** |
| easy/03_basic_capacity | 4 | ≤ 8 | **6** |
| medium/01_dead_end_trap | 5 | ≤ 15 | **8** |
| medium/02_circular_loop | 6 | ≤ 20 | **16** |
| medium/03_priority_puzzle | 4 | ≤ 12 | **7** |
| hard/01_maze_nightmare | 8 | ≤ 45 | **14** |
| hard/02_capacity_hell | 12 | ≤ 60 | **18** |
| hard/03_ultimate_challenge | 15 | ≤ 35 | **26** |
| challenger/01_the_impossible_dream | 25 | record 45 | **43** |

Every map meets its target, and the challenger map beats the 45-turn reference record.

## Instructions

### Requirements

- Python 3.10 or later
- The dependencies listed in `requirements.txt` (pygame, flake8, mypy, pytest)

### Installation

```bash
make install        # creates .venv and installs the dependencies
```

### Running

```bash
make run                                   # runs the default map (maps/easy/01_linear_path.txt)
make run MAP=maps/hard/02_capacity_hell.txt
# or directly:
.venv/bin/python fly-in.py <map_file>
```

### Other Makefile rules

| Rule | Purpose |
|---|---|
| `make debug` | Runs the program under `pdb` |
| `make lint` | Runs `flake8` and `mypy` with the flags required by the subject |
| `make lint-strict` | Runs `flake8` and `mypy --strict` |
| `make test` | Runs the unit tests in `tests/` with pytest |
| `make clean` | Removes `__pycache__`, `.mypy_cache` and `.pytest_cache` |
| `make fclean` | Runs `clean` and also removes the virtual environment |

### Output format

Each line is one turn. Every drone that moves in that turn appears on the line as `D<id>-<zone>`. A drone that is still travelling toward a restricted zone appears as `D<id>-<connection>`. Drones that wait are left out.

```
D1-junction
D1-path_a D2-junction
D1-goal D2-path_a D3-junction
D2-goal D3-path_a
D3-goal
```

### Map format

```
nb_drones: 3
start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: slow 2 1 [zone=restricted]
end_hub: goal 3 0 [color=red]
connection: start-junction [max_link_capacity=2]
connection: junction-slow
connection: slow-goal
```

The parser rejects malformed input with a clear `line N: reason` message. It checks the following:

- a missing or non-positive `nb_drones` on the first line
- duplicate start or end hubs
- duplicate zone names, or names containing dashes
- invalid coordinates or metadata
- unknown zone types
- non-positive capacities
- unknown zones in connections
- duplicate connections (`a-b` and `b-a` count as the same connection)

## Algorithm and implementation strategy

The problem is a small **multi-agent pathfinding** problem. fly-in solves it with **prioritized planning**: drones are planned one after another, and each one runs a **space-time A\*** search against a **reservation table** that holds the moves already booked by earlier drones.

```
Parser → GraphIndex → Heuristic → for each drone: TimeAStar → ReservationTable → to_turns → GUI
```

### 1. Graph index (`graph_index.py`)

Each connection becomes two directed edges, one in each direction. The cost of an edge depends on its **destination**: entering a `restricted` zone costs 2 turns and entering any other zone costs 1. No edge is created toward a `blocked` zone, so the pathfinder never sees one.

### 2. Heuristic: reverse Dijkstra (`heuristic.py`)

A single Dijkstra search runs **backwards from the end hub** and ignores other drones. It gives `h(zone)`, the minimum number of turns needed to reach the goal from each zone. This value is computed **once and cached**, and every drone reuses it.

Because the other drones are ignored, `h` never overestimates the real remaining time (it is *admissible*). It is also *consistent*. These two properties guarantee that A\* returns the earliest possible arrival for each drone.

A zone that cannot reach the goal gets no `h` value. A\* never expands it, which takes care of dead ends cheaply.

### 3. Reservation table (`reservation_table.py`)

The reservation table is a booking calendar with two counters:

- `zone_count[(zone, t)]`: the number of drones in `zone` at turn `t`
- `link_count[(connection, t)]`: the number of drones on `connection` during turn `t`. Connections are keyed by a `frozenset`, so both directions share one capacity. This rules out head-on swaps on a single-capacity link.

Rules:

- **wait** at `t`: allowed if `zone_count[(zone, t+1)] < max_drones`
- **move** at `t` along an edge of cost `c`: allowed if the link is below capacity for every turn `t+1 … t+c` **and** the destination is below capacity at `t+c`

A move into a restricted zone books the link for both turns and books the zone on arrival. This means a drone can never get stuck on a connection, as the subject requires.

### 4. Space-time A\* (`time_a_star.py`)

A search state is `(zone, t)`, meaning a position *and* a time. From each state a drone can either move along an available edge or wait one turn. States are ordered in a min-heap by the tuple

```
(f = t + h(zone),  bad,  t,  zone)
```

- `f` is the estimated arrival turn. The search always expands the most promising state first.
- `bad` counts the moves into non-priority zones. When two routes arrive at the same turn, the one that uses more **priority** zones wins.
- `best_bad[(zone, t)]` stops the search from expanding the same state again unless the new path is strictly better.
- `max_turn = h(start) + 2·nb_drones + nb_zones` limits how long a drone can wait, so the search always terminates. If no route exists within this horizon, a `PlanningError` is raised.

When the goal is popped, the route is rebuilt from the `came_from` map.

### 5. Planner (`planner.py`)

For each drone, the planner runs A\*, then books the resulting route in the reservation table. Each later drone sees those bookings as obstacles. This is how drones naturally spread out:

- **strategic waiting** at the start or in front of a bottleneck
- **path distribution** over alternative routes once the shortest route is saturated
- **no deadlocks**, because every drone follows a fully booked, conflict-free timetable

`to_turns` converts the routes into the output lines. For a restricted move, it prints the connection name during the transit turn.

### Complexity

Let `V` be the number of zones, `E` the number of connections, `N` the number of drones and `T` the time horizon (`max_turn`).

| Part | Time | Memory |
|---|---|---|
| Heuristic (once) | `O((V + E) log V)` | `O(V)` |
| One A\* search | `O(V·T·deg · log(V·T))` in the worst case; in practice far less, thanks to the heuristic | `O(V·T)` |
| Whole plan | `N ×` one A\* search | reservation table `O(N · route length)` |
| Capacity checks | `O(1)` dictionary lookups (`O(cost)` for links) | — |

Paths are **not recalculated**: the heuristic is cached, and each drone is planned exactly once. Memory grows linearly with the number of drones, so large fleets stay cheap.

### Limitations

Prioritized planning is optimal for each drone *given the drones planned before it*, but it is **not guaranteed to be globally optimal**: an early drone can take a slot that would have been better used by a later one. On the provided maps this greedy approach still meets every benchmark.

## Visual representation

Once the plan is printed, a resizable **pygame** window replays it.

- **Map**. Zones are drawn as circles in their `color` (grey if no color is given or the color is invalid). The start and end hubs have a white ring. Connections are drawn as lines. Zone names are placed below a zone, or above it when they would overlap another label.
- **Auto-scaling viewport**. Map coordinates are scaled and centered to fit the window and are recomputed whenever the window is resized. Zone and drone sizes follow the scale.
- **Smooth drone animation**. Drones are interpolated linearly between zones, so a restricted move visibly takes twice as long. Each drone is labelled `D<id>`.
- **Playback controls**
  - ⏮: back one turn
  - ▶/⏸: play or pause (also bound to `Space`)
  - ⏹: reset to turn 0
  - ⏭: forward one turn
  - `Esc` or closing the window quits
- **Turn counter** in the bottom-right corner (1 turn = 1 second).

Together these make it easy to see *why* the plan works: you can watch drones wait at a bottleneck, split onto parallel branches, or slow down through restricted zones. You can also step through the plan turn by turn and compare it with the terminal output.

## Resources

- P. E. Hart, N. J. Nilsson, B. Raphael, *A Formal Basis for the Heuristic Determination of Minimum Cost Paths* (1968), the original A\* paper
- E. W. Dijkstra, *A Note on Two Problems in Connexion with Graphs* (1959)
- D. Silver, *Cooperative Pathfinding* (AIIDE 2005), on space-time A\* with a reservation table (Cooperative A\*)
- R. Stern et al., *Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks* (SoCS 2019)
- Graph and search Alorithms - Chapter 2 and 4 *Algorithmen in Python. 32 Klassiker der Informatik* by David Kopec (2019)
- [Red Blob Games – Introduction to A\*](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [The A* Algorithm - Visual learner by TUM](https://algorithms.discrete.ma.tum.de/graph-algorithms/spp-a-star/index_de.html)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Python `dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html)
- [pygame documentation](https://www.pygame.org/docs/)
- [mypy documentation](https://mypy.readthedocs.io/)

### Use of AI

AI (Claude) was used as a learning and documentation aid:

- explaining the mathematics behind the algorithm (reverse Dijkstra, space-time A\*, the reservation table, viewport scaling and interpolation), with worked examples on the provided maps to prepare for the peer evaluation
- explaining Python concepts such as `@staticmethod`
- drafting this README
# Cloud Server Load Balancer Simulation
This project is a Python-based simulation of a cloud server load balancer that dynamically assigns and liberates servers to handle user requests. The load balancer ensures that CPU usage remains consistent across all active servers according to a target percentage set by the user. When server utilization drops below a threshold, the load balancer frees up resources by releasing servers.
## How to Run

Follow these steps to run the Cloud Server Load Balancer Simulation on your local machine:

### Prerequisites
- Python 3.x installed on your system.
- `pip` (Python package manager) to install dependencies.

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/santiago-MV/Load-Balancer-Simulation.git
   cd Load-Balancer-Simulation
2. **Install the required dependency:**
    ```bash
    pip install matplotlib
3. **Configure the simulation:**
    Customize the parameters of the load balancer by editing the `config.ini` file. Open it in any text editor and adjust the settings to your preferences.
4. **Run the simulation**
    ```bash
    python loadbalancer.py
5. **Observe the simulation:** The simulation will terminate either after completing the number of iterations specified in the `config.ini` file or upon reaching a failure state. A failure occurs if the CPU usage deviates by more than 25% from the desired value and the system is unable to assign or remove CPUs to correct it.

# Pamir Palace
Pamir Palace is a hotel resort simulation showcasing the efficiency of parallel computing in managing high-demand hospitality environments.

*Disclaimer: This simulation is developed focusing on parallel computing techniques.*

# Table of Contents
1. [Project Overview](#project-overview)
2. [Simulation Features](#simulation-features)
3. [Technology Stack](#technology-stack)
4. [Installation & Usage](#installation-&-usage)
5. [Simulation Constants](#simulation-constants)
6. [Further Improvements](#further-improvements)
7. [Credits](#credits)

# Project Overview
Pamir Palace models key operations of a hotel, demonstrating parallel computing in guest interaction and resource allocation. The simulation addresses managing varying guest needs and schedules in a high-demand environment.

# Simulation Features
- Check-in/Check-out Processes
- Room Allocation with Different Costs
- Dynamic Guest Activities
- Resource Management with Semaphores
- Emergency Handling Scenarios
- Parallel Computing to Simulate Concurrent Operations

# Technology Stack
- **Programming Language**: Python
- **Concurrency Framework**: Threading
- **Development Environment**: Any Python-supported IDE or Text Editor
- **Version Control**: Git (for source code management)

# Installation & Usage
**Clone the Repository**
``````
git clone https://github.com/whoisoscar/Pamir-Palace
``````

**Setup Environment**
``````
cd PamirPalace
python -m venv venv
source venv/bin/activate # On Windows use 'venv\Scripts\activate'
``````

**Install Dependencies**
``````
pip install -r requirements.txt # If any dependencies are listed
``````

**Run the Simulation**
``````
python pamir_palace_simulation.py
``````


# Simulation Constants
- Pool Seats: 15
- Buffet Seats: 15
- Receptionists: 2
- Gym Equipment Seats: 5
- Bus Capacity: 20
- Activity Costs and Probabilities: Various (see code for details)

# Further Improvements
- [ ] Implement a GUI for real-time simulation monitoring and interaction.
- [ ] Add a feature for dynamic adjustment of resource capacities (e.g., pool seats, gym equipment).
- [ ] Integrate a database for persistent storage of guest data and simulation results.
- [ ] Develop an analytics dashboard for performance metrics and guest behavior patterns.
- [ ] Incorporate AI algorithms for predictive analysis of guest preferences and resource utilization.
- [ ] Enhance emergency handling with more scenarios and automated response protocols.

# Credits
This project was created for our Operating Systems and Parallel Computing course at IE University. The project was created by:
- Alfonso del Saz
- Alvaro Garris
- Batriz Wahle
- Laura Vaquero
- Oscar Tluszcz
- Simão Varandas
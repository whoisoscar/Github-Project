# Pamir Palace
Pamir Palace is a dynamic hotel resort simulation that demonstrates the capabilities of parallel computing in efficiently managing complex, high-demand hospitality environments.

*Disclaimer: This simulation focuses on advanced parallel computing techniques.*

# Table of Contents
1. [Project Overview](#project-overview)
2. [Simulation Features](#simulation-features)
3. [Technology Stack](#technology-stack)
4. [Installation & Usage](#installation-&-usage)
5. [Simulation Configuration](#simulation-configuration)
6. [Database Interaction](#database-interaction)
7. [Further Improvements](#further-improvements)
8. [Credits](#credits)

# Project Overview
Pamir Palace realistically simulates the operations of a hotel, showcasing the effectiveness of parallel computing in handling guest interactions, resource allocation, and emergency scenarios in a high-demand setting.

# Simulation Features
- Efficient Check-in/Check-out Processes
- Dynamic Room Allocation with Variable Costs
- Diverse Guest Activities Including Emergencies
- Advanced Resource Management Using Semaphores
- Real-time Emergency Handling and Response
- Concurrent Operation Simulation Using Parallel Computing

# Technology Stack
- **Programming Language**: Python
- **Concurrency Framework**: Threading, concurrent.futures
- **Database Interaction**: MySQL for data management
- **Development Environment**: Compatible with any Python-supported IDE or Text Editor
- **Version Control**: Git for source code management

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


# Simulation Configuration
- Pool Seats: 50
- Restaurant Seats: 50
- Chefs: 50
- Receptionists: 50
- Gym Equipment Seats: 50
- Bus Capacity: 20 (constant)
- Maximum Nights Stay: 5 (constant)
- Room Types: Standard, Deluxe, Premium
- Costs & Probabilities: Detailed activity costs and guest probabilities (refer to code)

# Database Interaction
The simulation interacts with a MySQL database to store and manage simulation data. This interaction is handled through a separate Python file, which includes functions for creating and deleting the database, adding simulation data, retrieving and printing data, and saving data to a CSV file for analysis. The database schema is designed to store various metrics such as average waiting times for different activities, total revenue, and data about room downgrades.

- **Database Creation**: Function to create a table with appropriate fields for simulation data.
- **Data Management**: Functions to insert, retrieve, and print data from the database.
- **Exporting Data**: Capability to export simulation data to a CSV file for further analysis.

This integration allows for effective tracking and analysis of the simulation’s performance, aiding in understanding and optimizing the simulated hotel environment.


# Further Improvements
- [ ] Implement a GUI for interactive simulation monitoring.
- [ ] Dynamic resource capacity adjustments (e.g., pool seats, restaurant seats).
- [ ] Database integration for tracking simulation data and guest analytics.
- [ ] Comprehensive analytics dashboard for insights into performance and guest behaviors.
- [ ] Application of AI for predictive guest behavior analysis and resource optimization.
- [ ] Expansion of emergency scenarios with automated protocols for enhanced realism.

# Credits
This project was developed for the Operating Systems and Parallel Computing course at IE University. Team members:
- Alfonso del Saz
- Alvaro Garris
- Batriz Wahle
- Laura Vaquero
- Oscar Tluszcz
- Simão Varandas
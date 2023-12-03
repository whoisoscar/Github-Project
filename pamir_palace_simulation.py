# Importing libraries
import threading
import time
import queue
import random
import concurrent.futures
import uuid # Universal Unique Identifiers used to generate ID for the database 
import sql_database 

# Global dictionary to track waiting times tot he activities we are evaluating the change of parameters
waiting_times = {
    'check_in': {'total_time': 0, 'count': 0},
    'check_out': {'total_time': 0, 'count': 0},
    'gym': {'total_time': 0, 'count': 0},
    'pool': {'total_time': 0, 'count': 0},
    'dine': {'total_time': 0, 'count': 0}
}

# Class for defining the conffiguration settings for the hotel
class HotelConfig:
    def __init__(self):
        # Parameters changed to evaluate the impact in the simulation's result
        self.pool_seats = 50
        self.restaurant_seats = 50
        self.chefs = 50
        self.receptionists = 50
        self.gym_seats = 50
        self.bus_capacity = 20 # constant because you can do other activitiies while waiting for the bus
        self.max_nights_stay = 5 # constant, to evaluate the change over the same time interval
        # Types of room that are also changed for the simulations
        self.standard_room = 3
        self.deluxe_room = 20
        self.premium_room = 27
        self.time_between_activities = 1.5
        self.simulation_over = False

        # Room costs and Activity costs and probabilities for the guests
        self.room_costs = {'premium_room': 300, 'deluxe_room': 250, 'standard_room': 200} 
        self.activity_costs = {'pool_seats': 15, 'pee_fee': 30, 'buffet': 20, 'gym': 10, 'bus_excursion': 30, 'tourist_trip': 0}
        self.activity_probabilities = {'pool': 0.25, 'dine': 0.25, 'gym': 0.2, 'bus_excursion': 0.15, 'tourist_trip': 0.15}

# General class of the hotel
class Hotel:
    def __init__(self, num_guests, config):
        self.config = config
        self.pool = Pool(config)
        self.restaurant = Restaurant(config)
        self.reception = Reception(config)
        self.gym = Gym(config)
        self.bus_excursion = BusExcursion(config)
        self.tourist_trip = TouristTrip(config)
        self.guests = [Guest(guest_id, self) for guest_id in range(num_guests)]
        self.daily_earnings = 0
        self.premium_room_semaphore = threading.Semaphore(config.premium_room)
        self.deluxe_room_semaphore = threading.Semaphore(config.deluxe_room)
        self.standard_room_semaphore = threading.Semaphore(config.standard_room)
    
    def room_choice(self, guest):
        if guest.guest_income > 500000:
            if self.premium_room_semaphore.acquire(blocking=False):
                print(f"Guest {guest.guest_id} is staying in a premium room.")
                guest.expenses += guest.config.room_costs['premium_room']
                # add expense to hotel's daily earnings
                hotel.daily_earnings += guest.config.room_costs['premium_room']
            elif self.deluxe_room_semaphore.acquire(blocking=False):
                #add downgrade to export_data
                export_data['downgraded_from_premium'] += 1

                print(f"Guest {guest.guest_id} is staying in a deluxe room.")
                guest.expenses += guest.config.room_costs['deluxe_room']
                # add expense to hotel's daily earnings
                hotel.daily_earnings += guest.config.room_costs['deluxe_room']
            elif self.standard_room_semaphore.acquire(blocking=False):
                #add downgrade to export_data
                export_data['downgraded_from_deluxe'] += 1

                print(f"Guest {guest.guest_id} is staying in a standard room.")
                guest.expenses += guest.config.room_costs['standard_room']
                # add expense to hotel's daily earnings
                hotel.daily_earnings += guest.config.room_costs['standard_room']
            else:
                print(f"No rooms available for Guest {guest.guest_id}.")
        elif guest.guest_income > 150000:
            if self.deluxe_room_semaphore.acquire(blocking=False):
                print(f"Guest {guest.guest_id} is staying in a deluxe room.")
                guest.expenses += guest.config.room_costs['deluxe_room']
                # add expense to hotel's daily earnings
                hotel.daily_earnings += guest.config.room_costs['deluxe_room']
            elif self.standard_room_semaphore.acquire(blocking=False):
                #add downgrade to export_data
                export_data['downgraded_from_deluxe'] += 1

                print(f"Guest {guest.guest_id} is staying in a standard room.")
                guest.expenses += guest.config.room_costs['standard_room']
                # add expense to hotel's daily earnings
                hotel.daily_earnings += guest.config.room_costs['standard_room']
            else:
                print(f"No rooms available for Guest {guest.guest_id}.")
        else:
            if self.standard_room_semaphore.acquire(blocking=False):
                print(f"Guest {guest.guest_id} is staying in a standard room.")
                guest.expenses += guest.config.room_costs['standard_room']
                # add expense to hotel's daily earnings
                hotel.daily_earnings += guest.config.room_costs['standard_room']
            else:
                print(f"No rooms available for Guest {guest.guest_id}.")
        return

    def open_for_business(self): # Function to start the hotel
        self.restaurant.open_restaurant() # Starts the chefs
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.guests)) as executor:
            for guest in self.guests:
                executor.submit(guest.run)
            self.simulate_days_passing() 
        
        self.restaurant.close_restaurant()  # Stop the chefs

    def simulate_days_passing(self):
        while any(guest.active for guest in self.guests):
            time.sleep(24)  # Simulate a day passing (1 sec = 1 hr)
            # Decrement everyone's nights stay
            for guest in [guest for guest in self.guests if guest.active]:
                # If nights stay is 0, check out
                if guest.decrement_night_stay() == 0:
                    guest.check_out()

            self.end_of_day_report()
            self.daily_earnings = 0 # Setting the beg earnings for 0
        
        config.simulation_over = True
        print(f"\n---------------------\nEnd of simulation. Total earnings: {sum(guest.expenses for guest in self.guests)}$\n---------------------")
        # Print number of active guests and total earnings for the end of the simulation
        print(f"Number of guests currently staying: {len([guest for guest in self.guests if guest.active])}")
        print_average_waiting_times()

        #save total earnings to export_data
        export_data['total_revenue'] = sum(guest.expenses for guest in self.guests)

    def end_of_day_report(self): # Print number of active guests and total earnings for the end of each day
        print(f"\n---------------------\nEnd of Day Report:")
        print(f"Number of guests currently staying: {len([guest for guest in self.guests if guest.active])}")
        print(f"Daily earnings: {self.daily_earnings}$\n---------------------\n")

# Class to represent the receptioninsts
class Receptionist:
    def __init__(self, id):
        self.id = id # So there can be more than 1

    def check_in(self, guest):
        print(f"Receptionist {self.id} is checking in Guest {guest.guest_id}.")
        time.sleep(random.uniform(0.08, 0.2)) # simulate check in time
        print(f"Guest {guest.guest_id} has checked in for {guest.nights_stay} nights.")

    def check_out(self, guest):
        print(f"Receptionist {self.id} is checking out Guest {guest.guest_id}. Total expenses: {guest.expenses}$")
        time.sleep(random.uniform(0.08, 0.2)) # simulate check out time


# Class for the reception of the hotel
class Reception:
    def __init__(self, config):
        self.receptionists = [Receptionist(i) for i in range(config.receptionists)]
        self.reception_semaphore = threading.Semaphore(config.receptionists) # Allows x number of threads to enter based on the amount of recepcionists

    def check_in(self, guest):
        start_time = time.time()  # Start timing
        print(f"Guest {guest.guest_id} is waiting to be checked in.")
        while not self.reception_semaphore.acquire(blocking=False): # Same as in the pool and restaurant
            time.sleep(0.001)
        end_time = time.time()  # End timing
        waiting_times['check_in']['total_time'] += (end_time - start_time)
        waiting_times['check_in']['count'] += 1
        try:
            # Find an available receptionist
            available_receptionist = self.receptionists[guest.guest_id % len(self.receptionists)]
            available_receptionist.check_in(guest) # Do the check in
        finally:
            self.reception_semaphore.release() # release the receptionist

    def check_out(self, guest): # Exact same logic as above but for check out
        with guest.activity_lock:
            start_time = time.time()  
            print(f"Guest {guest.guest_id} is waiting to be checked out.")
            while not self.reception_semaphore.acquire(blocking=False):
                time.sleep(0.001)
            end_time = time.time() 
            waiting_times['check_out']['total_time'] += (end_time - start_time)
            waiting_times['check_out']['count'] += 1
            try:
                # Find the receptionist who checked in the guest (if needed)
                available_receptionist = self.receptionists[guest.guest_id % len(self.receptionists)]
                available_receptionist.check_out(guest)

            finally:
                self.reception_semaphore.release()


# Class to represent the guests
class Guest(threading.Thread):
    def __init__(self, guest_id, hotel):
        super().__init__()
        self.guest_id = guest_id
        self.stop_event = threading.Event()
        self.guest_income = random.paretovariate(1.16) * 55000 # $55,000 is the min income of the america middle class 
        # 1.16 is the standard value derived from empirical studies of income and wealth distributions with pareto's dist.
        self.hotel = hotel
        self.config = hotel.config  # Access the configurations through the hotel
        self.expenses = 0 # Start with no expenses
        self.nights_stay = random.randint(1, self.config.max_nights_stay) # Staying randomly between one and max_nights 
        self.active = True
        self.order_items = [] # Individual empty list to order items
        self.activity_lock = threading.Lock()
        
    
    def run(self):
        try:
            self.hotel.reception.check_in(self)
            self.hotel.room_choice(self)
            while self.active and not self.stop_event.is_set():
                activity = self.choose_activity()
                activity(self)
                time.sleep(0.1)
        except Exception as e:
            print(f"Error in Guest {self.guest_id}: {e}")



    def choose_activity(self): # Functioni to establish the guests activity choice
        activities = [self.hotel.pool.use, self.hotel.restaurant.dine, self.hotel.gym.use, 
                        self.hotel.bus_excursion.join, self.hotel.tourist_trip.join]
        
        probabilities = [self.config.activity_probabilities['pool'], self.config.activity_probabilities['dine'],
                            self.config.activity_probabilities['gym'], self.config.activity_probabilities['bus_excursion'],
                            self.config.activity_probabilities['tourist_trip']]

        chosen_activity = random.choices(activities, probabilities, k=1)[0] # Chose random activity, one per time
        with self.activity_lock:
            return chosen_activity # TTHe return will call the activity chosen
    
    def decrement_night_stay(self):
        with threading.Lock():
            if self.nights_stay > 0:
                self.nights_stay -= 1
            return self.nights_stay
        
    def check_out(self):
        self.active = False
        self.stop_event.set()
        self.hotel.reception.check_out(self)


#Class for the pool facilities of the hotel
class Pool:
    def __init__(self, config):
        self.config = config
        #self.lock = threading.Lock()
        self.pool_seats_semaphore = threading.Semaphore(config.pool_seats) # Allows x number of threads to enter
    
    def use(self, guest): # Function that describes the use of the pool
        #with self.lock:
            if random.random() <= 0.7: # Probability of 70% of use the pool_seats
                # To actually sit by the pool
                start_time = time.time()  # Start timing
                print(f"Guest {guest.guest_id} is waiting to use the pool seats")
                while not self.pool_seats_semaphore.acquire(blocking=False): # The 'acquire' method with 'blocking=False' tries to acquire a seat without blocking the thread.
                    time.sleep(0.001) # Guest checking for a pool seat to become available every 0.001 sec
                end_time = time.time()  # End timing
                waiting_times['pool']['total_time'] += (end_time - start_time) # Sum the diifference to the pool waiting time
                waiting_times['pool']['count'] += 1 # The nunmber of guests that waited
                try:
                    print(f"Guest {guest.guest_id} is using the pool seat.")
                    # Simulate pool usage
                    time.sleep(random.uniform(1, 5)) # Guest interval of usage from 1-5h (1h = 1sec of simulation)
                    guest.expenses += self.config.activity_costs['pool_seats'] # Change the guest once he/she finished to use it
                    hotel.daily_earnings += self.config.activity_costs['pool_seats'] # Add expense to hotel's daily earnings
                finally:
                    self.pool_seats_semaphore.release() # Resealse the semaphore of the chair being used.
            else: # Not using the pool seats, going stright into the water
                print(f"Guest {guest.guest_id} is in the pool.")
                if random.random() < 0.05: # Probability smaller than 5% of happening an emergency
                    self.handle_emergency(guest) # Pass the guest object
                if random.random() <0.05: # Probability smaller than 5% of the guest peeing in the pool
                    self.pee_in_the_pool(guest) 

    def handle_emergency(self, guest):
        print(f"Emergency for Guest {guest.guest_id} at the pool!")
        response_time = random.uniform(1, 5) # Random response time
        if response_time > 4:
            print(f"Guest {guest.guest_id} has drowned due to delayed response!")
            guest.active = False  # Set the guest's active status to False
        else: 
            print(f"Guest {guest.guest_id} has been saved by the lifeguard as they responded on time.")

    def pee_in_the_pool(self, guest):
        print(f"Guest {guest.guest_id} peed in the pool.")
        guest.expenses += self.config.activity_costs['pee_fee'] # Charge the guest the fee
        hotel.daily_earnings += self.config.activity_costs['pee_fee'] # Add expense to hotel's daily earnings

# Here we are appyliing the coffee shop assignment logic to our restaurant
class MenuItem:
    def __init__(self, name, price, preparation_time): # Structure of the menu items further on the coded
        self.name = name
        self.price = price
        self.preparation_time = preparation_time

class Order:
    def __init__(self, guest, items): # The structure of the guest's order
        self.guest = guest
        self.items = items

class Chef(threading.Thread):
    def __init__(self, name, order_queue):
        super().__init__(daemon=True) # To allow the program to exit even if these threads are still running
        self.name = name 
        self.order_queue = order_queue

    def run(self): # The chef(s') function
        while True:
            order = self.order_queue.get() # Get 1st order in queue (FIFO)
            if order is None or config.simulation_over:  # Check for the stop signal
                self.order_queue.task_done() 
                break
            self.prepare_order(order) # Call the prepare order functioni
            self.order_queue.task_done() # Dequeue the order from the queue and process it by calling task_done()
    
    def prepare_order(self, order):
        for item in order.items:
            print(f"{self.name} is preparing {item.name} for Guest {order.guest.guest_id}.")
            time.sleep(item.preparation_time) # Account the preparationi time of each meal
            if config.simulation_over:
                return
            print(f"{self.name} has finished preparing {item.name} for Guest {order.guest.guest_id}.")
            order.guest.expenses += item.price # Add the price of the meal to the guests' expenses
            #add expense to hotel's daily earnings
            hotel.daily_earnings += item.price

# Class for the restaurant facilities of the hotel
class Restaurant:
    def __init__(self, config):
        self.config = config
        #self.lock = threading.Lock() 
        self.restaurant_seats_semaphore = threading.Semaphore(config.restaurant_seats) # Allows x number of threads to enter
        self.order_queue = queue.Queue()
        self.order_lock = threading.Lock()

        self.menu_items = [ # Creating a menu with according prices and times for the guests
            MenuItem("Steak", 25.0, 0.3),
            MenuItem("Salad", 10.0, 0.15),
            MenuItem("Dessert", 8.0, 0.15),
            MenuItem("Soup", 12.0, 0.2),
            MenuItem("Pizza", 15.0, 0.25),
            MenuItem("Burger", 18.0, 0.3),
            MenuItem("Pasta", 20.0, 0.25),
            MenuItem("Sushi", 30.0, 0.35),
            MenuItem("Chicken", 22.0, 0.3),
            MenuItem("Fish", 28.0, 0.35),
            MenuItem("Rice", 10.0, 0.2),
            MenuItem("Sandwich", 15.0, 0.25),
            MenuItem("Ice Cream", 8.0, 0.15),
            MenuItem("Coffee", 5.0, 0.1),
            MenuItem("Tea", 4.0, 0.1),
            MenuItem("Juice", 6.0, 0.15),
            MenuItem("Pancakes", 12.0, 0.2),
            MenuItem("Waffles", 14.0, 0.25),
            MenuItem("Omelette", 16.0, 0.3),
            MenuItem("Fried Rice", 18.0, 0.3),
        ]
        self.chefs = [Chef(f"Chef {i+1}", self.order_queue) for i in range(config.chefs)]  # Chefs preparing the order from the queue
    
    def open_restaurant(self):
        for chef in self.chefs:
            chef.start() # Initiates chefs

    def close_restaurant(self):
        for _ in self.chefs:
            self.order_queue.put(None)  # Send the stop signal to each chef

    def order_menu(self, guest):
        chosen_items = random.sample(self.menu_items, k=random.randint(1, 5)) # Randomly order from the menu from 1 to 5 items.
        guest.order_items = chosen_items # Add the items to the guest's order
        order = Order(guest, chosen_items)
        self.order_queue.put(order) # Put this order on the queue
        print(f"Guest {guest.guest_id} has placed an order for {[item.name for item in chosen_items]}.")


    def dine(self, guest): # Main function of the dinning structure
        #with self.lock:
           start_time = time.time()  # Start timing
           print(f"Guest {guest.guest_id} is waiting to use the restaurant.")
           while not self.restaurant_seats_semaphore.acquire(blocking=False): # Same as for the pool
               time.sleep(0.001)
           end_time = time.time()  # End timing
           waiting_times['dine']['total_time'] += (end_time - start_time)  # Same as for the pool
           waiting_times['dine']['count'] += 1
           try: # Once there is an availabel seat in the restaurant
               if random.random() <= 0.5: # 50% of chance of the guest ordering from the menu
                    print(f"Guest {guest.guest_id} is ordering from the menu.")
                    with self.order_lock: # Only on thread per order
                        if guest.active:
                            self.order_menu(guest) # Guest order from the menu
                            total_prep_time = sum(item.preparation_time for item in guest.order_items) 
                            time.sleep(total_prep_time) # Program sleeps based on the order
                            if guest.active:
                                print(f"Guest {guest.guest_id}'s order is ready.")
                            # Simulate dining
                            time.sleep(random.uniform(1.5, 3)) # from hour and a half up to 3 hours
                            # Reset guest order items
                            guest.order_items = []
               else: # the other alternative is the buffet
                   print(f"Guest {guest.guest_id} is dining from the buffet.")
                   time.sleep(random.uniform(1.5, 3)) # Simulate dinning
                   if guest.active:
                    print(f"Guest {guest.guest_id} has finished dining in the buffet.")
                   guest.expenses += self.config.activity_costs['buffet'] # Charge the costs
                   hotel.daily_earnings += self.config.activity_costs['buffet'] # Add expense to hotel's daily earnings
           finally:
               self.restaurant_seats_semaphore.release() # Release the lock for that restaurant seat


# Class to represent the Gym
class Gym:
    def __init__(self, config):
        self.config = config
        #self.lock = threading.Lock()
        self.gym_seats_semaphore = threading.Semaphore(config.gym_seats)
    
    def use(self, guest): # Define general use of the gym
        #with self.lock:
            start_time = time.time()  # Start timing
            print(f"Guest {guest.guest_id} is waiting to use the gym.")
            while not self.gym_seats_semaphore.acquire(blocking=False):
                time.sleep(0.001)
            end_time = time.time()  # End timing
            waiting_times['gym']['total_time'] += (end_time - start_time)
            waiting_times['gym']['count'] += 1
            try:
                print(f"Guest {guest.guest_id} is using the gym.")
                # Simulate gym usage (from haf and hour to two h realistically)
                time.sleep(random.uniform(0.5, 2))
                guest.expenses += self.config.activity_costs['gym'] # Charge guest once the activity is completed
                # Add expense to hotel's daily earnings
                hotel.daily_earnings += self.config.activity_costs['gym']
            finally:
                self.gym_seats_semaphore.release()


# Class to simulate a bus excursion
class BusExcursion:
    def __init__(self, config):
        self.config = config
        self.excursion_list = [] # Create an empty list of interested people
        self.lock = threading.Lock()

    def join(self, guest):
        with self.lock:
            if len(self.excursion_list) < self.config.bus_capacity: # If the excursion list is smaller than the bus capacity
                if guest not in self.excursion_list: # And the guest is sttill not added to the lid
                    self.excursion_list.append(guest) # Add the guest
                    print(f"Guest {guest.guest_id} has shown interest for the bus excursion, there are currently {len(self.excursion_list)} guests interested, {self.config.bus_capacity - len(self.excursion_list)} missing for the bus to depart.")
                    if len(self.excursion_list) == self.config.bus_capacity: # Whenever the bus is full
                        self.start() # Call start
            else:
                print(f"Guest {guest.guest_id} cannot join now, bus is full.") # Error handling due to timming

    def start(self): 
        print(f"Bus excursion starting with guests {[guest.guest_id for guest in self.excursion_list]}.")
        time.sleep(4)  # Simulate excursion duration (4h = 4sec)
        for guest in self.excursion_list:
            guest.expenses += self.config.activity_costs['bus_excursion'] # Charge the guests
            hotel.daily_earnings += self.config.activity_costs['bus_excursion'] # Add expense to hotel's daily earnings
        
        print(f"Bus excursion has returned with guests {[guest.guest_id for guest in self.excursion_list]}.")
        self.excursion_list.clear() # Empty the list once the excurrsion is complete


# Class represent a tourist trip
class TouristTrip:
    def __init__(self, config):
        self.config = config

    def join(self, guest):
        print(f"Guest {guest.guest_id} is going on a tourist trip.")
        # Simulate trip duration
        trip_duration = random.uniform(1, 5)
        time.sleep(trip_duration)
        guest.expenses += self.config.activity_costs['tourist_trip'] # Charge the guest
        # Add expense to hotel's daily earnings
        hotel.daily_earnings += self.config.activity_costs['tourist_trip']

        if guest.active:
            print(f"Guest {guest.guest_id} has returned from the tourist trip.")



def print_average_waiting_times():
    print("\nAverage Waiting Times:")
    for activity, times in waiting_times.items():
        # Calculate average time in seconds
        average_time_seconds = times['total_time'] / times['count'] if times['count'] > 0 else 0

        # Convert to simulation time (1 real second = 1 simulation hour)
        average_time_hours = average_time_seconds  # 1 second = 1 hour in simulation

        # Format the time for display
        if average_time_hours >= 1:
            # Display in hours if more than or equal to 1 hour
            display_time = f"{average_time_hours:.2f} hour(s)"
        elif average_time_hours * 60 >= 1:
            # Convert to minutes if less than an hour but more than or equal to 1 minute
            display_time = f"{average_time_hours * 60:.2f} minute(s)"
        else:
            # Convert to seconds if less than a minute
            display_time = f"{average_time_hours * 3600:.2f} second(s)"

        print(f"{activity.capitalize()}: {display_time}")
        export_data[f"{activity}_avg_waiting_time_pretty"] = display_time
        export_data[f"{activity}_avg_waiting_time"] = str(average_time_hours * 3600)

# Main entry point of the script
if __name__ == "__main__":
    # Generate a unique simulation ID using UUID
    simulation_uuid = str(uuid.uuid4())
    # Dictionary to store data that will be exported to the database
    export_data = {'simulation_uuid': simulation_uuid, 'downgraded_from_premium': 0, 'downgraded_from_deluxe': 0}
    # Initialize the hotel configuration
    config = HotelConfig()
    # Create a Hotel instance with 50 guests
    hotel = Hotel(50, config)
    # Start the hotel's business operations
    hotel.open_for_business()

    # Once the simulation is complete, add the collected data to the SQL database
    sql_database.add_data(export_data)

    
    
    




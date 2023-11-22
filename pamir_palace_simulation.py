import threading
import time
import random

# Constants for the number of resources
pool_seats = 15
buffet_seats = 15
receptionists = 2  # Assuming there are two receptionists
gym_seats = 5  # Assuming 10 equipment in the gym
bus_capacity = 20  # Assuming a bus can take 20 guests

# Semaphores for resource management
pool_seats_semaphore = threading.Semaphore(pool_seats)
buffet_semaphore = threading.Semaphore(buffet_seats)
reception_semaphore = threading.Semaphore(receptionists)
gym_seats_semaphore = threading.Semaphore(gym_seats)

# Activity costs and probabilities
activity_costs = {'pool': 15, 'dine': 20, 'gym': 10, 'bus_excursion': 30, 'tourist_trip': 0}
activity_probabilities = {'pool': 0.25, 'dine': 0.25, 'gym': 0.2, 'bus_excursion': 0.15, 'tourist_trip': 0.15}

# Global variables
hotel_guests = []
bus_excursion_list = []
gym_seats_list = []
pool_seats_list = []
buffet_seats_list = []
is_bus_on_trip = False
bus_excursion_lock = threading.Lock()
day_count = 0

# Define the Guest class
class Guest(threading.Thread):
    def __init__(self, guest_id):
        super().__init__()
        self.guest_id = guest_id
        self.lock = threading.Lock()  # Lock for each guest
        self.expenses = 0
        self.emergency = False
        self.nights_stay = random.randint(1, 5)  # Random number of nights staying
        self.in_excursion = False
        self.active = True  # Flag to control the thread's life

    def run(self):
        self.check_in()
        while self.nights_stay > 0:
            # Probability-based activity selection
            activity = self.choose_activity()
            activity()
            if self.emergency:
                break
            time.sleep(3)  # Simulating time between activities
        if self.nights_stay == 0 and not self.in_excursion and not self.emergency:
            self.check_out()

    def check_in(self):
        with reception_semaphore:
            time.sleep(random.uniform(0.5, 1))
            print(f"Guest {self.guest_id} has checked in for {self.nights_stay} nights.")


    def choose_activity(self):
        activities = [self.use_pool, self.dine, self.use_gym, self.join_bus_excursion, self.go_on_tourist_trip]
        probabilities = [activity_probabilities['pool'], activity_probabilities['dine'],
                         activity_probabilities['gym'], activity_probabilities['bus_excursion'],
                         activity_probabilities['tourist_trip']]
        return random.choices(activities, probabilities, k=1)[0]


    def use_pool(self):
        with self.lock:  # Acquire lock for this guest
            print(f"Guest {self.guest_id} is trying to use the pool.")
            with pool_seats_semaphore:
                if random.random() < 0.01:  # 1% chance of drowning
                    print(f"Emergency for Guest {self.guest_id} at the pool!")
                    self.handle_emergency()
                else:
                    time.sleep(random.uniform(0.5, 2.5))
                    print(f"Guest {self.guest_id} is done using the pool.")
                    self.expenses += activity_costs['pool']

    def handle_emergency(self):
        response_time = random.uniform(1.0, 5.0)
        if response_time > 3.0:
            print(f"Guest {self.guest_id} drowned due to delayed medical response.")
            self.emergency = True
            self.active = False  # Deactivate the guest thread

        else:
            print(f"Guest {self.guest_id} rescued in time.")

    def use_gym(self):
        with self.lock:
            print(f"Guest {self.guest_id} wants to use the gym.")
            # Check if there are seats available in the gym
            if len(gym_seats_list) < gym_seats:
                gym_seats_list.append(self)
                print(f"There is space for guest {self.guest_id} to use the gym.")
                with gym_seats_semaphore:
                    # Guest is using the gym
                    time.sleep(random.uniform(0.5, 2.0))
                    print(f"Guest {self.guest_id} is done using the gym.")
                    self.expenses += activity_costs['gym']
                gym_seats_list.remove(self)  # Remove guest from the gym seats list after using the gym
            else:
                print(f"No seats available at the gym for Guest {self.guest_id}. Try again later.")    
    
    def dine(self):
        with self.lock:
            print(f"Guest {self.guest_id} is going down to the buffet.")
            with buffet_semaphore:
                time.sleep(random.uniform(1.0, 3.5))
                print(f"Guest {self.guest_id} has finished dining.")
                self.expenses += activity_costs['dine']

    def join_bus_excursion(self):
        with self.lock:
            with bus_excursion_lock:
                if self.in_excursion:
                    return  # Guest already on excursion
                print(f"Guest {self.guest_id} is interested in the bus excursion.")
                bus_excursion_list.append(self)
                print(f"There are currently {len(bus_excursion_list)} guests signed up for the bus excursion, {bus_capacity - len(bus_excursion_list)} missing for the excursion to begin.")
                if len(bus_excursion_list) == bus_capacity:
                    self.start_bus_excursion()

    def start_bus_excursion(self):
        print(f"Bus is departing with guests {[guest.guest_id for guest in bus_excursion_list]} to the beach.")
        excursion_time = random.uniform(1.0, 3.0)  # Random time spent on excursion
        for guest in bus_excursion_list:
            guest.in_excursion = True
            guest.expenses += activity_costs['bus_excursion']
        time.sleep(excursion_time)  # Simulate excursion time
        print(f"Bus is returning with guests {[guest.guest_id for guest in bus_excursion_list]} from the beach.")
        for guest in bus_excursion_list:
            guest.in_excursion = False
        bus_excursion_list.clear()
    
    def go_on_tourist_trip(self):
        with self.lock:
            self.in_excursion = True
            print(f"Guest {self.guest_id} is going on a tourist trip outside the resort.")
            trip_duration = random.uniform(0.5, 2.0)
            time.sleep(trip_duration)  # Simulate trip duration
            print(f"Guest {self.guest_id} has returned from the tourist trip.")
            self.expenses += activity_costs['tourist_trip']
            self.in_excursion = False
    
    def check_out(self):
        with self.lock:
            if self.active:  # Check if the guest hasn't already checked out
                print(f"Guest {self.guest_id} is checking out with total expenses: {self.expenses}$")
                self.active = False  # Prevent further check-out
                global hotel
                hotel.daily_earnings += self.expenses

        
# Define the Hotel class
class Hotel:
    def __init__(self, num_guests):
        self.guests = [Guest(guest_id) for guest_id in range(num_guests)]
        self.guests_lock = threading.Lock()  # Lock for synchronizing access to self.guests
        global hotel_guests
        hotel_guests = self.guests.copy()  # Initialize hotel_guests here
        self.day_count = 0
        self.daily_earnings = 0

    def open_for_business(self):
        print("Hotel is now open.")
        for guest in self.guests:
            guest.start()

        while any(guest.is_alive() for guest in self.guests):
            time.sleep(20)  # Simulate a day passing
            self.day_count += 1
            self.end_of_day_report()


    def end_of_day_report(self):
        print(f"\nEnd of Day {self.day_count} Report:")
        print("Once guests finish the activities they are currently doing, they will check out.")

        with self.guests_lock:
            for guest in self.guests:
                guest.nights_stay -= 1
                # Check if the guest's stay has ended
                if guest.nights_stay == 0:
                    # If the guest is waiting for the bus excursion or in any excursion, they should be checked out
                    if guest.in_excursion or (guest in bus_excursion_list):
                        guest.check_out()
                        # If they were waiting for the bus, remove them from the list
                        if guest in bus_excursion_list:
                            bus_excursion_list.remove(guest)
                    # If the guest is not in an excursion, also check out
                    elif guest.is_alive():
                        guest.check_out()
            
            # Update the guest list to remove guests who are no longer active
            self.guests = [guest for guest in self.guests if guest.active]

            print(f"\nNumber of guests currently staying: {len(self.guests)}\nDetailed guest list: {[guest.guest_id for guest in self.guests]}")
            print(f"\nDaily earnings: {self.daily_earnings}$")
            self.daily_earnings = 0  # Reset daily earnings for the next day
        
            if len(self.guests) > 0:
                print(f"\nDay {(self.day_count)+ 1} will begin shortly.\n")
                
            if len(self.guests) == 0:
                print("\nHotel is now closed.")
                print(f"Total earnings: {sum(guest.expenses for guest in hotel_guests)}$")

# Start the simulation
if __name__ == "__main__":
    num_guests = 50  # Let's say we have 50 guests for this simulation
    hotel = Hotel(num_guests)
    hotel.open_for_business()


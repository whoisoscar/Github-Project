
import threading
import time
import random
import concurrent.futures


class HotelConfig:
    def __init__(self):
        # Constants for the number of resources
        self.pool_seats = 15
        self.buffet_seats = 15
        self.receptionists = 2
        self.gym_seats = 10
        self.bus_capacity = 20

        # Activity costs and probabilities
        self.activity_costs = {'pool': 15, 'dine': 20, 'gym': 10, 'bus_excursion': 30, 'tourist_trip': 0}
        self.activity_probabilities = {'pool': 0.25, 'dine': 0.25, 'gym': 0.2, 'bus_excursion': 0.15, 'tourist_trip': 0.15}


class Pool:
    def __init__(self, config):
        self.config = config
        self.pool_seats_semaphore = threading.Semaphore(config.pool_seats)
    
    def use(self, guest):
        with self.pool_seats_semaphore:
            print(f"Guest {guest.guest_id} is using the pool.")
            # Simulate pool usage
            time.sleep(random.uniform(0.5, 2.5))
            guest.expenses += self.config.activity_costs['pool']


class Buffet:
    def __init__(self, config):
        self.config = config
        self.buffet_seats_semaphore = threading.Semaphore(config.buffet_seats)
    
    def dine(self, guest):
        with self.buffet_seats_semaphore:
            print(f"Guest {guest.guest_id} is dining.")
            # Simulate dining
            time.sleep(random.uniform(1.0, 3.5))
            guest.expenses += self.config.activity_costs['dine']

class Reception:
    def __init__(self, config):
        self.reception_semaphore = threading.Semaphore(config.receptionists)

    def check_in(self, guest):
        with self.reception_semaphore:
            print(f"Guest {guest.guest_id} is checking in.")
            time.sleep(random.uniform(0.5, 1.0))

    def check_out(self, guest):
        with self.reception_semaphore:
            print(f"Guest {guest.guest_id} is checking out. Total expenses: {guest.expenses}$")


class Gym:
    def __init__(self, config):
        self.config = config
        self.gym_seats_semaphore = threading.Semaphore(config.gym_seats)
    
    def use(self, guest):
        with self.gym_seats_semaphore:
            print(f"Guest {guest.guest_id} is using the gym.")
            # Simulate gym usage
            time.sleep(random.uniform(0.5, 2.0))
            guest.expenses += self.config.activity_costs['gym']

class BusExcursion:
    def __init__(self, config):
        self.config = config
        self.bus_capacity = config.bus_capacity
        self.excursion_list = []
        self.lock = threading.Lock()

    def join(self, guest):
        with self.lock:
            if len(self.excursion_list) < self.bus_capacity:
                self.excursion_list.append(guest)
                print(f"Guest {guest.guest_id} has joined the bus excursion.")
                if len(self.excursion_list) == self.bus_capacity:
                    self.start()
            else:
                print(f"Bus excursion is full. Guest {guest.guest_id} cannot join now.")

    def start(self):
        print(f"Bus excursion starting with guests {[guest.guest_id for guest in self.excursion_list]}.")
        # Simulate excursion duration
        time.sleep(random.uniform(1.0, 3.0))
        for guest in self.excursion_list:
            guest.expenses += self.config.activity_costs['bus_excursion']
        self.excursion_list.clear()
        print("Bus excursion has returned.")

class TouristTrip:
    def __init__(self, config):
        self.config = config

    def join(self, guest):
        print(f"Guest {guest.guest_id} is going on a tourist trip.")
        # Simulate trip duration
        trip_duration = random.uniform(0.5, 2.0)
        time.sleep(trip_duration)
        guest.expenses += self.config.activity_costs['tourist_trip']
        print(f"Guest {guest.guest_id} has returned from the tourist trip.")

class Guest(threading.Thread):
    def __init__(self, guest_id, hotel):
        super().__init__()
        self.guest_id = guest_id
        self.hotel = hotel
        self.config = hotel.config  # Access the configurations through the hotel
        self.expenses = 0
        self.nights_stay = random.randint(1, 5)
        self.active = True
        
    def run(self):
        self.hotel.reception.check_in(self)
        while self.nights_stay > 0:
            activity = self.choose_activity()
            activity(self)
            time.sleep(3)  # Time between activities
            self.nights_stay -= 1
        self.hotel.reception.check_out(self)

    def choose_activity(self):
        activities = [self.hotel.pool.use, self.hotel.buffet.dine, self.hotel.gym.use, 
                      self.hotel.bus_excursion.join, self.hotel.tourist_trip.join]
        probabilities = [self.config.activity_probabilities[activity.__name__.split('.')[1]] for activity in activities]
        return random.choices(activities, probabilities, k=1)[0]

    def handle_emergency(self):
        print(f"Emergency for Guest {self.guest_id}!")

class Hotel:
    def __init__(self, num_guests, config):
        self.config = config
        self.pool = Pool(config)
        self.buffet = Buffet(config)
        self.reception = Reception(config)
        self.gym = Gym(config)
        self.bus_excursion = BusExcursion(config)
        self.tourist_trip = TouristTrip(config)
        self.guests = [Guest(guest_id, self) for guest_id in range(num_guests)]
        
    def open_for_business(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.guests)) as executor:
            for guest in self.guests:
                executor.submit(guest.run)

# Start the simulation
if __name__ == "__main__":
    config = HotelConfig()
    hotel = Hotel(50, config)  # Number of guests
    hotel.open_for_business()

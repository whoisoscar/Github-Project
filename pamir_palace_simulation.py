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
            if random.random() < 0.1:
                guest.handle_emergency()
            guest.expenses += self.config.activity_costs['pool']

    def handle_emergency(self):
        print(f"Emergency for Guest {self.guest_id} at the pool!")
        response_time = random.uniform(1, 5)
        if response_time > 3:
            print(f"Guest {self.guest_id} has drowned due to delayed response !")
            self.active = False


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
    def __init__(self, receptionist_id, config):
        self.reception_semaphore = threading.Semaphore(config.receptionists)
        self.receptionist_id = receptionist_id

    def check_in(self, guest):
        with self.reception_semaphore:
            time.sleep(random.uniform(0.5, 1.5))
            print(f"Receptionist {self.receptionist_id} is checking in Guest {guest.guest_id}.")
            print(f"Guest {guest.guest_id} has checked in for {guest.nights_stay} nights.")

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
        self.excursion_list = []
        self.lock = threading.Lock()

    def join(self, guest):
        with self.lock:
            if len(self.excursion_list) < self.config.bus_capacity:
                self.excursion_list.append(guest)
                print(f"Guest {guest.guest_id} has shown interest for the bus excursion, there are currently {len(self.excursion_list)} guests interested, {self.config.bus_capacity - len(self.excursion_list)} missing for the bus to depart.")
                if len(self.excursion_list) == self.config.bus_capacity:
                    self.start()
            else:
                print(f"Guest {guest.guest_id} cannot join now, bus is full.")

    def start(self):
        print(f"Bus excursion starting with guests {[guest.guest_id for guest in self.excursion_list]}.")
        time.sleep(1)  # Simulate excursion duration
        for guest in self.excursion_list:
            guest.expenses += self.config.activity_costs['bus_excursion']
        self.excursion_list.clear()
        print(f"Bus excursion has returned with guests {[guest.guest_id for guest in self.excursion_list]}.")


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
        try:
            self.hotel.reception.check_in(self)
            while self.nights_stay > 0:
                activity = self.choose_activity()
                activity(self)
                self.nights_stay -= 1
                time.sleep(3)  # Time between activities
            self.hotel.reception.check_out(self)
        except Exception as e:
            print(f"Error in Guest {self.guest_id}: {e}")

    def choose_activity(self):

        activities = [self.hotel.pool.use, self.hotel.buffet.dine, self.hotel.gym.use, 
                        self.hotel.bus_excursion.join, self.hotel.tourist_trip.join]
        
        probabilities = [self.config.activity_probabilities['pool'], self.config.activity_probabilities['dine'],
                            self.config.activity_probabilities['gym'], self.config.activity_probabilities['bus_excursion'],
                            self.config.activity_probabilities['tourist_trip']]

        chosen_activity = random.choices(activities, probabilities, k=1)[0]
        return chosen_activity
        
    def check_out(self):
        self.active = False
        self.hotel.reception.check_out(self)
        print(f"Guest {self.guest_id} is checking out. Total expenses: {self.expenses}$")

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
        self.simulate_days_passing()

    def simulate_days_passing(self):
        while any(guest.active for guest in self.guests):
            time.sleep(20)  # Simulate a day passing
            for guest in self.guests:
                guest.nights_stay -= 1
                if guest.nights_stay <= 0 and guest.active:
                    guest.check_out()
# Start the simulation

config = HotelConfig()


if __name__ == "__main__":
    config = HotelConfig()
    hotel = Hotel(50, config)  # Number of guests
    hotel.open_for_business()
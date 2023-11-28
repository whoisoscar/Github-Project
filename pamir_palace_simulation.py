import threading
import time
import queue
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
        self.max_nights_stay = 5
        self.standard_room = 30 #NEW
        self.deluxe_room = 15 #NEW 
        self.premium_room = 5 #NEW

        # Activity costs and probabilities
        self.room_costs = {'premium_room': 300, 'deluxe_room': 250, 'standard_room': 200} #NEW
        self.activity_costs = {'pool_seats': 15, 'pee_fee': 30, 'dine': 20, 'gym': 10, 'bus_excursion': 30, 'tourist_trip': 0}
        self.activity_probabilities = {'pool': 0.25, 'dine': 0.25, 'gym': 0.2, 'bus_excursion': 0.15, 'tourist_trip': 0.15}

class Pool:
    def __init__(self, config):
        self.config = config
        self.pool_seats_semaphore = threading.Semaphore(config.pool_seats)
    
    def use(self, guest):
        if random.random() < 0.3:
            if self.pool_seats_semaphore._value == 0: # Check if the pool is full
                print(f"Guest {guest.guest_id} is waiting to use the pool seats")

            with self.pool_seats_semaphore:
                print(f"Guest {guest.guest_id} is using the pool seat.")
                # Simulate pool usage
                time.sleep(random.uniform(0.5, 2.5))
                guest.expenses += self.config.activity_costs['pool_seats']
        else:
            print(f"Guest {guest.guest_id} is in the pool.")
            if random.random() < 0.05:
                self.handle_emergency(guest)  # Pass the guest object
            if random.random() <0.1:
                self.pee_in_the_pool(guest)

    def handle_emergency(self, guest):
        print(f"Emergency for Guest {guest.guest_id} at the pool!")
        response_time = random.uniform(1, 5)
        if response_time > 4:
            print(f"Guest {guest.guest_id} has drowned due to delayed response!")
            guest.active = False  # Set the guest's active status to False
    
    def pee_in_the_pool(self, guest):
        print(f"Guest {guest.guest_id} peed in the pool.")
        guest.expenses += self.config.activity_costs['pee_fee']

# DO THE RESTAURANT AS THE COFFEE SHOP ASSIGNMENT
class MenuItem:
    def __init__(self, name, price, preparation_time):
        self.name = name
        self.price = price
        self.preparation_time = preparation_time

class Order:
    def __init__(self, guest, items):
        self.guest = guest
        self.items = items

class Chef(threading.Thread):
    def __init__(self, name, order_queue):
        super().__init__(daemon=True) # To allow the program to exit even if these threads are still running
        self.name = name
        self.order_queue = order_queue

    def run(self):
        while True:
            order = self.order_queue.get()
            if order is None:  # Check for the stop signal
                self.order_queue.task_done()
                break
            self.prepare_order(order)
            self.order_queue.task_done()
    
    def prepare_order(self, order):
        for item in order.items:
            print(f"{self.name} is preparing {item.name} for Guest {order.guest.guest_id}.")
            time.sleep(item.preparation_time)
            order.guest.expenses += item.price

class Buffet:
    def __init__(self, config):
        self.config = config
        self.buffet_seats_semaphore = threading.Semaphore(config.buffet_seats)
        self.order_queue = queue.Queue()

        self.menu_items = [
            MenuItem("Steak", 25.0, 0.5),
            MenuItem("Salad", 10.0, 0.4),
            MenuItem("Dessert", 8.0, 0.3),
        ]
        self.chefs = [Chef(f"Chef {i+1}", self.order_queue) for i in range(2)]  # Assume there are two chefs
    
    def open_buffet(self):
        for chef in self.chefs:
            chef.start()

    def close_buffet(self):
        for _ in self.chefs:
            self.order_queue.put(None)  # Send the stop signal to each chef


    def order_menu(self, guest):
        # Here you can implement the logic for a guest to choose items from the menu
        # and create an Order object to put in the order_queue
        chosen_items = random.sample(self.menu_items, k=random.randint(1, len(self.menu_items)))
        order = Order(guest, chosen_items)
        self.order_queue.put(order)
        print(f"Guest {guest.guest_id} has placed an order for {[item.name for item in chosen_items]}.")


    def dine(self, guest):
            with self.buffet_seats_semaphore:
                if random.random() < 0.4:
                    self.order_menu(guest)
                else:
                    print(f"Guest {guest.guest_id} is dining from the buffet.")
                    # Simulate dining
                    time.sleep(random.uniform(1.0, 3.5))
                    guest.expenses += self.config.activity_costs['dine']


class Receptionist:
    def __init__(self, id):
        self.id = id

    def check_in(self, guest):
        time.sleep(random.uniform(0.5, 1.5))
        print(f"Receptionist {self.id} is checking in Guest {guest.guest_id}.")
        print(f"Guest {guest.guest_id} has checked in for {guest.nights_stay} nights.")

    def check_out(self, guest):
        print(f"Receptionist {self.id} is checking out Guest {guest.guest_id}. Total expenses: {guest.expenses}$")

class Reception:
    def __init__(self, config):
        self.receptionists = [Receptionist(i) for i in range(config.receptionists)]
        self.reception_semaphore = threading.Semaphore(config.receptionists)

    def check_in(self, guest):
        with self.reception_semaphore:
            # Find an available receptionist
            available_receptionist = self.receptionists[guest.guest_id % len(self.receptionists)]
            available_receptionist.check_in(guest)

    def check_out(self, guest):
        with self.reception_semaphore:
            # Find the receptionist who checked in the guest (if needed)
            available_receptionist = self.receptionists[guest.guest_id % len(self.receptionists)]
            available_receptionist.check_out(guest)

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
        self.guest_income = random.paretovariate(1.16) * 55000 # $55,000 is the min income of the america middle class 
        # 1.16 is the standard value derived from empirical studies of income and wealth distributions with pareto's dist.
        self.hotel = hotel
        self.config = hotel.config  # Access the configurations through the hotel
        self.expenses = 0
        self.nights_stay = random.randint(1, self.config.max_nights_stay)
        self.active = True
    
    def run(self):
        try:
            self.hotel.reception.check_in(self)
            self.hotel.room_choice(self)
            while self.active:
                activity = self.choose_activity()
                activity(self)
                if self.decrement_night_stay() == 0:
                    self.check_out()
                    break
                time.sleep(3)  # Time between activities
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
    
    def decrement_night_stay(self):
        with threading.Lock():
            if self.nights_stay > 0:
                self.nights_stay -= 1
            return self.nights_stay
        
    def check_out(self):
        self.active = False
        self.hotel.reception.check_out(self)

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
        self.daily_earnings = 0
        self.premium_room_semaphore = threading.Semaphore(config.premium_room)
        self.deluxe_room_semaphore = threading.Semaphore(config.deluxe_room)
        self.standard_room_semaphore = threading.Semaphore(config.standard_room)
    
    def room_choice(self, guest):
        if guest.guest_income <= 150000: 
            with self.premium_room_semaphore:
                print(f"Guest {guest.guest_id} is staying in a premium room.")
                guest.expenses += guest.config.room_costs['premium_room']

        elif guest.guest_income <= 500000:
            with self.deluxe_room_semaphore:
                print(f"Guest {guest.guest_id} is staying in a deluxe room.")
                guest.expenses += guest.config.room_costs['deluxe_room']
        
        elif guest.guest_income > 500000:
            with self.standard_room_semaphore:
                print(f"Guest {guest.guest_id} is staying in a standard room.")
                guest.expenses += guest.config.room_costs['standard_room']
        else:
            print(f"No rooms available for Guest {guest.guest_id}.")
        
        return

    def open_for_business(self):
        self.buffet.open_buffet() # Starts the chefs
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.guests)) as executor:
            for guest in self.guests:
                executor.submit(guest.run)
        self.simulate_days_passing()
        self.buffet.close_buffet()  # Stop the chefs

    def simulate_days_passing(self):
        while any(guest.active for guest in self.guests):
            time.sleep(20)  # Simulate a day passing
            self.daily_earnings = sum(guest.expenses for guest in self.guests if not guest.active)
            self.end_of_day_report()

    def end_of_day_report(self):
        print(f"\nEnd of Day Report:")
        print(f"Number of guests currently staying: {len([guest for guest in self.guests if guest.active])}")
        print(f"Daily earnings: {self.daily_earnings}$")
# Start the simulation

config = HotelConfig()


if __name__ == "__main__":
    config = HotelConfig()
    hotel = Hotel(50, config)  # Number of guests
    hotel.open_for_business()
    
    
    





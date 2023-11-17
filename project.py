# Let's start developing the foundational structure of the code

import threading
import time
import concurrent.futures
import random

# Constants for the number of resources
pool_seats = 15
buffet_seats = 15
receptionists = 2  # Assuming there are two receptionists

# Semaphores for resource management
pool_seats_semaphore = threading.Semaphore(pool_seats)
buffet_semaphore = threading.Semaphore(buffet_seats)
reception_semaphore = threading.Semaphore(receptionists)

# Define the Guest class
class Guest(threading.Thread):
    def __init__(self, guest_id):
        super().__init__()
        self.guest_id = guest_id

    def run(self):
        self.check_in()
        # Randomly select whether to use the pool or dine first
        if random.choice([True, False]):
            self.use_pool()
            self.dine()
        else:
            self.dine()
            self.use_pool()
        self.check_out()

    def check_in(self):
        print(f"Guest {self.guest_id} is trying to check in.")
        with reception_semaphore:
            # Simulate the time taken for checking in
            time.sleep(random.uniform(0.5, 2.0))
            print(f"Guest {self.guest_id} has checked in.")

    def use_pool(self):
        print(f"Guest {self.guest_id} is trying to use the pool.")
        with pool_seats_semaphore:
            # Simulate the time spent at the pool
            time.sleep(random.uniform(0.5, 3.0))
            print(f"Guest {self.guest_id} is done using the pool.")

    def dine(self):
        print(f"Guest {self.guest_id} is trying to dine.")
        with buffet_semaphore:
            # Simulate the time taken to dine
            time.sleep(random.uniform(1.0, 3.5))
            print(f"Guest {self.guest_id} has finished dining.")

    def check_out(self):
        print(f"Guest {self.guest_id} is trying to check out.")
        with reception_semaphore:
            # Simulate the time taken for checking out
            time.sleep(random.uniform(0.5, 2.0))
            print(f"Guest {self.guest_id} has checked out.")

# Define the Hotel class
class Hotel:
    def __init__(self, num_guests):
        self.guests = [Guest(guest_id) for guest_id in range(num_guests)]

    def open_for_business(self):
        print("Hotel is now open.")
        for guest in self.guests:
            guest.start()
        for guest in self.guests:
            guest.join()
        print("Hotel is now closed.")

# Start the simulation
if __name__ == "__main__":
    num_guests = 50  # Let's say we have 50 guests for this simulation
    hotel = Hotel(num_guests)
    hotel.open_for_business()


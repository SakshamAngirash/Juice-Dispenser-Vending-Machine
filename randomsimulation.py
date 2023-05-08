import simpy
import random

class VendingMachine:
    def __init__(self, env, items_capacity, repair_time):
        self.env = env
        self.machine = simpy.Resource(env, capacity=1)
        self.items_available = {  # Dictionary to store available items and quantities
            'Fanta': {'quantity': items_capacity, 'price': 20},
            'Coke': {'quantity': items_capacity, 'price': 20},
            'Sprite': {'quantity': items_capacity, 'price': 20},
            # Add more items here with their respective quantities and prices
        }
        self.is_damaged = False
        self.repair_time = repair_time
        self.earnings = 0.0

    def vend_item(self, item):
        yield self.env.timeout(1)  # Time taken to dispense item
        self.items_available[item]['quantity'] -= 1
        self.earnings += self.items_available[item]['price']

    def refill_items(self, refill_time, refill_amount, item):
        yield self.env.timeout(refill_time)  # Time taken to refill items
        self.items_available[item]['quantity'] += refill_amount

    def damage_machine(self):
        self.is_damaged = True
        print(f'Vending machine is damaged at {self.env.now}')

    def repair_machine(self):
        yield self.env.timeout(self.repair_time)
        self.is_damaged = False
        print(f'Vending machine is repaired at {self.env.now}')

def customer(env, name, vending_machine):
    print(f'{name} arrives at the vending machine at {env.now}')

    if vending_machine.is_damaged:
        print(f'{name} finds the vending machine is damaged at {env.now}')
        yield env.process(vending_machine.repair_machine())
        print(f'{name} waits until the vending machine is repaired at {env.now}')

    with vending_machine.machine.request() as request:
        yield request

        item = random.choice(list(vending_machine.items_available.keys()))
        if vending_machine.items_available[item]['quantity'] > 0:
            print(f'{name} purchases {item} at {env.now}')

            yield env.process(vending_machine.vend_item(item))

            print(f'{name} receives {item} at {env.now}')
        else:
            print(f'{name} finds no {item} available at {env.now}')

        print(f'{name} leaves the vending machine at {env.now}')

def refill(env, vending_machine, refill_interval, refill_time, refill_amount, item):
    while True:
        yield env.timeout(refill_interval)  # Refill interval

        print(f'Refilling {item} at {env.now}')
        yield env.process(vending_machine.refill_items(refill_time, refill_amount, item))
        print(f'{item} refilled at {env.now}')

def simulate_vending_machine():
    # Get user inputs
    items_capacity = int(input("Enter the initial number of items in the vending machine: "))
    customer_count = int(input("Enter the number of customers: "))
    refill_interval = int(input("Enter the refill interval (in time units): "))
    refill_time = int(input("Enter the time taken to refill items (in time units): "))
    refill_amount = int(input("Enter the amount of items refilled during each refill: "))
    repair_time = int(input("Enter the time taken to repair the vending machine (in time units): "))

    env = simpy.Environment()
    vending_machine = VendingMachine(env, items_capacity, repair_time)

    # Create customers
    for i in range(customer_count):
        env.process(customer(env, f'Customer {i+1}', vending_machine))

    # Randomly damage the vending machine
    def damage_machine(env):
        while True:
            yield env.timeout(random.randint(10, 20))
            vending_machine.damage_machine()

    env.process(damage_machine(env))

    # Run the simulation
    for item in vending_machine.items_available.keys():
        env.process(refill(env, vending_machine, refill_interval, refill_time, refill_amount, item))

    simulation_duration = max(refill_interval * (customer_count + 1), refill_interval + refill_time) + 5
    env.run(until=simulation_duration)

    # Calculate earnings
    total_earnings = vending_machine.earnings
    print(f'Total earnings: {total_earnings}')

if __name__ == "__main__":
    simulate_vending_machine()

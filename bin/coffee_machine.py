import multiprocessing
from functools import partial
from multiprocessing import Manager, Pool
from time import sleep
from .coffee_machine_constants import *


def _process_order(lock, ret, items, given_order):
    """
    Process given_order with respect to quantity defined in items
    First we check if all the ingredients required to make the drink available or not, if yes, we process the order
    whilst updating the quantity in items, else we print if the item is unavailable or low in quantity.
    NOTE : Time to prepare a beverage is assumed the same for all cases.
    :param items: Structure containing total available quantity of all items in machine
    :param given_order: The current order to be processed with required quantities
    :return: None
    """
    beverage_name, beverage = given_order[0], given_order[1]
    build_order = True
    failed_ingredient = ""
    unavailable_ingredient = ""
    lock.acquire()
    for ingredient in beverage:
        required = beverage[ingredient]
        if ingredient in items:
            available = items[ingredient]
        else:
            build_order = False
            unavailable_ingredient = ingredient
            break
        if required > available:
            build_order = False
            if not failed_ingredient:
                failed_ingredient = ingredient
    if build_order:
        for ingredient in beverage:
            required = beverage[ingredient]
            items[ingredient] -= required
        #sleep(2)
        ret.append(beverage_name + PREPARED)
    else:
        if unavailable_ingredient:
            ret.append(beverage_name + UNAVAILABLE_INGREDIENT + unavailable_ingredient + UNAVAILABLE)
        else:
            ret.append(beverage_name + FAILED_INGREDIENT + failed_ingredient + INSUFFICIENT)
    lock.release()


class CoffeeMachine:
    """
    Class to simulate a Coffee Machine
    """
    def __init__(self):
        """
        Constructor for class variables
        """
        self.outlets = 0  # Number of outlets
        self.items = {}  # Items quantity stored in dict
        self.min_quantity = {}  # Min quantity of items
        self.manager = Manager()  # SyncManager between subprocesses
        self.lock = self.manager.Lock()  # Lock for critical section

    def _update_items(self, new_items):
        """
        Updates self.items to new_items after some drinks are prepared
        :param new_items: Modified items after some drinks are prepared
        :return: None
        """
        self.items = new_items

    def _fill_items(self, n, total_items):
        """
        Fills machine with initial quantity of all items
        :param n: Number of outlets
        :param total_items: Initial Quantity of all items
        :return: None
        """
        self.items = total_items
        self.outlets = n
        for item in self.items:
            self.min_quantity[item] = int(0.2 * self.items[item])  # 20% of initial quantity to be threshold

    def _process_order_queue(self, current_orders):
        """
        Process all the orders in current_orders parallely
        :param current_orders: The orders up to number of outlets
        :return: ret : List containing print statements of orders prepared or failed
        """
        process_queue = []
        self.lock.acquire()
        total_items = self.manager.dict(self.items)
        ret = self.manager.list()
        lock = self.manager.Lock()
        # We process orders in parallel to the degree of outlets or max cpus (whichever is lower) in the machine
        # assuming machine have multiple cpus for multiprocessing
        pool = Pool(min(self.outlets, multiprocessing.cpu_count()-1))
        func = partial(_process_order, lock, ret, total_items)
        pool.map(func, current_orders)
        pool.close()
        # for i in range(len(current_orders)):
        #     parallel_order = Process(target=_process_order, args=(ret, total_items, current_orders[i],))
        #     parallel_order.start()
        #     process_queue.append(parallel_order)
        # for proc in process_queue:
        #     proc.join()
        self._update_items(total_items)
        self.lock.release()
        return ret

    def refill_items(self, data):
        """
        Refills items in the machine
        :param data: New quantity of items to be filled
        :return: None
        """
        self.lock.acquire()
        for item in data:
            self.items[item] += data[item]
        self.lock.release()

    def all_item_indicator(self):
        """
        Indicates items which are low in quantity. Also exposed to know items in low quantity anytime
        :return: Copy of all items with their quantity in the machine
        """
        self.lock.acquire()
        items = self.items.copy()
        self.lock.release()
        return items

    def low_item_indicator(self):
        """
        Indicates items which are low in quantity. Also exposed to know items in low quantity anytime
        :return: None
        """
        self.lock.acquire()
        low_items = []
        for item in self.items:
            if self.items[item] <= self.min_quantity[item]:
                low_items.append(item)
        self.lock.release()
        return low_items

    def process_data(self, data):
        """
        Exposed function which initiates the class variables and process orders
        :param data: Complete json structure having details of machine with no of outlets, quantity of items
        and orders
        :return: result : List containing items either prepared or failed
        """
        if not self.items:
            self._fill_items(data[MACHINE][OUT][OUTLETS],
                             data[MACHINE][TOTAL_ITEMS])
        else:
            self.refill_items(data[MACHINE][TOTAL_ITEMS])
        ordered_beverages = data[MACHINE][BEVERAGES]
        ordered_beverages = list(ordered_beverages.items())
        result = self._process_order_queue(ordered_beverages)
        return result

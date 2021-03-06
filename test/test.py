import json
import os
import sys
import unittest

from bin.coffee_machine import CoffeeMachine
from bin.coffee_machine_constants import *

BLACK_TEA = "black_tea"
HOT_TEA = "hot_tea"
BLACK_TEA_IS_PREPARED = "black_tea is prepared"
TEST_RESULT_1 = ['hot_coffee is prepared', 'hot_tea is prepared',
                 'green_tea cannot be prepared because green_mixture is not available',
                 'black_tea cannot be prepared because item hot_water is not sufficient']
TEST_RESULT_2 = ['hot_tea is prepared',
                 'black_tea is prepared',
                 'green_tea cannot be prepared because green_mixture is not available',
                 'hot_coffee cannot be prepared because item hot_water is not sufficient']
TEST_RESULT_3 = ['hot_coffee is prepared',
                 'black_tea is prepared',
                 'green_tea cannot be prepared because green_mixture is not available',
                 'hot_tea cannot be prepared because item hot_water is not sufficient']
TEST_RESULT_4 = ['hot_tea is prepared', 'hot_coffee is prepared',
                 'green_tea cannot be prepared because green_mixture is not available', 'black_tea is prepared']
TEST_RESULT_5 = ['hot_water']
TEST_RESULT_6 = ['hot_milk']
TEST_RESULT_1.sort()
TEST_RESULT_2.sort()
TEST_RESULT_3.sort()
TEST_RESULT_4.sort()
TEST_RESULT = [TEST_RESULT_1, TEST_RESULT_2, TEST_RESULT_3]


def load_json_file(filename):
    """
    Loads input data from sample test file
    :param filename: Name of input file # we are taking items.json as the input file
    :return: json data read from the file
    """
    with open(os.path.join(sys.path[0], filename), "r") as f:
        json_data = json.load(f)
    return json_data


class CoffeeTest(unittest.TestCase):
    """
    Functional test cases for Coffee Machine
    """
    coffee_machine = CoffeeMachine()
    data = load_json_file("items.json")
    success_order = []

    def test_1_init_machine(self):
        """
        Initiates the coffee machine with total items quantity and process orders
        in the machine
        :return: Test case success if the machine works as desired else Assertion Exception and test fails
        """
        res = self.coffee_machine.process_data(self.data)
        res.sort()
        if BLACK_TEA_IS_PREPARED in res:
            self.success_order.append(BLACK_TEA)
        self.assertIn(list(res), TEST_RESULT)
        print("#############################")
        print(res)
        print("test_1_init_machine : SUCCESS")
        print("#############################")

    def test_2_low_item_indication(self):
        """
        Check which item are low after orders processed in test_1_init_machine.
        :return:
        """
        res = self.coffee_machine.low_item_indicator()
        if BLACK_TEA in self.success_order:
            self.assertEqual(list(res), TEST_RESULT_5)  # IF black tea is prepared successfully then hot_water should
            # be low in quantity
        else:
            self.assertEqual(list(res), TEST_RESULT_6)  # If hot_coffee is prepared then hot_milk should be low in
            # quantity
        print("############################")
        print(res)
        print("test_2_low_item_indication : SUCCESS")
        print("#############################")

    def test_3_refill_machine(self):
        """
        Refills the machine and checks if the total item values has been updated successfully
        :return: Test case success if the values are updated correctly else Assertion Exception and test fails
        """
        refill_items = self.data[MACHINE][TOTAL_ITEMS]
        initial_quantity = self.coffee_machine.all_item_indicator()
        self.coffee_machine.refill_items(refill_items)
        final_quantity = self.coffee_machine.all_item_indicator()
        # print(refill_items)
        # print(initial_quantity)
        # print(final_quantity)
        for item in refill_items:
            self.assertEqual(refill_items[item], final_quantity[item] - initial_quantity[item])
        print("############################")
        print("test_3_refill_machine : SUCCESS")
        print("#############################")

    def test_4_after_refill(self):
        """
        Checks if the orders can be processed or not after refilling the machine
        :return: None
        """
        res = self.coffee_machine.process_data(self.data)
        res.sort()
        self.assertEqual(list(res), TEST_RESULT_4)
        print("############################")
        print(res)
        print("test_4_after_refill : SUCCESS")
        print("#############################")


if __name__ == '__main__':
    unittest.main()

import enum
import random
from abc import ABC


class Input(ABC):
    def get_input_data(self):
        pass


class CLI(Input):
    def get_input_data(self):
        return input()


class Status(enum.Enum):
    ok = 1
    error = 2
    exit = 3
    log_out = 4
    create = 5


class MenuItems:
    def __init__(self, number, text):
        self.number = number
        self.text = text

    def get_number(self):
        return self.number

    def get_text(self):
        return self.text


class Banking:
    iin_number = 400000
    checksum_number = 9
    main_menu_dict = {"1": "Create an account", "2": "Log into account", "0": "Exit"}
    account_menu_dict = {"1": "Balance", "2": "Log out", "0": "Exit"}

    def __init__(self):
        self.main_menu = []
        self.account_menu = []
        self.tmp_account = None
        self.accounts = []

    @staticmethod
    def create_menu(menu_dict: dict):
        menu = []
        for digit, text in menu_dict.items():
            menu.append(MenuItems(digit, text))
        return menu

    @staticmethod
    def print_menu(menu: list):
        for item in menu:
            print("{}. {}".format(item.get_number(), item.get_text()))

    def print_main_menu(self):
        self.main_menu = self.create_menu(self.main_menu_dict)
        return self.print_menu(self.main_menu)

    def select_main_menu_action(self, input_value: str):
        main_menu_option = {"1": lambda: self.create_account(),
                            "2": lambda: self.log_into_account(),
                            "0": lambda: self.do_exit()}
        for item in self.main_menu:
            if item.get_number() == input_value:
                return main_menu_option.get(input_value)()
        return Status.error, None

    @staticmethod
    def do_exit():
        return Status.exit, "Bye!"

    def create_card_number(self):
        customer_account_number = random.randint(000000000, 999999999)
        card_number = str(self.iin_number) + str(customer_account_number) + str(self.checksum_number)
        if self.accounts:
            for account in self.accounts:
                if card_number == account.get_card_number():
                    return self.create_card_number()
        return card_number

    @staticmethod
    def create_pin():
        pin = str(random.randint(1000, 9999))
        return pin

    def create_account(self):
        card_number = self.create_card_number()
        pin = self.create_pin()
        print("\nYour card has been created")
        print("Your card number:")
        print(card_number)
        print("Your card PIN:")
        print(pin)
        print()
        self.accounts.append(Account(card_number, pin))
        return Status.create, None

    @staticmethod
    def print_message_to_enter_card_number():
        print()
        print("Enter your card number:")

    @staticmethod
    def print_message_to_enter_pin():
        print("Enter your PIN:")

    def log_into_account(self):
        self.print_message_to_enter_card_number()
        card_number_input = CLI().get_input_data()
        self.print_message_to_enter_pin()
        pin_input = CLI().get_input_data()
        for account in self.accounts:
            if account.get_card_number() == card_number_input and account.get_pin() == pin_input:
                self.tmp_account = account
        if self.tmp_account:
            return Status.ok, "\nYou have successfully logged in!\n"
        return Status.error, "\nWrong card number or PIN!\n"

    def print_account_menu(self):
        self.account_menu = self.create_menu(self.account_menu_dict)
        return self.print_menu(self.account_menu)

    def select_account_menu_action(self, input_value: str):
        account_menu_option = {"1": lambda: self.get_balance(),
                               "2": lambda: self.log_out(),
                               "0": lambda: self.do_exit(), }
        for item in self.main_menu:
            if item.get_number() == input_value:
                return account_menu_option.get(input_value)()
        return Status.error, None

    def get_balance(self):
        return Status.ok, "\nBalance: {}\n".format(str(self.tmp_account.get_balance()))

    def log_out(self):
        self.tmp_account = None
        return Status.log_out, "\nYou have successfully logged out!\n"


class Account:
    def __init__(self, card_number: str, pin: str):
        self.card_number = card_number
        self.pin = pin
        self.balance = 0

    def get_balance(self):
        return self.balance

    def get_card_number(self):
        return self.card_number

    def get_pin(self):
        return self.pin

    def update_balance(self, value:int):
        self.balance += value


def main():
    bank = Banking()
    status = Status.error
    while status is not Status.exit:
        bank.print_main_menu()
        main_menu_selected_number = input()
        status, value = bank.select_main_menu_action(main_menu_selected_number)
        if value:
            print(value)
        if status is Status.exit:
            break
        elif status is Status.error or status is Status.create:
            continue
        else:
            status_account_menu = None
            while status_account_menu is not Status.exit:
                bank.print_account_menu()
                account_menu_selected_number = input()
                bank.print_account_menu()
                status_account_menu, value_account_menu = bank.select_account_menu_action(account_menu_selected_number)
                if value_account_menu:
                    print(value_account_menu)
                if status_account_menu == Status.ok:
                    continue
                elif status_account_menu == Status.log_out:
                    break
                if status_account_menu == Status.exit:
                    status = Status.exit
                    break


main()

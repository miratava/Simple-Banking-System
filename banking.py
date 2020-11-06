import enum
import random
from abc import ABC
import sqlite3


class Input(ABC):
    def get_input_data(self):
        pass


class CLI(Input):
    @property
    def get_input_data(self):
        return input()

    @staticmethod
    def get_card_number():
        return input("\nEnter your card number:\n")

    @staticmethod
    def get_pin():
        return input("Enter your PIN:\n")

    @staticmethod
    def get_income():
        return input("\nEnter income:\n")

    @staticmethod
    def get_card_number_for_transfer():
        return input("\nTransfer\nEnter card number:\n")

    @staticmethod
    def get_sum_for_transfer():
        return input("Enter how much money you want to transfer:\n")


class Status(str, enum.Enum):
    once_more = "once more"
    log_in = "login"
    exit = "exit"
    log_out = "logout"
    created = "created"
    success = "success"
    closed = "closed"
    added = "added"
    ok = "ok"
    error = "error"
    wrong = "wrong"
    not_enough = "not enough"
    to_the_same_account = "same"
    mistake = "mistake"
    not_exist = "not_exist"


class MenuItem:
    def __init__(self, number, text):
        self.number = number
        self.text = text

    def get_number(self):
        return self.number

    def get_text(self):
        return self.text


class Banking:
    iin_number = "400000"
    main_menu_dict = {"1": "Create an account", "2": "Log into account", "0": "Exit"}
    account_menu_dict = {"1": "Balance", "2": "Add income", "3": "Do transfer",
                         "4": "Close account", "5": "Log out", "0": "Exit"}
    messages = {Status.exit: "Bye!",
                Status.created: "Your card has been created",
                Status.not_enough: "Not enough money!",
                Status.to_the_same_account: "You can't transfer money to the same account!",
                Status.mistake: "Probably you made a mistake in the card number.\nPlease try again!",
                Status.not_exist: "Such a card does not exist.",
                Status.success: "Success!",
                Status.log_in: "You have successfully logged in!",
                Status.closed: "The account has been closed!",
                Status.wrong: "Wrong card number or PIN!",
                Status.added: "Income was added!",
                Status.log_out: "You have successfully logged out!"
                }

    def __init__(self):
        self.main_menu = []
        self.account_menu = []
        self.account_number = 0
        self.storage = Storage()

    @staticmethod
    def create_menu(menu_dict: dict):
        menu = []
        for digit, text in menu_dict.items():
            menu.append(MenuItem(digit, text))
        return menu

    @staticmethod
    def print_menu(menu: list):
        for item in menu:
            print("{}. {}".format(item.get_number(), item.get_text()))

    def print_main_menu(self):
        self.main_menu = self.create_menu(self.main_menu_dict)
        return self.print_menu(self.main_menu)

    def select_main_menu_action(self):
        input_value = CLI().get_input_data
        main_menu_option = {"1": lambda: self.create_account(),
                            "2": lambda: self.log_into_account(),
                            "0": lambda: self.do_exit()}
        for digit, func in main_menu_option.items():
            if digit == input_value:
                return func()
        return Status.error, None

    def do_exit(self):
        self.storage.close_db()
        return Status.exit, self.messages.get(Status.exit)

    @staticmethod
    def calculate_checksum_number(card_number: str):
        card_digits = [int(x) for x in card_number]
        card_digits_after_step_1 = []
        for i in range(len(card_digits)):
            i += 1
            if i % 2 == 1:
                card_digits_after_step_1.append(2 * card_digits[i - 1])
            else:
                card_digits_after_step_1.append(card_digits[i - 1])
        card_digits_after_step_2 = []
        for each in card_digits_after_step_1:
            if each > 9:
                card_digits_after_step_2.append(each - 9)
            else:
                card_digits_after_step_2.append(each)
        total = sum(card_digits_after_step_2)
        checksum_number = 0
        if total % 10 != 0:
            checksum_number = 10 - total % 10
        return str(checksum_number)

    def create_card_number(self):
        customer_account_number = self.convert_number_to_needed_string_length(random.randint(0, 999999999), 9)
        checksum_number = self.calculate_checksum_number(self.iin_number + customer_account_number)
        card_number = self.iin_number + customer_account_number + checksum_number
        if card_number not in self.storage.select_card_numbers():
            return card_number
        return self.create_card_number()

    def create_pin(self):
        pin_number = random.randint(0, 9999)
        return self.convert_number_to_needed_string_length(pin_number, 4)

    @staticmethod
    def convert_number_to_needed_string_length(number: int, length: int):
        zero = "0"
        return (length - len(str(number))) * zero + str(number)

    def create_account(self):
        self.account_number += 1
        card_number = self.create_card_number()
        pin = self.create_pin()
        balance = 0
        account = Account((self.account_number, card_number, pin, balance))
        self.storage.insert_data_to_card_table(account)
        print("\n" + self.messages.get(Status.created))
        self.print_card_number(card_number)
        self.print_pin(pin)
        return Status.ok, None

    @staticmethod
    def print_card_number(number):
        print("Your card number:")
        print(number)

    @staticmethod
    def print_pin(pin):
        print("Your card PIN:")
        print(pin + "\n")

    def log_into_account(self):
        card_number_input = CLI().get_card_number()
        pin_input = CLI().get_pin()
        account = self.storage.login_into_account((card_number_input, pin_input))
        if account is None:
            return Status.error, self.messages.get(Status.wrong)
        return Status.log_in, self.messages.get(Status.log_in)

    def print_account_menu(self):
        self.account_menu = self.create_menu(self.account_menu_dict)
        return self.print_menu(self.account_menu)

    def select_account_menu_action(self):
        input_value = CLI().get_input_data
        account_menu_option = {"1": lambda: self.get_balance(),
                               "2": lambda: self.add_income(),
                               "3": lambda: self.do_transfer(),
                               "4": lambda: self.close_account(),
                               "5": lambda: self.log_out(),
                               "0": lambda: self.do_exit()
                               }
        for digit, func in account_menu_option.items():
            if digit == input_value:
                return func()
        return Status.error, None

    def add_income(self):
        income = CLI().get_income()
        self.storage.account.update_balance(int(income))
        self.storage.change_balance(self.storage.account.get_card_number(), income)
        return Status.ok, self.messages.get(Status.added)

    def get_balance(self):
        return Status.ok, "\nBalance: {}".format(str(self.storage.account.get_balance()))

    def log_out(self):
        self.storage.account = None
        return Status.log_out, "\n" + self.messages.get(Status.log_out)

    def validate_card_number_to_be_the_same(self, number):
        if number == self.storage.account.get_card_number():
            return Status.error, self.messages.get(Status.to_the_same_account)
        return Status.ok, None

    def validate_checksum_number(self, number):
        checksum_number = self.calculate_checksum_number(number[:-1])
        if checksum_number != number[-1]:
            return Status.once_more, self.messages.get(Status.mistake)
        return Status.ok, None

    def validate_card_for_existing(self, number):
        if number in self.storage.select_card_numbers():
            return Status.ok, None
        return Status.once_more, self.messages.get(Status.not_exist)

    def do_transfer(self):
        number_for_transfer = CLI().get_card_number_for_transfer()
        status, message = self.validate_card_number(number_for_transfer)
        if status is Status.ok:
            how_much_money = int(CLI().get_sum_for_transfer())
            if self.storage.account.get_balance() - int(how_much_money) < 0:
                return Status.once_more, self.messages.get(Status.not_enough)
            else:
                self.storage.do_transfer(number_for_transfer, how_much_money)
                return Status.ok, self.messages.get(Status.success)
        return status, message

    def validate_card_number(self, number):
        validate_same_status, validate_same_message = self.validate_card_number_to_be_the_same(number)
        if validate_same_status is Status.ok:
            checksum_status, checksum_message = self.validate_checksum_number(number)
            if checksum_status is Status.ok:
                existing_status, existing_message = self.validate_card_for_existing(number)
                if existing_status is Status.ok:
                    return Status.ok, None
                return existing_status, existing_message
            return checksum_status, checksum_message
        return validate_same_status, validate_same_message

    def close_account(self):
        self.storage.delete_account()
        return Status.closed, "\n" + self.messages.get(Status.closed)


class DB:
    def __init__(self):
        self.connection = sqlite3.connect('card.s3db')
        self.cursor = self.connection.cursor()

    def commit(self):
        return self.connection.commit()

    def execute_query(self, sql, *args):
        return self.cursor.execute(sql, *args)

    def create_table_card(self):
        sql = '''CREATE TABLE card(
                                id INTEGER, 
                                number TEXT UNIQUE, 
                                pin TEXT, 
                                balance INTEGER DEFAULT 0)'''
        self.cursor.execute(sql)
        self.connection.commit()

    def delete_table(self):
        drop_query = 'DROP TABLE card'
        try:
            self.cursor.execute(drop_query)
        except NameError:
            pass
        self.connection.commit()

    def return_one_row(self):
        return self.cursor.fetchone()

    def return_all_results(self):
        return self.cursor.fetchall()


class Storage:
    def __init__(self):
        self.db = DB()
        self.delete_table()
        self.create_table_card()
        self.account = None

    def create_table_card(self):
        self.db.create_table_card()

    def select_card_numbers(self):
        sql = 'SELECT number FROM card'
        self.db.execute_query(sql)
        return [x[0] for x in self.db.return_all_results()]

    def insert_data_to_card_table(self, account):
        sql = 'INSERT INTO card (id, number, pin, balance) VALUES (?, ?, ?, ?)'
        data = account.get_account_number(), account.get_card_number(), account.get_pin(), account.get_balance()
        self.db.execute_query(sql, data)
        self.db.commit()

    def select_balance(self):
        number = self.account.get_card_number()
        sql = '''SELECT balance
                 FROM card
                 WHERE number=?'''
        self.db.execute_query(sql, (number,))
        self.account.update_balance(self.db.return_one_row()[0])

    def change_balance(self, number, value):
        sql = '''UPDATE card
                 SET balance = ? + balance
                 WHERE number = ?;'''
        self.db.execute_query(sql, (value, number))
        self.db.commit()

    def do_transfer(self, number, value):
        self.change_balance(self.account.get_card_number(), value * (-1))
        self.change_balance(number, value)
        self.select_balance()

    def select_account(self, *args):
        sql = '''SELECT * 
                 FROM card 
                 WHERE number = ?
                 AND pin = ?'''
        self.db.execute_query(sql, *args)
        one_row = self.db.return_one_row()
        if one_row:
            return one_row
        return None

    def login_into_account(self, input_data):
        data = self.select_account(input_data)
        if data is None:
            return None
        else:
            self.account = Account(data)
            return self.account

    def delete_table(self):
        self.db.delete_table()

    def delete_account(self):
        sql = 'DELETE FROM card WHERE number=?'
        number = self.account.get_card_number()
        self.db.execute_query(sql, (number,))
        self.db.commit()
        return Status.ok

    def close_db(self):
        self.db.connection.close()


class Account:
    def __init__(self, data: tuple):
        self.account_number, self.card_number, self.pin, self.balance = data

    def get_balance(self):
        return self.balance

    def get_card_number(self):
        return self.card_number

    def get_pin(self):
        return self.pin

    def update_balance(self, value: int):
        self.balance += value

    def get_account_number(self):
        return self.account_number


def main():
    bank = Banking()
    status = Status.ok
    while status is not Status.exit:
        bank.print_main_menu()
        status, value = bank.select_main_menu_action()
        if value:
            print("\n" + value + "\n")
        if status is Status.error:
            continue
        elif status is Status.log_in:
            status_account_menu = None
            while status_account_menu is not Status.exit:
                bank.print_account_menu()
                status_account_menu, value_account_menu = bank.select_account_menu_action()
                if value_account_menu:
                    print(value_account_menu + "\n")
                if status_account_menu is Status.ok or status_account_menu is Status.once_more:
                    continue
                elif status_account_menu is Status.exit:
                    status = Status.exit
                    break
                else:
                    break


main()

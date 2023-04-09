import sys
from collections import UserDict

tip = ("""
List of available commands:
    add <name> | add <name> <phone>         - Add new contact (<phone> : 10 or 11 digits)
    change <name> <old phone> <new phone>   - Change phone number (10 or 11 digits) for existing contact name
    del <name>                              - Delete existing contact
    del <name> <phone>                      - Delete existing phone number for existing contact
    phone <name>                            - View phone number(s) for existing contact name
    show all                                - View all contacts
    good bye | close | exit | <ENTER>       - Close program
""")


class Field:
    def __init__(self, str_: str):
        self.value = str_

    def __str__(self):
        return self.value


class Name(Field):
    ...


class Phone(Field):
    ...


class Record:
    def __init__(self, name: Name, phone: Phone = None):
        self.name = name
        self.phones = []
        if phone:
            self.add_phone(phone)

    def _is_true(self, phone: Phone) -> bool:
        existing_phones = [p.value for p in self.phones]
        return True if self.phones and phone.value in existing_phones else False

    def add_phone(self, phone: Phone):
        if self._is_true(phone):
            raise ValueError(f'Phone {phone} is already exists')
        self.phones.append(phone)
        return self.phones

    def del_phone(self, phone: Phone):
        if self._is_true(phone):
            for i, p in enumerate(self.phones):
                if p.value == phone.value:
                    self.phones.pop(i)
                    return self.phones
        raise ValueError(f'Phone {phone} does not exist')

    def change_phone(self, old_phone: Phone, new_phone: Phone):
        if self._is_true(new_phone):
            raise ValueError(f'Phone {new_phone} already exist in contact')
        if self._is_true(old_phone):
            self.del_phone(old_phone)
            self.add_phone(new_phone)
            return self.phones
        raise ValueError(f'Phone {old_phone} does not exist')

    def __str__(self):
        return self.phones

    def __repr__(self):
        return str(self)


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def view_all(self):
        if self.data:
            return ''.join([f'{k} : {"; ".join([p.value for p in v.phones])}\n' for k, v in self.data.items()])
        return 'Your contact list is EMPTY'

    def del_record(self, record: Record):
        del self.data[record.name.value]


def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return f'Error: {type(e).__name__}. Message: {e}'

    return wrapper


@handle_errors
def command_parse(prompt: str):
    global new_phone, name_1, old_phone, name_2
    commands = ('add', 'change', 'del', 'show', 'phone')
    prompt_list = prompt.strip().replace(',', '').replace('.', '').split()
    command = prompt_list.pop(0)
    if not prompt_list or command not in commands:
        raise ValueError('Check your command')

    name_0 = Name(' '.join(list(map(lambda i: i.capitalize(), prompt_list))))
    try:
        new_phone = Phone(prompt_list[-1])
        name_1 = Name(' '.join(list(map(lambda i: i.capitalize(), prompt_list[:-1]))))
        old_phone = Phone(prompt_list[-2])
        name_2 = Name(' '.join(list(map(lambda i: i.capitalize(), prompt_list[:-2]))))
    except IndexError:
        pass

    if command == 'add':
        if len(prompt_list) >= 2 \
                and prompt_list[-1].isdigit() \
                and len(prompt_list[-1]) in (10, 11):
            if new_phone:
                return add(name_1, new_phone)
        return add(name_0)

    elif command == 'change':
        if len(prompt_list) >= 3 \
                and prompt_list[-1].isdigit() \
                and prompt_list[-2].isdigit() \
                and len(prompt_list[-1]) in (10, 11) \
                and len(prompt_list[-2]) in (10, 11):
            return change(name_2, old_phone, new_phone)

    elif command == 'del':
        if len(prompt_list) >= 2 \
                and prompt_list[-1].isdigit() \
                and len(prompt_list[-1]) in (10, 11):
            return delete_phone(name_1, new_phone)
        return delete_contact(name_0)

    elif command == 'show':
        if len(prompt_list) == 1 and prompt_list[-1] == 'all':
            return ab.view_all()

    elif command == 'phone':
        if len(prompt_list) >= 1:
            return view_phones_by_name(name_0)

    raise ValueError('Check your command')


def add(name: Name, phone: Phone = None):
    keys = ab.get(name.value)
    if not phone:
        if not keys:
            rec = Record(name)
            ab.add_record(rec)
            return f'Contact {name} created'
        return f'Contact {name} already exist'
    if keys:
        keys.add_phone(phone)
        return f'Phone {phone} added to record {name}'
    ab.add_record(Record(name, phone))
    return f'Contact {name} created with phone {phone}'


def view_phones_by_name(name: Name):
    keys = ab.get(name.value)
    if keys:
        return ''.join([f'{k} : {"; ".join([p.value for p in v.phones])}' for k, v in ab.items()
                        if k == name.value])
    return f'Contact {name} doesn\'t exist'


def change(name: Name, old_phone: Phone, new_phone: Phone):
    keys = ab.get(name.value)
    if keys:
        keys.change_phone(old_phone, new_phone)
        return f'Phone {old_phone} was changed to {new_phone} for {name}'
    return f'Contact {name} doesn\'t exist'


def delete_phone(name: Name, phone: Phone):
    keys = ab.get(name.value)
    if keys:
        keys.del_phone(phone)
        return f'Phone {phone} deleted for record {name}'
    return f'Contact {name} doesn\'t exist'


def delete_contact(name: Name):
    keys = ab.get(name.value)
    if keys:
        confirm = input('Are you sure? (Y/n)\n>>> ').lower()
        if confirm not in 'yn':
            raise ValueError('Check your command. Only "Y" or "n"')
        if confirm == 'y' or not confirm:
            rec = Record(name)
            ab.del_record(rec)
            return f'Contact {name} was completely removed'
        return 'Aborted'
    return f'Contact {name} doesn\'t exist'


def main():
    print(tip)
    exits = ('exit', 'good bye', 'close')
    while True:
        try:
            choice = input('>>> ').lower()
            if choice in exits or not choice:
                raise KeyboardInterrupt
            else:
                print(command_parse(choice))
        except KeyboardInterrupt:
            print('Bye')
            sys.exit(0)


if __name__ == '__main__':
    ab = AddressBook()
    main()

from binarytree import BinarySearchTree
storage = BinarySearchTree
# storage = dict


class DatabaseException(RuntimeError):
    pass


class Database(object):
    DEFAULT_VALUE = None

    def __init__(self):
        self._store = storage()
        self._count = storage()
        self._transactions = []

    def set(self, name, value):
        un_set = object()
        old_value = self.get(name, default=un_set)

        if self._transactions and name in self._transactions[-1]['deleted_keys']:
            self._transactions[-1]['deleted_keys'].delete(name)

        if old_value == value:
            return  # No change

        store = self._transactions[-1]['store'] if self._transactions else self._store
        value_counter = self._transactions[-1]['count'] if self._transactions else self._count

        store[name] = value
        value_counter[value] = self.num_equal_to(value) + 1
        if old_value is not un_set:
            value_counter[old_value] = self.num_equal_to(old_value) - 1

    def get(self, name, default=DEFAULT_VALUE):
        if self._transactions and name in self._transactions[-1]['deleted_keys']:
            return default

        for tran in self._transactions[::-1]:
            if name in tran['store']:
                return tran['store'][name]

        return self._store.get(name, default)

    def unset(self, name):
        un_set = object()
        old_value = self.get(name, default=un_set)

        if old_value is un_set:
            return  # Nothing changes

        store = self._transactions[-1]['store'] if self._transactions else self._store
        value_counter = self._transactions[-1]['count'] if self._transactions else self._count
        value_counter[old_value] = self.num_equal_to(old_value) - 1

        if self._transactions:
            self._transactions[-1]['deleted_keys'][name] = None

        if name in store:
            del store[name]

    def num_equal_to(self, value):
        for tran in self._transactions[::-1]:
            if value in tran['count']:
                return tran['count'][value]

        return self._count.get(value, 0)

    def begin_transaction(self):
        self._transactions.append({'store': storage(), 'count': storage(), 'deleted_keys': storage()})

    def rollback_transaction(self):
        if self._transactions:
            self._transactions.pop()
        else:
            raise DatabaseException("NO TRANSACTION")

    def commit_all_transactions(self):
        if not self._transactions:
            raise DatabaseException("NO TRANSACTION")

        while self._transactions:
            tran = self._transactions.pop()

            for k in tran['deleted_keys']:
                self.unset(k)

            for k in tran['store']:
                self.set(k, tran['store'][k])


class DatabaseCommandParserException(RuntimeError):
    pass


class DatabaseCommandParser(object):
    ACTIONS = {
        'GET', 'SET', 'UNSET', 'NUMEQUALTO', 'BEGIN', 'ROLLBACK', 'COMMIT', 'END'
    }

    def __init__(self):
        self.db = Database()

    def execute(self, command):
        try:
            parts = command.split()
            if parts and parts[0].upper() in self.ACTIONS:
                action = parts[0].upper()
                if action == 'GET':
                    return self.db.get(parts[1], "NULL")
                elif action == 'SET':
                    self.db.set(*parts[1:3])
                elif action == 'UNSET':
                    self.db.unset(parts[1])
                elif action == 'NUMEQUALTO':
                    return self.db.num_equal_to(parts[1])
                elif action == 'BEGIN':
                    self.db.begin_transaction()
                elif action == 'ROLLBACK':
                    self.db.rollback_transaction()
                elif action == 'COMMIT':
                    self.db.commit_all_transactions()
                elif action == 'END':
                    quit()
            else:
                raise DatabaseCommandParserException("Command not valid")
        except DatabaseException as e:
            raise DatabaseCommandParserException(e.message)
        except AttributeError:
            raise DatabaseCommandParserException("Command not valid")
        except (IndexError, TypeError):
            raise DatabaseCommandParserException("Incorrect number of arguments")
from mock import patch, Mock
import unittest
from db import Database, DatabaseException, DatabaseCommandParser


class SimpleDataBaseTests(unittest.TestCase):
    def testGetSet(self):
        db = Database()
        db.set("name", "value")

        expected = db.get("name")
        self.assertEqual(expected, "value", "The value could not be retrieved")

        db.unset("name")
        self.assertEqual(db.get("name"), None, "The value could not be unset")

    def testNumEqualTo(self):
        db = Database()
        db.set("a", 10)
        db.set("b", 10)

        self.assertEqual(db.num_equal_to(10), 2, "num_equal_to is incorrect for set values!")
        self.assertEqual(db.num_equal_to(20), 0, "num_equal_to is incorrect for unset values!")

        db.set("b", 30)
        self.assertEqual(db.num_equal_to(10), 1, "num_equal_to is incorrect for changed values!")

    def testRollbackNestedTransactions(self):
        db = Database()

        db.begin_transaction()
        db.set("a", 10)
        self.assertEqual(db.get("a"), 10, "The value set within a transaction is incorrect!")

        db.begin_transaction()
        db.set("a", 20)
        self.assertEqual(db.get("a"), 20, "The value set within a nested transaction is incorrect!")

        db.rollback_transaction()
        self.assertEqual(db.get("a"), 10, "The value is incorrect after a nested transaction is rolled back!")

        db.rollback_transaction()
        self.assertEqual(db.get("a"), None, "The value is incorrect after the first of a nested transaction is rolled "
                                            "back!")

    def testCommitTransaction(self):
        db = Database()

        db.set("a", 30)

        db.begin_transaction()
        db.set("a", 40)
        db.commit_all_transactions()
        self.assertEqual(db.get("a"), 40, "The value set and committed in a transaction is incorrect!")

        self.assertRaisesRegexp(DatabaseException, "NO TRANSACTION", db.rollback_transaction)
        self.assertRaisesRegexp(DatabaseException, "NO TRANSACTION", db.commit_all_transactions)

    def testUnsetInTransaction(self):
        db = Database()

        db.set("a", 50)
        db.begin_transaction()
        self.assertEqual(db.get("a"), 50, "The value set out of a transaction is incorrect within a transaction!")
        db.set("a", 60)
        db.begin_transaction()
        db.unset("a")
        self.assertEqual(db.get("a"), None, "The value unset in a nested transaction")
        db.rollback_transaction()
        self.assertEqual(db.get("a"), 60, "The value is incorrect after being unset in a transaction that was rolled "
                                          "back!")
        db.commit_all_transactions()
        self.assertEqual(db.get("a"), 60, "Incorrect value after commit all, after being set, unset and rolled back!")

    def testNumEqualToInTransaction(self):
        db = Database()

        db.set("a", 10)
        db.begin_transaction()
        self.assertEqual(db.num_equal_to(10), 1, "count is incorrect inside the transaction")

        db.begin_transaction()
        db.unset("a")
        self.assertEqual(db.num_equal_to(10), 0, "count is incorrect after unsetting inside the transaction")

        db.rollback_transaction()
        self.assertEqual(db.num_equal_to(10), 1, "count is incorrect after unsetting and rolling back the transaction")


class CommandProcessorTests(unittest.TestCase):
    def testCommands(self):
        db = DatabaseCommandParser()
        db.db.get = Mock()
        db.db.set = Mock()
        db.db.unset = Mock()
        db.db.num_equal_to = Mock()
        db.db.begin_transaction = Mock()
        db.db.rollback_transaction = Mock()
        db.db.commit_all_transactions = Mock()

        db.execute("GET a")
        db.db.get.assert_called_with("a", "NULL")

        db.execute("SET a 10")
        db.db.set.assert_called_with("a", "10")

        db.execute("UNSET a")
        db.db.unset.assert_called_with("a")

        db.execute("NUMEQUALTO 10")
        db.db.num_equal_to.assert_called_with("10")

        db.execute("BEGIN")
        db.db.begin_transaction.assert_called_with()

        db.execute("ROLLBACK")
        db.db.rollback_transaction.assert_called_with()

        db.execute("COMMIT")
        db.db.commit_all_transactions.assert_called_with()

        q = Mock()
        @patch("__builtin__.quit", q)
        def end():
            db.execute("END")

        end()
        q.assert_called_with()


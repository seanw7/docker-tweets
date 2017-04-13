from psycopg2 import pool

# All objects of the type, Database are sharing this resource.
class Database:
    __connection_pool = None

    # This static method removes reference to current class completely or anything else in the class.
    @classmethod
    def initialise(cls, **kwargs):
        # Database connection pool constraints
        Database.__connection_pool = pool.SimpleConnectionPool(1,
                                                               10,
                                                               **kwargs)

    @classmethod
    def get_connection(cls):
        # makes it more simple to interact with the DB
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        # returns a connection and puts it back
        Database.__connection_pool.putconn(connection)

    # Just incase we need this for later on we will put this here
    @classmethod
    def close_all_connections(cls):
        Database.__connection_pool.closeall()



# Connects cursors back up into the pool instead of closing them.
class CursorFromConnectionFromPool:
    def __init__(self):
        self.connection = None
        self.cursor = None

    # this method controls what happens when we start the 'with' clause, this creates a connection pool everytime you
    # call 'with'
    def __enter__(self):
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    # controls what happens at the end of the with clause, it should close cursor, commit, and return connection
    # to pool
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None: # e.g. TypeError, AttributeError, ValueError
            self.connection.rollback()
        else: # if there is no error then run these Commands
            self.cursor.close()
            self.connection.commit()
        Database.return_connection(self.connection)




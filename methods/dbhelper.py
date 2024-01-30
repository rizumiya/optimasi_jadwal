from datas import database as db

class Query:
    def __init__(self):
        self.query = ''
        self.values = None

    # Add new data
    def create_data(self, table_name, fields, values):
        placeholders = ', '.join(['?' for _ in values])
        self.query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        self.values = values
        self.dml()

    # Read existed data
    def read_datas(self, table_name, fields=None, condition=None, condition_values=None):
        self.query = f"SELECT {', '.join(fields) if fields else '*'} FROM {table_name}"
        if condition:
            self.query += f" WHERE {condition}"
        self.values = condition_values
        return self.dml(False)

    # Change value existed data
    def update_data(self, table_name, fields, values, condition=None, condition_values=None):
        set_values = ', '.join([f"{field} = ?" for field in fields])
        self.query = f"UPDATE {table_name} SET {set_values}"
        if condition:
            self.query += f" WHERE {condition}"

        self.values = values + condition_values if condition_values else values
        self.dml()

    # Detele existed data
    def delete_data(self, table_name, condition=None, condition_values=None):
        self.query = f"DELETE FROM {table_name}"
        if condition:
            self.query += f" WHERE {condition}"
        
        self.values = condition_values
        self.dml()

    def dml(self, commit=True):
        dbs = db.Database()
        # print(self.query, self.values)
        try:
            if self.values is not None:
                dbs.cursor.execute(self.query, self.values)
            else:
                dbs.cursor.execute(self.query)
            if not commit:
                rows = dbs.cursor.fetchall()
                return rows
            else:
                dbs.conn.commit()
        except Exception as e:
            dbs.conn.rollback()
            raise e
        finally:
            dbs.dumpSQL()
            dbs.conn.close()






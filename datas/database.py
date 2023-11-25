import os
import sqlite3

class Database:
    def __init__(self):
        self.SQLPATH = os.path.join(os.path.dirname(__file__), 'autobot.db')
        self.conn = sqlite3.connect(self.SQLPATH, uri=True)
        self.cursor = self.conn.cursor()


    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username text null,
                            password text null,
                            role text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                            id INTEGER PRIMARY KEY,
                            nama_ruang text null,
                            max_siswa integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS daytimes (
                            id INTEGER PRIMARY KEY,
                            unique_id text null,
                            nama_hari text null,
                            waktu_kuliah text null,
                            durasi_jam integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS professors (
                            id INTEGER PRIMARY KEY,
                            nidn text null,
                            nama text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS unavailable_times (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_dosen integer null,
                            id_waktu integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                            id INTEGER PRIMARY KEY,
                            unique_id text null,
                            nama_matkul text null,
                            metode text null,
                            sks integer null,
                            perkiraan_peserta integer null,
                            kelas integer null
                        )''')
        
        # prof has many courses and otherwise
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS profs_courses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_dosen integer null,
                            id_matkul integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS profs_classes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_dosen integer null,
                            id_matkul integer null,
                            kelas text null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS semesters (
                            id INTEGER PRIMARY KEY,
                            semester_ke integer null,
                            tahun_ajaran text null,
                            total_sks integer null
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sems_courses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_semester integer null,
                            id_matkul integer null
                        )''')
        
        try:
            self.cursor.execute('INSERT INTO users VALUES(1, "admin", "admin", "boss")')
        except:
            pass
        
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Hapus table
    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()
        self.dumpSQL()

    # Add new data
    def create_data(self, table_name, fields, values):
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        # print(query)
        self.conn.execute(query, values)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Read existed data
    def read_datas(self, table_name, fields=None, condition=None, values=None):
        query = f"SELECT {', '.join(fields) if fields else '*'} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if values:
            # print(query, values)
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.dumpSQL()
        self.conn.close()
        return rows

    # Change value existed data
    def update_data(self, table_name, fields, values, condition=None, condition_values=None):
        set_values = ', '.join([f"{field} = ?" for field in fields])
        query = f"UPDATE {table_name} SET {set_values}"
        if condition:
            query += f" WHERE {condition}"
        if condition_values:
            self.conn.execute(query, values + condition_values)
        else:
            self.conn.execute(query, values)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Detele existed data
    def delete_data(self, table_name, condition=None, values=None):
        query = f"DELETE FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if values:
            self.conn.execute(query, values)
        else:
            self.conn.execute(query)
        self.conn.commit()
        self.dumpSQL()
        self.conn.close()

    # Dumping sql database as txt
    def dumpSQL(self):
        with open('base_sqlite_values.txt', 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)


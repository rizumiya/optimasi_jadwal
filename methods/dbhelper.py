from datas import database as db
import streamlit as st


class DB_Umum:
    def __init__(self):
        self.table_name: str = ""
        self.fields: str = None
        self.values:str = None
        self.condition: str = None
        self.condition_value: str = None

    def create_new_data(self):
        dbase = db.Database()
        dbase.create_data(
            self.table_name, 
            self.fields, 
            self.values
        )

    def read_data(self):
        dbase = db.Database()
        rows = dbase.read_datas(
            self.table_name,
            self.fields,
            self.condition,
            self.values
        )
        return rows
    
    def update_data(self):
        dbase = db.Database()
        dbase.update_data(
            self.table_name,
            self.fields, 
            self.values,
            self.condition,
            self.condition_value
        )
    
    def delete_data(self):
        dbase = db.Database()
        dbase.delete_data(
            self.table_name,
            self.condition, 
            self.values
        )
    
    def restart_table(self, table_name):
        dbase = db.Database()
        dbase.drop_table(table_name)
        dbase.create_tables()


class DB_Ruang(DB_Umum):
    def __init__(self):
        super().__init__()
        self.table_name = "rooms"
    
    def tambah_ruang(self, fields, values):
        self.fields = fields
        self.values = values
        self.create_new_data()
    
    def check_ruang(self, nama_ruang, max_siswa):
        self.fields = None
        if not nama_ruang or not max_siswa:
            self.condition = None
            self.values = None 
        else:
            self.condition = "nama_ruang=? AND max_siswa=?"
            self.values = [nama_ruang, max_siswa]
        data_ruang = self.read_data()

        if data_ruang:
            return data_ruang
        return False

    def hapus_ruang(self, nama_ruang, max_siswa):
        self.condition = "nama_ruang=? AND max_siswa=?"
        self.values = [nama_ruang, max_siswa]
        self.delete_data()


class DB_Hari(DB_Umum):
    def __init__(self):
        super().__init__()
        self.table_name = "daytimes"
        
    def tambah_hari(self, fields, values):
        self.fields = fields
        self.values = values
        self.create_new_data()

    def get_unique_id(self, nama_hari, kode):
        self.condition = "nama_hari=?"
        self.values = [nama_hari]
        hari = self.read_data()

        if hari:
            i = len(hari)
            unique_id = kode + str(i + 1)
            return unique_id

        unique_id = kode + str(1)
        return unique_id
    
    def check_hari_jam(self, hari, jam, unique_id=None):
        self.fields = None
        if not hari and not jam and not unique_id:
            self.condition = None
            self.values = None 
        elif unique_id:
            self.condition = "unique_id=?"
            self.values = [unique_id]
        else:
            self.condition = "nama_hari=? AND waktu_kuliah=?"
            self.values = [hari, jam]
        hari_jam = self.read_data()

        if hari_jam:
            return hari_jam
        return False

    def ambil_semua_hari(self):
        self.fields = None
        self.condition = None
        self.values = None
        data_hari = self.read_data()
        return data_hari
    
    def hapus_hari(self, id_waktu):
        self.condition = "id=?"
        self.values = [id_waktu]
        self.delete_data()


class DB_Dosen(DB_Umum):
    def __init__(self):
        super().__init__()

    def ambil_dosen_waktu(self, id_dosen):
        self.fields = ['ps.id', 'ps.nidn', 'ps.nama', 
                       'dt.id', 'dt.unique_id', 'dt.nama_hari', 'dt.waktu_kuliah']
        self.table_name = (
            "daytimes AS dt JOIN unavailable_times AS ut ON dt.id = ut.id_waktu "
            "JOIN professors AS ps ON ps.id = ut.id_dosen"
        )
        self.condition = "ps.id=?"
        self.values = [id_dosen]
        data_dosen = self.read_data()
        return data_dosen
    
    def ambil_dosen_matkul(self, id_dosen):
        self.fields = ['ps.id', 'ps.nidn', 'ps.nama', 
                       'cc.id', 'cc.unique_id', 'cc.nama_matkul']
        self.table_name = (
            "courses AS cc JOIN profs_courses AS pc ON cc.id = pc.id_matkul "
            "JOIN professors AS ps ON ps.id = pc.id_dosen"
        )
        self.condition = "ps.id=?"
        self.values = [id_dosen]
        data_dosen = self.read_data()
        return data_dosen
    
    def ambil_dosen(self):
        self.fields = None
        self.table_name = "professors"
        self.condition = None
        self.values = None
        data_dosen = self.read_data()
        return data_dosen
    
    def check_dosen(self, nidn, nama):
        self.table_name = "professors"
        self.fields = None
        if not nidn or not nama:
            self.condition = None
            self.values = None 
        else:
            self.condition = "nidn=? AND nama=?"
            self.values = [nidn, nama]
        data_dosen = self.read_data()

        if data_dosen:
            return data_dosen
        return False

    def tambah_dosen(self, field, values):
        self.table_name = "professors"
        self.fields = field
        self.values = values
        self.create_new_data()

    def hapus_dosen(self, id):
        self.table_name = "professors"
        self.condition = "id=?"
        self.values = [id]
        self.delete_data()


class DB_Unavailable(DB_Umum):
    def __init__(self):
        super().__init__()
        self.table_name = "unavailable_times"

    @st.cache_resource
    def check_waktu_bl(_self):
        _self.fields = None
        _self.condition = None
        _self.values = None
        data_waktu_bl = _self.read_data()
        return data_waktu_bl

    def tambah_waktu_bl(self, values):
        self.fields = ["id_dosen", "id_waktu"]
        self.values = values
        self.create_new_data()

    def hapus_unavailable_times(self, *args):
        self.condition = f"{args[0]}=?"
        self.values = [args[1]]
        self.delete_data()


class DB_Matkul(DB_Umum):
    def __init__(self):
        super().__init__()
        self.table_name = "courses"

    def tambah_matkul(self, fields, values):
        self.fields = fields
        self.values = values
        self.create_new_data()
        
    def ambil_matkul(self):
        self.fields = None
        self.condition = None
        self.values = None
        data_dosen = self.read_data()
        return data_dosen
    
    def check_matkul(self, unique_id, nama_matkul):
        self.fields = None
        if not unique_id and not nama_matkul:
            self.condition = None
            self.values = None 
        elif unique_id and not nama_matkul:
            self.condition = "unique_id=?"
            self.values = [unique_id]
        else:
            self.condition = "unique_id=? AND nama_matkul=?"
            self.values = [unique_id, nama_matkul]
        data_matkul = self.read_data()

        if data_matkul:
            return data_matkul
        return False


class Data_ProfsCourses(DB_Umum):
    def __init__(self):
        super().__init__()
        self.table_name = 'profs_courses'
    
    def tambah_dosen_pengampu(self, values):
        self.fields = ["id_dosen", "id_matkul"]
        self.values = values
        self.create_new_data()

    def check_profs_courses(self):
        self.fields = None
        self.condition = None
        self.values = None
        datas = self.read_data()
        return datas

    def hapus_profs_courses(self, *args):
        self.condition = f"{args[0]}=?"
        self.values = [args[1]]
        self.delete_data()


class DB_Semester(DB_Umum):
    def __init__(self):
        self.table_name = 'semesters'
    
    def tambah_data_semester(self, values):
        self.fields = ['id', 'semester_ke', 'tahun_ajaran', 'total_sks']
        self.values = values
        self.create_new_data()

    def ambil_data_semester(self, semester=None, tahun=None):
        self.fields = None
        if semester and tahun:
            self.condition = "semester_ke=? AND tahun_ajaran=?"
            self.values = [semester, tahun]
        else:
            self.condition = None
            self.values = None
        data_semester = self.read_data()
        if data_semester:
            return data_semester
        return False

    
class DB_SemsCourses(DB_Umum):
    def __init__(self):
        super().__init__()
        self.table_name = 'sems_courses'
    
    def tambah_sems_courses(self, values):
        self.fields = ["id_semester", "id_matkul"]
        self.values = values
        self.create_new_data()

    def ambil_sems_courses(self, id_semester):
        self.fields = ['c.id', 'c.unique_id', 'c.nama_matkul', 'c.sks', 
                       's.id', 's.semester_ke', 's.tahun_ajaran', 's.total_sks']
        self.table_name = (
            "courses AS c JOIN sems_courses AS sc ON c.id = sc.id_matkul "
            "JOIN semesters AS s ON s.id = sc.id_semester"
        )
        self.condition = "s.id=?"
        self.values = [id_semester]
        data_dosen = self.read_data()
        return data_dosen
    
    def check_sems_courses(self):
        self.fields = None
        self.condition = None
        self.values = None
        datas = self.read_data()
        return datas

    def hapus_sems_courses(self, *args):
        self.condition = f"{args[0]}=?"
        self.values = [args[1]]
        self.delete_data()


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






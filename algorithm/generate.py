import prettytable as prettytable
import random as rnd
import openpyxl as xl

from .normalize import *
from .export_excel import PY_XL

UKURAN_POPULASI = 30 #15 #30
JUMLAH_JADWAL_ELIT = 3 #1 #4
UKURAN_SELEKSI_TURNAMEN = 8 #3 #10
TINGKAT_MUTASI = 0.1
MAX_PERULANGAN = 100
JADWAL_PAGI = ("1", "2")

class Data:
    def __init__(self, id_semester):
        self.ROOMS = table_rooms_to_list()
        self.INSTRUCTORS, self.UT_DOSEN, self.KELAS_DOSEN = table_professor_to_list()
        self.MEETING_TIMES = table_daytime_to_list()
        self.KODEMAT, self.NAMAKUL, self.DOSEN, self.ROW = table_course_to_list()
        self.SEMESTERS, self.LIST_MATKUL = table_semester_to_list(id_semester)

        self._rooms = []
        self._meetingTimes = []
        self._dosen = []
        self._courses = []
        for i in range(0, len(self.ROOMS)):
            self._rooms.append(RuangKelas(self.ROOMS[i][0], self.ROOMS[i][1]))

        for i in range(0, len(self.MEETING_TIMES)):
            self._meetingTimes.append(WaktuPertemuan(
                self.MEETING_TIMES[i][0], self.MEETING_TIMES[i][1], self.MEETING_TIMES[i][2]))

        self._no_time = []
        for i in range(0, len(self.INSTRUCTORS)):
            for ut_dosen in self.UT_DOSEN[i]:
                for j in range(0, len(self.MEETING_TIMES)):
                    if ut_dosen == self.MEETING_TIMES[j][0]:
                        self._no_time.append(self._meetingTimes[j])
            self._dosen.append(Dosen(
                self.INSTRUCTORS[i][0], self.INSTRUCTORS[i][1], self._no_time, self.KELAS_DOSEN[i]))
            self._no_time = []

        self._courses = []
        self._l_dosen = []
        for i in range(0, len(self.NAMAKUL)):
            for dosen in self.DOSEN[i]:
                for k in range(0, len(self.INSTRUCTORS)):
                    if dosen[0] == self.INSTRUCTORS[k][0]:
                        self._l_dosen.append(self._dosen[k])
            self._courses.append(MataKuliah(
                self.KODEMAT[i], self.NAMAKUL[i], self._l_dosen, 50, self.ROW[i][3], self.ROW[i][4], self.ROW[i][6], self.ROW[i][7]))
            self._l_dosen = []

        self._semesters = []  # gantinya self._depts
        self._l_matkul = []

        for i in range(0, len(self.SEMESTERS)):
            for list_matkul in self.LIST_MATKUL[i]:
                for k in range(0, len(self.KODEMAT)):
                    if list_matkul == self.KODEMAT[k]:
                        self._l_matkul.append(self._courses[k])
            self._semesters.append(Semester(self.SEMESTERS[i], self._l_matkul))
            self._l_matkul = []

        self._numberOfClasses = 0

        for i in range(0, len(self._semesters)):
            self._numberOfClasses += len(self._semesters[i].ambil_mata_kuliah())

    def ambil_ruangan(self):
        return self._rooms

    def ambil_dosen(self):
        return self._dosen

    def ambil_mata_kuliah(self):
        return self._courses

    def ambil_semester(self):
        return self._semesters

    def ambil_waktu_pertemuan(self):
        return self._meetingTimes

    def get_numberOfClasses(self):
        return self._numberOfClasses

# Pengaturan untuk algoritma genetika


class Jadwal:
    def __init__(self):
        self._data = data
        self._kelas = []
        self._jumlah_konflik = 0
        self._fitness = -1
        self._nomorClass = 0
        self._fitnessBerubah = True

    def ambil_kelas(self):
        self._fitnessBerubah = True
        return self._kelas

    def ambil_jumlahKonflik(self):
        return self._jumlah_konflik

    def ambil_fitnes(self):
        if (self._fitnessBerubah == True):
            self._fitness = self.hitung_fitnes()
            self._fitnessBerubah = False
        return self._fitness

    def inisialisasi(self):
        semester = self._data.ambil_semester()
        # banyak semester yang di generate
        for i in range(0, len(semester)):
            matkul = semester[i].ambil_mata_kuliah()
            list_waktu_pagi = []

            for j in range(0, len(matkul)): # banyak matkul di 1 semester
                kelas = matkul[j].ambil_kelas() 
                pagi = [waktu.ambil_id() for waktu in data.ambil_waktu_pertemuan() if str(waktu.ambil_id()).endswith(JADWAL_PAGI) and len(waktu.ambil_id()) == 4]

                for k in range(1, kelas + 1): # banyak kelas yang di 1 matkul
                    letter = chr(k + 64)
                    newClass = Class(self._nomorClass, semester[i], matkul[j], letter)
                    self._nomorClass += 1
                    dosen = None

                    # atur dosen pengampu kelas
                    try:
                        for l in range(0, len(matkul[j].ambil_dosen())):
                            for m in range(0, len(matkul[j].ambil_dosen()[l].ambil_kelas())):
                                id_matk, kls = matkul[j].ambil_dosen()[l].ambil_kelas()[m].split(" - ")
                                if id_matk == matkul[j].ambil_nomor() and kls == letter:
                                    newClass.atur_dosen(matkul[j].ambil_dosen()[l])
                                    dosen = matkul[j].ambil_dosen()[l]
                                    break
                            if dosen:
                                break
                        if not dosen:
                            raise ValueError("Tidak ada dosen terpilih")
                    except:
                        data_dosen = []
                        for l in range(0, len(matkul[j].ambil_dosen())):
                            id_dosen = matkul[j].ambil_dosen()[l].ambil_id()
                            for dosen in data.ambil_dosen():
                                if dosen.ambil_id() == id_dosen:    
                                    data_dosen.append(dosen)

                        id_dosen = rnd.randrange(0, len(data_dosen))
                        dosen = data_dosen[id_dosen]
                        newClass.atur_dosen(dosen)

                    # atur waktu
                    waktu_pagi = [[item.ambil_id() for item in data.ambil_waktu_pertemuan()].index(jam_pagi) for jam_pagi in pagi]    
                    tot_sks = matkul[j].ambil_sks()
                    while True:
                        id_waktu = rnd.randrange(0, len(data.ambil_waktu_pertemuan()))
                        if int(matkul[j].ambil_sks()) > 1:
                            if int(matkul[j].ambil_sks()) >= 3 and matkul[j].ambil_nama().lower() not in matkul_3_sks_2_teori:
                                waktu = data.ambil_waktu_pertemuan()[id_waktu:id_waktu + 3]
                            else:
                                waktu = data.ambil_waktu_pertemuan()[id_waktu:id_waktu + 2]
                        else:
                            waktu = [data.ambil_waktu_pertemuan()[id_waktu]]

                        # if waktu[0].ambil_id() in pagi:
                        #     if list_waktu_pagi:
                        #         if not any(item['kelas_pagi'] == letter for item in list_waktu_pagi):
                        #             newClass.atur_waktu_pertemuan(waktu)
                        #             list_waktu_pagi.append({"kelas_pagi": letter})
                        #             break
                        #         continue
                        #     else:
                        #         newClass.atur_waktu_pertemuan(waktu)
                        #         list_waktu_pagi.append({"kelas_pagi": letter})
                        #         break
                        # hilangkan komentar bagian ini jika ingin memaksa jam pagi tiap kelas
                        # elif waktu[0].ambil_id() not in pagi:
                        #     if not any(item['kelas_pagi'] == letter for item in list_waktu_pagi):
                        #         id_waktu_pagi = rnd.choice(waktu_pagi)
                        #         waktu = data.ambil_waktu_pertemuan()[id_waktu_pagi:id_waktu_pagi+int(matkul[j].ambil_sks())]
                        #         newClass.atur_waktu_pertemuan(waktu)
                        #         list_waktu_pagi.append({"kelas_pagi": letter})
                        #         break
                        # else:
                        panjang_kode_hari = str(waktu[0].ambil_id()[:3]) # SEN
                        sks3sakral = [panjang_kode_hari + sakral for sakral in waktu_sakral_3] # SEN5, SEN6, ..
                        sks2sakral = [panjang_kode_hari + sakral for sakral in waktu_sakral_2] # SEN6, SEN9, ..
                        if ((tot_sks == 3 or tot_sks == 4) and str(waktu[0].ambil_id()) in sks3sakral):
                            continue
                        elif (tot_sks == 2 and str(waktu[0].ambil_id()) in sks2sakral):
                            continue

                        newClass.atur_waktu_pertemuan(waktu)
                        break

                    # atur ruangan
                    online_id = [item.ambil_nomor().lower() for item in data.ambil_ruangan()].index("online")
                    if matkul[j].ambil_metode_belajar().lower() == 'online':
                        newClass.atur_ruangan(data.ambil_ruangan()[online_id])
                    else:
                        while True:
                            ruangan = rnd.randrange(0, len(data.ambil_ruangan()))
                            if ruangan != online_id:
                                newClass.atur_ruangan(data.ambil_ruangan()[ruangan])
                                break
                    self._kelas.append(newClass)
        return self

    # ATUR KEMUNGKINAN ============================================
    def hitung_fitnes(self):
        self._jumlah_konflik = 0
        pagi = [waktu.ambil_id() for waktu in data.ambil_waktu_pertemuan() if str(waktu.ambil_id()).endswith(JADWAL_PAGI) and len(waktu.ambil_id()) == 4]
        list_kelas_pagi = []

        classes = self.ambil_kelas() # ambil semua data hasil acak di inisalisasi
        for i in range(0, len(classes)):
            # buat pengecekan waktu dosen tidak bisa hadir
            # konflik + 1 apabila terdapat dosen yang memiliki waktu sakral yang sama dengan waktu yang diacak pada jadwal inisialisasi
            if classes[i].ambil_detail_dosen().ambil_waktu_sakral():
                for instructor_time in classes[i].ambil_detail_dosen().ambil_waktu_sakral():
                    if any(instructor_time.ambil_id() == meeting_time.ambil_id() for meeting_time in classes[i].ambil_detail_waktu_pertemuan()):
                        self._jumlah_konflik += 1
                        break

            # buat pengecekan jika metode online, tapi gak dapet kelas online konflik + 1 dan sebaliknya
            # if (classes[i].ambil_detail_mata_kuliah().ambil_metode_belajar().lower() == 'online' and 
            #     classes[i].ambil_detail_ruangan().ambil_nomor().lower() != 'online'):
            #     self._jumlah_konflik += 1
            # if classes[i].ambil_detail_mata_kuliah().ambil_metode_belajar().lower() == 'offline':
            #     if classes[i].ambil_detail_ruangan().ambil_nomor().lower() == 'online':
            #         self._jumlah_konflik += 1

            # buat pengecekan antar jadwal 1 dengan yang lainnya
            panjang_kode_hari = str(classes[i].ambil_detail_waktu_pertemuan()[0].ambil_id()[:3]) # SEN
            for j in range(0, len(classes)):
                if (j >= i):
                    dosen_bentrok = False # beda matkul tapi -> waktu sama + dosen sama
                    ruangan_bentrok = False # beda matkul tapi -> waktu sama + ruangan sama
                    kelas_bentrok = False # sama matkul + waktu sama + ruangan sama (online)
                    # Intinya bagian ini kalo ada salah satu waktu di 2/3 sks dan dosen pengampu yang sama maka konflik + 1
                    for l in range(0, len(classes[j].ambil_detail_waktu_pertemuan())):
                        if (classes[j].ambil_detail_waktu_pertemuan()[l] in classes[i].ambil_detail_waktu_pertemuan() and
                            classes[i].ambil_id() != classes[j].ambil_id()):

                            if (classes[i].ambil_detail_dosen() == classes[j].ambil_detail_dosen() and
                                "dosen" not in classes[i].ambil_detail_dosen().ambil_nama().lower() and
                                not dosen_bentrok):
                                dosen_bentrok = True
                                self._jumlah_konflik += 1
                                break
                            
                            if (classes[i].ambil_detail_ruangan() == classes[j].ambil_detail_ruangan() and 
                                not ruangan_bentrok):
                                ruangan_bentrok = True
                                self._jumlah_konflik += 1
                                break
                            
                            if (classes[i].ambil_kelas() != classes[j].ambil_kelas() and 
                                classes[i].ambil_detail_mata_kuliah().ambil_nama() == classes[j].ambil_detail_mata_kuliah().ambil_nama() and
                                not kelas_bentrok):
                                kelas_bentrok = True
                                self._jumlah_konflik += 1
                                break
                            
                    if dosen_bentrok or ruangan_bentrok or kelas_bentrok: # and jadi or
                        break

                    # cek jenis matkul topsus di hari yang sama = konflik + 1
                    jenis_matkul = classes[i].ambil_detail_mata_kuliah().ambil_jenis_matkul()
                    if (panjang_kode_hari == str(classes[j].ambil_detail_waktu_pertemuan()[0].ambil_id()[:3]) and
                        jenis_matkul == classes[j].ambil_detail_mata_kuliah().ambil_jenis_matkul() and jenis_matkul == 'Pilihan' and
                        classes[i].ambil_detail_mata_kuliah().ambil_nama() != classes[j].ambil_detail_mata_kuliah().ambil_nama() and
                        classes[i].ambil_id() != classes[j].ambil_id()):
                        self._jumlah_konflik += 1
                        break

                    # buat pengecekan dosen yang sama mengampu matkul yang sama jika tidak 1 hari konflik + 1
                    # memaksa di 1 hari yang sama untuk dosen = matkul yang sama
                    # if (classes[i].ambil_detail_mata_kuliah() == classes[j].ambil_detail_mata_kuliah() and
                    #     classes[i].ambil_detail_dosen() == classes[j].ambil_detail_dosen() and 
                    #     "dosen" not in classes[j].ambil_detail_dosen().ambil_nama().lower() and 
                    #     not str(classes[i].ambil_detail_waktu_pertemuan()[-1].ambil_id()).startswith(str(classes[j].ambil_detail_waktu_pertemuan()[-1].ambil_id())[:3]) and
                    #     classes[i].ambil_id() != classes[j].ambil_id()):
                    #     self._jumlah_konflik += 1
                    #     break

                    # buat pengecekan dosen yang sama mengampu matkul yang sama dalam ruangan yang sama dalam 1 hari, jika tidak konflik + 1
                    # memaksa 1 ruangan untuk dosen = matkul = hari yang sama
                    # if (classes[i].ambil_detail_mata_kuliah() == classes[j].ambil_detail_mata_kuliah() and
                    #     classes[i].ambil_detail_dosen() == classes[j].ambil_detail_dosen() and 
                    #     "dosen" not in classes[j].ambil_detail_dosen().ambil_nama().lower() and 
                    #     classes[i].ambil_detail_ruangan() != classes[j].ambil_detail_ruangan() and
                    #     str(classes[i].ambil_detail_waktu_pertemuan()[-1].ambil_id()).startswith(str(classes[j].ambil_detail_waktu_pertemuan()[-1].ambil_id())[:3]) and
                    #     classes[i].ambil_id() != classes[j].ambil_id()):
                    #     self._jumlah_konflik += 1
                    #     break

            # buat pengecekan yang sudah dapat kelas pagi, gak boleh dapet kelas pagi lagi
            if classes[i].ambil_detail_waktu_pertemuan()[0].ambil_id() in pagi:
                if classes[i].ambil_kelas() in [kelas["kelas"] for kelas in list_kelas_pagi]:
                    self._jumlah_konflik += 1
                    continue
                list_kelas_pagi.append({"kelas": classes[i].ambil_kelas(), "pagi": True})

        return 1 / ((1.0 * self._jumlah_konflik + 1))

    def __str__(self):
        # it returns all the classes of schedule separated by comas
        returnValue = ""
        for i in range(0, len(self._kelas) - 1):
            returnValue += str(self._kelas[i]) + ", "
        returnValue += str(self._kelas[len(self._kelas) - 1])
        return returnValue


class Populasi:
    def __init__(self, size):
        self._size = size
        self._data = data
        self._schedules = []
        for i in range(0, size):
            self._schedules.append(Jadwal().inisialisasi())

    def ambil_seluruh_jadwal(self):
        return self._schedules


class AlgoritmaGenetika:
    def evolve(self, populasi):
        return self._mutasi_populasi(self._persilangan_populasi(populasi))

    def _persilangan_populasi(self, pop):
        crossover_pop = Populasi(0)
        for i in range(JUMLAH_JADWAL_ELIT):
            crossover_pop.ambil_seluruh_jadwal().append(pop.ambil_seluruh_jadwal()[i])
        i = JUMLAH_JADWAL_ELIT
        while i < UKURAN_POPULASI:
            schedule1 = self._pilih_turnamen_populasi(pop).ambil_seluruh_jadwal()[0]
            schedule2 = self._pilih_turnamen_populasi(pop).ambil_seluruh_jadwal()[0]
            crossover_pop.ambil_seluruh_jadwal().append(
                self._persilangan_jadwal(schedule1, schedule2))
            i += 1
        return crossover_pop

    def _mutasi_populasi(self, populasi):
        for i in range(JUMLAH_JADWAL_ELIT, UKURAN_POPULASI):
            self._mutasi_jadwal(populasi.ambil_seluruh_jadwal()[i])
        return populasi

    def _persilangan_jadwal(self, schedule1, schedule2):
        crossoverSchedule = Jadwal().inisialisasi()
        for i in range(0, len(crossoverSchedule.ambil_kelas())):
            if (rnd.random() > 0.5):
                crossoverSchedule.ambil_kelas()[i] = schedule1.ambil_kelas()[i]
            else:
                crossoverSchedule.ambil_kelas()[i] = schedule2.ambil_kelas()[i]
        return crossoverSchedule

    def _mutasi_jadwal(self, mutateSchedule):
        schedule = Jadwal().inisialisasi()
        for i in range(0, len(mutateSchedule.ambil_kelas())):
            if (TINGKAT_MUTASI > rnd.random()):
                mutateSchedule.ambil_kelas()[i] = schedule.ambil_kelas()[i]
        return mutateSchedule

    def _pilih_turnamen_populasi(self, pop):
        tournament_pop = Populasi(0)
        i = 0
        while i < UKURAN_SELEKSI_TURNAMEN:
            tournament_pop.ambil_seluruh_jadwal().append(
                pop.ambil_seluruh_jadwal()[rnd.randrange(0, UKURAN_POPULASI)])
            i += 1
        tournament_pop.ambil_seluruh_jadwal().sort(key=lambda x: x.ambil_fitnes(), reverse=True)
        return tournament_pop

# Pengaturan data untuk optimasi


class MataKuliah:
    def __init__(self, number, name, instructors, maxNumbOfStudents, metode, sks, kelas, jenis):
        self._nomor = number
        self._sks = sks
        self._nama = name
        self._kelas = kelas
        self._metode = metode
        self._dosen = instructors
        self._total_mahasiswa = maxNumbOfStudents
        self._jenis_matkul = jenis

    def ambil_nama(self):
        return self._nama

    def ambil_sks(self):
        return self._sks

    def ambil_kelas(self):
        return self._kelas

    def ambil_nomor(self):
        return self._nomor

    def ambil_metode_belajar(self):
        return self._metode

    def ambil_dosen(self):
        return self._dosen

    def ambil_total_mahasiswa(self):
        return self._total_mahasiswa

    def ambil_jenis_matkul(self):
        return self._jenis_matkul

    def __str__(self):
        return self._nama


class WaktuPertemuan:
    def __init__(self, id, time, durasi=None):
        self._waktu = time
        self._id = id
        self._durasi = durasi

    def ambil_id(self):
        return self._id

    def ambil_waktu(self):
        return self._waktu

    def ambil_durasi(self):
        return self._durasi

    def __str__(self):
        return self._id


class Dosen:
    def __init__(self, id, name, no_times, kelas):
        self._id = id
        self._nama = name
        self._waktu_sakral = no_times
        self._kelas = kelas

    def ambil_id(self):
        return self._id

    def ambil_nama(self):
        return self._nama

    def ambil_waktu_sakral(self):
        return self._waktu_sakral

    def ambil_kelas(self):
        return self._kelas

    def __str__(self):
        return self._nama


class RuangKelas:
    def __init__(self, number, seatingCapacity):
        self._nomor_ruangan = number
        self._total_kapasitas_mahasiswa = seatingCapacity

    def ambil_nomor(self):
        return self._nomor_ruangan

    def ambil_kapasitas_mahasiswa(self):
        return self._total_kapasitas_mahasiswa

    def __str__(self):
        return self._nomor_ruangan


class Semester:
    # Batch for my case
    def __init__(self, name, matkul):
        self._nama = name
        self._courses = matkul     # Courses that Semester offers

    def ambil_nama(self): return self._nama
    def ambil_mata_kuliah(self): return self._courses


# merujuk pada hasil generated jadwal bukan data asli
class Class:
    # MataKuliah to be scheduled at specific room of department host by an instructor at specific Meeting Time
    def __init__(self, id, dept, course, kelas):
        self._id = id
        self._semester = dept
        self._mata_kuliah = course
        self._kelas = kelas
        self._dosen = None
        self._waktu_pertemuan = None
        self._ruang_kelas = None

    def ambil_id(self):
        return self._id

    def ambil_semester(self):
        return self._semester

    def ambil_detail_ruangan(self):
        return self._ruang_kelas

    def ambil_detail_mata_kuliah(self):
        return self._mata_kuliah

    def ambil_kelas(self):
        return self._kelas

    def ambil_detail_dosen(self):
        return self._dosen

    def ambil_detail_waktu_pertemuan(self):
        return self._waktu_pertemuan

    def atur_dosen(self, instructor):
        self._dosen = instructor

    def atur_waktu_pertemuan(self, meetingTime):
        self._waktu_pertemuan = meetingTime

    def atur_ruangan(self, room):
        self._ruang_kelas = room

    def __str__(self):
        return str(self._semester.ambil_nama()) + ", " + str(self._mata_kuliah.ambil_nomor()) + ", " + \
            str(self._ruang_kelas.ambil_nomor()) + ", " + str(self._dosen.ambil_id()) + ", " + \
            str(self._kelas) + ", " + \
            (', ').join([waktu.ambil_id() for waktu in self._waktu_pertemuan])


# Pengaturan untuk tampilan akhir
class DisplayMgr:
    def cetak_seluruh_data(self):
        print("> Seluruh Data Tersedia")
        self.cetak_semester()
        self.cetak_mata_kuliah()
        self.cetak_ruang_kelas()
        self.cetak_dosen()
        self.cetak_waktu_pertemuan()

    def cetak_semester(self):
        semester = data.ambil_semester()
        tableSemesterTersedia = prettytable.PrettyTable(
            ['Semester', 'Mata kuliah'])
        for i in range(0, len(semester)):
            matkul = semester.__getitem__(i).ambil_mata_kuliah()
            tempStr = ""
            for j in range(0, len(matkul) - 1):
                tempStr += matkul[j].__str__() + "\n"
            tempStr += matkul[len(matkul) - 1].__str__() + ""
            tableSemesterTersedia.add_row(
                [semester.__getitem__(i).ambil_nama(), tempStr])
        print(tableSemesterTersedia)

    def cetak_mata_kuliah(self):
        tableMatkulTersedia = prettytable.PrettyTable(
            ['ID', 'Mata kuliah # ', 'SKS', 'Pelaksanaan', 'Kelas', 'Dosen'])
        matkul = data.ambil_mata_kuliah()
        for i in range(0, len(matkul)):
            instructors = matkul[i].ambil_dosen()
            tempStr = ""
            for j in range(0, len(instructors)-1):
                tempStr += instructors[j].__str__() + ", "
            tempStr += instructors[len(instructors) - 1].__str__()
            tableMatkulTersedia.add_row(
                [matkul[i].ambil_nomor(),
                 matkul[i].ambil_nama(),
                 matkul[i].ambil_sks(),
                 matkul[i].ambil_metode_belajar(),
                 #  str(matkul[i].ambil_total_mahasiswa()),
                 matkul[i].ambil_kelas(),
                 tempStr]
            )
        print(tableMatkulTersedia)

    def cetak_dosen(self):
        tableDosenTersedia = prettytable.PrettyTable(
            ['ID', 'Dosen', 'Waktu tidak bisa hadir'])
        instructors = data.ambil_dosen()
        for i in range(0, len(instructors)):
            times = instructors[i].ambil_waktu_sakral()
            tempStr = ""
            for j in range(0, len(times) - 1):
                tempStr += times[j].__str__() + " | "
            if times:
                tempStr += times[len(times) - 1].__str__()
            tableDosenTersedia.add_row(
                [instructors[i].ambil_id(), instructors[i].ambil_nama(), tempStr])
        print(tableDosenTersedia)

    def cetak_ruang_kelas(self):
        tableRuanganTersedia = prettytable.PrettyTable(
            ['Ruangan #', 'Kapasitas maksimal'])
        rooms = data.ambil_ruangan()
        for i in range(0, len(rooms)):
            tableRuanganTersedia.add_row(
                [str(rooms[i].ambil_nomor()), str(rooms[i].ambil_kapasitas_mahasiswa())])
        print(tableRuanganTersedia)

    def cetak_waktu_pertemuan(self):
        tableWaktuPertemuanTersedia = prettytable.PrettyTable(
            ['ID', 'Waktu pertemuan', 'Durasi'])
        meetingTimes = data.ambil_waktu_pertemuan()
        for i in range(0, len(meetingTimes)):
            tableWaktuPertemuanTersedia.add_row(
                [meetingTimes[i].ambil_id(),
                 meetingTimes[i].ambil_waktu(),
                 str(meetingTimes[i].ambil_durasi()) + ' Jam'])
        print(tableWaktuPertemuanTersedia)

    def cetak_generasi(self, populasi):
        table1 = prettytable.PrettyTable(
            ['Jadwal # ', 'fitness', '# Konflik', 'Komponen [Semester, Mata kuliah, Ruangan, Dosen, Waktu]'])
        schedules = populasi.ambil_seluruh_jadwal()
        fittest = []
        for i in range(0, len(schedules)):
            table1.add_row(
                [str(i), 
                 round(schedules[i].ambil_fitnes(), 3), 
                 schedules[i].ambil_jumlahKonflik(), 
                 schedules[i]])
            fittest.append(round(schedules[i].ambil_fitnes(), 3))
        print(table1)
        return max(fittest)

    def cetak_jadwal_sebagai_table(self, schedule):
        classes = schedule.ambil_kelas()
        table = prettytable.PrettyTable(
            ['No', 'Mata Kuliah', 'SKS', 'Kelas', 'Dosen', 'Waktu', 'Ruangan'])
        matkul = None
        for i in range(0, len(classes)):
            waktu = [waktu.ambil_id() for waktu in classes[i].ambil_detail_waktu_pertemuan()]

            nama_matkul = classes[i].ambil_detail_mata_kuliah().ambil_nama() if matkul != classes[i].ambil_detail_mata_kuliah().ambil_nama() else ''
            matkul = classes[i].ambil_detail_mata_kuliah().ambil_nama()

            table.add_row(
                [str(i + 1),
                 nama_matkul,
                 classes[i].ambil_detail_mata_kuliah().ambil_sks(),
                 classes[i].ambil_kelas(),
                 classes[i].ambil_detail_dosen().ambil_nama(),
                 (', ').join(waktu),
                 classes[i].ambil_detail_ruangan().ambil_nomor()
                 ])
        print(table)
        return table


def cetak_ke_txt(hasil):
    # membuka file teks untuk ditulis
    file = open("hasil.txt", "w")
    # menulis hasil print ke dalam file teks
    print(hasil, file=file)
    # menutup file teks
    file.close()


def export_beban_sks(schedule, path: str):
    workbook = xl.load_workbook(path)
    sheet = workbook.worksheets[1]

    classes = schedule.ambil_kelas()
    data_beban_sks = []

    for kelas in classes:
        dosen = kelas.ambil_detail_dosen().ambil_nama()
        nama_matkul = kelas.ambil_detail_mata_kuliah().ambil_nama()
        sks = int(kelas.ambil_detail_mata_kuliah().ambil_sks())

        if not any(item["dosen"] == dosen and item["nama_matkul"] == nama_matkul for item in data_beban_sks):
            data_beban_sks.append({
                "dosen": dosen,
                "nama_matkul": nama_matkul,
                "sks": sks,
                "total_sks": 0,
                "kelas": ""
            })

    for beban in data_beban_sks:
        for kelas in classes:
            if beban["dosen"] == kelas.ambil_detail_dosen().ambil_nama():
                beban["total_sks"] += int(kelas.ambil_detail_mata_kuliah().ambil_sks())
                beban["kelas"] += kelas.ambil_kelas()

    data_beban_sks.sort(key=lambda x: (x["dosen"], x["nama_matkul"]))

    for i, beban in enumerate(data_beban_sks):
        if i == 0 or beban["dosen"] != data_beban_sks[i-1]["dosen"] or beban["nama_matkul"] != data_beban_sks[i-1]["nama_matkul"]:
            sheet.append([beban["dosen"], beban["nama_matkul"], beban["sks"], beban["total_sks"], beban["kelas"]])

    workbook.save(path)


def export_ke_excel(name: str, schedule):
    excel_manager = PY_XL(f"Rancangan Jadwal {name}.xlsx")
    excel_manager.create_excel_file()

    xlPath = excel_manager.xlPath
    # menyimpan data ke sheet 1
    workbook = xl.load_workbook(xlPath)
    workbook._active_sheet_index = 0
    sheet = workbook.active

    classes = schedule.ambil_kelas()
    data = []

    for kelas in classes:
        nama_matkul = kelas.ambil_detail_mata_kuliah().ambil_nama()
        total_mhs = kelas.ambil_detail_mata_kuliah().ambil_total_mahasiswa()
        perkiraan_mhs = int(kelas.ambil_detail_mata_kuliah().ambil_kelas()) * total_mhs
        metode = kelas.ambil_detail_mata_kuliah().ambil_metode_belajar()
        dosen = kelas.ambil_detail_dosen().ambil_nama()
        kelas_kuliah = kelas.ambil_kelas()
        ruangan = kelas.ambil_detail_ruangan().ambil_nomor()

        waktu_senin = [str(waktu.ambil_id())[3:] for waktu in kelas.ambil_detail_waktu_pertemuan() if str(waktu.ambil_id()).startswith("SEN")]
        waktu_senin = (",").join(waktu_senin) + f" {kelas_kuliah}" + "/" + ruangan if waktu_senin else ""
        waktu_selasa = [str(waktu.ambil_id())[3:] for waktu in kelas.ambil_detail_waktu_pertemuan() if str(waktu.ambil_id()).startswith("SEL")]
        waktu_selasa = (",").join(waktu_selasa) + f" {kelas_kuliah}" + "/" + ruangan if waktu_selasa else ""
        waktu_rabu = [str(waktu.ambil_id())[3:] for waktu in kelas.ambil_detail_waktu_pertemuan() if str(waktu.ambil_id()).startswith("RAB")]
        waktu_rabu = (",").join(waktu_rabu) + f" {kelas_kuliah}" + "/" + ruangan if waktu_rabu else ""
        waktu_kamis = [str(waktu.ambil_id())[3:] for waktu in kelas.ambil_detail_waktu_pertemuan() if str(waktu.ambil_id()).startswith("KAM")]
        waktu_kamis = (",").join(waktu_kamis) + f" {kelas_kuliah}" + "/" + ruangan if waktu_kamis else ""
        waktu_jumat = [str(waktu.ambil_id())[3:] for waktu in kelas.ambil_detail_waktu_pertemuan() if str(waktu.ambil_id()).startswith("JUM")]
        waktu_jumat = (",").join(waktu_jumat) + f" {kelas_kuliah}" + "/" + ruangan if waktu_jumat else ""
        waktu_sabtu = [str(waktu.ambil_id())[3:] for waktu in kelas.ambil_detail_waktu_pertemuan() if str(waktu.ambil_id()).startswith("SAB")]
        waktu_sabtu = (",").join(waktu_sabtu) + f" {kelas_kuliah}" + "/" + ruangan if waktu_sabtu else ""

        data.append((nama_matkul, perkiraan_mhs, metode, kelas_kuliah, dosen, waktu_senin, waktu_selasa, waktu_rabu, waktu_kamis, waktu_jumat, waktu_sabtu, total_mhs))

    data.sort(key=lambda x: (x[0], x[4]))

    for i, item in enumerate(data):
        sheet.append(item)

    workbook.save(xlPath)
    export_beban_sks(schedule, xlPath)

# Mulai proses / MAIN

data = None

def jalankan(nilai_data):
    global data
    data = nilai_data
    banyak_iterasi = 0
    nilai_fitnes = None
    exported = False
    displayMgr = DisplayMgr()
    # displayMgr.cetak_seluruh_data()
    generationNumber = 0
    print("\n> Generation # " + str(generationNumber))
    populasi = Populasi(UKURAN_POPULASI)
    populasi.ambil_seluruh_jadwal().sort(key=lambda x: x.ambil_fitnes(), reverse=True)
    nilai_fitnes = displayMgr.cetak_generasi(populasi)
    # it will print fittest generation of schedule
    hasil = displayMgr.cetak_jadwal_sebagai_table(populasi.ambil_seluruh_jadwal()[0])
    geneticAlgorithm = AlgoritmaGenetika()
    while (populasi.ambil_seluruh_jadwal()[0].ambil_fitnes() != 1.0):
        generationNumber += 1
        # print("\n> Generation # " + str(generationNumber))
        populasi = geneticAlgorithm.evolve(populasi)
        populasi.ambil_seluruh_jadwal().sort(key=lambda x: x.ambil_fitnes(), reverse=True)
        nilai_fitnes_2 = displayMgr.cetak_generasi(populasi)
        hasil = displayMgr.cetak_jadwal_sebagai_table(populasi.ambil_seluruh_jadwal()[0])
        if nilai_fitnes == nilai_fitnes_2 and banyak_iterasi < MAX_PERULANGAN:
            banyak_iterasi += 1
        elif nilai_fitnes != nilai_fitnes_2:
            nilai_fitnes = nilai_fitnes_2
            banyak_iterasi = 0
        else:
            export_ke_excel(data.ambil_semester()[-1].ambil_nama(), populasi.ambil_seluruh_jadwal()[0])
            exported = True
            break
    cetak_ke_txt(hasil)
    if not exported:
        export_ke_excel(data.ambil_semester()[-1].ambil_nama(), populasi.ambil_seluruh_jadwal()[0])
    return 'OK', f'{nilai_fitnes}, dan konflik : {int((1 / nilai_fitnes) - 1)}'

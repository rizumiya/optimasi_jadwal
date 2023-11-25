import prettytable as prettytable
import random as rnd

from .normalize import *
from methods.dbhelper import Query

query = Query()
POPULATION_SIZE = 15
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.1


class Data:
    def __init__(self, id_semester):
        self.ROOMS = table_rooms_to_list()
        self.INSTRUCTORS, self.UT_DOSEN, self.KELAS_DOSEN = table_professor_to_list()
        self.MEETING_TIMES = table_daytime_to_list()
        self.KODEMAT, self.NAMAKUL, self.DOSEN, self.ROW = table_course_to_list()
        self.SEMESTERS, self.LIST_MATKUL = table_semester_to_list(id_semester)

        self._rooms = []
        self._meetingTimes = []
        self._instructors = []
        self._courses = []
        for i in range(0, len(self.ROOMS)):
            self._rooms.append(Room(self.ROOMS[i][0], self.ROOMS[i][1]))

        for i in range(0, len(self.MEETING_TIMES)):
            self._meetingTimes.append(MeetingTime(
                self.MEETING_TIMES[i][0], self.MEETING_TIMES[i][1], self.MEETING_TIMES[i][2]))

        self._no_time = []
        for i in range(0, len(self.INSTRUCTORS)):
            for ut_dosen in self.UT_DOSEN[i]:
                for j in range(0, len(self.MEETING_TIMES)):
                    if ut_dosen == self.MEETING_TIMES[j][0]:
                        self._no_time.append(self._meetingTimes[j])
            self._instructors.append(Instructor(
                self.INSTRUCTORS[i][0], self.INSTRUCTORS[i][1], self._no_time, self.KELAS_DOSEN[i]))
            self._no_time = []

        self._courses = []
        self._l_dosen = []
        for i in range(0, len(self.NAMAKUL)):
            for dosen in self.DOSEN[i]:
                for k in range(0, len(self.INSTRUCTORS)):
                    if dosen[0] == self.INSTRUCTORS[k][0]:
                        self._l_dosen.append(self._instructors[k])
            self._courses.append(Course(
                self.KODEMAT[i], self.NAMAKUL[i], self._l_dosen, 50, self.ROW[i][3], self.ROW[i][4], self.ROW[i][6]))
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
            self._numberOfClasses += len(self._semesters[i].get_courses())

    def get_rooms(self):
        return self._rooms

    def get_instructors(self):
        return self._instructors

    def get_courses(self):
        return self._courses

    def get_depts(self):
        return self._semesters

    def get_meetingTimes(self):
        return self._meetingTimes

    def get_numberOfClasses(self):
        return self._numberOfClasses

# Pengaturan untuk algoritma genetika


class Schedule:
    def __init__(self):
        self._data = data
        self._classes = []
        self._numberOfConflicts = 0
        self._fitness = -1
        self._classNumb = 0
        self._isFitnessChanged = True

    def get_classes(self):
        self._isFitnessChanged = True
        return self._classes

    def get_numberOfConflicts(self):
        return self._numberOfConflicts

    def get_fitness(self):
        if (self._isFitnessChanged == True):
            self._fitness = self.calculate_fitness()
            self._isFitnessChanged = False
        return self._fitness

    def initialize(self):
        depts = self._data.get_depts()
        # banyak semester yang di generate
        for i in range(0, len(depts)):
            courses = depts[i].get_courses()
            for j in range(0, len(courses)):                # banyak matkul di 1 semester
                kelas = courses[j].get_kelas()
                for k in range(1, kelas + 1):
                    # banyak kelas yang di 1 matkul
                    letter = chr(k + 64)
                    newClass = Class(
                        self._classNumb, depts[i], courses[j], letter)
                    self._classNumb += 1

                    # atur waktu
                    id_waktu = rnd.randrange(0, len(data.get_meetingTimes()))
                    waktu = data.get_meetingTimes(
                    )[id_waktu:id_waktu+int(courses[j].get_sks())]
                    newClass.set_meetingTime(waktu)

                    # atur dosen pengampu kelas
                    for l in range(0, len(courses[j].get_instructors())):
                        for m in range(0, len(courses[j].get_instructors()[l].get_kelas())):
                            id_matk, kls = courses[j].get_instructors()[l].get_kelas()[
                                m].split(" - ")
                            if id_matk == courses[j].get_number() and kls == letter:
                                newClass.set_instructor(
                                    courses[j].get_instructors()[l])
                                break

                    # atur ruangan
                    for n in range(0, len(data.get_rooms())):
                        if courses[j].get_metode() == 'Online' and courses[j].get_metode() == data.get_rooms()[n].get_number():
                            newClass.set_room(data.get_rooms()[n])
                            break
                        if courses[j].get_metode() == 'Offline':
                            # karna kelas online ada di data paling bawah
                            newClass.set_room(
                                data.get_rooms()[rnd.randrange(0, len(data.get_rooms()) - 1)])
                            break

                    self._classes.append(newClass)
        return self

    # ATUR KEMUNGKINAN ============================================
    def calculate_fitness(self):
        self._numberOfConflicts = 0
        classes = self.get_classes()
        for i in range(0, len(classes)):
            # buat pengecekan waktu dosen tidak bisa hadir
            if classes[i].get_instructor().get_no_times():
                for instructor_time in classes[i].get_instructor().get_no_times():
                    if any(instructor_time.get_id() == meeting_time.get_id() for meeting_time in classes[i].get_meetingTime()):
                        self._numberOfConflicts += 1
                        break

            # buat pengecekan jika metode online, tapi gak dapet online konflik +=1 dan sebaliknya
            if classes[i].get_course().get_metode() == 'Online' and classes[i].get_room().get_number() != 'Online':
                self._numberOfConflicts += 1
            if classes[i].get_course().get_metode() == 'Offline' and classes[i].get_room().get_number() == 'Online':
                self._numberOfConflicts += 1

            # buat pengecekan jika waktu = sks
            waktu_sakral = ['SEN11', 'SEN12', 'SEL11', 'SEL12', 'RAB11', 'RAB12',
                            'KAM11', 'KAM12', 'JUM11', 'JUM12', 'SAB11', 'SAB12']
            if int(classes[i].get_course().get_sks()) == 3 and any(time.get_id() in waktu_sakral for time in classes[i].get_meetingTime()):
                self._numberOfConflicts += 1
            waktu_sakral_sks2 = ['SEN12', 'SEL12',
                                 'RAB12', 'KAM12', 'JUM12', 'SAB12']
            if int(classes[i].get_course().get_sks()) == 2 and any(time.get_id() in waktu_sakral_sks2 for time in classes[i].get_meetingTime()):
                self._numberOfConflicts += 1

            for j in range(0, len(classes)):
                if (j >= i):
                    for l in range(0, len(classes[j].get_meetingTime())):
                        if (classes[j].get_meetingTime()[l] in classes[i].get_meetingTime() and
                           classes[i].get_instructor() == classes[j].get_instructor() and
                           classes[i].get_id() != classes[j].get_id()):
                            # print(classes[i].get_course().get_name(), " - ", classes[i].get_instructor().get_name(),  " | ", classes[j].get_course().get_name(), " - ",  classes[j].get_instructor().get_name())
                            self._numberOfConflicts += 1
                            break

                    if (classes[i].get_meetingTime() == classes[j].get_meetingTime() and
                       classes[i].get_id() != classes[j].get_id()):
                        if (classes[i].get_room() == classes[j].get_room() and classes[j].get_room().get_number() != 'Online'):
                            self._numberOfConflicts += 1
                        if (classes[i].get_instructor() == classes[j].get_instructor()):
                            self._numberOfConflicts += 1
        return 1 / ((1.0*self._numberOfConflicts + 1))

    def __str__(self):
        # it returns all the classes of schedule separated by comas
        returnValue = ""
        for i in range(0, len(self._classes) - 1):
            returnValue += str(self._classes[i]) + ", "
        returnValue += str(self._classes[len(self._classes) - 1])
        return returnValue


class Population:
    def __init__(self, size):
        self._size = size
        self._data = data
        self._schedules = []
        for i in range(0, size):
            self._schedules.append(Schedule().initialize())

    def get_schedules(self):
        return self._schedules


class GeneticAlgorithm:
    def evolve(self, population):
        return self._mutate_population(self._crossover_population(population))

    def _crossover_population(self, pop):
        crossover_pop = Population(0)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = NUMB_OF_ELITE_SCHEDULES
        while i < POPULATION_SIZE:
            schedule1 = self._select_tournament_population(pop).get_schedules()[
                0]
            schedule2 = self._select_tournament_population(pop).get_schedules()[
                0]
            crossover_pop.get_schedules().append(
                self._crossover_schedule(schedule1, schedule2))
            i += 1
        return crossover_pop

    def _mutate_population(self, population):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population

    def _crossover_schedule(self, schedule1, schedule2):
        crossoverSchedule = Schedule().initialize()
        for i in range(0, len(crossoverSchedule.get_classes())):
            if (rnd.random() > 0.5):
                crossoverSchedule.get_classes()[i] = schedule1.get_classes()[i]
            else:
                crossoverSchedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossoverSchedule

    def _mutate_schedule(self, mutateSchedule):
        schedule = Schedule().initialize()
        for i in range(0, len(mutateSchedule.get_classes())):
            if (MUTATION_RATE > rnd.random()):
                mutateSchedule.get_classes()[i] = schedule.get_classes()[i]
        return mutateSchedule

    def _select_tournament_population(self, pop):
        tournament_pop = Population(0)
        i = 0
        while i < TOURNAMENT_SELECTION_SIZE:
            tournament_pop.get_schedules().append(
                pop.get_schedules()[rnd.randrange(0, POPULATION_SIZE)])
            i += 1
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop

# Pengaturan data untuk optimasi


class Course:
    def __init__(self, number, name, instructors, maxNumbOfStudents, metode, sks, kelas):
        self._number = number
        self._sks = sks
        self._name = name
        self._kelas = kelas
        self._metode = metode
        self._instructors = instructors
        self._maxNumbOfStudents = maxNumbOfStudents

    def get_name(self):
        return self._name

    def get_sks(self):
        return self._sks

    def get_kelas(self):
        return self._kelas

    def get_number(self):
        return self._number

    def get_metode(self):
        return self._metode

    def get_instructors(self):
        return self._instructors

    def get_maxNumbOfStudents(self):
        return self._maxNumbOfStudents

    def __str__(self):
        return self._name


class MeetingTime:
    def __init__(self, id, time, durasi=None):
        self._time = time
        self._id = id
        self._durasi = durasi

    def get_id(self):
        return self._id

    def get_time(self):
        return self._time

    def get_durasi(self):
        return self._durasi

    def __str__(self):
        return self._id


class Instructor:
    def __init__(self, id, name, no_times, kelas):
        self._id = id
        self._name = name
        self._no_times = no_times
        self._kelas = kelas

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_no_times(self):
        return self._no_times

    def get_kelas(self):
        return self._kelas

    def __str__(self):
        return self._name


class Room:
    def __init__(self, number, seatingCapacity):
        self._number = number
        self._seatingCapacity = seatingCapacity

    def get_number(self):
        return self._number

    def get_seatingCapacity(self):
        return self._seatingCapacity

    def __str__(self):
        return self._number


class Semester:
    # Batch for my case
    def __init__(self, name, courses):
        self._name = name
        self._courses = courses     # Courses that Semester offers

    def get_name(self): return self._name
    def get_courses(self): return self._courses


class Class:
    # Course to be scheduled at specific room of department host by an instructor at specific Meeting Time
    def __init__(self, id, dept, course, kelas):
        self._id = id
        self._dept = dept
        self._course = course
        self._kelas = kelas
        self._instructor = None
        self._meetingTime = None
        self._room = None

    def get_id(self):
        return self._id

    def get_dept(self):
        return self._dept

    def get_room(self):
        return self._room

    def get_course(self):
        return self._course

    def get_kelas(self):
        return self._kelas

    def get_instructor(self):
        return self._instructor

    def get_meetingTime(self):
        return self._meetingTime

    def set_instructor(self, instructor):
        self._instructor = instructor

    def set_meetingTime(self, meetingTime):
        self._meetingTime = meetingTime

    def set_room(self, room):
        self._room = room

    def __str__(self):
        return str(self._dept.get_name()) + ", " + str(self._course.get_number()) + ", " + \
            str(self._room.get_number()) + ", " + str(self._instructor.get_id()) + ", " + \
            str(self._kelas) + ", " + \
            (', ').join([waktu.get_id() for waktu in self._meetingTime])

# Pengaturan untuk tampilan akhir


class DisplayMgr:
    def print_available_data(self):
        print("> All Available Data")
        self.print_dept()
        self.print_course()
        self.print_room()
        self.print_instructor()
        self.print_meeting_times()

    def print_dept(self):
        depts = data.get_depts()
        availableDeptsTable = prettytable.PrettyTable(
            ['Semester', 'Mata kuliah'])
        for i in range(0, len(depts)):
            courses = depts.__getitem__(i).get_courses()
            tempStr = ""
            for j in range(0, len(courses) - 1):
                tempStr += courses[j].__str__() + "\n"
            tempStr += courses[len(courses) - 1].__str__() + ""
            availableDeptsTable.add_row(
                [depts.__getitem__(i).get_name(), tempStr])
        print(availableDeptsTable)

    def print_course(self):
        availabelCoursesTable = prettytable.PrettyTable(
            ['ID', 'Mata kuliah # ', 'SKS', 'Pelaksanaan', 'Kelas', 'Dosen'])
        courses = data.get_courses()
        for i in range(0, len(courses)):
            instructors = courses[i].get_instructors()
            tempStr = ""
            for j in range(0, len(instructors)-1):
                tempStr += instructors[j].__str__() + ", "
            tempStr += instructors[len(instructors) - 1].__str__()
            availabelCoursesTable.add_row(
                [courses[i].get_number(),
                 courses[i].get_name(),
                 courses[i].get_sks(),
                 courses[i].get_metode(),
                 #  str(courses[i].get_maxNumbOfStudents()),
                 courses[i].get_kelas(),
                 tempStr]
            )
        print(availabelCoursesTable)

    def print_instructor(self):
        availableInstructorsTable = prettytable.PrettyTable(
            ['ID', 'Dosen', 'Waktu tidak bisa hadir'])
        instructors = data.get_instructors()
        for i in range(0, len(instructors)):
            times = instructors[i].get_no_times()
            tempStr = ""
            for j in range(0, len(times) - 1):
                tempStr += times[j].__str__() + " | "
            if times:
                tempStr += times[len(times) - 1].__str__()
            availableInstructorsTable.add_row(
                [instructors[i].get_id(), instructors[i].get_name(), tempStr])
        print(availableInstructorsTable)

    def print_room(self):
        availableRoomsTable = prettytable.PrettyTable(
            ['Ruangan #', 'Kapasitas maksimal'])
        rooms = data.get_rooms()
        for i in range(0, len(rooms)):
            availableRoomsTable.add_row(
                [str(rooms[i].get_number()), str(rooms[i].get_seatingCapacity())])
        print(availableRoomsTable)

    def print_meeting_times(self):
        availableMeetingTimeTable = prettytable.PrettyTable(
            ['ID', 'Waktu pertemuan', 'Durasi'])
        meetingTimes = data.get_meetingTimes()
        for i in range(0, len(meetingTimes)):
            availableMeetingTimeTable.add_row(
                [meetingTimes[i].get_id(),
                 meetingTimes[i].get_time(),
                 str(meetingTimes[i].get_durasi()) + ' Jam'])
        print(availableMeetingTimeTable)

    def print_generation(self, population):
        table1 = prettytable.PrettyTable(
            ['Jadwal # ', 'fitness', '# Konflik', 'Komponen [Semester, Mata kuliah, Ruangan, Dosen, Waktu]'])
        schedules = population.get_schedules()
        fittest = []
        for i in range(0, len(schedules)):
            table1.add_row(
                [str(i), 
                 round(schedules[i].get_fitness(), 3), 
                 schedules[i].get_numberOfConflicts(), 
                 schedules[i]])
            fittest.append(round(schedules[i].get_fitness(), 3))
        # print(table1)
        return max(fittest)

    # def print_schedule_as_table(self, schedule): ASLII
    #     classes = schedule.get_classes()
    #     table = prettytable.PrettyTable(['Class # ', 'Semester', 'Course (number, max # of students)', 'Room (Capacity)', 'Instructor', 'Time'])
    #     for i in range(0, len(classes)):
    #         table.add_row([str(i), classes[i].get_dept().get_name(), classes[i].get_course().get_name() + " (" +
    #                        classes[i].get_course().get_number() + ", " +
    #                        str(classes[i].get_course().get_maxNumbOfStudents()) + ")",
    #                        classes[i].get_room().get_number() + " (" + str(classes[i].get_room().get_seatingCapacity()) + ")",
    #                        classes[i].get_instructor().get_name() + " (" + str(classes[i].get_instructor().get_id()) +")",
    #                        classes[i].get_meetingTime().get_time() + " (" + str(classes[i].get_meetingTime().get_id()) +")"
    #                        ])
    #     print(table)

    def print_schedule_as_table(self, schedule):
        classes = schedule.get_classes()
        table = prettytable.PrettyTable(
            ['No', 'Mata Kuliah', 'SKS', 'Kelas', 'Dosen', 'Waktu', 'Ruangan'])
        matkul = None
        for i in range(0, len(classes)):
            waktu = [waktu.get_id() for waktu in classes[i].get_meetingTime()]

            nama_matkul = classes[i].get_course().get_name(
            ) if matkul != classes[i].get_course().get_name() else ''
            matkul = classes[i].get_course().get_name()

            table.add_row(
                [str(i + 1),
                 nama_matkul,
                 classes[i].get_course().get_sks(),
                 classes[i].get_kelas(),
                 classes[i].get_instructor().get_name(),
                 (', ').join(waktu),
                 classes[i].get_room().get_number()
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


# Mulai proses / MAIN

data = None

def run(nilai_data):
    global data
    data = nilai_data
    banyak_iterasi = 0
    nilai_fitnes = None
    displayMgr = DisplayMgr()
    displayMgr.print_available_data()
    generationNumber = 0
    print("\n> Generation # " + str(generationNumber))
    population = Population(POPULATION_SIZE)
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
    nilai_fitnes = displayMgr.print_generation(population)
    # it will print fittest generation of schedule
    hasil = displayMgr.print_schedule_as_table(population.get_schedules()[0])
    geneticAlgorithm = GeneticAlgorithm()
    while (population.get_schedules()[0].get_fitness() != 1.0):
        generationNumber += 1
        print("\n> Generation # " + str(generationNumber))
        population = geneticAlgorithm.evolve(population)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        nilai_fitnes_2 = displayMgr.print_generation(population)
        hasil = displayMgr.print_schedule_as_table(population.get_schedules()[0])
        if nilai_fitnes == nilai_fitnes_2 and banyak_iterasi < 50:
            banyak_iterasi += 1
        elif nilai_fitnes != nilai_fitnes_2:
            nilai_fitnes = nilai_fitnes_2
            banyak_iterasi = 0
        else:
            break
    print("\n\n - - - - - - - - - - - - - - - - - - - - ", nilai_fitnes)
    cetak_ke_txt(hasil)
    return 'OK'

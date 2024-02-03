from methods.dbhelper import Query

query = Query()

def table_rooms_to_list():
    row = query.read_datas('rooms')
    new_data = [[item[1], item[2]] for item in row]
    return new_data

def table_professor_to_list():
    row = query.read_datas('professors')
    new_data = [[item[1], item[2]] for item in row]
    no_time = query.read_datas(
        'professors AS p JOIN unavailable_times AS ut ON p.id = ut.id_dosen '
        'JOIN daytimes AS dt ON dt.id = ut.id_waktu ',
        [
            'p.nidn', 'p.nama', 'dt.unique_id', 'dt.nama_hari', 'dt.waktu_kuliah', 'dt.durasi_jam'
        ]
    )
    kelases = query.read_datas(
        'profs_classes AS pc JOIN courses AS c ON c.id = pc.id_matkul '
        'JOIN professors AS p ON p.id = pc.id_dosen ',
        ['c.unique_id', 'p.nidn', 'pc.kelas'],
    )

    unavailable_time = []
    ut_dosen = []

    for i in range(0, len(row)):
        for j in range(0, len(no_time)):
            if row[i][1] == no_time[j][0]:
                ut_dosen.append(no_time[j][2])
        unavailable_time.append(ut_dosen)
        ut_dosen = []
    
    matkul_kelas = []
    kelas_dosen = []

    for i in range(0, len(row)):
        for j in range(0, len(kelases)):
            if row[i][1] == kelases[j][1]:
                matkul_kelas.append(f'{kelases[j][0]} - {kelases[j][2]}')
        kelas_dosen.append(matkul_kelas)
        matkul_kelas = []
    
    return new_data, unavailable_time, kelas_dosen

def table_daytime_to_list():
    row = query.read_datas('daytimes')
    new_data = [[item[1], f'{item[2]}, {item[3]}', item[4]] for item in row]

    return new_data

def table_course_to_list():
    row = query.read_datas('courses')
    profs = table_professor_to_list()[0]
    dosens = query.read_datas(
        'courses AS C JOIN profs_courses AS pc ON c.id = pc.id_matkul '
        'JOIN professors AS p ON p.id = pc.id_dosen ',
        [
            'c.unique_id', 'c.nama_matkul', 'c.metode', 'c.sks', 'c.perkiraan_peserta', 'c.kelas',
            'p.nidn', 'p.nama'
        ]
    )

    kombinasi = []

    kode_matkul = [item[1] for item in row]
    nama_matkul = [item[2] for item in row]

    kombinasi = [[next(prof for prof in profs if prof[0] == dosen[6]) for dosen in dosens if dosen[1] == nama] for nama in nama_matkul]

    return kode_matkul, nama_matkul, kombinasi, row

def table_semester_to_list(id):
    row = query.read_datas('semesters', None, 'id=?', [id])
    isi_semester = query.read_datas(
        'semesters AS s JOIN sems_courses AS sc ON s.id = sc.id_semester '
        'JOIN courses AS c ON c.id = sc.id_matkul',
        [
            's.semester_ke', 's.tahun_ajaran', 's.total_sks',
            'c.unique_id', 'c.nama_matkul'
        ],
        's.id=?',
        [id]
    )

    list_semester = []
    semester = [f'{item[1]}, {item[2]}' for item in row]

    for semes in semester:
        list_matkul = [data[3] for data in isi_semester if f'{data[0]}, {data[1]}' == semes]
        list_semester.append(list_matkul)

    return semester, list_semester


# SKS yang dilarang
waktu_sakral_4 = ("4", "5", "6", "7", "8", "9", "10", "11", "12") # 
waktu_sakral_3 = ("5", "6", "8", "9", "11", "12") # 
waktu_sakral_2 = ("6", "9", "12") # 


# Matkul khusus teori + praktik
matkul_3_sks_2_teori = [
    "sistem operasi",
    "logika informatika",
    "dasar sistem komputer",
    "struktur data",
    "keamanan komputer",
    "pemrograman mobile",
    "forensik digital",
    "pemrograman web dinamis",
    "data mining",
    "penjaminan kualitas perangkat lunak",
    "robotika informatika",
    "teknik optimasi",
    "grafika terapan",
    "pembelajaran mesin",
    "pengolahan citra",
    "sistem pendukung keputusan",
    "sistem temu balik informasi",
    "pemrograman berorentiasi objek",
    "artitektur komputer",
    "matematika diskrit",
    "pemrograman web",
    "grafika komputer",
    "analisis dan perancangan perangkat lunak",
    "strategi algoritma",
    "kecerdasan buatan",
    "interaksi manusia dan komputer",
    "teknologi multimedia",
    "keamanan informasi",
    "kriptografi",
    "rekayasa web",
    "sistem informasi geografis",
    "visualisasi data",
    "deep learning",
    "pemrosesan bahasa alami",
    "pengembangan aplikasi game",
    "pengenalan pola",
    "penglihatan komputer",
    "sister terdistribusi"
]


matkul_paket = [
    "dasar pemrograman",
    "sistem operasi",
    "dasar sistem komputer",
    "kalkulus informatika",
    "logika informatika",
    "manajemen data dan informasi",
    "struktur data",
    "pemrograman berorientasi objek" ,
    "basis data",
    "statistika informatika",
    "aljabar linear matriks",
    "algoritma pemrograman",
    "praktikum algoritma pemrograman",
    "matematika diskrit",
    "pemrograman web",
    "arsitektur komputer",
    "analisis dan perancangan pl",
    "interaksi manusia komputer",
    "kecerdasan buatan",
    "grafika komputer",
    "komunikasi data dan jaringan komputer" ,
    "strategi algoritma"
]

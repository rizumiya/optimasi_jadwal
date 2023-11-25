import streamlit as st
import pandas as pd
import time

from datas import database
from methods import st_pages, dbhelper

st_pages.clean_view()
db = database.Database()
dbu = dbhelper.DB_Umum()
dbh = dbhelper.DB_Hari()
dbd = dbhelper.DB_Dosen()
dbm = dbhelper.DB_Matkul()
dbut = dbhelper.DB_Unavailable()
dbpc = dbhelper.Data_ProfsCourses()
query = dbhelper.Query()


# Mengambil data hari, dan mengubahnya menjadi format yang hari, jam
def tampil_hari():
    list_hari = dbh.ambil_semua_hari()
    if list_hari:
        hari = [f"{hari}, {jam}" for _, _, hari, jam, _ in list_hari]
    else:
        hari = ['Belum ada data hari']
    return hari


def tampil_matkul():
    list_matkul = dbm.ambil_matkul()
    if list_matkul:
        matkul = [f'{data[1]} - {data[2]}' for data in list_matkul]
    else:
        matkul = ['Belum ada data mata kuliah']
    return matkul


def tampil_matkul_dosen(id_dosen):
    list_matkul = query.read_datas(
        'profs_courses AS pc JOIN courses AS c ON c.id = pc.id_matkul ',
        ['c.unique_id', 'c.nama_matkul'],
        'id_dosen=?',
        [id_dosen]
    )

    if list_matkul:
        matkul = [f'{data[0]} - {data[1]}' for data in list_matkul]
    else:
        matkul = ['Mata Kuliah yang diampu belum diatur']

    return matkul


#cek waktu bl
@st.cache_resource(show_spinner="Memvalidasi data dosen")
def check_n_delete_waktu_bl():
    datas = dbut.check_waktu_bl()
    for data in datas:
        if data[2] not in [hari[0] for hari in dbh.check_hari_jam(None, None)]:
            dbut.hapus_unavailable_times("id_waktu", data[2])
        if data[1] not in [dosen[0] for dosen in dbd.check_dosen(None, None)]:
            dbut.hapus_unavailable_times("id_dosen", data[1])


#cek dan hapus data prof_courses
@st.cache_resource(show_spinner="Memvalidasi data dosen")
def check_n_delete_prof_courses():
    datas = dbpc.check_profs_courses()
    for data in datas:
        if data[1] not in [dosen[0] for dosen in dbd.check_dosen(None, None)]:
            dbpc.hapus_profs_courses("id_dosen", data[1])
        if data[2] not in [matkul[0] for matkul in dbm.check_matkul(None, None)]:
            dbpc.hapus_profs_courses("id_matkul", data[2])


# Menambahkan data waktu yang tidak bisa dihadiri dosen
def tambah_unavailable_time(hari_jam_bl, nidn, nama, imp=False):
    id_dosen = dbd.check_dosen(nidn, nama)[0][0]
    if imp:
        if not hari_jam_bl == 'Tersedia setiap waktu':
            array_hari = hari_jam_bl.split(", ")
            for h in array_hari:
                id_hari = dbh.check_hari_jam(None, None, h)[0][0]
                if id_hari:
                    values = [id_dosen, id_hari]
                    dbut.tambah_waktu_bl(values)
        return
    for i in range(0, len(hari_jam_bl)):
        hari, jam = hari_jam_bl[i].split(", ")
        id_hari = dbh.check_hari_jam(hari, jam)[0][0]
        values = [id_dosen, id_hari]
        dbut.tambah_waktu_bl(values)


#def buat tambah data dosen pengampu
def tambah_profs_courses(matkuls, nidn, nama, imp=False):
    id_dosen = dbd.check_dosen(nidn, nama)[0][0]
    if imp:
        if not matkuls == 'Belum diatur':
            array_matkul = matkuls.split(", ")
            for m in array_matkul:
                matkul, array_kelas = m.split(" - ")
                id_matkul = dbm.check_matkul(matkul, None)[0][0]
                if id_matkul:
                    kelas = array_kelas.split(" | ")
                    for k in kelas:
                        query.create_data('profs_classes', ['id_dosen', 'id_matkul', 'kelas'], [id_dosen, id_matkul, k])
                    values = [id_dosen, id_matkul]
                    dbpc.tambah_dosen_pengampu(values)
        return
    for i in range(0, len(matkuls)):
        kode, nama = matkuls[i].split(" - ")
        id_matkul = dbm.check_matkul(kode, nama)[0][0]
        values = [id_dosen, id_matkul]
        dbpc.tambah_dosen_pengampu(values)


# Menambahkan data dosen jika data dosen dengan nisn dan nama yang sama belum ada
def add_dosen(id_dosen, nidn, nama):
    if not dbd.check_dosen(nidn, nama):
        if not id_dosen:
            try:
                dosens = dbd.check_dosen(None, None)
                id_dosen = max(dosens, key=lambda x: x[0])[0] + 1
            except:
                id_dosen = 1
        dbd.table_name = "professors"
        fields = ["id", "nidn", "nama"]
        values = [id_dosen, nidn, nama]
        dbd.tambah_dosen(fields, values)
        return True
    return False


@st.cache_resource(show_spinner="Memuat data dosen")
def get_dosen_waktu(id_dosen, for_list=False):
    waktu_bl = []
    waktu_hari = dbd.ambil_dosen_waktu(id_dosen)
    if for_list:
        return waktu_hari
    if waktu_hari:
        for data in waktu_hari:
            waktu_bl.append(data[4])
            # for i in len(waktu_bl):
        list_waktu_bl = ', '.join(waktu_bl)
        waktu_bl = []
        return list_waktu_bl
    else:
        return "Tersedia setiap waktu"
    

@st.cache_resource(show_spinner="Memuat data dosen")
def get_dosen_matkul(id_dosen, for_list=False):
    matkul = []
    mata_kuliah = dbd.ambil_dosen_matkul(id_dosen)
    if for_list:
        return mata_kuliah
    kelases = query.read_datas(
        'profs_classes AS pc JOIN courses AS c ON c.id = pc.id_matkul '
        'JOIN professors AS p ON p.id = pc.id_dosen ',
        ['p.nidn', 'c.unique_id', 'pc.kelas'],
        'pc.id_dosen=?',
        [id_dosen]
        )
    l_kelas = []
    if mata_kuliah:
        for data in mata_kuliah:
            for i in range(len(kelases)):
                if data[4] == kelases[i][1]:
                    l_kelas.append(kelases[i][2])
            kls = (' | ').join(l_kelas)
            matkul.append(f'{data[4]} - {kls}')
            l_kelas = []
        list_matkul = ', '.join(matkul)
        matkul = []
        return list_matkul
    else:
        return "Belum diatur"


# Mengambil data seluruh dosen
@st.cache_resource(show_spinner="Memuat data dosen")
def get_dosen():
    dosens = dbd.ambil_dosen()
    result = []

    if dosens:
        for dosen in dosens:
            list_waktu_bl = get_dosen_waktu(dosen[0])
            list_matkul = get_dosen_matkul(dosen[0])

            result.append({"id": dosen[0], "nidn": dosen[1], "nama": dosen[2], "matkul": list_matkul, "waktu": list_waktu_bl})
        return result
        
    result = [{"id": 1, "nidn": None, "nama": None}]
    return result


# Tambah data dari tabel
def simpan_data(table, conn, keys, data_iter):
    # drop table terkait
    dbu.restart_table('professors')
    data = [dict(zip(keys, row)) for row in data_iter]

    for x in data:
        id_dosen, nidn, nama = x['id'], x['nidn'], x['nama']
        add_dosen(id_dosen, nidn, nama)


# Konten dari tab1 Tampil data dosen
def inside_tab1():
    dosen = get_dosen()
    savetable = False
    export_csv = False

    cols = st.columns([1,1,1,6])
    with cols[0]:
        refresh_btn = st.button("Refresh")
    with cols[1]:
        simpan_btn = st.button('Simpan')
    with cols[2]:
        export_btn = st.button('Export')

    if refresh_btn:
        st.cache_resource.clear()
        st.rerun()
    if simpan_btn:
        savetable = True
    if export_btn:
        export_csv = True

    # argumen = C, U, D, Section
    st_pages.tampil_usage(True, True, True, 'Dosen')

    df = pd.DataFrame(dosen)
    edited_df = st.data_editor(
        df,
        column_order=['nidn', 'nama', 'matkul', 'waktu'],
        column_config={
            "nidn": st.column_config.TextColumn("NIP/NIY"),
            "nama": st.column_config.TextColumn("Nama Dosen"),
            "matkul": st.column_config.ListColumn("Mata Kuliah dan Kelas yang diampu"),
            "waktu": st.column_config.ListColumn("Waktu tidak tersedia")
        },
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=False
        )

    if savetable:
        savetable = False
        edited_df.to_sql('professors', db.conn, if_exists='append', index=False, method=simpan_data)
        st.cache_resource.clear()
        st.rerun()
    
    if export_csv:
        export_csv = False
        st_pages.export_dataframe(dosen, 'data dosen.csv')


# Konten dari tab2 Tambah data dosen
def inside_tab2():
    with st.form(key='my_form'):
        cols1 = st.columns([1, 2])
        with cols1[0]:
            nidn = st.text_input('NIP/NIY')
        with cols1[1]:
            nama = st.text_input('Nama Dosen')
        
        matkul = tampil_matkul()
        mengampu_matkul = st.multiselect(
            'Mata kuliah yang diampu',
            matkul, placeholder= 'Pilih setidaknya 1 mata kuliah')
        
        hari = tampil_hari()
        hari_jam_bl = st.multiselect(
            'Hari dimana dosen tidak tersedia', 
            hari, placeholder = "Kosongkan jika dosen selalu tersedia")
        
        submit = st.form_submit_button('Tambah')

        if submit:
            if nidn and nama and mengampu_matkul:
                if add_dosen(None, nidn, nama):
                    tambah_unavailable_time(hari_jam_bl, nidn, nama)
                    tambah_profs_courses(mengampu_matkul, nidn, nama)
                    st.success('Data dosen berhasil ditambahkan', icon="✅")
                    time.sleep(1)
                    st.cache_resource.clear()
                    st.rerun()
                else:
                    st.error('Data dosen sudah ada', icon="🚨")
            else:
                st.error('Harap isi seluruh data!', icon="🚨")


def import_section():
    raw_data = None
    raw_data, df = st_pages.tampilan_import(raw_data)
    
    if raw_data and st.button("💾 Tambahkan", key="add_dosen"):
        try:
            for row in df.itertuples():
                add_dosen(None, row[2], row[3])
                tambah_profs_courses(row[4], row[2], row[3], True)
                tambah_unavailable_time(row[5], row[2], row[3], True)
            st.success('Data dosen berhasil ditambahkan', icon="✅")
        except:
            st.error("Terjadi kesalahan saat menambahkan data!", icon="🚨")


def reset_session():
    st.session_state['id_dosen'] = True
    st.session_state['nama_dosen'] = ""
    st.session_state['nip_dosen'] = ""

    st.session_state['list_waktu_db'] = []
    st.session_state['list_matkul_db'] = []


def atur_waktu_multiselect(hari):
    l_hari = []
    list_waktu_bl = get_dosen_waktu(st.session_state['id_dosen'], True)
    l_hari = [index for waktu in list_waktu_bl for index, value in enumerate(hari) if value == f'{waktu[5]}, {waktu[6]}']

    st.session_state['list_waktu_db'] = l_hari


def atur_matkul_multiselect(matkul):
    l_matkul = []
    list_matkul = get_dosen_matkul(st.session_state['id_dosen'], True)
    l_matkul = [index for matak in list_matkul for index, value in enumerate(matkul) if value == f'{matak[4]} - {matak[5]}']
    
    st.session_state['list_matkul_db'] = l_matkul


# Konten dari tab3 Ubah data dosen
def inside_tab3():
    dosens = dbd.ambil_dosen()
    hari = tampil_hari()
    matkul = tampil_matkul()

    if 'id_dosen' not in st.session_state:
        reset_session()
    
    list_dosen = [dosen[2] for dosen in dosens] if dosens else ['Belum ada data']

    cari = st.selectbox(
        'Cari Nama Dosen', 
        list_dosen, 
        disabled=False)
    cols1 = st.columns([1,1,4])
    with cols1[0]:
        submit = st.button('Pilih Dosen')
    with cols1[1]:
        reset = st.button('Reset')

    # Pilih dosen
    if submit:
        if cari != 'Belum ada data':
            st.session_state['nama_dosen'] = cari
            for dosen in dosens:
                if dosen[2] == cari:
                    st.session_state['nip_dosen'] = dosen[1]
                    st.session_state['id_dosen'] = dosen[0]

            atur_matkul_multiselect(matkul)
            atur_waktu_multiselect(hari)
            st.cache_resource.clear()

    if reset:
        reset_session()
    
    default_hari = [hari[id] for id in st.session_state['list_waktu_db']]
    default_matkul = [matkul[id] for id in st.session_state['list_matkul_db']]

    # Form tampil data dosen
    cols2 = st.columns([1, 2])
    with cols2[0]:
        st.text_input('NIP/NIY', disabled=True, key='show_nip', value=st.session_state['nip_dosen'])
    with cols2[1]:
        st.text_input('Nama Dosen', disabled=True, key='show_nama', value=st.session_state['nama_dosen'])

    # Form ubah matkul
    with st.form(key='ubah_matkul'):
        list_matkul = st.multiselect(
            'Mata kuliah yang diampu', 
            matkul, default = default_matkul,
            placeholder = "Pilih setidaknya 1 mata kuliah")
        submit_btn2 = st.form_submit_button('Tambahkan mata kuliah')

        if submit_btn2:
            if not st.session_state['nip_dosen'] == '' and not st.session_state['id_dosen'] == '':
                dbpc.hapus_profs_courses('id_dosen', st.session_state['id_dosen'])
                tambah_profs_courses(
                    list_matkul, 
                    st.session_state['nip_dosen'], 
                    st.session_state['nama_dosen'])
                st.success('Data dosen berhasil diubah', icon="✅")
            else:
                st.error('Pilih dosen terlebih dahulu!', icon="🚨")

    # Form ubah waktu
    with st.form(key='ubah_waktu'):
        hari_jam_bl = st.multiselect(
            'Hari dimana dosen tidak tersedia', 
            hari, default = default_hari,
            placeholder = "Kosongkan jika dosen selalu tersedia")
        submit_btn1 = st.form_submit_button('Tambahkan waktu')

        if submit_btn1:
            if not st.session_state['nip_dosen'] == '' and not st.session_state['id_dosen'] == '':
                dbut.hapus_unavailable_times('id_dosen', st.session_state['id_dosen'])
                tambah_unavailable_time(
                    hari_jam_bl, 
                    st.session_state['nip_dosen'], 
                    st.session_state['nama_dosen'])
                st.success('Data dosen berhasil diubah', icon="✅")
            else:
                st.error('Pilih dosen terlebih dahulu!', icon="🚨")


def tampil_kelas():
    st.session_state['unique_id'], _ = st.session_state['matkul_dipilih'].split(' - ')
    list_kelas = query.read_datas('courses', ['id', 'kelas'], 'unique_id=?', [st.session_state['unique_id']])[0]
    db_kelas = query.read_datas('profs_classes', None, 'id_dosen=? AND id_matkul=?', [st.session_state['nidn'], list_kelas[0]])
    st.session_state['kelas'] = [chr(i + 65) for i in range(0, int(list_kelas[1]))]
    id_list_kelas = []
    if db_kelas:
        for kelas in db_kelas:
            id_list_kelas.append(st.session_state['kelas'].index(kelas[3]))
        st.session_state['default_kelas'] = id_list_kelas
    else:
        st.session_state['default_kelas'] = []
        

def on_selectbox_change():
    st.session_state['nidn'] = query.read_datas('professors', ['id'], 'nama=?', [st.session_state['cari_dosen_tab4']])[0][0]
    st.session_state['matkul'] = tampil_matkul_dosen(st.session_state['nidn'])
    st.session_state['matkul_dipilih'] = st.session_state['matkul'][0]

    tampil_kelas()


def inside_tab4():
    dosens = dbd.ambil_dosen()

    if 'tab4' not in st.session_state:
        st.session_state['tab4'] = True
        st.session_state['default_kelas'] = []
        st.session_state['matkul'] = ['Pilih dosen terlebih dahulu']
        st.session_state['kelas'] = ['Pilih mata kuliah terlebih dahulu']
    
    list_dosen = [dosen[2] for dosen in dosens] if dosens else ['Belum ada data']

    cols = st.columns([1, 1])
    with cols[0]:
        st.selectbox(
            'Cari Nama Dosen', 
            list_dosen, key='cari_dosen_tab4', 
            disabled=False, on_change=on_selectbox_change)
    
    with cols[1]:
        st.selectbox(
            'Pilih Mata Kuliah', 
            st.session_state['matkul'],
            key='matkul_dipilih',
            on_change=tampil_kelas)
    
    list_kelas = st.multiselect(
        'Pilih kelas yang diampu',
        st.session_state['kelas'], 
        default=[st.session_state['kelas'][i] for i in st.session_state['default_kelas']],
        placeholder='Pilih setidaknya 1 kelas'
    )

    submit = st.button('Tambahkan kelas', key='beban_sks')
    if submit:
        id_dosen = st.session_state['nidn']
        id_matkul = query.read_datas('courses', ['id'], 'unique_id=?', [st.session_state['unique_id']])[0][0]

        if query.read_datas('profs_classes', None, 'id_dosen=? AND id_matkul=?', [id_dosen, id_matkul]):
            query.delete_data('profs_classes', 'id_dosen=? AND id_matkul=?', [id_dosen, id_matkul])
        for kelas in list_kelas:
            query.create_data(
                'profs_classes',
                ['id_dosen', 'id_matkul', 'kelas'], 
                [id_dosen, id_matkul, kelas]
            )
        st.success('Beban SKS berhasil diubah', icon="✅")


def main():
    st.header("Data Dosen 🧑🏻‍🏫")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Data Dosen", "Tambah Data Dosen", "Ubah Data Dosen", "Beban SKS"])
    
    with tab1:
        inside_tab1()
        check_n_delete_waktu_bl()
        check_n_delete_prof_courses()
    with tab2:
        with st.expander("Tambah Data Manual", expanded=False):
            inside_tab2()
        with st.expander("Import Data", expanded=False):
           import_section() 
    with tab3:
        inside_tab3()
    with tab4:
        inside_tab4()


if not st_pages.check_login():
    st.error("Silahkan Login terlebih dahulu pada menu Utama")
else:
    main()

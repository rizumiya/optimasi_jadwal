import streamlit as st
import pandas as pd

from methods import st_pages, dbhelper
from datas import database

st_pages.clean_view()

db = database.Database()
query = dbhelper.Query()


def get_sem_course(id_semester, for_list=None):
    matkul = []
    list_semmat = query.read_datas(
        "courses AS c JOIN sems_courses AS sc ON c.id = sc.id_matkul "
        "JOIN semesters AS s ON s.id = sc.id_semester",
        ['c.id', 'c.unique_id', 'c.nama_matkul', 'c.sks', 's.id', 's.semester_ke', 's.tahun_ajaran', 's.total_sks'],
        f's.id={id_semester}'
    )
    if for_list:
        return list_semmat
    

@st.cache_resource(show_spinner="Memuat data semester")
def get_semester():
    dt_semester = query.read_datas('semesters')
    result = []
    
    if dt_semester:
        for semester in dt_semester:
            tot_matk = len(get_sem_course(semester[0], True))
            result.append({"id": semester[0], "semester_ke": semester[1], "tahun_ajaran": semester[2], "total_sks": semester[3], "total_matkul":tot_matk})
        return result
        
    result = [{"id": 1, "semester_ke": None, "tahun_ajaran": None, "total_sks": None}]
    return result


#cek dan hapus data sems_courses
@st.cache_resource(show_spinner="Memvalidasi data semester")
def check_n_delete_sems_courses():
    datas = query.read_datas('sems_courses')
    for data in datas:
        try:
            if data[1] not in [semester[0] for semester in query.read_datas('semesters')]:
                query.delete_data('sems_courses', f'id_semester = {data[1]}')
            if data[2] not in [matkul[0] for matkul in query.read_datas('courses')]:
                query.delete_data('sems_courses', f'id_matkul = {data[2]}')
        except:
            query.delete_data('sems_courses', f'id_semester = {data[1]}')
            query.delete_data('sems_courses', f'id_matkul = {data[2]}')

    
def tampil_matkul():
    list_matkul = query.read_datas('courses')
    if list_matkul:
        matkul = [f'{data[1]} - {data[2]}' for data in list_matkul]
    else:
        matkul = ['Belum ada data mata kuliah']
    return matkul


def tambah_semester(id_sems, semester, tahun, sks):
    if not query.read_datas('semesters', None, 'semester_ke=? AND tahun_ajaran=?', [semester, tahun]):
        if not id_sems:
            try:
                sems = query.read_datas('semesters')
                id_sems = max(sems, key=lambda x: x[0])[0] + 1
            except:
                id_sems = 1
        values = [id_sems, semester, tahun, sks]
        query.create_data('semesters', ['id', 'semester_ke', 'tahun_ajaran', 'total_sks'], values)
        return True
    return False


def tambah_sems_courses(matkuls, semester, tahun_ajaran, imp=False):
    id_semester = query.read_datas('semesters', ['id'], 'semester_ke=? AND tahun_ajaran=?', [semester, tahun_ajaran])[0][0]
    if imp:
        if not matkuls == 'Belum diatur':
            array_matkul = matkuls.split(", ")
            for m in array_matkul:
                id_matkul = query.read_datas('courses', ['id'], f'unique_id={m}')[0][0]
                values = [id_semester, id_matkul]
                query.create_data('sems_courses', ["id_semester", "id_matkul"], values)
        return
    for i in range(0, len(matkuls)):
        kode, nama = matkuls[i].split(" - ")
        id_matkul = query.read_datas('courses', ['id'], 'unique_id=? AND nama_matkul=?', [kode, nama])[0][0]
        values = [id_semester, id_matkul]
        query.create_data('sems_courses', ["id_semester", "id_matkul"], values)


# Tambah data dari tabel
def simpan_data(table, conn, keys, data_iter):
    # drop table terkait
    st_pages.restart_table('semesters')
    data = [dict(zip(keys, row)) for row in data_iter]

    for x in data:
        id_sems, semester, tahun, sks = x['id'], x['semester_ke'], x['tahun_ajaran'], x['total_sks']
        if semester and tahun and sks:
            tambah_semester(id_sems, semester, tahun, sks)


def inside_tab1():
    semester = get_semester()
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
    st_pages.tampil_usage(True, True, True, 'Semester')

    df = pd.DataFrame(semester)
    edited_df = st.data_editor(
        df,
        column_order=['semester_ke', 'tahun_ajaran', 'total_sks', 'total_matkul'],
        column_config={
            "semester_ke": st.column_config.TextColumn("Semester"),
            "tahun_ajaran": st.column_config.TextColumn("Tahun Ajaran"),
            "total_sks": st.column_config.NumberColumn("Total SKS", format='%d SKS'),
            "total_matkul": st.column_config.NumberColumn("Total Mata Kuliah"),
        },
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=False
        )

    if savetable:
        savetable = False
        edited_df.to_sql('semesters', db.conn, if_exists='append', index=False, method=simpan_data)
        st.cache_resource.clear()
        st.rerun()
    
    if export_csv:
        export_csv = False
        st_pages.export_dataframe(semester, 'data semester.csv')


def inside_tab2():
    sems_list = ['Gasal', 'Genap']

    with st.form(key='semester_form'):
        cols = st.columns([1, 1, 1])
        with cols[0]:
            pilih_sems = st.selectbox('Jenis Semester', sems_list)
        with cols[1]:
            tahun_ajaran = st.text_input('Tahun Ajaran')
        with cols[2]:
            tot_sks = st.text_input('Total SKS')
        
        if st.form_submit_button('Simpan'):
            if pilih_sems and tahun_ajaran and tot_sks:
                if tot_sks.isdigit() or tahun_ajaran.isdigit():
                    if tambah_semester(None, pilih_sems, tahun_ajaran, tot_sks):
                        st.success('Data Semester berhasil ditambahkan', icon="✅")
                    else:
                        st.error('Data Semester sudah ada!', icon="🚨")
                else:
                    st.error('Tahun Ajaran dan Total SKS harus dalam satuan angka!', icon="🚨")
            else:
                st.error('Harap isi seluruh data!', icon="🚨")


def atur_matkul_multiselect(matkul):
    l_matkul = []
    list_matkul = get_sem_course(st.session_state['id_semester'], True)
    l_matkul = [index for matak in list_matkul for index, value in enumerate(matkul) if value == f'{matak[1]} - {matak[2]}']
    
    st.session_state['list_matkul_sms'] = l_matkul


def reset_session():
    st.session_state['id_semester'] = ""
    st.session_state['semester_ke'] = ""
    st.session_state['tahun_ajaran'] = ""
    st.session_state['total_sks'] = ""
    st.session_state['list_matkul_sms'] = []


def inside_tab3():
    semesters = query.read_datas('semesters')
    matkul = tampil_matkul()

    list_sems = [f'{sems[1]}, {sems[2]}' for sems in semesters] if semesters else ['Belum ada data']

    if 'id_semester' not in st.session_state:
        reset_session()

    cari = st.selectbox(
        'Pilih Semester', 
        list_sems, 
        disabled=False)
    cols1 = st.columns([1,1,4])
    with cols1[0]:
        submit = st.button('Pilih Semester')
    with cols1[1]:
        reset = st.button('Reset')

    # Pilih semester
    if submit:
        if cari != 'Belum ada data':
            st.session_state['semester_ke'], st.session_state['tahun_ajaran'] = cari.split(', ')
            for sems in semesters:
                if sems[1] == st.session_state['semester_ke'] and sems[2] == st.session_state['tahun_ajaran']:
                    st.session_state['id_semester'] = sems[0]
                    st.session_state['total_sks'] = sems[3]
                    break
            
            atur_matkul_multiselect(matkul)

    if reset:
        reset_session()
        
    if st.session_state['semester_ke']:
        value = st.session_state['semester_ke'] + ', ' + st.session_state['tahun_ajaran']
    else:
        value = ' '

    cols2 = st.columns([2, 1, 3])
    
    with cols2[0]:
        st.text_input('Semester, Tahun Ajaran', disabled=True, key='show_semester', value=value)
    with cols2[1]:
        st.text_input('Total SKS', disabled=True, key='show_nama', value=st.session_state['total_sks'])

    # Form ubah matkul
    with st.form(key='ubah_matkul_semester'):
        list_matkul = st.multiselect(
            'Pilih seluruh mata kuliah di semester ganjil', 
            matkul, default = [matkul[id] for id in st.session_state['list_matkul_sms']],
            placeholder = "Pilih setidaknya 1 mata kuliah")
        submit_btn2 = st.form_submit_button('Tambahkan mata kuliah')

        if submit_btn2:
            if not st.session_state['id_semester'] == '':
                query.delete_data('sems_courses', 'id_semester = ?', [st.session_state['id_semester']])
                tambah_sems_courses(
                    list_matkul, 
                    st.session_state['semester_ke'], 
                    st.session_state['tahun_ajaran']
                )
                st.success('Data semester berhasil diubah', icon="✅")
            else:
                st.error('Pilih semester terlebih dahulu!', icon="🚨")


def main():
    st.header("Data Semeter 📚")
    tab1, tab2, tab3 = st.tabs(
        ["Data Semester", "Tambah Data Semester", "Ubah Data Semester"])

    with tab1:
        check_n_delete_sems_courses()
        inside_tab1()
    with tab2:
        inside_tab2()
    with tab3:
        inside_tab3()


if not st_pages.check_login():
    st.error("Silahkan Login terlebih dahulu pada menu Utama")
else:
    main()

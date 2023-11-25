import streamlit as st
import pandas as pd
import time

from datas import database
from methods import st_pages, dbhelper

st_pages.clean_view()
db = database.Database()
dbu = dbhelper.DB_Umum()
dbr = dbhelper.DB_Ruang()


# Menambahkan data ruangan jika data ruangan dengan nisn dan max_siswa yang sama belum ada
def add_ruangan(id_ruang, nama_ruang, max_siswa):
    if not dbr.check_ruang(nama_ruang, max_siswa):
        if not id_ruang:
            try:
                ruangs = dbr.check_ruang(None, None)
                id_ruang = max(ruangs, key=lambda x: x[0])[0] + 1
            except:
                id_ruang = 1
        fields = ['id', 'nama_ruang', 'max_siswa']
        values = [id_ruang, nama_ruang, max_siswa]
        dbr.tambah_ruang(fields, values)
        return True
    return False


# Mengambil data seluruh ruangan
@st.cache_resource(show_spinner="Memuat data ruang kelas")
def get_ruangan():
    ruangs = dbr.check_ruang(None, None)
    result = []
    if ruangs:
        for ruangan in ruangs:
            result.append({"id":ruangan[0], "nama_ruang": ruangan[1], "max_siswa": ruangan[2]})
        return result
    
    result = [{"id":1 , "nama_ruang": None, "max_siswa": None}]
    return result


# Tambah data dari tabel
def simpan_data(table, conn, keys, data_iter):
    # drop table terkait
    dbu.restart_table('rooms')
    data = [dict(zip(keys, row)) for row in data_iter]

    for x in data:
        id_ruang, nama_ruang, max_siswa = x['id'], x['nama_ruang'], x['max_siswa']
        add_ruangan(id_ruang, nama_ruang, max_siswa)


# Konten dari tab1 Tampil data ruang
def inside_tab1():
    ruang = get_ruangan()
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
    st_pages.tampil_usage(True, True, True, 'Ruangan')

    df = pd.DataFrame(ruang)
    edited_df = st.data_editor(
        df, 
        # width=500,
        column_order=("nama_ruang", "max_siswa"),
        column_config={
            "id": st.column_config.TextColumn("No", default=int(len(df) + 1), disabled=True),
            "nama_ruang": "Nama Ruangan",
            "max_siswa": st.column_config.NumberColumn("Kapasitas Mahasiswa", format='%d Mahasiswa')
        },
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=False
        )

    if savetable:
        savetable = False
        edited_df.to_sql('rooms', db.conn, if_exists='append', index=False, method=simpan_data)
        st.cache_resource.clear()
        st.rerun()

    if export_csv:
        export_csv = False
        st_pages.export_dataframe(ruang, 'data ruangan.csv')


# Konten dari tab2 Tampil data ruangan
def inside_tab2():
    with st.form(key='my_form'):
        nama_ruang = st.text_input('Nama Ruangan')
        max_siswa = st.text_input('Kapasitas Mahasiswa')
        submit = st.form_submit_button('Tambah')

        if submit:
            if nama_ruang and max_siswa:
                if st_pages.is_number([max_siswa], ["kapasitas mahasiswa"]):
                    if add_ruangan(None, nama_ruang, max_siswa):
                        st.success('Data ruangan berhasil ditambahkan', icon="✅")
                        time.sleep(1)
                        st.cache_resource.clear()
                        st.rerun()
                    else:
                        st.error('Data ruangan sudah ada', icon="🚨")
            else:
                st.error('Harap isi seluruh data!', icon="🚨")


def import_section():
    raw_data = None
    raw_data, df = st_pages.tampilan_import(raw_data)
        
    if raw_data and st.button("💾 Tambahkan", key="add_ruangan"):
        try:
            for row in df.itertuples():
                add_ruangan(None, row[2], row[3])
            st.success('Data ruangan berhasil ditambahkan', icon="✅")
        except Exception as e:
            st.error("Terjadi kesalahan saat menambahkan data!", e, icon="🚨")


def main():
    st.header("Data Ruang Kelas 🏢")
    tab1, tab2 = st.tabs(["Data Ruangan", "Tambah Data Ruangan"])

    with tab1:
        inside_tab1()
    with tab2:
        with st.expander('Tambah Data Manual', expanded=False):
            inside_tab2()
        with st.expander('Import Data', expanded=False):
            import_section()


if not st_pages.check_login():
    st.error("Silahkan Login terlebih dahulu pada menu Utama")
else:
    main()
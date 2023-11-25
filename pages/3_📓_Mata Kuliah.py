import streamlit as st
import pandas as pd
import time

from datas import database
from methods import st_pages, dbhelper

st_pages.clean_view()
db = database.Database()
dbu = dbhelper.DB_Umum()
dbm = dbhelper.DB_Matkul()


# Menambahkan data Mata Kuliah jika data Mata Kuliah dengan kode atau nama yang sama belum ada
def add_matkul(id_matkul, kode_matkul, nama_matkul, metode, sks, peserta):
    kelas = None
    list_gak_ada_kelas = [211880260, 211870520] # Atur mata kuliah yang gak butuh kelas disini..
    if not dbm.check_matkul(kode_matkul, nama_matkul):
        if not id_matkul:
            try:
                matkuls = dbm.check_matkul(None, None)
                id_matkul = max(matkuls, key=lambda x: x[0])[0] + 1
            except:
                id_matkul = 1
        dbm.table_name = "courses"
        if peserta:
            kelas = (int(peserta) // 50) + 1

        if int(kode_matkul) in list_gak_ada_kelas:
            kelas = 1
        fields = ["id", "unique_id", "nama_matkul", "metode", 
                  "sks", "perkiraan_peserta", "kelas"]
        values = [id_matkul, kode_matkul, nama_matkul, 
                  metode, sks, peserta, kelas]
        try:
            dbm.tambah_matkul(fields, values)
            return True
        except:
            return
    return False


# Mengambil data seluruh Mata Kuliah
@st.cache_resource(show_spinner="Memuat data mata kuliah")
def get_matkul():
    matkuls = dbm.ambil_matkul()
    result = []

    if matkuls:
        for matkul in matkuls:
            result.append({"id": matkul[0], "unique_id": matkul[1], "nama_matkul": matkul[2], "metode": matkul[3], "sks": matkul[4], "perkiraan_peserta": matkul[5], "kelas": matkul[6]})
        return result
    
    result = [{"id": 1, "unique_id": None, "nama_matkul": None, "metode": None, "sks": None, "perkiraan_peserta": None, "kelas": None}]
    return result


# Tambah data dari tabel
def simpan_data(table, conn, keys, data_iter):
    # drop table terkait
    dbu.restart_table('courses')
    data = [dict(zip(keys, row)) for row in data_iter]

    for x in data:
        id, unique_id, nama_matkul, metode, sks, peserta = x['id'], x['unique_id'], x['nama_matkul'], x['metode'], x['sks'], x['perkiraan_peserta']
        add_matkul(id, unique_id, nama_matkul, metode, sks, peserta)


# Konten dari tab1 Tampil data ruang
def inside_tab1():
    matkul = get_matkul()
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
    st_pages.tampil_usage(True, True, True, 'Mata Kuliah')

    df = pd.DataFrame(matkul)
    edited_df = st.data_editor(
        df, 
        column_order=['unique_id', 'nama_matkul', 'metode', 'sks', 'perkiraan_peserta', 'kelas'],
        column_config={
            "unique_id": st.column_config.TextColumn("Kode"), 
            "nama_matkul": st.column_config.TextColumn("Nama Mata Kuliah"), 
            "metode": st.column_config.SelectboxColumn("Metode", required=True, options=['Offline', 'Online']),
            "sks": st.column_config.NumberColumn("SKS"),
            "perkiraan_peserta": st.column_config.NumberColumn("Peserta"),
            "kelas": st.column_config.NumberColumn("Kelas")
        },
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=False
        )

    if savetable:
        savetable = False
        edited_df.to_sql('courses', db.conn, if_exists='replace', index=False, method=simpan_data)
        st.cache_resource.clear()
        st.rerun()
    
    if export_csv:
        export_csv = False
        st_pages.export_dataframe(matkul, 'data mata_kuliah.csv')


# Konten dari tab2 Tampil data Mata Kuliah
def inside_tab2():
    with st.form(key='my_form'):        
        cols1 = st.columns([1,2])
        with cols1[0]:
            kode_matkul = st.text_input('Kode Mata Kuliah')
        with cols1[1]:
            nama_matkul = st.text_input('Nama Mata Kuliah')

        cols2 = st.columns([1, 1, 1])
        with cols2[0]:
            metode = st.selectbox('Metode Kuliah', ['Online', 'Offline'])
        with cols2[1]:
            sks = st.text_input('Jumlah SKS')
        with cols2[2]:
            peserta = st.text_input('Perkiraan Peserta')

        submit = st.form_submit_button('Tambah')

        if submit:
            if nama_matkul and metode and sks and peserta:
                if st_pages.is_number([sks, peserta], ['SKS', 'perkiraan peserta']):
                    if add_matkul(None, kode_matkul, nama_matkul, metode, sks, peserta):
                        st.success('Data mata kuliah berhasil ditambahkan', icon="✅")
                        time.sleep(1)
                        st.cache_resource.clear()
                        st.rerun()
                    else:
                        st.error('Data mata kuliah sudah ada', icon="🚨")
            else:
                st.error('Harap isi seluruh data!', icon="🚨")


# Konten dari tab3 Import data Mata Kuliah
def import_section():
    raw_data = None
    raw_data, df = st_pages.tampilan_import(raw_data)
    
    if raw_data and st.button("💾 Tambahkan", key="add_matkul"):
        try:
            for row in df.itertuples():
                add_matkul(None, row[2], row[3], row[4], row[5], row[6])
            st.success('Data mata kuliah berhasil ditambahkan', icon="✅")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat menambahkan data! {e}", icon="🚨")


def main():
    st.header("Data Mata Kuliah 📓")
    tab1, tab2 = st.tabs(
        ["Data Mata Kuliah", "Tambah Data Mata Kuliah"])

    with tab1:
        inside_tab1()
    with tab2:
        with st.expander("Tambah Data Manual", expanded=False):
            inside_tab2()
        with st.expander("Import Data", expanded=False):
            import_section()


if not st_pages.check_login():
    st.error("Silahkan Login terlebih dahulu pada menu Utama")
else:
    main()
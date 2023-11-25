import streamlit as st
import pandas as pd
import time

from datas import database
from methods import st_pages, dbhelper

st_pages.clean_view()
db = database.Database()
dbu = dbhelper.DB_Umum()
dbw = dbhelper.DB_Hari()


# Menambahkan data hari_jam jika data hari_jam dengan nama_hari dan waktu_kuliah yang sama belum ada
def add_hari_jam(id_waktu, nama_hari, waktu_kuliah, durasi):
    if not dbw.check_hari_jam(nama_hari, waktu_kuliah):
        if not id_waktu:
            try:
                waktus = dbw.check_hari_jam(None, None)
                id_waktu = max(waktus, key=lambda x: x[0])[0] + 1
            except:
                id_waktu = 1
        kode = nama_hari[:3].upper()
        unique_id = dbw.get_unique_id(nama_hari, kode)
        fields = ["id", "unique_id", "nama_hari", "waktu_kuliah", "durasi_jam"]
        values = [id_waktu, unique_id, nama_hari, waktu_kuliah, durasi]
        dbw.tambah_hari(fields, values)
        return True
    return False


# Mengambil data seluruh hari_jam
@st.cache_resource(show_spinner="Memuat data waktu pertemuan")
def get_hari_jam():
    hari_jams = dbw.check_hari_jam(None, None)
    result = []
    
    if hari_jams:
        for hari_jam in hari_jams:
            result.append({"id":hari_jam[0], "unique_id":hari_jam[1], "nama_hari": hari_jam[2], "waktu_kuliah": hari_jam[3], "durasi_jam": hari_jam[4]})
        return result
    
    result = [{"id":1, "unique_id":None, "nama_hari": None, "waktu_kuliah": None, "durasi_jam":None}]
    return result


# Tambah data dari tabel
def simpan_data(table, conn, keys, data_iter):
    # drop table terkait
    dbu.restart_table('daytimes')
    data = [dict(zip(keys, row)) for row in data_iter]

    for x in data:
        id_waktu, unique_id, hari, jam, durasi = x['id'], x['unique_id'], x['nama_hari'], x['waktu_kuliah'], x['durasi_jam']
        add_hari_jam(id_waktu, hari, jam, durasi)


def inside_tab1():
    hari_jam = get_hari_jam()
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
        hari_jam = get_hari_jam()
    if export_btn:
        export_csv = True
    
    # argumen = C, U, D, Section
    st_pages.tampil_usage(False, True, True, 'Hari & Jam')

    df = pd.DataFrame(hari_jam)
    edited_df = st.data_editor(
        df,
        column_order=("unique_id", "nama_hari", "waktu_kuliah", "durasi_jam"),
        column_config={
            "id": st.column_config.NumberColumn("No", default=len(df) + 1, disabled=True),
            "unique_id": st.column_config.TextColumn("Kode Hari"),
            "nama_hari": st.column_config.TextColumn("Nama Hari"), 
            "waktu_kuliah": st.column_config.TextColumn("Waktu", disabled=True),
            "durasi_jam": st.column_config.NumberColumn("Durasi", format='%d jam', disabled=True)
        },
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=False
        )

    if savetable:
        savetable = False
        edited_df.to_sql('daytimes', db.conn, if_exists='append', index=False, method=simpan_data)
        st.cache_resource.clear()
        st.rerun()
    
    if export_csv:
        export_csv = False
        st_pages.export_dataframe(hari_jam, 'data hari&jam.csv')


def inside_tab2():
    hari = [
        ["SEN", "Senin"], 
        ["SEL", "Selasa"], 
        ["RAB", "Rabu"], 
        ["KAM", "Kamis"], 
        ["JUM", "Jum'at"], 
        ["SAB", "Sabtu"]]
    
    jam = [
        [1,"07.00"],
        [2,"07.50"],
        [3,"08.40"],
        [4,"08.45"],
        [5,"09.35"],
        [6,"10.25"],
        [7,"10.30"],
        [8,"11.20"],
        [9,"12.10"],
        [10,"12.30"],
        [11,"13.20"],
        [12,"14.10"],
        [13,"14.15"],
        [14,"15.05"],
        [15,"15.15"],
        [16,"16.05"],
        [17,"16.10"],
        [18,"17.00"],
        [19,"17.50"]
        ]
    
    with st.form(key="day_times_form"):
        selected_hari = st.selectbox('Pilih Hari', [f"{h[0]} - {h[1]}" for h in hari])

        cols = st.columns([1,1])
        with cols[0]:
            jam_awal = st.selectbox('Pilih Waktu Mulai', [j[1] for j in jam])
        with cols[1]:
            jam_akhir = st.selectbox('Pilih Waktu Selesai', [j[1] for j in jam], index=1)
        
        submit_btn = st.form_submit_button('Tambah Hari & Jam')

        if submit_btn:
            if jam_awal == jam_akhir or jam_awal > jam_akhir:
                st.error('Periksa kembali waktu yang dipilih!', icon="🚨")
            else:
                # Mengambil hari yang dipilih
                hari_dipilih = None
                for h in hari:
                    if f"{h[0]} - {h[1]}" == selected_hari:
                        hari_dipilih = h[1]
                        break

                jam_awal_index = [j[1] for j in jam].index(jam_awal)
                jam_akhir_index = [j[1] for j in jam].index(jam_akhir)
                total_waktu = jam_akhir_index - jam_awal_index
                waktu_kuliah = str(jam_awal) + " - " + str(jam_akhir)

                if add_hari_jam(None, hari_dipilih, waktu_kuliah, total_waktu):
                    st.success('Data hari dan jam berhasil ditambahkan', icon="✅")
                    time.sleep(1)
                    st.cache_resource.clear()
                    st.rerun()
                else:
                    st.error('Data hari dan jam sudah ada!', icon="🚨")
    

def import_section():
    raw_data = None
    raw_data, df = st_pages.tampilan_import(raw_data)
    
    if raw_data and st.button("💾 Tambahkan", key="add_hari_jam"):
        try:
            for row in df.itertuples():
                add_hari_jam(None, row[3], row[4], row[5])
            st.success('Data hari dan jam berhasil ditambahkan', icon="✅")
        except:
            st.error("Terjadi kesalahan saat menambahkan data!", icon="🚨")


def main():
    st.header("Data Hari 🗓️ & Jam 🕖")
    tab1, tab2 = st.tabs(["Data Hari & Jam", "Tambah Data Hari & Jam"])

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
import streamlit as st
import pandas as pd

from io import StringIO

from . import dbhelper as dbh
from datas import database as dbs

db = dbs.Database()

def clean_view():
    st.set_page_config(
        page_title='Optimasi Jadwal - Rizumiya', 
        page_icon='🧊', layout='wide')

    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@st.cache_data
def create_database():
    db = dbs.Database()
    db.create_tables()


def restart_table(table_name):
    db = dbs.Database()
    db.drop_table(table_name)
    db.create_tables()


def check_login():
    if "login" not in st.session_state or st.session_state["login"]==False:
        return False
    elif st.session_state["login"]==True:
        return True
    else:
        return False


def tampil_usage(*args):
    c, u, d, section = args
    messages = []

    # Tambah data
    messages.append(f"- Tambah data : Tekan kolom paling bawah pada tabel, atau dapat menggunakan bagian 'Tambah Data {section}'") if c else messages.append(f"- Tambah data : **TIDAK DAPAT** dilakukan pada tabel, gunakan bagian 'Tambah Data {section}'")
    # Ubah data
    messages.append(f"- Ubah data : Seleksi kolom pada tabel untuk mengubah nilainya") if u else messages.append(f"- Ubah data : **TIDAK DAPAT** dilakukan pada tabel, gunakan bagian 'Ubah Data {section}'")
    # Hapus data
    messages.append(f"- Hapus data : Pilih baris pada tabel yang ingin dihapus, kemudian tekan delete pada keyboard") if d else messages.append(f"- Hapus data : **TIDAK DAPAT** dilakukan pada tabel, gunakan bagian 'Ubah Data {section}'")
    messages.append("- Tekan tombol 'Simpan' setiap kali terdapat perubahan pada tabel")

    if st.checkbox("Tampilkan cara penggunaan"):
        for message in messages:
            st.caption(message)


# Export dataframe menjadi csv
def export_dataframe(dataframe, file_name):
    df = pd.DataFrame(dataframe)
    df.to_csv(f'{file_name}', index=False)
    st.success('Data berhasil diekspor', icon="✅")


def tampilan_import(raw_data):
    data_hari_jam = st.file_uploader(
        label="Pilih file untuk dimuat",
        type=['csv'],
        accept_multiple_files=False,
        key="uploader"
    )

    if data_hari_jam is not None:
        bytes_data = data_hari_jam.getvalue()
        raw_data = StringIO(bytes_data.decode('utf-8'))
        st.success('File berhasil dimuat', icon="✅")

    if raw_data:
        df = pd.read_csv(data_hari_jam, index_col=False, delimiter = ',')
        if st.checkbox('Tampilkan file dalam bentuk tabel'):
            try:
                st.dataframe(df, use_container_width=True)
            except:
                st.error("Terjadi kesalahan saat membaca file yang dimuat!", icon="🚨")
    
    if raw_data:
        return raw_data, df
    return False, False


def is_number(values:list, variable:list):
    invalid = False
    for i, value in enumerate(values):
        if not value.isdigit():
            st.error(f'Nilai {variable[i]} harus berupa angka!', icon="🚨")
            invalid = True
    
    if invalid:
        return False
    return True


def get_unique_id(hari, kode):
    if hari:
        i = len(hari)
        unique_id = kode + str(i + 1)
        return unique_id

    unique_id = kode + str(1)
    return unique_id

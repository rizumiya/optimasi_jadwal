import streamlit as st
import time


from methods import st_pages, dbhelper
from algorithm.normalize import *
from algorithm.generate import run, Data

st_pages.clean_view()
dbs = dbhelper.DB_Semester()


def tampil_hasil():
    with open('hasil.txt', 'r') as file:
        text = file.read()
    return text


def main():
    st.header("Optimasi Jadwal 🧮")

    text = None

    with st.expander('Baca sebelum memulai optimasi jadwal'):
        st.info(
            '''
            **PERHATIAN**  \n
            Pastikan data berikut ini sudah ditambahkan dengan benar sebelum melakukan optimasi jadwal :
            - **Data Ruang Kelas**
            - **Data Hari** dan **Jam**
            - **Data Mata Kuliah**
            - **Data Dosen**
            - **Data Semester**
            ''', icon="ℹ️")
        st.warning(
            '''
            **PERINGATAN**  \n
            - Jangan menambahkan data yang tidak ingin diikutsertakan dalam proses optimasi jadwal
            - Jangan menambahkan data Hari dan Jam secara tidak terurut (e.g.: ~~Selasa, Jum'at, Kamis~~)
            - Proses optimasi jadwal menggunakan kode unik, pastikan setiap kode unik bersifat unik
            ''', icon="⚠️")
    
    with st.expander('Mulai proses optimasi jadwal'):
        req1 = st.checkbox('Seluruh data telah ditambahkan dengan benar')
        req2 = st.checkbox('Tidak ada data yang tidak diikutsertakan dalam proses optimasi jadwal')
        st.caption('Contoh : Data Dosen yang tidak memiliki mata kuliah yang diampu atau sebaliknya')
        req3 = st.checkbox('Data Hari dan Jam sudah diurutkan sebagaimana semestinya')
        st.caption('Contoh : Senin, Selasa, dst. **Bukan** Selasa, Senin, dst.')

        cols = st.columns([1, 1])
        semesters = dbs.ambil_data_semester(None, None)
        list_sems = [f'{sems[1]}, {sems[2]}' for sems in semesters] if semesters else ['Belum ada data']

        with cols[0]:
            cari = st.selectbox(
                'Pilih Semester yang ingin dibuatkan jadwal', 
                list_sems,
                disabled=False)
        
        colbtn = st.columns([1, 6])
        with colbtn[0]:
            jadwal_btn = st.button('Buat Jadwal', type='primary')
        with colbtn[1]:
            lihat_jadwal = st.button('Lihat hasil optimasi sebelumnya')
        

        if jadwal_btn:
            if req1 and req2 and req3:
                if cari != 'Belum ada data':
                    semester, tahun_ajaran = cari.split(', ')
                    id_semester = query.read_datas('semesters', None, 'semester_ke=? AND tahun_ajaran=?', [semester, tahun_ajaran])[0]
                    try:
                        start_time = time.time()
                        run_optimizer = run(Data(id_semester[0]))
                        if  run_optimizer[0] == 'OK':
                            text = tampil_hasil()
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        if elapsed_time >= 60:
                            elapsed_time = elapsed_time / 60
                            waktu = "{:.3f} menit".format(elapsed_time)
                        else:
                            waktu = "{:.3f} detik".format(elapsed_time)
                        st.write(f"Waktu yang dibutuhkan: {waktu}, dengan nilai fitnes : {run_optimizer[1]}")
                            
                    except Exception as e:
                        st.error('Pastikan seluruh data benar!', icon="🚨")
                        raise e
                else:
                    st.error('Jangan buang-buang waktu ku..', icon="🚨")
            else:
                st.error('Pastikan seluruh persyaratan di atas terpenuhi', icon="🚨")

        if lihat_jadwal:
            text = tampil_hasil()
    
    if text:
        st.code(text)


if not st_pages.check_login():
    st.error("Silahkan Login terlebih dahulu pada menu Utama")
else:
    main()
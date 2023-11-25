import streamlit as st
import time
import pandas as pd

from methods import st_pages, dbhelper


st_pages.clean_view()
st_pages.create_database()

@st.cache_data
def check_login(usern, passw):
    dbh = dbhelper.DB_Umum()
    dbh.table_name="users"
    dbh.condition="username=? AND password=?"
    dbh.values=[usern, passw]
    exist = dbh.read_data()
    if exist:
        return True
    return False


def login():
    st.title("Halaman Login")
    with st.form(key='login_form'):
        cols = st.columns([1, 1])
        with cols[0]:
            username = st.text_input("Username").strip()
        with cols[1]:
            password = st.text_input("Password", type="password").strip()
        login_button = st.form_submit_button('Login')

    if login_button:
        if check_login(username, password):
            st.session_state["login"] = True
            st.success("Login Berhasil!", icon="✅")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Kombinasi username dan password salah!")
            st.session_state["login"] = False


def hitung_data():
    query = dbhelper.Query()
    ruang = query.read_datas('rooms', ['COUNT(*)'])[0]
    waktu = query.read_datas('daytimes', ['COUNT(*)'])[0]
    matkul = query.read_datas('courses', ['COUNT(*)'])[0]
    dosen = query.read_datas('professors', ['COUNT(*)'])[0]

    return ruang[0], waktu[0], matkul[0], dosen[0]

    
def show_dashboard():
    r, w, m, d = hitung_data()

    cols = st.columns([1, 1, 1, 1])
    st.markdown(
        """
        <style>
        .rcorners4 {
            border-radius: 10px;
            background: #225199;
            padding: 20px;
            width: 240px;
            height: 150px;
            cursor: pointer;
            transition: transform 0.3s ease-in-out;
        }

        .rcorners4:hover {
            transform: translateY(-5px);
        } 

        .rcorners4 .emoji,
        .rcorners4 .data, 
        .rcorners4 .total {
            text-align: center;
        }

        .rcorners4 .emoji {
            padding: 0px 20px !important;
            font-size: 30px;
            margin: 0px;
        }

        .rcorners4 .data {
            font-size: 15px;
            margin: 0px;
        }

        .rcorners4 b.total {
            font-size: 24px;
            padding: 10px;
            display: block;
        }

        @media screen and (max-width: 1400px) {
            .rcorners4 {
                width: 200px;
                height: 120px;
            }
            
            .rcorners4 .emoji {
                padding: 0px 20px !important;
                font-size: 26px;
            }

            .rcorners4 .data {
                font-size: 12px;
            }

            .rcorners4 b.total {
                font-size: 16px;
                padding: 0px;
            }
        } 
        </style>
        """, unsafe_allow_html=True)

    with cols[0]:
        st.markdown(f"""
        <div class="rcorners4">
            <p class='emoji'>🏢</p>
            <p class='data'>Data Ruang Kelas</p>
            <b class='total'>{r}</b>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[1]:
        st.markdown(f"""
        <div class="rcorners4">
            <p class='emoji'>🗓️</p>
            <p class='data'>Data Hari & Jam</p>
            <b class='total'>{w}</b>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        st.markdown(f"""
        <div class="rcorners4">
            <p class='emoji'>📓</p>
            <p class='data'>Data Mata Kuliah</p>
            <b class='total'>{m}</b>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[3]:
        st.markdown(f"""
        <div class="rcorners4">
            <p class='emoji'>🧑🏻‍🏫</p>
            <p class='data'>Data Dosen</p>
            <b class='total'>{d}</b>
        </div>
        """, unsafe_allow_html=True)
        
    st.title("EduPlanr 📔")
    with open('intro.txt', 'r') as file:
        text = file.read()
    st.write(text)

        
def main():
    if not st_pages.check_login():
        login()
    else:
        show_dashboard()

if __name__ == '__main__':
    main()

import streamlit as st
import main
import mau

tab1, tab2 = st.tabs(["Trang chính", "Kết quả mẫu"])

with tab1:
    main.run()

with tab2:
    mau.run()
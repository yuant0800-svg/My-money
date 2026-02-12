import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="简易账本", page_icon="💰")

# 检查文件是否存在
DATA_FILE = "data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["时间", "分类", "金额", "备注"]).to_csv(DATA_FILE, index=False)

st.title("💰 我的极简账本")

with st.form("my_form", clear_on_submit=True):
    amount = st.number_input("金额", min_value=0.0)
    cat = st.selectbox("分类", ["吃饭", "交通", "购物", "娱乐", "其他"])
    note = st.text_input("备注")
    if st.form_submit_button("记录"):
        df = pd.read_csv(DATA_FILE)
        new_data = pd.DataFrame([[datetime.now().strftime("%m-%d %H:%M"), cat, amount, note]], columns=df.columns)
        pd.concat([df, new_data]).to_csv(DATA_FILE, index=False)
        st.success("记好啦！")

st.subheader("历史明细")
st.dataframe(pd.read_csv(DATA_FILE).iloc[::-1], use_container_width=True)

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt

# --- 1. 基础配置与用户库 ---
st.set_page_config(page_title="极简私人账本", page_icon="💰")

# 这里定义账号和密码
USERS = {
    "admin": "password123",
    "user1": "guest"
}

# --- 2. 登录逻辑 (纯手工打造，最稳) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user'] = ""

def login():
    st.title("🔐 请登录")
    user = st.text_input("用户名")
    pw = st.text_input("密码", type="password")
    if st.button("登录"):
        if user in USERS and USERS[user] == pw:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user
            st.rerun()
        else:
            st.error("用户名或密码错误")

if not st.session_state['logged_in']:
    login()
    st.stop()

# --- 3. 登录成功后的账本逻辑 ---
current_user = st.session_state['user']
st.sidebar.title(f"👤 {current_user}")
if st.sidebar.button("退出登录"):
    st.session_state['logged_in'] = False
    st.rerun()

# 数据文件独立化
DATA_FILE = f"data_{current_user}.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["时间", "分类", "金额", "备注"]).to_csv(DATA_FILE, index=False)

st.title("💰 我的私人账本")

# --- 4. 记账表单 ---
with st.form("add_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("金额", min_value=0.0)
    with col2:
        cat = st.selectbox("分类", ["吃饭", "交通", "购物", "娱乐", "居家", "其他"])
    note = st.text_input("备注")
    if st.form_submit_button("记录这一笔"):
        df = pd.read_csv(DATA_FILE)
        new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), cat, amount, note]], columns=df.columns)
        pd.concat([df, new_row]).to_csv(DATA_FILE, index=False)
        st.success("记好啦！")

# --- 5. 饼图与历史记录 ---
df = pd.read_csv(DATA_FILE)
if not df.empty:
    st.divider()
    # 简单的饼图统计
    st.subheader("📊 支出占比 (最近记录)")
    cat_data = df.groupby("分类")["金额"].sum()
    if cat_data.sum() > 0:
        fig, ax = plt.subplots()
        ax.pie(cat_data, labels=cat_data.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal') 
        st.pyplot(fig)
    
    st.subheader("📜 历史明细")
    st.dataframe(df.iloc[::-1], use_container_width=True)

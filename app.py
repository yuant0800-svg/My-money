import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. 页面样式美化 ---
st.set_page_config(page_title="Money+ 智能记账", page_icon="💰", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 账号系统 ---
USERS = {"admin": "password123", "user1": "guest"}

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🍀 Money+ 欢迎回来")
    col1, col2 = st.columns([1,1])
    with col1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type="password")
        if st.button("开启记账之旅", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("账号或密码不对哦")
    st.stop()

# --- 3. 智能数据修复逻辑 (解决 KeyError 问题) ---
user_file = f"data_{st.session_state.user}.csv"
cols = ["日期", "分类", "金额", "备注"]

def load_data():
    if not os.path.exists(user_file):
        return pd.DataFrame(columns=cols)
    try:
        temp_df = pd.read_csv(user_file)
        # 如果旧文件列名不对，强制修正
        if "日期" not in temp_df.columns:
            return pd.DataFrame(columns=cols)
        temp_df['日期'] = pd.to_datetime(temp_df['日期'])
        return temp_df
    except:
        return pd.DataFrame(columns=cols)

df = load_data()

# --- 4. 侧边栏 ---
st.sidebar.header(f"✨ {st.session_state.user} 的空间")
if st.sidebar.button("登出"):
    st.session_state.auth = False
    st.rerun()

# --- 5. 核心看板 ---
st.title("💸 财务概览")
m_col1, m_col2, m_col3 = st.columns(3)

now = datetime.now()
today_data = df[df['日期'].dt.date == now.date()]
month_data = df[df['日期'].dt.month == now.month]

m_col1.metric("今日消费", f"￥ {today_data['金额'].sum():,.2f}")
m_col2.metric("本月累计", f"￥ {month_data['金额'].sum():,.2f}")
m_col3.metric("总记账单", f"{len(df)} 笔")

st.divider()

# --- 6. 交互式操作区 ---
left, right = st.columns([1, 2])

with left:
    st.subheader("➕ 快速记账")
    with st.form("add_form", clear_on_submit=True):
        amount = st.number_input("金额", min_value=0.0, step=10.0)
        cat = st.selectbox("分类", ["🍱 餐饮", "🛍️ 购物", "🚗 交通", "🎮 娱乐", "🏠 居家", "🎁 其他"])
        note = st.text_input("备注")
        date = st.date_input("日期", now)
        if st.form_submit_button("确认支出", use_container_width=True):
            new_row = pd.DataFrame([[pd.to_datetime(date), cat, amount, note]], columns=cols)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(user_file, index=False)
            st.toast("记账成功！", icon='✅')
            st.rerun()

with right:
    st.subheader("📊 支出分布")
    if not df.empty:
        fig = px.pie(df, values='金额', names='分类', hole=0.6,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("还没有数据，先记一笔吧！")

# --- 7. 历史明细 ---
st.subheader("📑 账单明细")
st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)

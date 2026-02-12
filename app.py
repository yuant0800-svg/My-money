import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. 页面高级感配置 ---
st.set_page_config(page_title="Money+ 随身账本", page_icon="🛍️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    div[data-testid="metric-container"] {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); border: 1px solid #F0F2F6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 账号系统 ---
USERS = {"admin": "password123", "user1": "guest"}

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛍️ Money+ 欢迎使用")
    with st.container():
        u = st.text_input("账号")
        p = st.text_input("密码", type="password")
        if st.button("开始使用", use_container_width=True):
            if u in USERS and USERS[u] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("账号或密码不匹配")
    st.stop()

# --- 3. 智能数据加载 (核心修复逻辑) ---
user_file = f"data_{st.session_state.user}.csv"
COLS = ["日期", "分类", "金额", "备注"]

def load_clean_data():
    if not os.path.exists(user_file):
        return pd.DataFrame(columns=COLS)
    try:
        df = pd.read_csv(user_file)
        # 强制检查列名
        if list(df.columns) != COLS:
            return pd.DataFrame(columns=COLS)
        # 强制转换日期，错误的变为空值并删除
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        df = df.dropna(subset=['日期'])
        return df
    except:
        return pd.DataFrame(columns=COLS)

df = load_clean_data()

# --- 4. 界面布局 ---
st.sidebar.title(f"✨ {st.session_state.user}")
if st.sidebar.button("退出登录"):
    st.session_state.auth = False
    st.rerun()

st.title("💸 财务概览")

# 顶部三指标
now = datetime.now()
m_col1, m_col2, m_col3 = st.columns(3)

# 计算数据
if not df.empty:
    today_sum = df[df['日期'].dt.date == now.date()]['金额'].sum()
    month_sum = df[df['日期'].dt.month == now.month]['金额'].sum()
else:
    today_sum, month_sum = 0.0, 0.0

m_col1.metric("今日支出", f"￥ {today_sum:,.2f}")
m_col2.metric("本月累计", f"￥ {month_sum:,.2f}")
m_col3.metric("总记录", f"{len(df)} 笔")

st.divider()

# 操作区
left, right = st.columns([1, 1.5])

with left:
    st.subheader("➕ 记一笔")
    with st.form("add_form", clear_on_submit=True):
        amt = st.number_input("金额", min_value=0.0, step=1.0)
        category = st.selectbox("分类", ["🍱 餐饮", "🚗 交通", "购物", "娱乐", "居家", "其他"])
        note = st.text_input("备注")
        d = st.date_input("日期", now)
        if st.form_submit_button("保存账单", use_container_width=True):
            new_entry = pd.DataFrame([[pd.to_datetime(d), category, amt, note]], columns=COLS)
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(user_file, index=False)
            st.success("入账成功")
            st.rerun()

with right:
    st.subheader("📊 消费构成")
    if not df.empty and df['金额'].sum() > 0:
        fig = px.pie(df, values='金额', names='分类', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无消费统计")

# 底部记录
st.subheader("📑 历史记录")
st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)

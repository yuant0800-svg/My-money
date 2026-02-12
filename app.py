import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 页面配置 ---
st.set_page_config(page_title="Money+ 智能记账", layout="wide")

# --- 极简登录系统 ---
USERS = {"admin": "password123", "user1": "guest"}

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("💰 Money+ 欢迎回来")
    with st.container():
        user = st.text_input("用户名")
        pw = st.text_input("密码", type="password")
        if st.button("进入账本", use_container_width=True):
            if user in USERS and USERS[user] == pw:
                st.session_state.auth = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("信息不匹配，请重试")
    st.stop()

# --- 数据处理逻辑 ---
user_file = f"data_{st.session_state.username}.csv"
if not os.path.exists(user_file):
    pd.DataFrame(columns=["日期", "分类", "金额", "备注"]).to_csv(user_file, index=False)

def get_data():
    return pd.read_csv(user_file)

df = get_data()
df['日期'] = pd.to_datetime(df['日期'])

# --- 侧边栏 ---
st.sidebar.title(f"你好, {st.session_state.username}")
if st.sidebar.button("登出账户"):
    st.session_state.auth = False
    st.rerun()

# --- 主界面 ---
st.title("💸 我的资产看板")

# 顶部看板数据
col1, col2, col3 = st.columns(3)
today_sum = df[df['日期'].dt.date == datetime.now().date()]['金额'].sum()
month_sum = df[df['日期'].dt.month == datetime.now().month]['金额'].sum()

col1.metric("今日支出", f"￥{today_sum:,.2f}")
col2.metric("本月总计", f"￥{month_sum:,.2f}")
col3.metric("记账笔数", f"{len(df)} 笔")

st.divider()

# 记账区域与图表
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("➕ 记一笔")
    with st.form("input_form", clear_on_submit=True):
        amount = st.number_input("支出金额", min_value=0.0, step=1.0)
        cat = st.selectbox("选择分类", ["🍱 餐饮", "🚗 交通", "🛍️ 购物", "🎮 娱乐", "🏠 居家", "💊 医疗", "💡 水电", "🎁 其他"])
        note = st.text_input("备注 (可选)")
        date_pick = st.date_input("选择日期", datetime.now())
        if st.form_submit_button("确认入账", use_container_width=True):
            new_data = pd.DataFrame([[date_pick, cat, amount, note]], columns=df.columns)
            pd.concat([df, new_row]).to_csv(user_file, index=False) # 修正：应为 new_data
            # 修正拼接逻辑以防止报错
            updated_df = pd.concat([df, new_data], ignore_index=True)
            updated_df.to_csv(user_file, index=False)
            st.success("入账成功！")
            st.rerun()

with right_col:
    st.subheader("📊 支出结构分析")
    if not df.empty:
        # 使用 Plotly 制作精美环形图
        fig = px.pie(df, values='金额', names='分类', hole=0.5,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("尚无记录，开始记账吧！")

# 历史列表
st.subheader("📑 历史明细")
st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True)

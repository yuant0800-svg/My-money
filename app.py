import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. 强力数据修复函数 (解决报错的关键) ---
def get_clean_df(file_path, columns):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)
    try:
        data = pd.read_csv(file_path)
        # 如果列名不对或者数据为空，直接重置，防止 AttributeError
        if "日期" not in data.columns:
            return pd.DataFrame(columns=columns)
        # 转换日期格式
        data['日期'] = pd.to_datetime(data['日期'], errors='coerce')
        # 删除日期转换失败的坏数据
        data = data.dropna(subset=['日期'])
        return data
    except:
        return pd.DataFrame(columns=columns)

# --- 2. 页面配置与粉色美化 ---
st.set_page_config(page_title="Money+ Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFF9FA; }
    .metric-card { background-color: white; padding: 20px; border-radius: 20px; border: 1px solid #FFD1DC; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 50px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; color: #FF6B8B; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 极简登录 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("💖 Money+ 欢迎回来")
    u = st.text_input("账号"); p = st.text_input("密码", type="password")
    if st.button("开启梦幻账本", use_container_width=True):
        if u == "admin" and p == "password123":
            st.session_state.auth = True; st.session_state.user = u; st.rerun()
    st.stop()

# --- 4. 加载数据 ---
USER_FILE = f"data_{st.session_state.user}_v4.csv" # 换个文件名，彻底告别旧坏数据
COLS = ["日期", "类型", "分类", "金额", "备注"]
df = get_clean_df(USER_FILE, COLS)

# --- 5. 页面布局 ---
st.title("📑 我的梦幻账本")

tab1, tab2, tab3 = st.tabs(["📝 明细", "📊 分析", "⚙️ 设置"])

with tab1:
    # 顶部指标 (复刻截图 1)
    c1, c2, c3 = st.columns(3)
    now = datetime.now()
    
    # 使用更稳健的过滤方式，不直接用 .dt
    month_df = df[df['日期'].map(lambda x: x.month == now.month and x.year == now.year)] if not df.empty else df
    
    income = month_df[month_df['类型'] == "收入"]['金额'].sum()
    expense = month_df[month_df['类型'] == "支出"]['金额'].sum()
    
    c1.metric("总额", f"￥{income - expense:,.2f}")
    c2.metric("收入", f"￥{income:,.2f}")
    c3.metric("支出", f"-￥{expense:,.2f}")

    st.divider()

    # 记账表单
    with st.expander("✨ 点击记一笔"):
        with st.form("add"):
            a1, a2, a3 = st.columns(3)
            t_type = a1.selectbox("类型", ["支出", "收入"])
            t_amt = a2.number_input("金额", min_value=0.0)
            t_cat = a3.selectbox("分类", ["🍱 饮食", "交通", "购物", "社交", "医疗", "其他"])
            t_note = st.text_input("备注")
            t_date = st.date_input("日期", now)
            if st.form_submit_button("确认保存", use_container_width=True):
                new_row = pd.DataFrame([[pd.to_datetime(t_date), t_type, t_cat, t_amt, t_note]], columns=COLS)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(USER_FILE, index=False)
                st.success("入账成功！")
                st.rerun()

    st.subheader("🗓️ 历史单据")
    st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🎨 消费分布")
    exp_only = df[df['类型'] == "支出"]
    if not exp_only.empty:
        fig = px.pie(exp_only, values='金额', names='分类', hole=0.7, 
                     color_discrete_sequence=px.colors.sequential.RdPu)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("还没有支出数据哦")

with tab3:
    if st.button("⚠️ 清空所有数据并重置"):
        if os.path.exists(USER_FILE): os.remove(USER_FILE)
        st.rerun()

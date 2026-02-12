import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. 强效防御逻辑：如果数据坏了，自动重置 ---
def load_and_fix_data(file_path):
    cols = ["日期", "类型", "分类", "金额", "备注"]
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(file_path)
        # 核心检查：如果缺少关键列，直接舍弃旧数据，防止 KeyError
        if "日期" not in df.columns or "金额" not in df.columns:
            return pd.DataFrame(columns=cols)
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        return df.dropna(subset=['日期'])
    except:
        return pd.DataFrame(columns=cols)

# --- 2. 页面配置 (复刻 Money+ 樱花粉) ---
st.set_page_config(page_title="Money+ Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFF5F7; }
    [data-testid="stMetric"] { background-color: white; border-radius: 15px; border: 2px solid #FFC1CC; padding: 15px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #FFC1CC; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 简单的登录系统 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("💖 Money+ 欢迎回来")
    u = st.text_input("账号", value="admin")
    p = st.text_input("密码", type="password")
    if st.button("进入梦幻账本", use_container_width=True):
        if u == "admin" and p == "password123":
            st.session_state.auth = True; st.rerun()
    st.stop()

# --- 4. 数据初始化 (使用新文件名规避旧数据) ---
DATA_FILE = "money_v6_data.csv" 
df = load_and_fix_data(DATA_FILE)

# --- 5. 核心功能区 (复刻截图中的 Tabs) ---
tab_list, tab_chart, tab_asset = st.tabs(["📝 记账明细", "📊 图表分析", "📈 资产趋势"])

with tab_list:
    # 顶部数据卡片
    now = datetime.now()
    if not df.empty:
        # 使用更稳健的过滤，不直接用 .dt 访问，防止 AttributeError
        this_month_df = df[df['日期'].map(lambda x: x.month == now.month and x.year == now.year)]
        income = this_month_df[this_month_df['类型'] == "收入"]['金额'].sum()
        expense = this_month_df[this_month_df['类型'] == "支出"]['金额'].sum()
    else:
        income, expense = 0.0, 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("总资产", f"￥{income - expense:,.2f}")
    c2.metric("本月收入", f"￥{income:,.2f}")
    c3.metric("本月支出", f"￥{expense:,.2f}")

    st.divider()

    # 快捷记账表单
    with st.expander("➕ 记一笔 (复刻分类图标)"):
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            t_type = col1.radio("方向", ["支出", "收入"], horizontal=True)
            t_date = col2.date_input("日期", now)
            
            # 复刻截图中的可爱分类
            cats = ["🍱 餐饮", "🚗 交通", "🛍️ 购物", "🎮 娱乐", "🏠 居家", "🏥 医疗", "💰 工资", "🎁 礼物"]
            t_cat = st.selectbox("分类选择", cats)
            t_amt = st.number_input("金额", min_value=0.0)
            t_note = st.text_input("备注 (选填)")
            
            if st.form_submit_button("保存账单", use_container_width=True):
                new_row = pd.DataFrame([[pd.to_datetime(t_date), t_type, t_cat, t_amt, t_note]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.toast("入账成功！💖")
                st.rerun()

    # 历史列表
    st.subheader("🗓️ 历史账单")
    if not df.empty:
        st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("还没有账单，点击上方“记一笔”开始吧！")

with tab_chart:
    st.subheader("🍩 支出构成分析")
    exp_df = df[df['类型'] == "支出"]
    if not exp_df.empty:
        fig = px.pie(exp_df, values='金额', names='分类', hole=0.6, 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无分析数据")

with tab_asset:
    st.subheader("📈 净资产增长趋势")
    if not df.empty:
        trend = df.sort_values("日期").copy()
        trend['val'] = trend.apply(lambda x: x['金额'] if x['类型'] == "收入" else -x['金额'], axis=1)
        trend['balance'] = trend['val'].cumsum()
        st.line_chart(trend.set_index("日期")['balance'], color="#FF6B8B")
      

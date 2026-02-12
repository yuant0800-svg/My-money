import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. 深度美化：复刻 Money+ 樱花粉主题 ---
st.set_page_config(page_title="Money+ 梦幻账本", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFF5F7; }
    .metric-box { background-color: white; padding: 20px; border-radius: 20px; border: 2px solid #FFC1CC; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { background-color: #FFC1CC; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心修复逻辑：彻底解决 AttributeError ---
def safe_load_data(file_name):
    cols = ["日期", "类型", "分类", "金额", "备注"]
    if not os.path.exists(file_name):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(file_name)
        # 如果列名不对，直接重置
        if "日期" not in df.columns: return pd.DataFrame(columns=cols)
        # 核心修复：强制转换日期，无法转换的直接删掉，确保 .dt 能用
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        df = df.dropna(subset=['日期']) 
        return df
    except:
        return pd.DataFrame(columns=cols)

# --- 3. 简单的账户 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("💖 Money+ 欢迎你")
    u = st.text_input("账号"); p = st.text_input("密码", type="password")
    if st.button("进入账本", use_container_width=True):
        if u == "admin" and p == "password123":
            st.session_state.auth = True; st.session_state.user = u; st.rerun()
    st.stop()

# --- 4. 数据读取 ---
# 换一个全新的文件名 v5，彻底避开你之前的旧坏数据文件
DB_FILE = f"money_plus_v5_{st.session_state.user}.csv"
df = safe_load_data(DB_FILE)

# --- 5. 功能布局 (复刻截图中的底部菜单) ---
tab_home, tab_chart, tab_asset = st.tabs(["📝 记账明细", "📊 图表分析", "📈 资产趋势"])

with tab_home:
    # 顶部看板 (复刻截图中的预算条)
    now = datetime.now()
    # 稳健的月份过滤，不报错
    month_mask = (df['日期'].dt.month == now.month) & (df['日期'].dt.year == now.year) if not df.empty else False
    this_month_df = df[month_mask]
    
    exp = this_month_df[this_month_df['类型']=="支出"]['金额'].sum()
    inc = this_month_df[this_month_df['类型']=="收入"]['金额'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("总结余", f"￥{inc - exp:,.2f}")
    c2.metric("本月收入", f"￥{inc:,.2f}")
    c3.metric("本月支出", f"￥{exp:,.2f}")

    st.write("---")
    
    # 记账表单 (复刻截图中的图标分类选择)
    with st.expander("✨ 记一笔新账"):
        with st.form("add_bill", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            t_type = col_a.radio("类型", ["支出", "收入"], horizontal=True)
            t_date = col_b.date_input("日期", now)
            
            t_cat = st.selectbox("分类", ["🍱 饮食", "🚗 交通", "🛍️ 购物", "🎮 娱乐", "🏠 居家", "🏥 医疗", "💰 工资", "🎁 零花钱"])
            t_amt = st.number_input("金额", min_value=0.0)
            t_note = st.text_input("备注")
            
            if st.form_submit_button("保存到账本", use_container_width=True):
                new_data = pd.DataFrame([[pd.to_datetime(t_date), t_type, t_cat, t_amt, t_note]], columns=df.columns)
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("已保存！")
                st.rerun()

    st.subheader("🗓️ 最近账单")
    st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)

with tab_chart:
    st.subheader("🍩 支出构成")
    exp_df = df[df['类型'] == "支出"]
    if not exp_df.empty:
        fig = px.pie(exp_df, values='金额', names='分类', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("还没有支出数据")

with tab_asset:
    st.subheader("📈 资产起伏图")
    if not df.empty:
        df_sorted = df.sort_values("日期")
        df_sorted['计算金额'] = df_sorted.apply(lambda x: x['金额'] if x['类型']=="收入" else -x['金额'], axis=1)
        df_sorted['累计资产'] = df_sorted['计算金额'].cumsum()
        st.line_chart(df_sorted.set_index("日期")['累计资产'], color="#FF6B8B")

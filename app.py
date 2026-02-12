import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. 网页页面设计 (CSS 注入) ---
# 这部分就是你刚才问的“装修”代码，我把它放在了最开头
st.set_page_config(page_title="Money+ 梦幻账本", layout="wide")

st.markdown("""
    <style>
    /* 全局背景色：柔和奶白粉 */
    .stApp {
        background-color: #FFF9FA;
    }
    /* 顶部指标卡片：白色圆角+粉色阴影 */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(255, 182, 193, 0.15);
        padding: 20px;
        border: 1px solid #FFE4E8;
    }
    /* 按钮：樱花粉圆角 */
    .stButton>button {
        border-radius: 25px;
        background-color: #FF6B8B;
        color: white;
        border: none;
        height: 3em;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF8EAA;
        transform: scale(1.02);
    }
    /* 标签页导航栏样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #FF6B8B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 账号系统 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🍭 Money+ 登录")
    u = st.text_input("用户名", value="admin")
    p = st.text_input("密码", type="password")
    if st.button("开启梦幻账本"):
        if (u == "admin" and p == "password123") or (u == "user1" and p == "guest"):
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
    st.stop()

# --- 3. 稳健数据加载 ---
USER_FILE = f"money_v7_{st.session_state.user}.csv"
COLS = ["日期", "类型", "分类", "金额", "备注"]

def load_data():
    if not os.path.exists(USER_FILE): return pd.DataFrame(columns=COLS)
    try:
        df = pd.read_csv(USER_FILE)
        df['日期'] = pd.to_datetime(df['日期'])
        return df
    except: return pd.DataFrame(columns=COLS)

df = load_data()

# --- 4. 页面布局 (复刻 App 看板) ---
st.title("💖 我的资产看板")

# 顶部三张精美卡片
c1, c2, c3 = st.columns(3)
now = datetime.now()
month_df = df[df['日期'].map(lambda x: x.month == now.month and x.year == now.year)] if not df.empty else df
inc = month_df[month_df['类型'] == "收入"]['金额'].sum()
exp = month_df[month_df['类型'] == "支出"]['金额'].sum()

c1.metric("总结余", f"￥{inc - exp:,.2f}")
c2.metric("本月收入", f"￥{inc:,.2f}")
c3.metric("本月支出", f"￥{exp:,.2f}")

st.write("---")

# 模拟 App 底部导航
tab1, tab2, tab3 = st.tabs(["📝 记账", "📊 分析", "📈 趋势"])

with tab1:
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.subheader("➕ 快速记账")
        with st.form("my_form", clear_on_submit=True):
            t_type = st.radio("账单类型", ["支出", "收入"], horizontal=True)
            t_amt = st.number_input("金额", min_value=0.0, step=10.0)
            # 这里的 Emoji 分类就是画龙点睛之笔
            t_cat = st.selectbox("分类", ["🍱 餐饮", "🛍️ 购物", "🚗 交通", "🎮 娱乐", "🏠 居家", "🏥 医疗", "💰 工资", "🎁 礼物"])
            t_date = st.date_input("日期", now)
            t_note = st.text_input("备注")
            if st.form_submit_button("保存账单"):
                new_row = pd.DataFrame([[pd.to_datetime(t_date), t_type, t_cat, t_amt, t_note]], columns=COLS)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(USER_FILE, index=False)
                st.rerun()
    
    with col_r:
        st.subheader("🗓️ 历史明细")
        st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🍩 消费构成 (支出)")
    exp_df = df[df['类型'] == "支出"]
    if not exp_df.empty:
        # 使用 Plotly 制作空心圆环图
        fig = px.pie(exp_df, values='金额', names='分类', hole=0.6,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("还没有支出数据记录记录哦~")

with tab3:
    st.subheader("📈 资产增长曲线")
    if not df.empty:
        df_t = df.sort_values("日期").copy()
        df_t['val'] = df_t.apply(lambda x: x['金额'] if x['类型'] == "收入" else -x['金额'], axis=1)
        df_t['balance'] = df_t['val'].cumsum()
        st.line_chart(df_t.set_index("日期")['balance'], color="#FF6B8B")

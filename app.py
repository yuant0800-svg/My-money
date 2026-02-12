import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- 1. 视觉风格复刻 (粉色系) ---
st.set_page_config(page_title="Money+ 复刻版", page_icon="💖", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFF5F7; }
    .main-card { background-color: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2); margin-bottom: 20px; }
    .pink-header { color: #FF6B8B; font-weight: bold; }
    div[data-testid="stMetric"] { background-color: #FFF; border-radius: 15px; padding: 10px; border: 1px solid #FFE4E8; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 账号系统 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("💖 Money+ 欢迎你")
    u = st.text_input("用户名"); p = st.text_input("密码", type="password")
    if st.button("进入梦幻账本", use_container_width=True):
        if u == "admin" and p == "password123":
            st.session_state.auth = True; st.session_state.user = u; st.rerun()
    st.stop()

# --- 3. 数据初始化 ---
user_file = f"money_plus_{st.session_state.user}.csv"
COLS = ["日期", "类型", "分类", "金额", "备注"]

def load_data():
    if not os.path.exists(user_file): return pd.DataFrame(columns=COLS)
    df = pd.read_csv(user_file)
    df['日期'] = pd.to_datetime(df['日期'])
    return df

df = load_data()

# --- 4. 底部导航栏模拟 ---
tab1, tab2, tab3 = st.tabs(["📝 记账明细", "📊 图表分析", "📈 资产趋势"])

# --- 页面 1：记账明细 (复刻截图 1 & 2) ---
with tab1:
    # 顶部预算看板
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    this_month = df[df['日期'].dt.month == datetime.now().month]
    income = this_month[this_month['类型'] == "收入"]['金额'].sum()
    expense = this_month[this_month['类型'] == "支出"]['金额'].sum()
    
    col1.metric("总额 (余额)", f"￥{income - expense:,.2f}")
    col2.metric("本月收入", f"￥{income:,.2f}")
    col3.metric("本月支出", f"-￥{expense:,.2f}", delta_color="inverse")
    
    # 预算进度条 (模拟截图中的 9%)
    budget = 10000.0
    progress = min(expense / budget, 1.0)
    st.write(f"📅 本月预算使用率: {progress*100:.1f}%")
    st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)

    # 快捷记账
    with st.expander("➕ 记一笔 (点击展开)"):
        with st.form("add_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            tt = c1.selectbox("类型", ["支出", "收入"])
            amt = c2.number_input("金额", min_value=0.0)
            cat = c3.selectbox("分类", ["饮食", "交通", "购物", "娱乐", "居家", "社交", "医疗", "其他"])
            note = st.text_input("备注")
            date = st.date_input("日期", datetime.now())
            if st.form_submit_button("确认保存", use_container_width=True):
                new_row = pd.DataFrame([[pd.to_datetime(date), tt, cat, amt, note]], columns=COLS)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(user_file, index=False); st.rerun()

    # 历史列表 (复刻截图中的日历感列表)
    st.subheader("🗓️ 历史账单")
    st.dataframe(df.sort_values("日期", ascending=False), use_container_width=True, hide_index=True)

# --- 页面 2：图表分析 (复刻截图 3) ---
with tab2:
    st.subheader("🍩 支出构成分析")
    exp_df = df[df['类型'] == "支出"]
    if not exp_df.empty:
        fig = px.pie(exp_df, values='金额', names='分类', hole=0.6,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(annotations=[dict(text='总支出', x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("本月还没有支出数据哦")

# --- 页面 3：资产趋势 (复刻截图 7) ---
with tab3:
    st.subheader("📈 净资产趋势")
    if not df.empty:
        trend_df = df.sort_values("日期").copy()
        trend_df['调整金额'] = trend_df.apply(lambda x: x['金额'] if x['类型'] == "收入" else -x['金额'], axis=1)
        trend_df['余额'] = trend_df['调整金额'].cumsum()
        
        fig_line = px.area(trend_df, x="日期", y="余额", line_shape="spline",
                          color_discrete_sequence=['#FF6B8B'])
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

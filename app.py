import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import streamlit_authenticator as stauth
import matplotlib.pyplot as plt

# --- 配置页面 ---
st.set_page_config(page_title="多用户极简账本", page_icon="📈", layout="centered")

# --- 认证配置 ---
# 注意：在生产环境中，这些应该从环境变量或更安全的地方加载
# 密码是哈希过的，不能直接明文存储。这里为了演示，使用了一个简单的哈希。
# 实际应用中，用户注册时应进行哈希。
names = ['admin', 'user1']
usernames = ['admin', 'user1']
# 预计算一些密码哈希值
# import bcrypt
# print(bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()))
# print(bcrypt.hashpw("guest".encode('utf-8'), bcrypt.gensalt()))
hashed_passwords = ['$2b$12$DqXb.2S.G.yXp.B0WJ.P.jEa9cQY4kM8.tLp.x0n.xJmY9w/k0.tLp',  # password123
                    '$2b$12$R.S.W.1.L.m.C.f.Z.p.Y.n.o.Q.s.T.u.v.a.D.e.F.g.h.i.j.k.l.m.n'] # guest
# 为方便演示，这里直接给出了哈希值，实际应在用户注册时生成。
# password123 对应的哈希值 (请替换成您自己密码的哈希值)
# guest 对应的哈希值

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=30)

# --- 登录 ---
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('用户名/密码错误')
elif authentication_status == None:
    st.warning('请输入您的用户名和密码')
elif authentication_status:
    # --- 登录成功后的应用逻辑 ---
    st.sidebar.title(f"欢迎, {name}")
    authenticator.logout('退出登录', 'sidebar')

    # 每个用户一个独立的数据文件
    DATA_FILE = f"{username}_expenses.csv"

    # 初始化数据文件
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["时间", "分类", "金额", "备注"]).to_csv(DATA_FILE, index=False)

    def load_data():
        return pd.read_csv(DATA_FILE)

    def save_data(time, category, amount, note):
        df = load_data()
        new_row = pd.DataFrame([[time, category, amount, note]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        return df # 返回更新后的数据框

    st.title("💰 个人极简账本")

    # --- 记账表单 ---
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("金额 (￥)", min_value=0.0, step=0.1)
        with col2:
            category = st.selectbox("分类", ["餐饮", "交通", "购物", "娱乐", "居家", "学习", "健身", "其他"])
        
        note = st.text_input("备注 (选填)")
        submit = st.form_submit_button("记录这一笔")

        if submit:
            if amount > 0:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated_df = save_data(now, category, amount, note)
                st.success(f"已记录: {category} ￥{amount}")
            else:
                st.error("请输入有效金额")

    # --- 统计和图表 ---
    st.divider()
    df_display = load_data()

    if not df_display.empty:
        df_display['时间'] = pd.to_datetime(df_display['时间']) # 转换为日期时间类型

        # 今日统计
        today = datetime.now().date()
        today_total = df_display[df_display['时间'].dt.date == today]['金额'].sum()
        st.metric("今日总支出", f"￥{today_total:.2f}")

        # 一周饼图
        st.subheader("最近一周支出概览")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        recent_week_df = df_display[(df_display['时间'] >= start_date) & (df_display['时间'] <= end_date)]
        
        if not recent_week_df.empty:
            category_totals = recent_week_df.groupby('分类')['金额'].sum()
            
            # 过滤掉金额为0的分类，避免饼图绘制问题
            category_totals = category_totals[category_totals > 0]

            if not category_totals.empty:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=90,
                       wedgeprops={'edgecolor': 'black', 'linewidth': 0.5},
                       colors=plt.cm.Paired.colors) # 使用Paired颜色方案
                ax.axis('equal') # 确保饼图是圆的
                st.pyplot(fig)
            else:
                st.info("最近一周还没有支出记录。")
        else:
            st.info("最近一周还没有支出记录。")

        # 最近记录
        st.subheader("所有历史记录")
        st.dataframe(df_display.sort_values(by='时间', ascending=False), use_container_width=True)
    else:
        st.info("还没有记录，开始记账吧！")


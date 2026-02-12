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
# --- 修正后的认证配置 ---
# 定义一个配置字典，这是新版本插件的要求
config = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': '管理员',
                'password': 'password123'  # 简单起见，暂时用明文测试
            },
            'user1': {
                'name': '用户1',
                'password': 'guest'
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'some_signature_key',
        'name': 'some_cookie_name'
    }
}

# 使用新版本的初始化方式
https://github.com/yuant0800-svg/My-money/blob/main/app.py

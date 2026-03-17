import streamlit as st
import pandas as pd
import os
import time
import threading
import requests

# --- 0. 保活逻辑 ---
def keep_alive():
    while True:
        try:
            url = "https://policy-search-vk.streamlit.app/" 
            requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        except: pass
        time.sleep(300)

if "keep_alive_started" not in st.session_state:
    threading.Thread(target=keep_alive, daemon=True).start()
    st.session_state.keep_alive_started = True

# --- 1. 页面配置 ---
st.set_page_config(page_title="政策直通车", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 终极 CSS 注入方案 ---
st.markdown("""
    <style>
    /* 全局背景 */
    .stApp { background-color: #ffffff; }

    /* 标题与胶囊线 */
    .main-title { font-size: 24px !important; font-weight: 700; color: #003366; text-align: center; padding-top: 15px; }
    .capsule-line-container { display: flex; justify-content: center; margin-bottom: 25px; }
    .capsule-line {
        width: 100px; height: 4px; background: #004a99; border-radius: 10px; position: relative;
        background: linear-gradient(90deg, transparent, #004a99, transparent);
    }

    /* --- 首页按钮：强制染色逻辑 --- */
    /* 锁定 ID 容器内的按钮 */
    div#national-btn button {
        background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%) !important;
        color: #0369a1 !important;
        border-radius: 50px !important;
        height: 60px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    div#local-btn button {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%) !important;
        color: #15803d !important;
        border-radius: 50px !important;
        height: 60px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }

    /* --- 返回主页按钮：真正的微型化 --- */
    div#back-btn button {
        height: 28px !important;
        padding: 0 10px !important;
        font-size: 11px !important; /* 极小字号 */
        color: #888 !important;
        background-color: #f8f9fa !important;
        border: 1px solid #eee !important;
        border-radius: 4px !important;
        width: auto !important;
        min-width: 80px !important;
    }
    div#back-btn button:hover { color: #004a99 !important; border-color: #004a99 !important; }

    /* 文件卡片 */
    .file-card {
        background-color: #fcfdfe; padding: 12px; border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3; border-radius: 6px; margin-bottom: 10px;
    }
    .footer-note { text-align: center; padding: 25px; color: #999; font-size: 13px; border-top: 1px solid #f9f9f9; }
    
    /* Excel 指标卡片 */
    .metric-card {
        padding: 8px; border-radius: 6px; border-left: 4px solid;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 导航逻辑 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

# --- 4. 界面渲染 ---

st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)
st.markdown('<div class="capsule-line-container"><div class="capsule-line"></div></div>', unsafe_allow_html=True)

# L1: 首页 (使用 ID 容器确保底色生效)
if st.session_state.step == 'L1':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, mid, c3 = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div id="national-btn">', unsafe_allow_html=True)
        st.button("国家级政策", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        
        st.markdown('<div id="local-btn">', unsafe_allow_html=True)
        st.button("地方性政策", use_container_width=True, on_click=nav_to, args=('L2', "地方"))
        st.markdown('</div>', unsafe_allow_html=True)

# L2: 内容展示页
elif st.session_state.step == 'L2':
    # 微型返回按钮
    st.markdown('<div id="back-btn">', unsafe_allow_html=True)
    st.button("⬅️ 返回主页", on_click=nav_to, args=('L1',))
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.l1 == "国家":
        dept = st.selectbox("请选择政策部门", ["国家医保局", "国家卫健委"])
        st.markdown(f"#### 📂 {dept}")
        
        # 数据结构 (保持之前逻辑)
        nat_struct = {
            "国家卫健委": {
                "抗菌药物管理办法": ["2012年抗菌药物管理办法", "2015年抗菌药物评价指标"],
                "绩效监测": ["2025版公立医院绩效监测手册"],
                "基本药物": ["基药目录管理办法通知", "国家基本药物目录管理办法", "2026版基药目录管理办法"],
                "医院管理质控": ["2025年药事管理医疗质量控制指标"], "超品规备案": [], "其他": []
            },
            "国家医保局": {
                "国谈落地": ["2025年医保药品目录通知", "做好谈判药品落地工作的通知"],
                "红黄标": ["挂网药品价格风险预警标识通知"],
                "基金监管": ["2026年医保基金监管工作通知"],
                "其他": ["药品RWE价值评价指南", "RWE国家可信点公约", "支持创新药高质量发展若干措施", "药品RWE指南汇总"],
                "VBP": [], "DRG/DIP": []
            }
        }
        for cat, files in nat_struct[dept].items():
            with st.expander(f"🔹 {cat}", expanded=False):
                if not files: st.caption("暂无相关文件")
                else:
                    for f in files:
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="#" style="font-size:12px; color:#0066cc;">🔗 查看原文</a></div>', unsafe_allow_html=True)

    else: # 地方性政策
        biz_options = ["国谈落地", "集采", "超品规备案", "VBP", "DRG/DIP", "其他"]
        biz = st.selectbox("请选择政策领域", biz_options)
        
        if biz == "集采":
            st.markdown("##### 📁 广东联盟接续采购")
            st.markdown('<div class="file-card"><b>【广东】集采药品接续采购公告(1-4号)</b><br><a href="#" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)
        # ... 其他业务逻辑 ...

# --- 5. 注脚 ---
st.markdown('<div class="footer-note">© 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网</div>', unsafe_allow_html=True)

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
            headers = {"User-Agent": "Mozilla/5.0"}
            requests.get(url, headers=headers)
        except: pass
        time.sleep(300)

if "keep_alive_started" not in st.session_state:
    t = threading.Thread(target=keep_alive, daemon=True)
    t.start()
    st.session_state.keep_alive_started = True

# --- 1. 页面配置 ---
st.set_page_config(page_title="政策直通车", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 强效 CSS 注入 (解决底色消失与按钮大小问题) ---
st.markdown("""
    <style>
    /* 1. 标题与装饰线 */
    .main-title {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #003366;
        text-align: center;
        padding-top: 20px;
    }
    .capsule-line-container { display: flex; justify-content: center; margin: 10px 0 25px 0; }
    .capsule-line {
        width: 120px; height: 6px; 
        background: linear-gradient(90deg, rgba(0,74,153,0) 0%, #004a99 50%, rgba(0,74,153,0) 100%);
        border-radius: 10px; position: relative;
    }
    .capsule-line::after {
        content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 20px; height: 10px; background: #004a99; border-radius: 10px; border: 2px solid white;
    }

    /* 2. 首页大按钮：用 data-testid 强力锁定 */
    /* 这种写法能绕过布局层级，直接锁定按钮文字内容 */
    div.stButton > button {
        border-radius: 50px !important;
        height: 65px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: 0.3s !important;
    }
    
    /* 锁定：国家级政策 (蓝色渐变) */
    div.stButton > button p:contains("国家级政策"), 
    div.stButton > button:has(p:contains("国家级政策")) {
        background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%) !important;
        color: #0369a1 !important;
    }

    /* 锁定：地方性政策 (绿色渐变) */
    div.stButton > button p:contains("地方性政策"), 
    div.stButton > button:has(p:contains("地方性政策")) {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%) !important;
        color: #15803d !important;
    }

    /* 3. 微型返回键：强制宽度自适应，不占全行 */
    div.stButton > button:has(p:contains("返回主页")) {
        height: 32px !important;
        width: auto !important;
        min-width: 100px !important;
        padding: 0 15px !important;
        font-size: 13px !important;
        background-color: #f8f9fa !important;
        color: #666 !important;
        border: 1px solid #eee !important;
        margin-bottom: 20px !important;
        box-shadow: none !important;
    }

    /* 4. 文件卡片 */
    .file-card {
        background-color: #fcfdfe; padding: 15px; border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3; border-radius: 8px; margin-bottom: 12px;
    }
    .footer-note { text-align: center; padding: 30px; color: #888; font-size: 14px; border-top: 1px solid #eee; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

# --- 4. 目录与链接 ---
BASE_URL = "https://vicky-0831.github.io/policy/pdfs/"
LINKS = {
    # ... (此处保持你之前的 LINKS 字典内容)
    "2012年抗菌药物管理办法": BASE_URL + "nhc_kjyw_2012.pdf",
    "2015年抗菌药物评价指标": BASE_URL + "nhc_kjyw_zk_2015.pdf",
    "2025版公立医院绩效监测手册": BASE_URL + "nhc_jxjc_2025.pdf",
    "基药目录管理办法通知": BASE_URL + "nhc_jy_tz.pdf",
    "国家基本药物目录管理办法": BASE_URL + "nhc_jy_glbf.pdf",
    "2026版基药目录管理办法": BASE_URL + "nhc_jy_2026.pdf",
    "2025年药事管理医疗质量控制指标": BASE_URL + "nhc_zk_2025.pdf",
    "2025年医保药品目录通知": BASE_URL + "nhsa_ypml_2025.pdf",
    "做好谈判药品落地工作的通知": BASE_URL + "nhsa_tpyp_ld.pdf",
    "挂网药品价格风险预警标识通知": BASE_URL + "nhsa_fx_yj.pdf",
    "2026年医保基金监管工作通知": BASE_URL + "nhsa_jjjg_2026.pdf",
    "药品RWE价值评价指南": BASE_URL + "nhsa_rwe_yj.pdf",
    "RWE国家可信点公约": BASE_URL + "nhsa_rwe_kxd.pdf",
    "支持创新药高质量发展若干措施": BASE_URL + "nhsa_cxyp_cs.pdf",
    "药品RWE指南汇总": BASE_URL + "nhsa_rwe_hz.pdf",
    "【北京】DRG付费新药新技术除外支付通知": BASE_URL + "bj_drg.pdf",
    "【广东】集采药品接续采购公告(第1号)": BASE_URL + "gd_vbp_1.pdf",
    "【广东】集采药品接续采购公告(第2号)": BASE_URL + "gd_vbp_2.pdf",
    "【广东】集采药品接续采购公告(第3号)": BASE_URL + "gd_vbp_3.pdf",
    "【广东】集采药品接续采购公告(第4号)": BASE_URL + "gd_vbp_4.pdf",
    "【浙江】第一批创新医药技术医保支付激励名单": BASE_URL + "zj_incentive.pdf"
}

# --- 5. 渲染 ---
st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)
st.markdown('<div class="capsule-line-container"><div class="capsule-line"></div></div>', unsafe_allow_html=True)

# L1: 首页
if st.session_state.step == 'L1':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.button("国家级政策", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.button("地方性政策", use_container_width=True, on_click=nav_to, args=('L2', "地方"))

# L2: 内容页
elif st.session_state.step == 'L2':
    # 关键：这里去掉 use_container_width=True，配合 CSS 实现微型化
    st.button("⬅️ 返回主页", on_click=nav_to, args=('L1',))
    
    if st.session_state.l1 == "国家":
        dept = st.selectbox("请选择政策部门", ["国家医保局", "国家卫健委"])
        st.markdown(f"##### 📁 {dept}")
        
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
                if not files: st.caption("暂无文件")
                else:
                    for f in files:
                        url = LINKS.get(f, "#")
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#0066cc; text-decoration:none;">🔗 查看原文</a></div>', unsafe_allow_html=True)

    else: # 地方性政策渲染... (略，保持业务逻辑一致)
        biz_options = ["国谈落地", "集采", "DRG/DIP", "超品规备案", "VBP", "其他"]
        biz = st.selectbox("请选择政策领域", biz_options)
        # (后续业务逻辑同前文...)

# --- 6. 注脚 ---
st.markdown("""<div class="footer-note">© 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网</div>""", unsafe_allow_html=True)

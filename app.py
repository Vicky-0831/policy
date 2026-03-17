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
        except:
            pass
        time.sleep(300)

if "keep_alive_started" not in st.session_state:
    t = threading.Thread(target=keep_alive, daemon=True)
    t.start()
    st.session_state.keep_alive_started = True

# --- 1. 页面配置 ---
st.set_page_config(page_title="政策直通车", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 深度定制：药学美学 & 微型导航 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }

    /* 标题：26px 精致主标题 */
    .main-title {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #003366;
        text-align: center;
        padding-top: 30px;
        letter-spacing: 2px;
    }

    /* 💊 胶囊式标题装饰线：升级版 */
    .capsule-line-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0 25px 0;
    }
    .capsule-line {
        width: 120px;
        height: 6px;
        background: linear-gradient(90deg, rgba(0,74,153,0) 0%, #004a99 50%, rgba(0,74,153,0) 100%);
        position: relative;
        border-radius: 10px;
    }
    .capsule-line::after {
        content: "";
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 24px; height: 10px;
        background: #004a99;
        border-radius: 12px;
        border: 2px solid white;
    }

    /* 首页大按钮：延续胶囊渐变设计 */
    .stButton > button {
        border-radius: 50px !important;
        height: 65px !important;
        font-size: 19px !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }

    /* ⬅️ 返回按钮：极简化缩小处理 */
    /* 专门锁定包含“⬅️”的按钮 */
    div[data-testid="stHeader"] + div button:has(div:contains("⬅️")) {
        height: 35px !important;
        width: auto !important;
        padding: 0 15px !important;
        font-size: 13px !important;
        background-color: #f8f9fa !important;
        color: #666 !important;
        border: 1px solid #eee !important;
        box-shadow: none !important;
        margin-bottom: 15px !important;
    }
    div[data-testid="stHeader"] + div button:has(div:contains("⬅️")):hover {
        background-color: #eef2f6 !important;
        color: #004a99 !important;
    }

    /* 首页专属颜色锁定 */
    button[aria-label="国家级政策"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%) !important;
        color: #0369a1 !important;
    }
    button[aria-label="地方性政策"] {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%) !important;
        color: #15803d !important;
    }

    /* 备注 & 注脚 */
    .footer-note { 
        text-align: center; padding: 35px; color: #888; 
        font-size: 14px !important; margin-top: 60px; border-top: 1px solid #f5f5f5; 
    }
    
    /* 卡片美化 */
    .file-card {
        background-color: #fcfdfe; padding: 15px; border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3; border-radius: 8px; margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 核心功能 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

@st.cache_data
def load_excel_data():
    file_path = '数据.xlsx'
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path)
        df['省份'] = df['省份'].ffill()
        cols = ['药事会召开时限', '思福诺是否纳入双通道', '康新博胶囊是否纳入双通道', 
                '康新博胶囊是否纳入双通道单独支付', '国谈药医保总额单列', '国谈药DRG/DIP除外支付']
        df[cols] = df[cols].ffill()
        return df
    except: return None

# --- 4. 目录与链接 ---
BASE_URL = "https://vicky-0831.github.io/policy/pdfs/"
LINKS = {
    # 国家级... (保持不变)
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
    # 地方性... (保持不变)
    "【北京】DRG付费新药新技术除外支付通知": BASE_URL + "bj_drg.pdf",
    "【广东】集采药品接续采购公告(第1号)": BASE_URL + "gd_vbp_1.pdf",
    "【广东】集采药品接续采购公告(第2号)": BASE_URL + "gd_vbp_2.pdf",
    "【广东】集采药品接续采购公告(第3号)": BASE_URL + "gd_vbp_3.pdf",
    "【广东】集采药品接续采购公告(第4号)": BASE_URL + "gd_vbp_4.pdf",
    "【浙江】第一批创新医药技术医保支付激励名单": BASE_URL + "zj_incentive.pdf"
}

# --- 5. 渲染流程 ---

# 标题区：胶囊装饰线
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
    # 缩小版的返回按钮
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
                if not files: st.caption("暂无相关文件")
                else:
                    for f in files:
                        url = LINKS.get(f, "#")
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#0066cc; text-decoration:none;">🔗 查看原文</a></div>', unsafe_allow_html=True)

    else: # 地方性政策
        biz_options = ["国谈落地", "集采", "DRG/DIP", "超品规备案", "VBP", "其他"]
        biz = st.selectbox("请选择政策领域", biz_options)
        
        if biz == "国谈落地":
            df = load_excel_data()
            if df is None: st.warning("请上传数据文件。")
            else:
                prov = st.selectbox("查询省份", df['省份'].unique().tolist())
                row = df[df['省份'] == prov].iloc[0]
                metrics = [("📅 药事会时限", '药事会召开时限'), ("💊 思福诺双通道", '思福诺是否纳入双通道'),
                           ("💊 康新博双通道", '康新博胶囊是否纳入双通道'), ("💰 康新博单独支付", '康新博胶囊是否纳入双通道单独支付'),
                           ("📊 总额单列", '国谈药医保总额单列'), ("🚫 DRG/DIP除外", '国谈药DRG/DIP除外支付')]
                # (数据栅格代码同前...)
                st.write(f"指标展示：{prov}")
                # ...此处保持前文 Excel 渲染逻辑...

        elif biz == "集采":
            st.markdown("##### 📁 采购公告")
            for f in ["【广东】集采药品接续采购公告(第1号)", "【广东】集采药品接续采购公告(第2号)"]:
                url = LINKS.get(f, "#")
                st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

# --- 6. 注脚 ---
st.markdown("""
    <div class="footer-note">
        © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网
    </div>
""", unsafe_allow_html=True)

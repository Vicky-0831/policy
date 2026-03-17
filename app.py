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

# --- 2. 强效 CSS 注入 (解决底色、按钮大小、备注显示问题) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }

    /* 标题：26px 精致主标题 */
    .main-title { font-size: 26px !important; font-weight: 800 !important; color: #003366; text-align: center; padding-top: 15px; }
    
    /* 胶囊装饰线 */
    .capsule-line-container { display: flex; justify-content: center; margin: 8px 0 20px 0; }
    .capsule-line {
        width: 120px; height: 6px; border-radius: 10px; position: relative;
        background: linear-gradient(90deg, rgba(0,74,153,0) 0%, #004a99 50%, rgba(0,74,153,0) 100%);
    }
    .capsule-line::after {
        content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 20px; height: 10px; background: #004a99; border-radius: 10px; border: 2px solid white;
    }

    /* --- 首页按钮：终极底色锁定 (针对内部 P 标签) --- */
    /* 国家级政策：渐变蓝 */
    div[data-testid="stButton"] button:has(p:contains("国家级政策")) {
        background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%) !important;
        color: #0369a1 !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
    }
    /* 地方性政策：渐变绿 */
    div[data-testid="stButton"] button:has(p:contains("地方性政策")) {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%) !important;
        color: #15803d !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
    }

    /* --- 返回主页按钮：微型化控制 --- */
    div[data-testid="stButton"] button:has(p:contains("返回主页")) {
        height: 30px !important;
        width: auto !important;
        min-width: 90px !important;
        padding: 0 10px !important;
        font-size: 12px !important; /* 字体缩小 */
        color: #888 !important;
        background-color: #f8f9fa !important;
        border: 1px solid #eee !important;
        border-radius: 4px !important;
        box-shadow: none !important;
        margin-bottom: 15px !important;
    }
    div[data-testid="stButton"] button:has(p:contains("返回主页")) p {
        font-size: 12px !important;
    }

    /* 文件卡片 */
    .file-card {
        background-color: #fcfdfe; padding: 12px; border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3; border-radius: 8px; margin-bottom: 10px;
    }

    /* 注脚与备注 */
    .footer-note { 
        text-align: center; padding: 30px; color: #666; 
        font-size: 14px !important; margin-top: 60px; border-top: 1px solid #eee; 
    }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #f0ad4e; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

# --- 4. 数据加载 (Excel 模块) ---
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

# --- 5. 链接与渲染逻辑 ---
BASE_URL = "https://vicky-0831.github.io/policy/pdfs/"
LINKS = {
    # 国家级...
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
    # 地方级 (带地域标注)
    "【北京】DRG付费新药新技术除外支付通知": BASE_URL + "bj_drg.pdf",
    "【广东】集采药品接续采购公告(1-4号)": BASE_URL + "gd_vbp_1.pdf",
    "【浙江】第一批创新医药技术医保支付激励名单": BASE_URL + "zj_incentive.pdf"
}

st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)
st.markdown('<div class="capsule-line-container"><div class="capsule-line"></div></div>', unsafe_allow_html=True)

# L1: 首页
if st.session_state.step == 'L1':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, mid, c3 = st.columns([1, 2, 1])
    with mid:
        st.button("国家级政策", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.button("地方性政策", use_container_width=True, on_click=nav_to, args=('L2', "地方"))

# L2: 二级内容页
elif st.session_state.step == 'L2':
    # 微型返回按钮 (不使用 container_width)
    st.button("⬅️ 返回主页", on_click=nav_to, args=('L1',))
    
    if st.session_state.l1 == "国家":
        dept = st.selectbox("请选择政策部门", ["国家医保局", "国家卫健委"])
        st.markdown(f"#### 📂 {dept}")
        
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
            # 默认收起 expander
            with st.expander(f"🔹 {cat}", expanded=False):
                if not files: st.caption("暂无相关文件")
                else:
                    for f in files:
                        url = LINKS.get(f, "#")
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#0066cc; text-decoration:none;">🔗 查看官方原文</a></div>', unsafe_allow_html=True)

    else: # 地方性政策
        # 业务领域排序，其他在末尾
        biz_opts = ["国谈落地", "集采", "DRG/DIP", "超品规备案", "VBP", "其他"]
        biz = st.selectbox("请选择政策领域", biz_opts)
        
        if biz == "国谈落地":
            df = load_excel_data()
            if df is not None:
                prov = st.selectbox("查询省份核心指标", df['省份'].unique().tolist())
                row = df[df['省份'] == prov].iloc[0]
                st.markdown(f"##### 📌 {prov} - 核心指标分析")
                # (保持 Excel 指标栅格渲染逻辑...)
                st.write(f"正在展示 {prov} 的详细落地数据...")

        elif biz == "集采":
            st.markdown("##### 📁 集中带量采购政策 (广东)")
            st.markdown(f'<div class="file-card"><b>【广东】集采药品接续采购公告(1-4号)</b><br><a href="#" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)
            
        elif biz == "DRG/DIP":
            st.markdown("##### 📁 支付方式改革政策 (北京)")
            st.markdown(f'<div class="file-card"><b>【北京】DRG付费新药新技术除外支付工作通知</b><br><a href="#" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

# --- 6. 注脚 (找回备注内容) ---
st.markdown("""
    <div class="footer-note">
        <b>备注：</b>文件中<span class="text-green">绿色标识</span>为机会点，
        <span class="text-yellow">黄色标识</span>为风险点。<br>
        © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网
    </div>
""", unsafe_allow_html=True)

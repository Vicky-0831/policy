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

# --- 2. 增强版 CSS 样式表 ---
st.markdown("""
    <style>
    /* 全局背景：白色 */
    .stApp { background-color: #ffffff; }

    /* 28px 标题：比之前缩小了一点，保持精致 */
    .main-title {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #003366;
        text-align: center;
        padding: 30px 0 10px 0;
    }

    /* 20px 部门标题 */
    .dept-header {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #004a99;
        margin-bottom: 15px;
    }

    /* 首页按钮样式：强制显色 */
    .stButton > button {
        border-radius: 8px !important;
        height: 60px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        transition: 0.3s;
    }
    
    /* 国家级政策按钮：淡蓝色底色 */
    div[data-testid="stButton"]:nth-of-type(1) button {
        background-color: #e3f2fd !important;
        border: 1px solid #bbdefb !important;
        color: #004a99 !important;
    }
    
    /* 地方性政策按钮：淡红色底色 */
    div[data-testid="stButton"]:nth-of-type(2) button {
        background-color: #ffebee !important;
        border: 1px solid #ffcdd2 !important;
        color: #c62828 !important;
    }

    /* 卡片布局 */
    .policy-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; margin-top: 10px; }
    .file-card {
        background-color: #fcfdfe; padding: 15px; border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3; border-radius: 6px;
    }
    
    /* 指标卡片 (Excel 模块) */
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; }
    .metric-card {
        padding: 10px; border-radius: 6px; border-left: 4px solid;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* 备注 & 注脚 */
    .footer-note { 
        text-align: center; padding: 30px; color: #666; 
        font-size: 13px !important; margin-top: 60px; border-top: 1px solid #eee; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 数据加载逻辑 (国谈落地分析) ---
@st.cache_data
def load_excel_data():
    file_path = '数据.xlsx'
    if not os.path.exists(file_path): return None
    df = pd.read_excel(file_path)
    df['省份'] = df['省份'].ffill()
    cols = ['药事会召开时限', '思福诺是否纳入双通道', '康新博胶囊是否纳入双通道', 
            '康新博胶囊是否纳入双通道单独支付', '国谈药医保总额单列', '国谈药DRG/DIP除外支付']
    df[cols] = df[cols].ffill()
    return df

# --- 4. 目录与链接定义 ---
BASE_URL = "https://vicky-0831.github.io/policy/pdfs/"
LINKS = {
    # 国家级文件 (NHC & NHSA)
    "2012年抗菌药物管理办法": BASE_URL + "nhc_kjyw_2012.pdf",
    "2015年抗菌药物评价指标": BASE_URL + "nhc_kjyw_zk_2015.pdf",
    "2025版三级公立医院绩效监测手册": BASE_URL + "nhc_jxjc_2025.pdf",
    "基药目录管理办法通知": BASE_URL + "nhc_jy_tz.pdf",
    "国家基本药物目录管理办法": BASE_URL + "nhc_jy_glbf.pdf",
    "2026版基药目录管理办法": BASE_URL + "nhc_jy_2026.pdf",
    "2025年药事管理医疗质量控制指标": BASE_URL + "nhc_zk_2025.pdf",
    "2025年医保药品目录通知": BASE_URL + "nhsa_ypml_2025.pdf",
    "做好谈判药品落地工作的通知": BASE_URL + "nhsa_tpyp_ld.pdf",
    "挂网药品价格风险预警标识通知": BASE_URL + "nhsa_fx_yj.pdf",
    "2026年医保基金监管工作通知": BASE_URL + "nhsa_jjjg_2026.pdf",
    "药品RWE价值评价指南": BASE_URL + "nhsa_rwe_yj.pdf",
    "RWE国家可信评价点公告": BASE_URL + "nhsa_rwe_kxd.pdf",
    "支持创新药高质量发展若干措施": BASE_URL + "nhsa_cxyp_cs.pdf",
    "药品RWE综合指南汇总": BASE_URL + "nhsa_rwe_hz.pdf",
    
    # 地方级文件 (带省份标注)
    "【北京】DRG付费新药新技术除外支付通知": BASE_URL + "bj_drg.pdf",
    "【广东】集采药品接续采购公告(第1号)": BASE_URL + "gd_vbp_1.pdf",
    "【广东】集采药品接续采购公告(第2号)": BASE_URL + "gd_vbp_2.pdf",
    "【广东】集采药品接续采购公告(第3号)": BASE_URL + "gd_vbp_3.pdf",
    "【广东】集采药品接续采购公告(第4号)": BASE_URL + "gd_vbp_4.pdf",
    "【浙江】第一批创新医药技术医保支付激励名单": BASE_URL + "zj_incentive.pdf"
}

# --- 5. 界面渲染 ---

if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1
    st.rerun()

st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)

# L1: 首页
if st.session_state.step == 'L1':
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.button("国家级政策", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.button("地方性政策", use_container_width=True, on_click=nav_to, args=('L2', "地方"))

# L2: 二级页面
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回主页"): nav_to('L1')
    
    if st.session_state.l1 == "国家":
        dept = st.selectbox("请选择政策部门", ["国家医保局", "国家卫健委"])
        st.markdown(f'<div class="dept-header">{dept}</div>', unsafe_allow_html=True)
        
        nat_struct = {
            "国家卫健委": {
                "抗菌药物管理办法": ["2012年抗菌药物管理办法", "2015年抗菌药物评价指标"],
                "绩效监测": ["2025版三级公立医院绩效监测手册"],
                "基本药物": ["基药目录管理办法通知", "国家基本药物目录管理办法", "2026版基药目录管理办法"],
                "医院管理质控": ["2025年药事管理医疗质量控制指标"],
                "超品规备案": [], "其他": []
            },
            "国家医保局": {
                "国谈落地": ["2025年医保药品目录通知", "做好谈判药品落地工作的通知"],
                "红黄标": ["挂网药品价格风险预警标识通知"],
                "基金监管": ["2026年医保基金监管工作通知"],
                "其他": ["药品RWE价值评价指南", "RWE国家可信评价点公告", "支持创新药高质量发展若干措施", "药品RWE综合指南汇总"],
                "VBP": [], "DRG/DIP": []
            }
        }
        
        for cat, files in nat_struct[dept].items():
            with st.expander(f"📁 {cat}", expanded=True):
                if not files: st.caption("暂无文件")
                else:
                    st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
                    for f in files:
                        url = LINKS.get(f, "#")
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#0066cc;">🔗 查看原文</a></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

    else: # 地方性政策：按业务分类
        # 排序：国谈落地、集采、超品规备案、VBP、DRG/DIP、其他
        biz_options = ["国谈落地", "集采", "超品规备案", "VBP", "DRG/DIP", "其他"]
        biz = st.selectbox("请选择政策领域", biz_options)
        
        if biz == "国谈落地":
            st.markdown("### 📊 指标分析 (基于 数据.xlsx)")
            df = load_excel_data()
            if df is None: st.warning("根目录下未找到 '数据.xlsx'。")
            else:
                prov = st.selectbox("查询省份", df['省份'].unique().tolist())
                row = df[df['省份'] == prov].iloc[0]
                
                metrics = [
                    ("📅 药事会时限", '药事会召开时限'), ("💊 思福诺双通道", '思福诺是否纳入双通道'),
                    ("💊 康新博双通道", '康新博胶囊是否纳入双通道'), ("💰 康新博单独支付", '康新博胶囊是否纳入双通道单独支付'),
                    ("📊 总额单列/调整", '国谈药医保总额单列'), ("🚫 DRG/DIP除外", '国谈药DRG/DIP除外支付')
                ]
                
                html_m = '<div class="metric-grid">'
                for label, key in metrics:
                    val = str(row[key])
                    color = "#28a745" if "是" in val else "#dc3545" if "否" in val else "#007bff"
                    bg = "#e6fffa" if "是" in val else "#ffe6e6" if "否" in val else "#e6f2ff"
                    html_m += f'<div class="metric-card" style="border-left-color:{color}; background-color:{bg};"><div style="font-size:11px; color:#666;">{label}</div><div style="font-size:15px; font-weight:700; color:{color};">{val}</div></div>'
                st.markdown(html_m + '</div>', unsafe_allow_html=True)
                
                st.markdown("#### 🔗 关联原文")
                for _, r in df[df['省份'] == prov].iterrows():
                    if pd.notna(r['链接']): st.markdown(f"📄 [{r['原文']}]({r['链接']})")

        elif biz == "集采":
            st.markdown("### 📁 药品集中带量采购接续")
            files = ["【广东】集采药品接续采购公告(第1号)", "【广东】集采药品接续采购公告(第2号)", "【广东】集采药品接续采购公告(第3号)", "【广东】集采药品接续采购公告(第4号)"]
            st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
            for f in files:
                url = LINKS.get(f, "#")
                st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        elif biz == "DRG/DIP":
            st.markdown("### 📁 支付方式改革")
            url = LINKS.get("【北京】DRG付费新药新技术除外支付通知")
            st.markdown(f'<div class="file-card"><b>【北京】DRG付费新药新技术除外支付工作通知</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

        elif biz == "其他":
            st.markdown("### 📁 其他政策汇总")
            url = LINKS.get("【浙江】第一批创新医药技术医保支付激励名单")
            st.markdown(f'<div class="file-card"><b>【浙江】关于浙江省第一批创新医药技术医保支付激励名单公示</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

# --- 6. 注脚 ---
st.markdown("""
    <div class="footer-note">
        © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网
    </div>
""", unsafe_allow_html=True)

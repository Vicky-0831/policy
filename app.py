import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import threading
import requests

# ==========================================
# --- 0. 技术保活 ---
# ==========================================
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

# ==========================================
# --- 1. 网页基础配置 ---
# ==========================================
st.set_page_config(page_title="政策直通车", layout="wide", initial_sidebar_state="collapsed")

@st.dialog("📢 政策更新动态")
def show_update_announcement():
    st.markdown("""
    **最新进度说明：**
    * 📅 **截止日期**：数据已实时同步至 **2026.04.01**。
    * ✅ **覆盖范围**：1-8批集采接续文件，除天津外，所有已发文省份的执行政策均已更新入库。
    * ⏳ **特别提醒**：**天津市** 相关政策文件目前尚未发布，一经发文将立即上线。
    """)

if "announcement_read" not in st.session_state:
    st.session_state.announcement_read = True
    show_update_announcement()

# ==========================================
# --- 2. 界面装修 (CSS 样式合并) ---
# ==========================================
st.markdown("""
    <style>
    /* ========== 全局与看板高级样式 ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stApp { background-color: #ffffff; }

    /* 看板大标题 */
    .dash-title { 
        font-size: 36px; 
        font-weight: 900; 
        margin-bottom: 40px; 
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: left; 
        letter-spacing: 2px; 
    }
    
    /* 看板模块副标题 */
    .sub-section-title { 
        font-size: 24px; 
        font-weight: 800; 
        margin-top: 50px; 
        margin-bottom: 30px; 
        color: #0F172A; 
        display: flex; 
        align-items: center; 
        letter-spacing: 0.5px;
    }
    .sub-section-title::before {
        content: "";
        display: block;
        width: 6px;
        height: 24px;
        background: linear-gradient(180deg, #3B82F6 0%, #60A5FA 100%);
        border-radius: 4px;
        margin-right: 12px;
    }
    
    /* 左右两栏横向流动布局 */
    .row-container { 
        display: flex; 
        align-items: stretch; 
        margin-bottom: 20px; 
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08); 
        border-radius: 16px; 
        overflow: hidden; 
        background-color: #FFFFFF; 
        border: 1px solid #CBD5E1; 
    }
    
    /* 左侧大标题区 */
    .left-title-box { 
        width: 160px; 
        min-width: 160px; 
        color: #FFFFFF !important; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 15px; 
        font-weight: 800; 
        text-align: center !important; 
        padding: 24px 12px; 
        white-space: nowrap !important; 
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-right: 1px solid #CBD5E1;
    }
    
    /* 右侧内容区与网格 */
    .right-content-box { flex: 1; display: flex; flex-direction: column; background-color: #FFFFFF; }
    .content-sub-row { display: flex; align-items: stretch; border-bottom: 1px solid #CBD5E1; } 
    .content-sub-row:last-child { border-bottom: none; }
    .grid-cells-wrapper { flex: 1; display: flex; align-items: stretch; }
    
    /* --- 修复点 1: 强制忽略内容宽度，均等分配 --- */
    .inner-cell { 
        flex: 1 1 0%; /* 关键修复：让电脑端也无视文字长度完美均分 */
        padding: 24px 16px; 
        text-align: center !important; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        border-right: 1px solid #CBD5E1; 
        word-break: break-word; /* 防止长串文字撑破格子 */
    }
    .inner-cell:last-child { border-right: none; }
    
    .bg-light-green { background-color: #ECFDF5 !important; }
    .bg-light-orange { background-color: #FFF7ED !important; }
    
    .cell-t1 { font-size: 16px; font-weight: 800; color: #1E293B; margin-bottom: 8px; width: 100%; }
    .cell-t2 { font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 6px; width: 100%; }
    .cell-t3 { font-size: 16px; font-weight: 500; color: #000000 !important; font-style: italic !important; line-height: 1.6; width: 100%; }
    
    /* 看板图例与标签 */
    .board-legend {
        display: flex; align-items: center; justify-content: flex-start; gap: 24px;
        margin-top: 15px; margin-bottom: 40px; padding: 12px 20px;
        background-color: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;
        font-size: 13px; color: #475569;
    }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .legend-dot { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
    
    .color-guotan { background: linear-gradient(135deg, #2563EB 0%, #60A5FA 100%); } 
    .color-drg { background: linear-gradient(135deg, #059669 0%, #34D399 100%); }    
    .color-vbp { background: linear-gradient(135deg, #D97706 0%, #FBBF24 100%); }    
    .color-fenji { background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%); }
    
    .status-tag {
        display: inline-block; padding: 6px 14px; border-radius: 8px;
        font-size: 15px; font-weight: 800; line-height: 1.4; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* ========== 原本小程序的样式 ========== */
    .main-title { font-size: 26px !important; font-weight: 800; color: #003366; text-align: center; padding-top: 15px; margin-bottom: 0px;}
    .capsule-line-container { display: flex; justify-content: center; margin: 10px 0 25px 0; }
    .capsule-line {
        width: 120px; height: 6px; border-radius: 10px; position: relative;
        background: linear-gradient(90deg, rgba(0,74,153,0) 0%, #004a99 50%, rgba(0,74,153,0) 100%);
    }
    .st-key-nat_btn button {
        background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%) !important;
        height: 85px !important; border-radius: 15px !important; border: none !important;
        box-shadow: 0 4px 15px rgba(0,74,153,0.2) !important;
    }
    .st-key-nat_btn button p { color: #0369a1 !important; font-size: 20px !important; font-weight: 700 !important; }
    .st-key-loc_btn button {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%) !important;
        height: 85px !important; border-radius: 15px !important; border: none !important;
        box-shadow: 0 4px 15px rgba(21,128,61,0.2) !important;
    }
    .st-key-loc_btn button p { color: #15803d !important; font-size: 20px !important; font-weight: 700 !important; }
    .st-key-back_btn, .st-key-back_to_dash_btn { width: auto !important; margin-bottom: 15px !important; }
    .st-key-back_btn button, .st-key-back_to_dash_btn button {
        height: 24px !important; min-height: 24px !important; width: auto !important;
        padding: 0 10px !important; background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important; border-radius: 4px !important;
    }
    .st-key-back_btn button p, .st-key-back_to_dash_btn button p { font-size: 10px !important; color: #888 !important; }
    .footer-note { text-align: center; padding: 30px; color: #666; font-size: 14px !important; border-top: 1px solid #eee; margin-top: 60px; }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #f0ad4e; font-weight: bold; }
    .file-card { background-color: #fcfdfe; padding: 15px; border: 1px solid #eef2f6; border-top: 3px solid #0056b3; border-radius: 8px; margin-bottom: 12px; }
    .metric-card { padding: 10px; border-radius: 6px; border-left: 4px solid; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; }

    /* ========== 移动端自适应 (Mobile Responsiveness) ========== */
    @media (max-width: 768px) {
        .dash-title { font-size: 24px !important; margin-bottom: 20px !important; text-align: center !important;}
        .row-container { flex-direction: column !important; }
        .left-title-box { 
            width: 100% !important; 
            min-width: 100% !important; 
            border-right: none !important; 
            border-bottom: 1px solid #CBD5E1 !important;
            padding: 12px !important; 
        }
        .right-content-box {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important; /* 丝滑滚动 */
        }
        
        /* --- 修复点 2: 解决手机端上下边框错位 --- */
        .content-sub-row, .grid-cells-wrapper {
            min-width: max-content !important; 
            display: flex !important; 
        }
        .inner-cell {
            flex: 1 0 140px !important; /* 每个格子最低140px，如有空间等比放大 */
            width: 0 !important; /* 关键修复：完全无视文字长度，强行对齐所有格子的线 */
            padding: 16px 8px !important;
        }

        .board-legend {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# --- 3. 状态管理 ---
# ==========================================
# 默认进入 Dashboard 看板
if 'step' not in st.session_state: st.session_state.step = 'L0' 
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

# ==========================================
# --- 4. 数据加载 (含 Dashboard 数据) ---
# ==========================================
@st.cache_data
def load_app_data():
    file_path = 'APP表.xlsx'
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1', header=[0, 1, 2])
        return df
    except: return None

@st.cache_data
def load_excel_data():
    file_path = '数据.xlsx'
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(subset=['省份']) 
        df['省份'] = df['省份'].ffill()
        cols = ['药事会召开时限', '思福诺是否纳入双通道', '康新博胶囊是否纳入双通道', 
                '康新博胶囊是否纳入双通道单独支付', '国谈药医保总额单列', '国谈药DRG/DIP除外支付']
        df[cols] = df[cols].ffill()
        return df
    except: return None

@st.cache_data
def load_vbp_data():
    file_path = 'VBP.xlsx'
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(subset=['省份']) 
        if '中选:非中选比例' in df.columns:
            df['中选:非中选比例'] = df['中选:非中选比例'].astype(str).str.replace('：', ':').str.strip()
        return df
    except: return None

@st.cache_data
def load_cpzba_data():
    if not os.path.exists('cpzba.xlsx'): return None
    return pd.read_excel('cpzba.xlsx').dropna(subset=['省份'])

@st.cache_data
def load_cfjmlpzba_data():
    if not os.path.exists('cfjmlpzba.xlsx'): return None
    return pd.read_excel('cfjmlpzba.xlsx').dropna(subset=['省份'])

# ==========================================
# --- 5. 链接仓库 ---
# ==========================================
BASE_URL = "https://vicky-0831.github.io/policy/pdfs/"
LEVEL_CATALOG_PDFS = {
    "北京": BASE_URL + "bj_tj_hb_2024.pdf",
    "天津": BASE_URL + "bj_tj_hb_2024.pdf",
    "河北": BASE_URL + "bj_tj_hb_2024.pdf",
    "重庆": BASE_URL + "cq2015.pdf",
    "安徽": BASE_URL + "ah2012.pdf",
    "宁夏": BASE_URL + "nx2012.pdf",
    "福建": BASE_URL + "fj2022.pdf",
    "海南": BASE_URL + "hn2022.pdf",
    "湖南": BASE_URL + "hunan2021.pdf",
    "四川": BASE_URL + "sc2025.pdf",
    "陕西": BASE_URL + "sx2023.pdf",
    "河南": BASE_URL + "henan2021.pdf",
    "广东": BASE_URL + "gd2024.pdf",
    "湖北": BASE_URL + "hubei2021.pdf",
    "新疆": BASE_URL + "xj2025.pdf",
    "甘肃": BASE_URL + "gansu2025.pdf",
    "江苏": BASE_URL + "js2024.pdf",
    "江西": BASE_URL + "jiangxi2012.pdf",
    "辽宁": BASE_URL + "liaoning2012.pdf",
    "内蒙古": BASE_URL + "nmg2012.pdf",
    "青海": BASE_URL + "qh2025.pdf",
    "浙江": BASE_URL + "zj2021.pdf"
}

LINKS = {
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
    "【浙江】第一批创新医药技术医保支付激励名单": BASE_URL + "zj_incentive.pdf",
    "国采1-8批接续采购政策要点详表(详细版)": "https://view.officeapps.live.com/op/view.aspx?src=https://vicky-0831.github.io/policy/pdfs/vbp_policy_detail.xlsx",
    "国采1-8批接续采购政策要点详表(招标版)": "https://view.officeapps.live.com/op/view.aspx?src=https://vicky-0831.github.io/policy/pdfs/vbp_policy_bid.xlsx"
}

# ==========================================
# --- 6. 界面渲染 ---
# ==========================================

# ----------------- Dashboard 页面 (L0) -----------------
if st.session_state.step == 'L0':
    
    # 顶部标题 & 右上角跳转按钮
    col_title, col_btn = st.columns([8, 2])
    with col_title:
        st.markdown('<div class="dash-title">政策执行智能化透视看板</div>', unsafe_allow_html=True)
    with col_btn:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.button("进入政策查询系统 ➡️", on_click=nav_to, args=('L1',), use_container_width=True)

    df_raw = load_app_data()
    
    st.markdown('<div class="sub-section-title">全局政策Dashboard</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="row-container">
        <div class="left-title-box color-guotan">国谈落地</div>
        <div class="right-content-box">
            <div class="content-sub-row">
                <div class="grid-cells-wrapper">
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Emb纳入双通道</div><div class="cell-t3">·20省</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Cre Oral纳入双通道</div><div class="cell-t3">·29省</div></div>
                </div>
            </div>
            <div class="content-sub-row">
                <div class="grid-cells-wrapper">
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Cre Oral</div><div class="cell-t2">双通道单独支付</div><div class="cell-t3">·21省</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Emb/Cre Oral</div><div class="cell-t2">医保总额单列/合理调整</div><div class="cell-t3">·16省医保总额单列<br>·14省医保总额合理调整</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Emb/Cre Oral</div><div class="cell-t2">DRG、DIP除外支付/超支补偿</div><div class="cell-t3">·2省3年除外<br>·10省2年除外<br>·2省1年除外<br>·14省超支补偿</div></div>
                </div>
            </div>
        </div>
    </div>

    <div class="row-container">
        <div class="left-title-box color-drg" style="white-space: normal !important; line-height: 1.4; padding: 16px 12px;">创新药DRG<br>除外/激励支付</div>
        <div class="right-content-box">
            <div class="content-sub-row">
                <div class="grid-cells-wrapper">
                    <div class="inner-cell bg-light-green">
                        <div class="cell-t1" style="margin-bottom: 0;">Zavi：<span class="cell-t3" style="display: inline; width: auto;">1省除外支付</span></div>
                    </div>
                    <div class="inner-cell bg-light-green">
                        <div class="cell-t1" style="margin-bottom: 0;">Cre IV：<span class="cell-t3" style="display: inline; width: auto;">1省激励支付</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row-container">
        <div class="left-title-box color-vbp">1-8批续约</div>
        <div class="right-content-box">
            <div class="content-sub-row">
                <div class="grid-cells-wrapper">
                    <div class="inner-cell bg-light-green"><div class="cell-t1">中选:非中选比例</div><div class="cell-t3">·3省未明确<br>·3省5：5<br>·25省中选品完成任务量</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">提及合并考核</div><div class="cell-t3">·6省</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">提及不一刀切</div><div class="cell-t3">·25省</div></div>
                </div>
            </div>
            <div class="content-sub-row">
                <div class="grid-cells-wrapper">
                    <div class="inner-cell bg-light-orange"><div class="cell-t1">提及红黄标色</div><div class="cell-t3">·13省</div></div>
                    <div class="inner-cell bg-light-orange"><div class="cell-t1">提及关注高价非中选产品异常使用等现象</div><div class="cell-t3">·18省</div></div>
                    <div class="inner-cell bg-light-orange"><div class="cell-t1">提及“按医保支付价支付”</div><div class="cell-t3">·10省</div></div>
                </div>
            </div>
        </div>
    </div>

    <div class="row-container">
        <div class="left-title-box color-fenji">分级目录管理</div>
        <div class="right-content-box">
            <div class="content-sub-row">
                <div class="grid-cells-wrapper">
                    <div class="inner-cell bg-light-green"><div class="cell-t1">提及超品种备案</div><div class="cell-t3">·8省</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">提及超分级目录备案</div><div class="cell-t3">·25省</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Cre IV</div><div class="cell-t3">·18省特殊级管理</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Cre Oral</div><div class="cell-t3">·15省限制级管理<br>·3省特殊级管理</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">Emb</div><div class="cell-t3">·1省特殊级管理</div></div>
                    <div class="inner-cell bg-light-green"><div class="cell-t1">X</div><div class="cell-t3">·2省特殊级管理</div></div>
                </div>
            </div>
        </div>
    </div>

    <div class="board-legend">
        <span style="font-weight: 700; color: #1E293B;">💡 看板图例说明：</span>
        <div class="legend-item">
            <span class="legend-dot" style="background-color: #ECFDF5; border: 1px solid #A7F3D0;"></span>
            <span>绿色背景：<strong>有利方面</strong></span>
        </div>
        <div class="legend-item">
            <span class="legend-dot" style="background-color: #FFF7ED; border: 1px solid #FED7AA;"></span>
            <span>橙色背景：<strong>需关注方面</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sub-section-title">单省份执行细节穿透查询</div>', unsafe_allow_html=True)

    if df_raw is not None:
        raw_provs = df_raw.iloc[:, 0].dropna().unique()
        clean_provs = [p for p in raw_provs if str(p).strip().lower() not in ['none', 'nan', '0', '', '省份']]
        
        selected_prov = st.selectbox("🔍 请选择或输入搜索你想查看的省份：", options=clean_provs)
        
        if selected_prov:
            prov_row = df_raw[df_raw.iloc[:, 0].astype(str).str.strip() == str(selected_prov).strip()]
            
            if not prov_row.empty:
                row_data = prov_row.iloc[0]
                
                def parse_cell(val, style_type, col_idx=None):
                    v = str(val).strip()
                    if pd.isna(val) or v.lower() in ['none', 'nan', '', '-']:
                        return '<span style="color: #94A3B8; font-weight:400; font-size:18px;">-</span>'
                    
                    def make_tag(bg, color, border, text):
                        return f'<div class="status-tag" style="background-color: {bg}; color: {color}; border: 1px solid {border};">{text}</div>'
                    
                    if style_type == "guotan":
                        if any(x in v for x in ['Y', '总额单列', '两年除外', '三年除外', '首年除外']):
                            return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                        if '合理调整' in v or '超支补偿' in v:
                            return make_tag("#EFF6FF", "#1D4ED8", "#BFDBFE", v)
                    elif style_type == "drg":
                        v_clean = v.replace(" ", "")
                        if 'Zavi' in v_clean or 'Cre' in v_clean or 'IV' in v_clean or v_clean == 'Y': 
                            return make_tag("#ECFDF5", "#047857", "#A7F3D0", "Y")
                        elif v: 
                            return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                    elif style_type == "vbp":
                        if '5：5' in v or '5:5' in v: return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                        if col_idx in [4, 5, 6] and v == 'Y': return make_tag("#FFF7ED", "#C2410C", "#FED7AA", v)
                        if '任务量' in v or (col_idx in [2, 3] and v == 'Y'): return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                    elif style_type == "fenji":
                        if col_idx == 3 and '特殊' in v: return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                        if col_idx == 4:
                            if '限制' in v: return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                            if '特殊' in v: return make_tag("#FFF7ED", "#C2410C", "#FED7AA", v)
                        if col_idx in [5, 6] and '特殊' in v: return make_tag("#FFF7ED", "#C2410C", "#FED7AA", v)
                        if v == 'Y': return make_tag("#ECFDF5", "#047857", "#A7F3D0", v)
                    
                    return f'<span style="color: #334155; font-weight: 700; font-size:16px;">{v}</span>'

                txt_0 = parse_cell(row_data.iloc[1], "guotan")
                txt_1 = parse_cell(row_data.iloc[2], "guotan")
                txt_2 = parse_cell(row_data.iloc[3], "guotan")
                txt_3 = parse_cell(row_data.iloc[4], "guotan")
                txt_4 = parse_cell(row_data.iloc[5], "guotan")
                
                drg_raw_val = str(row_data.iloc[6]).strip()
                txt_drg0 = parse_cell(drg_raw_val if "Zavi" in drg_raw_val else "", "drg")
                txt_drg1 = parse_cell(drg_raw_val if ("Cre" in drg_raw_val or "IV" in drg_raw_val) else "", "drg")
                
                txt_v0 = parse_cell(row_data.iloc[7], "vbp", 1)
                txt_v1 = parse_cell(row_data.iloc[8], "vbp", 2)
                txt_v2 = parse_cell(row_data.iloc[9], "vbp", 3)
                txt_v3 = parse_cell(row_data.iloc[10], "vbp", 4)
                txt_v4 = parse_cell(row_data.iloc[11], "vbp", 5)
                txt_v5 = parse_cell(row_data.iloc[12], "vbp", 6)
                
                txt_f0 = parse_cell(row_data.iloc[13], "fenji", 1)
                txt_f1 = parse_cell(row_data.iloc[14], "fenji", 2)
                txt_f2 = parse_cell(row_data.iloc[15], "fenji", 3)
                txt_f3 = parse_cell(row_data.iloc[16], "fenji", 4)
                txt_f4 = parse_cell(row_data.iloc[17], "fenji", 5)
                txt_f5 = parse_cell(row_data.iloc[18], "fenji", 6)

                html_prov = f"""
                <div class="row-container">
                    <div class="left-title-box color-guotan">国谈落地</div>
                    <div class="right-content-box">
                        <div class="content-sub-row" style="background-color: #F8FAFC;">
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Emb<br>纳入双通道</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Cre Oral<br>纳入双通道</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Cre Oral<br>双通道单独支付</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Emb/Cre Oral<br>医保总额单列/合理调整</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Emb/Cre Oral<br>DRG、DIP除外支付/超支补偿</div>
                        </div>
                        <div class="content-sub-row" style="border-bottom: none;">
                            <div class="inner-cell">{txt_0}</div>
                            <div class="inner-cell">{txt_1}</div>
                            <div class="inner-cell">{txt_2}</div>
                            <div class="inner-cell">{txt_3}</div>
                            <div class="inner-cell">{txt_4}</div>
                        </div>
                    </div>
                </div>

                <div class="row-container">
                    <div class="left-title-box color-drg" style="white-space: normal !important; line-height: 1.4; padding: 16px 12px;">创新药DRG<br>除外/激励支付</div>
                    <div class="right-content-box">
                        <div class="content-sub-row" style="background-color: #F8FAFC;">
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Zavi</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Cre IV</div>
                        </div>
                        <div class="content-sub-row" style="border-bottom: none;">
                            <div class="inner-cell">{txt_drg0}</div>
                            <div class="inner-cell">{txt_drg1}</div>
                        </div>
                    </div>
                </div>

                <div class="row-container">
                    <div class="left-title-box color-vbp">1-8批续约</div>
                    <div class="right-content-box">
                        <div class="content-sub-row" style="background-color: #F8FAFC;">
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">中选:非中选比例</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及合并考核</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及不一刀切</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及红黄标色</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及异常使用现象</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及医保支付价</div>
                        </div>
                        <div class="content-sub-row" style="border-bottom: none;">
                            <div class="inner-cell">{txt_v0}</div>
                            <div class="inner-cell">{txt_v1}</div>
                            <div class="inner-cell">{txt_v2}</div>
                            <div class="inner-cell">{txt_v3}</div>
                            <div class="inner-cell">{txt_v4}</div>
                            <div class="inner-cell">{txt_v5}</div>
                        </div>
                    </div>
                </div>

                <div class="row-container">
                    <div class="left-title-box color-fenji">分级目录管理</div>
                    <div class="right-content-box">
                        <div class="content-sub-row" style="background-color: #F8FAFC;">
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及超品种备案</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">提及超分级目录备案</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Cre IV</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Cre Oral</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">Emb</div>
                            <div class="inner-cell" style="padding: 16px 8px; color: #475569; font-weight: 700; font-size: 13px;">X</div>
                        </div>
                        <div class="content-sub-row" style="border-bottom: none;">
                            <div class="inner-cell">{txt_f0}</div>
                            <div class="inner-cell">{txt_f1}</div>
                            <div class="inner-cell">{txt_f2}</div>
                            <div class="inner-cell">{txt_f3}</div>
                            <div class="inner-cell">{txt_f4}</div>
                            <div class="inner-cell">{txt_f5}</div>
                        </div>
                    </div>
                </div>
                """
                
                st.markdown(html_prov, unsafe_allow_html=True)
    else:
        st.error("未检测到源数据。")

# ----------------- 原小程序第一页 (L1) -----------------
elif st.session_state.step == 'L1':
    st.button("⬅️ 返回Dashboard", key="back_to_dash_btn", on_click=nav_to, args=('L0',))
    
    st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)
    st.markdown('<div class="capsule-line-container"><div class="capsule-line"></div></div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, mid, c3 = st.columns([1, 2, 1])
    with mid:
        st.button("国家政策", key="nat_btn", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.button("地方政策", key="loc_btn", use_container_width=True, on_click=nav_to, args=('L2', "地方"))

# ----------------- 原小程序第二页 (L2) -----------------
elif st.session_state.step == 'L2':
    st.button("⬅️ 返回", key="back_btn", on_click=nav_to, args=('L1',))
    
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
                "VBP": [], "DRG/DIP": [],
                "其他": ["药品RWE价值评价指南", "RWE国家可信点公约", "支持创新药高质量发展若干措施", "药品RWE指南汇总"]
            }
        }
        for cat, files in nat_struct[dept].items():
            with st.expander(f"🔹 {cat}", expanded=False):
                if not files: st.caption("暂无文件")
                else:
                    for f in files:
                        url = LINKS.get(f, "#")
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#0066cc;">🔗 查看原文</a></div>', unsafe_allow_html=True)

    else:
        biz_opts = ["国谈落地", "1-8批集采续约", "PVBP", "DRG/DIP", "分级管理目录", "其他"]
        biz = st.selectbox("请选择政策领域", biz_opts)
        
        if biz == "国谈落地":
            df = load_excel_data()
            if df is None: st.warning("⚠️ 没找到 '数据.xlsx'！")
            else:
                prov = st.selectbox("查询省份核心指标分析", df['省份'].unique().tolist())
                row = df[df['省份'] == prov].iloc[0]
                st.markdown(f"##### 📌 {prov} - 核心落地指标分析")
                metrics = [("📅 药事会时限", '药事会召开时限'), ("💊 思福诺双通道", '思福诺是否纳入双通道'),
                           ("💊 康新博双通道", '康新博胶囊是否纳入双通道'), ("💰 康新博单独支付", '康新博胶囊是否纳入双通道单独支付'),
                           ("📊 总额单列/调整", '国谈药医保总额单列'), ("🚫 DRG/DIP除外", '国谈药DRG/DIP除外支付')]
                html_m = '<div class="metric-grid">'
                for label, key in metrics:
                    val = str(row[key]) if pd.notna(row[key]) else ""
                    color, bg = "#007bff", "#e6f2ff"
                    if label == "📅 药事会时限":
                        if "1个月" in val or "2个月" in val: color, bg = "#28a745", "#e6fffa" # 绿
                    elif label in ["💊 思福诺双通道", "💊 康新博双通道", "💰 康新博单独支付"]:
                        if "是" in val: color, bg = "#28a745", "#e6fffa" # 绿
                        elif "否" in val: color, bg = "#007bff", "#e6f2ff" # 蓝
                    elif label == "📊 总额单列/调整":
                        if "单列" in val: color, bg = "#28a745", "#e6fffa" # 绿
                        elif "合理调整" in val: color, bg = "#007bff", "#e6f2ff" # 蓝
                    elif label == "🚫 DRG/DIP除外":
                        if "首年" in val or "除外" in val: color, bg = "#28a745", "#e6fffa" # 绿
                        elif "超支补偿" in val: color, bg = "#007bff", "#e6f2ff" # 蓝
                    else: 
                        if "是" in val: color, bg = "#28a745", "#e6fffa"
                        elif "否" in val: color, bg = "#f0ad4e", "#fff9e6"
                    html_m += f'<div class="metric-card" style="border-left-color:{color}; background-color:{bg};"><div style="font-size:11px; color:#666;">{label}</div><div style="font-size:15px; font-weight:700; color:{color};">{val}</div></div>'
                st.markdown(html_m + '</div>', unsafe_allow_html=True)
                st.markdown("---")
                for _, r in df[df['省份'] == prov].iterrows():
                    if pd.notna(r['链接']): st.markdown(f"📄 [{r['原文']}]({r['链接']})")

        elif biz == "1-8批集采续约":
            df_vbp = load_vbp_data()
            if df_vbp is None: st.warning("⚠️ 没找到 'VBP.xlsx'！")
            else:
                prov_v = st.selectbox("查询省份", df_vbp['省份'].unique().tolist())
                row_v = df_vbp[df_vbp['省份'] == prov_v].iloc[0]
                st.markdown(f"##### 📌 {prov_v} - 1-8批集采续约政策要点")
                v_metrics = [
                    ("⚖️ 中选:非中选比例", '中选:非中选比例'), ("📊 提及合并考核", '提及合并考核'),
                    ("🚦 提及红黄标色", '提及红黄标色'), ("🛡️ 提及不一刀切", '提及不一刀切'),
                    ("👁️ 提及高价非中选异常使用", '提及高价非中选异常使用')
                ]
                html_v = '<div class="metric-grid">'
                for label, key in v_metrics:
                    val = str(row_v[key]) if pd.notna(row_v[key]) else ""
                    if key in ['提及合并考核', '提及不一刀切']:
                        color = "#28a745" if val == "是" else "#f0ad4e" if val == "否" else "#007bff"
                        bg = "#e6fffa" if val == "是" else "#fff9e6" if val == "否" else "#e6f2ff"
                    else:
                        if val in ["否", "5:5"]:
                            color, bg = "#28a745", "#e6fffa"
                        elif val in ["是", "中选品完成任务量"]:
                            color, bg = "#f0ad4e", "#fff9e6"
                        else:
                            color, bg = "#007bff", "#e6f2ff"
                    html_v += f'<div class="metric-card" style="border-left-color:{color}; background-color:{bg};"><div style="font-size:11px; color:#666;">{label}</div><div style="font-size:15px; font-weight:700; color:{color};">{val}</div></div>'
                st.markdown(html_v + '</div>', unsafe_allow_html=True)
                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1: st.markdown(f"📄 [接续政策详表]({LINKS['国采1-8批接续采购政策要点详表(详细版)']})")
                if pd.notna(row_v['原文链接']):
                    st.markdown(f'🔗 <a href="{row_v["原文链接"]}" target="_blank" style="color:#0066cc; font-size:14px;">查看该省份执行文件原文</a>', unsafe_allow_html=True)

        elif biz == "分级管理目录":
            df_cp = load_cpzba_data()
            df_cf = load_cfjmlpzba_data()
            all_provs = sorted(list(set(df_cp['省份'].unique()) if df_cp is not None else [] | set(df_cf['省份'].unique()) if df_cf is not None else []))
            prov_sel = st.selectbox("查询省份", all_provs)
            st.markdown(f"##### 📌 {prov_sel} - 抗菌药物备案管理政策")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<p style="font-size:14px; font-weight:bold; color:#003366;">📁 超50/35品种备案</p>', unsafe_allow_html=True)
                if df_cp is not None and not df_cp[df_cp['省份'] == prov_sel].empty:
                    rc = df_cp[df_cp['省份'] == prov_sel].iloc[0]
                    for lab, k in [("🔹 是否提及", "是否提及"), ("📝 明确流程", "是否有明确流程")]:
                        v = str(rc[k]) if pd.notna(rc[k]) else "未提及"
                        clr = "#28a745" if v == "是" else "#f0ad4e" if v == "否" else "#666"
                        b_clr = "#e6fffa" if v == "是" else "#fff9e6" if v == "否" else "#f8f9fa"
                        st.markdown(f'<div class="metric-card" style="border-left-color:{clr}; background-color:{b_clr}; margin-bottom:5px;"><div style="font-size:11px; color:#666;">{lab}</div><div style="font-size:14px; font-weight:700; color:{clr};">{v}</div></div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<p style="font-size:14px; font-weight:bold; color:#003366;">📁 超分级目录品种备案</p>', unsafe_allow_html=True)
                if df_cf is not None and not df_cf[df_cf['省份'] == prov_sel].empty:
                    rf = df_cf[df_cf['省份'] == prov_sel].iloc[0]
                    for lab, k in [("🔹 是否提及", "是否提及"), ("📝 明确流程", "是否有明确流程")]:
                        v = str(rf[k]) if pd.notna(rf[k]) else "未提及"
                        clr = "#28a745" if v == "是" else "#f0ad4e" if v == "否" else "#666"
                        b_clr = "#e6fffa" if v == "是" else "#fff9e6" if v == "否" else "#f8f9fa"
                        st.markdown(f'<div class="metric-card" style="border-left-color:{clr}; background-color:{b_clr}; margin-bottom:5px;"><div style="font-size:11px; color:#666;">{lab}</div><div style="font-size:14px; font-weight:700; color:{clr};">{v}</div></div>', unsafe_allow_html=True)

            st.markdown("---")
            if prov_sel in LEVEL_CATALOG_PDFS:
                pdf_url = LEVEL_CATALOG_PDFS[prov_sel]
                st.markdown(f'<div class="file-card"><b>📄 {prov_sel}抗菌药物分级管理目录原文</b><br><a href="{pdf_url}" target="_blank" style="font-size:12px; color:#0066cc;">🔗 立即查看原文</a></div>', unsafe_allow_html=True)
            else:
                st.caption("ℹ️ 该省份分级目录文件非公开")

        elif biz == "PVBP":
            st.markdown("##### 📁 集中带量采购政策公告 (广东)")
            for f in ["【广东】集采药品接续采购公告(第1号)", "【广东】集采药品接续采购公告(第2号)", "【广东】集采药品接续采购公告(第3号)", "【广东】集采药品接续采购公告(第4号)"]:
                url = LINKS.get(f, "#")
                st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

        elif biz == "DRG/DIP":
            st.markdown("##### 📁 支付改革文件 (北京)")
            f_n = "【北京】DRG付费新药新技术除外支付通知"
            url = LINKS.get(f_n, "#")
            st.markdown(f'<div class="file-card"><b>{f_n}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

# 共用页脚
if st.session_state.step != 'L0':
    st.markdown("""
        <div class="footer-note">
            <b>备注：</b>引用链接文件中<span class="text-green">绿色标识</span>为机会点，
            <span class="text-yellow">黄色标识</span>为风险点。<br>
            © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网
        </div>
    """, unsafe_allow_html=True)

import streamlit as st
import pandas as pd
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

# ==========================================
# --- 2. 界面装修 (CSS 样式) ---
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 26px !important; font-weight: 800; color: #003366; text-align: center; padding-top: 15px; }
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
    .st-key-back_btn { width: auto !important; margin-bottom: 15px !important; }
    .st-key-back_btn button {
        height: 24px !important; min-height: 24px !important; width: auto !important;
        padding: 0 10px !important; background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important; border-radius: 4px !important;
    }
    .st-key-back_btn button p { font-size: 10px !important; color: #888 !important; }
    .footer-note { text-align: center; padding: 30px; color: #666; font-size: 14px !important; border-top: 1px solid #eee; margin-top: 60px; }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #f0ad4e; font-weight: bold; }
    .file-card { background-color: #fcfdfe; padding: 15px; border: 1px solid #eef2f6; border-top: 3px solid #0056b3; border-radius: 8px; margin-bottom: 12px; }
    .metric-card { padding: 10px; border-radius: 6px; border-left: 4px solid; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

# ==========================================
# --- 4. 数据加载 (含符号自动修正) ---
# ==========================================
@st.cache_data
def load_excel_data():
    file_path = '数据.xlsx'
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(subset=['省份']) # 只读到有省份内容的地方
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
        df = df.dropna(subset=['省份']) # 关键：只读到陕西，后面空行不读
        # 💡 新增：自动修正比例中的中文冒号，确保格式统一
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

# --- 6. 界面渲染 ---
st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)
st.markdown('<div class="capsule-line-container"><div class="capsule-line"></div></div>', unsafe_allow_html=True)

if st.session_state.step == 'L1':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, mid, c3 = st.columns([1, 2, 1])
    with mid:
        st.button("国家政策", key="nat_btn", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.button("地方政策", key="loc_btn", use_container_width=True, on_click=nav_to, args=('L2', "地方"))

elif st.session_state.step == 'L2':
    st.button("⬅️ 返回主页", key="back_btn", on_click=nav_to, args=('L1',))
    
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
                    # --- 💡 核心逻辑更新处 ---
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
                        if "首年" in val: color, bg = "#28a745", "#e6fffa" # 绿
                        elif "超支补偿" in val: color, bg = "#007bff", "#e6f2ff" # 蓝
                    else: # 其他兜底逻辑
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

st.markdown("""
    <div class="footer-note">
        <b>备注：</b>文件中<span class="text-green">绿色标识</span>为机会点，
        <span class="text-yellow">黄色标识</span>为风险点。<br>
        © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网
    </div>
""", unsafe_allow_html=True)

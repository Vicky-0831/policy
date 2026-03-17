import streamlit as st
import pandas as pd
import os
import time
import threading
import requests

# ==========================================
# --- 0. 技术保活（后台自动运行，通常不用管） ---
# #️⃣后面的这些内容都是注释，是不会在运行代码时候生效的
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
# --- 2. 界面装修（CSS 样式：管字号、颜色、按钮大小） ---
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }

    /* 【修改处】主标题设置 */
    .main-title { font-size: 26px !important; font-weight: 800; color: #003366; text-align: center; padding-top: 15px; }
    
    /* 标题下方的小横线装饰 */
    .capsule-line-container { display: flex; justify-content: center; margin: 10px 0 25px 0; }
    .capsule-line {
        width: 120px; height: 6px; border-radius: 10px; position: relative;
        background: linear-gradient(90deg, rgba(0,74,153,0) 0%, #004a99 50%, rgba(0,74,153,0) 100%);
    }

    /* --- 【核心：首页大按钮设置】 --- */
    /* 1. 国家级政策按钮（蓝色渐变） */
    .st-key-nat_btn button {
        background: linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%) !important;
        height: 85px !important;    /* 按钮高度：85px */
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,74,153,0.2) !important;
    }
    .st-key-nat_btn button p {
        color: #0369a1 !important;  /* 文字颜色 */
        font-size: 20px !important; /* 字体大小：20px */
        font-weight: 700 !important;
    }

    /* 2. 地方性政策按钮（绿色渐变） */
    .st-key-loc_btn button {
        background: linear-gradient(135deg, #f0fdf4 0%, #bbf7d0 100%) !important;
        height: 85px !important;
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(21,128,61,0.2) !important;
    }
    .st-key-loc_btn button p {
        color: #15803d !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    /* --- 【核心：返回主页小按钮设置】 --- */
    .st-key-back_btn { width: auto !important; margin-bottom: 15px !important; }
    .st-key-back_btn button {
        height: 24px !important;      /* 极致缩小高度 */
        min-height: 24px !important;
        width: auto !important;
        padding: 0 10px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 4px !important;
    }
    .st-key-back_btn button p {
        font-size: 10px !important;   
        color: #888 !important;
    }

    /* 备注信息样式：管绿色和黄色加粗 */
    .footer-note { text-align: center; padding: 30px; color: #666; font-size: 14px !important; border-top: 1px solid #eee; margin-top: 60px; }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #f0ad4e; font-weight: bold; }
    
    /* 文件夹卡片和 Excel 指标方块样式 */
    .file-card { background-color: #fcfdfe; padding: 15px; border: 1px solid #eef2f6; border-top: 3px solid #0056b3; border-radius: 8px; margin-bottom: 12px; }
    .metric-card { padding: 10px; border-radius: 6px; border-left: 4px solid; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# --- 3. 页面跳转管理 ---
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1

# ==========================================
# --- 4. Excel 表格读取逻辑 ---
# ==========================================
@st.cache_data
def load_excel_data():
    file_path = '数据.xlsx' # 【注意】文件名必须严格一致
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path)
        df['省份'] = df['省份'].ffill()
        cols = ['药事会召开时限', '思福诺是否纳入双通道', '康新博胶囊是否纳入双通道', 
                '康新博胶囊是否纳入双通道单独支付', '国谈药医保总额单列', '国谈药DRG/DIP除外支付']
        df[cols] = df[cols].ffill()
        return df
    except: return None

# ==========================================
# --- 5. 【PDF 链接仓库】在这里改链接 ---
# 类似"nhc_kjyw_2012.pdf"的文件命名都是我修改的，这样在代码可以避免中文或者是空格的出现而出错
# ==========================================
BASE_URL = "https://vicky-0831.github.io/policy/pdfs/"
LINKS = {
    # 国家级
    "2012年抗菌药物管理办法": BASE_URL + "nhc_kjyw_2012.pdf",  #不要在代码中出现空格，空格都使用_代替
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
    # 地方级
    "【北京】DRG付费新药新技术除外支付通知": BASE_URL + "bj_drg.pdf",
    "【广东】集采药品接续采购公告(第1号)": BASE_URL + "gd_vbp_1.pdf",
    "【广东】集采药品接续采购公告(第2号)": BASE_URL + "gd_vbp_2.pdf",
    "【广东】集采药品接续采购公告(第3号)": BASE_URL + "gd_vbp_3.pdf",
    "【广东】集采药品接续采购公告(第4号)": BASE_URL + "gd_vbp_4.pdf",
    "【浙江】第一批创新医药技术医保支付激励名单": BASE_URL + "zj_incentive.pdf"
}

# ==========================================
# --- 6. 界面内容渲染 ---
# ==========================================
st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)
st.markdown('<div class="capsule-line-container"><div class="capsule-line"></div></div>', unsafe_allow_html=True)

# --- 首页展示 ---
if st.session_state.step == 'L1':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, mid, c3 = st.columns([1, 2, 1])
    with mid:
        # 国家级和地方性两个大按钮
        st.button("国家级政策", key="nat_btn", use_container_width=True, on_click=nav_to, args=('L2', "国家"))
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.button("地方性政策", key="loc_btn", use_container_width=True, on_click=nav_to, args=('L2', "地方"))

# --- 二级页面内容 ---
elif st.session_state.step == 'L2':
    st.button("⬅️ 返回主页", key="back_btn", on_click=nav_to, args=('L1',))
    
    if st.session_state.l1 == "国家":
        dept = st.selectbox("请选择政策部门", ["国家医保局", "国家卫健委"])
        st.markdown(f"#### 📂 {dept}")
        
        # 这里的目录结构，想加文件直接在名字后面加引号填入即可，但是要保持和前面已经加过的文件格式一致
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
            with st.expander(f"🔹 {cat}", expanded=False): # 默认折叠，我觉得这样看着比较干净
                if not files: st.caption("暂无文件")
                else:
                    for f in files:
                        url = LINKS.get(f, "#")
                        st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#0066cc;">🔗 查看原文</a></div>', unsafe_allow_html=True)

    else: # --- 地方性政策 ---
        biz_opts = ["国谈落地", "集采", "DRG/DIP", "超品规备案", "VBP", "其他"]
        biz = st.selectbox("请选择政策领域", biz_opts)
        
        if biz == "国谈落地":
            # --- Excel 分析模块 ---
            df = load_excel_data()
            if df is None: st.warning("⚠️ 没找到 '数据.xlsx'，请检查文件名！")  #可以自定义一些小emoji😈，比较有意思哈哈哈哈哈
            else:
                prov = st.selectbox("查询省份核心指标分析", df['省份'].unique().tolist())
                row = df[df['省份'] == prov].iloc[0]
                st.markdown(f"##### 📌 {prov} - 核心落地指标分析")
                metrics = [("📅 药事会时限", '药事会召开时限'), ("💊 思福诺双通道", '思福诺是否纳入双通道'),
                           ("💊 康新博双通道", '康新博胶囊是否纳入双通道'), ("💰 康新博单独支付", '康新博胶囊是否纳入双通道单独支付'),
                           ("📊 总额单列/调整", '国谈药医保总额单列'), ("🚫 DRG/DIP除外", '国谈药DRG/DIP除外支付')]
                
                html_m = '<div class="metric-grid">'
                for label, key in metrics:
                    val = str(row[key])
                    color = "#28a745" if "是" in val else "#dc3545" if "否" in val else "#007bff"
                    bg = "#e6fffa" if "是" in val else "#ffe6e6" if "否" in val else "#e6f2ff"
                    html_m += f'<div class="metric-card" style="border-left-color:{color}; background-color:{bg};"><div style="font-size:11px; color:#666;">{label}</div><div style="font-size:15px; font-weight:700; color:{color};">{val}</div></div>'
                st.markdown(html_m + '</div>', unsafe_allow_html=True)
                st.markdown("---")
                for _, r in df[df['省份'] == prov].iterrows():
                    if pd.notna(r['链接']): st.markdown(f"📄 [{r['原文']}]({r['链接']})")

        elif biz == "集采":
            st.markdown("##### 📁 集中带量采购政策公告 (广东)")
            gd_list = ["【广东】集采药品接续采购公告(第1号)", "【广东】集采药品接续采购公告(第2号)", "【广东】集采药品接续采购公告(第3号)", "【广东】集采药品接续采购公告(第4号)"]
            for f in gd_list:
                url = LINKS.get(f, "#")
                st.markdown(f'<div class="file-card"><b>{f}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

        elif biz == "DRG/DIP":
            st.markdown("##### 📁 支付改革文件 (北京)")
            f_n = "【北京】DRG付费新药新技术除外支付通知"
            url = LINKS.get(f_n, "#")
            st.markdown(f'<div class="file-card"><b>{f_n}</b><br><a href="{url}" target="_blank" style="font-size:12px; color:#c62828;">🔗 查看原文</a></div>', unsafe_allow_html=True)

# ==========================================
# --- 7. 底部注脚与备注 ---
# ==========================================
st.markdown("""
    <div class="footer-note">
        <b>备注：</b>文件中<span class="text-green">绿色标识</span>为机会点，
        <span class="text-yellow">黄色标识</span>为风险点。<br>
        © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局及各地医保局官网
    </div>
""", unsafe_allow_html=True)

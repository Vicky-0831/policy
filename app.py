import streamlit as st

# 1. 页面配置
st.set_page_config(page_title="政策直通车", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 药学专业配色 & 标题强化 CSS ---
st.markdown("""
    <style>
    /* 全局背景：洁净白 */
    .stApp { background-color: #ffffff; }

    /* 2. 标题字号：全界面最大 */
    .main-title {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: #003366;
        text-align: center;
        padding: 40px 0 20px 0;
        letter-spacing: 2px;
    }

    /* 1. 一级菜单按钮：增设底色并保持文字凸显 */
    /* 国家级按钮：深医学蓝 */
    div[data-testid="stButton"] > button:first-child[aria-label*="国家级"] {
        background-color: #004a99 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 60px !important;
    }
    /* 地方性按钮：医学朱红（代表临床/急救） */
    div[data-testid="stButton"] > button:first-child[aria-label*="地方性"] {
        background-color: #c62828 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 60px !important;
    }

    /* 三级卡片布局 */
    .policy-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 15px; margin-top: 10px; }
    .simple-card {
        background-color: #fcfdfe; padding: 20px; border: 1px solid #eef2f6;
        border-top: 4px solid #0056b3; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .card-title { font-size: 14px !important; font-weight: 700 !important; color: #003366; margin-bottom: 12px; }

    /* 3. 备注内容放大 */
    .footer-note { 
        text-align: center; padding: 40px; color: #555; 
        font-size: 15px !important;  /* 字体放大 */
        margin-top: 80px; border-top: 1px solid #eee; 
    }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #f0ad4e; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 状态管理 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None

def nav_to(step, l1=None):
    st.session_state.step = step
    if l1 is not None: st.session_state.l1 = l1
    st.rerun()

# --- 3. 目录与真实链接数据 ---
STRUCTURE = {
    "国家": {
        "国家卫健委": {
            "抗菌药物管理办法": ["2012年抗菌药物管理办法", "2015年抗菌药物管理评价指标"],
            "绩效监测": ["2025版公立医院绩效监测手册"],
            "基本药物": ["基药目录管理办法通知", "国家基本药物目录管理办法(通用版)", "2026版基药目录管理办法"],
            "超品规备案": [],
            "医院管理质控": ["2025年药事管理医疗质量控制指标"],
            "其他": []
        },
        "国家医保局": {
            "国谈落地": ["2025年医保药品目录通知", "做好谈判药品落地工作的通知"],
            "红黄标": ["挂网药品价格风险预警标识通知"],
            "基金监管": ["2026年医保基金监管工作通知"],
            "其他": [
                "药品RWE价值评价指南征求意见", "RWE国家可信评价点网络公约公告", 
                "支持创新药高质量发展若干措施", "药品RWE综合价值评价系列指南汇总"
            ]
        }
    },
    "地方": {
        "北京": ["第二批DRG付费新药新技术除外支付工作通知"],
        "广东": [
            "集采药品接续采购公告（第1号）", "集采药品接续采购公告（第2号）", 
            "集采药品接续采购公告（第3号）", "集采药品接续采购公告（第4号）"
        ],
        "浙江": ["第一批创新医药技术医保支付激励名单公示"]
    }
}

BASE_RAW_URL = "https://vicky-0831.github.io/policy/pdfs/"
LINKS = {
    "第二批DRG付费新药新技术除外支付工作通知": BASE_RAW_URL + "bj_drg.pdf",
    "集采药品接续采购公告（第1号）": BASE_RAW_URL + "gd_vbp_1.pdf",
    "集采药品接续采购公告（第2号）": BASE_RAW_URL + "gd_vbp_2.pdf",
    "集采药品接续采购公告（第3号）": BASE_RAW_URL + "gd_vbp_3.pdf",
    "集采药品接续采购公告（第4号）": BASE_RAW_URL + "gd_vbp_4.pdf",
    "第一批创新医药技术医保支付激励名单公示": BASE_RAW_URL + "zj_incentive.pdf",
    "2012年抗菌药物管理办法": BASE_RAW_URL + "nhc_kjyw_2012.pdf",
    "2015年抗菌药物评价指标": BASE_RAW_URL + "nhc_kjyw_zk_2015.pdf",
    "2025版公立医院绩效监测手册": BASE_RAW_URL + "nhc_jxjc_2025.pdf",
    "基药目录管理办法通知": BASE_RAW_URL + "nhc_jy_tz.pdf",
    "国家基本药物目录管理办法(通用版)": BASE_RAW_URL + "nhc_jy_glbf.pdf",
    "2026版基药目录管理办法": BASE_RAW_URL + "nhc_jy_2026.pdf",
    "2025年药事管理医疗质量控制指标": BASE_RAW_URL + "nhc_zk_2025.pdf",
    "2025年医保药品目录通知": BASE_RAW_URL + "nhsa_ypml_2025.pdf",
    "做好谈判药品落地工作的通知": BASE_RAW_URL + "nhsa_tpyp_ld.pdf",
    "挂网药品价格风险预警标识通知": BASE_RAW_URL + "nhsa_fx_yj.pdf",
    "2026年医保基金监管工作通知": BASE_RAW_URL + "nhsa_jjjg_2026.pdf",
    "药品RWE价值评价指南征求意见": BASE_RAW_URL + "nhsa_rwe_yj.pdf",
    "RWE国家可信评价点网络公约公告": BASE_RAW_URL + "nhsa_rwe_kxd.pdf",
    "支持创新药高质量发展若干措施": BASE_RAW_URL + "nhsa_cxyp_cs.pdf",
    "药品RWE综合价值评价系列指南汇总": BASE_RAW_URL + "nhsa_rwe_hz.pdf"
}

# --- 4. 界面渲染 ---
st.markdown('<div class="main-title">🏥 政策直通车</div>', unsafe_allow_html=True)

# L1: 首页选择（上下排列，高辨识度医学色）
if st.session_state.step == 'L1':
    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.button("🏛️ 国家级政策维度", use_container_width=True, on_click=nav_to, args=('L2', "国家"), key="btn_nat")
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.button("📍 地方性政策维度", use_container_width=True, on_click=nav_to, args=('L2', "地方"), key="btn_loc")

# 二级及以上：内容呈现
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回主页"): nav_to('L1')
    st.markdown(f"### 🔍 {st.session_state.l1}政策概览")
    
    if st.session_state.l1 == "国家":
        # 4. 国家部分：少一级跳转，采用下拉框+折叠面板
        col_side, col_main = st.columns([1, 3])
        with col_side:
            dept = st.selectbox("⬇️ 选择部门", ["国家卫健委", "国家医保局"])
        
        with col_main:
            st.write(f"📂 {dept} 相关政策")
            categories = STRUCTURE["国家"][dept]
            for cat, files in categories.items():
                with st.expander(f"📁 {cat}", expanded=True):
                    if not files:
                        st.caption("暂无跳转文件")
                    else:
                        st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
                        for f in files:
                            url = LINKS.get(f, "#")
                            st.markdown(f'''
                                <div class="simple-card">
                                    <div class="card-title">{f}</div>
                                    <a href="{url}" target="_blank" style="text-decoration:none; color:#0066cc; font-weight:600; font-size:12px;">🔗 点击阅读原文</a>
                                </div>
                            ''', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # 地方部分：保持扁平化切换
        provinces = list(STRUCTURE["地方"].keys())
        p_tab = st.tabs(provinces)
        for i, prov in enumerate(provinces):
            with p_tab[i]:
                files = STRUCTURE["地方"][prov]
                st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
                for f in files:
                    url = LINKS.get(f, "#")
                    st.markdown(f'''
                        <div class="simple-card">
                            <div class="card-title">{f}</div>
                            <a href="{url}" target="_blank" style="text-decoration:none; color:#c62828; font-weight:600; font-size:12px;">🔗 点击阅读原文</a>
                        </div>
                    ''', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# 5. 注脚：备注字样及字号放大
st.markdown(f"""
    <div class="footer-note">
        <b>备注：</b>文件中<span class="text-green">绿色标识</span>为机会点，
        <span class="text-yellow">黄色标识</span>为风险点。<br>
        © 2026 政策直通车 | 数据来源：国家卫健委、国家医保局、京粤浙医保局官网 [cite: 1, 3, 50, 151, 170, 212, 254]
    </div>
""", unsafe_allow_html=True)

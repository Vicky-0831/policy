import streamlit as st

# 1. 页面配置
st.set_page_config(page_title="政策直通车", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 医疗专业配色 & 极简布局 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1 { font-size: 20px !important; font-weight: 700 !important; color: #003366; text-align: center; padding: 20px 0; }
    h3 { font-size: 16px !important; font-weight: 600 !important; color: #004a99; margin-bottom: 15px !important; }
    p, div, span { font-size: 13px !important; color: #333333; }
    
    .stButton>button {
        border-radius: 4px; font-size: 14px; font-weight: 500; height: 50px;
        background-color: #f8fbff; border: 1px solid #d1e2f3; color: #003366; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #eef6ff; border-color: #004a99; color: #004a99; }

    .policy-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; margin-top: 10px; }
    .simple-card {
        background-color: #fcfdfe; padding: 18px; border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .card-title { font-size: 13px !important; font-weight: 700 !important; color: #003366; margin-bottom: 10px; line-height: 1.4; }
    
    .footer-note { text-align: center; padding: 30px; color: #888; font-size: 12px !important; margin-top: 60px; border-top: 1px solid #f0f0f0; }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #ffcc00; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 状态管理 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None
if 'l2' not in st.session_state: st.session_state.l2 = None
if 'l3' not in st.session_state: st.session_state.l3 = None

def nav_to(step, l1=None, l2=None, l3=None):
    st.session_state.step = step
    if l1 is not None: st.session_state.l1 = l1
    if l2 is not None: st.session_state.l2 = l2
    if l3 is not None: st.session_state.l3 = l3
    st.rerun()

# --- 3. 目录与真实链接数据 ---
# 国家级为 4 层结构，地方级为 3 层结构
BASE_RAW_URL = "https://vicky-0831.github.io/policy/pdfs/"

STRUCTURE = {
    "国家": {
        "国家卫健委": {
            "抗菌药物管理办法": ["2012年抗菌药物管理办法", "2015年抗菌药物评价指标"],
            "绩效监测": ["2025版三级公立医院绩效监测手册"],
            "基本药物": ["基药目录管理办法通知", "基药目录管理办法(通用版)", "2026版基药目录管理办法"],
            "超品规备案": [],
            "医院管理质控": ["2025年药事管理医疗质量控制指标"],
            "其他": []
        },
        "国家医保局": {
            "国谈落地": ["2025年医保药品目录通知", "做好谈判药品落地工作的通知"],
            "红黄标": ["挂网药品价格风险预警标识通知"],
            "基金监管": ["2026年医保基金监管工作通知"],
            "VBP": [], 
            "DRG/DIP": [],
            "其他": [
                "药品RWE价值评价指南征求意见", 
                "RWE国家可信评价点网络公约公告", 
                "支持创新药高质量发展若干措施", 
                "药品RWE综合价值评价系列指南汇总"
            ]
        }
    },
    "地方": {
        "北京": ["第二批DRG付费新药新技术除外支付工作通知"],
        "广东": [
            "集采药品接续采购公告（第1号）", 
            "集采药品接续采购公告（第2号）", 
            "集采药品接续采购公告（第3号）", 
            "集采药品接续采购公告（第4号）"
        ],
        "浙江": ["第一批创新医药技术医保支付激励名单公示"]
    }
}

LINKS = {
    # 1. 地方政策文件
    "第二批DRG付费新药新技术除外支付工作通知": BASE_RAW_URL + "bj_drg.pdf",
    "集采药品接续采购公告（第1号）": BASE_RAW_URL + "gd_vbp_1.pdf",
    "集采药品接续采购公告（第2号）": BASE_RAW_URL + "gd_vbp_2.pdf",
    "集采药品接续采购公告（第3号）": BASE_RAW_URL + "gd_vbp_3.pdf",
    "集采药品接续采购公告（第4号）": BASE_RAW_URL + "gd_vbp_4.pdf",
    "第一批创新医药技术医保支付激励名单公示": BASE_RAW_URL + "zj_incentive.pdf",

    # 2. 国家卫健委文件
    "2012年抗菌药物管理办法": BASE_RAW_URL + "nhc_kjyw_2012.pdf",
    "2015年抗菌药物评价指标": BASE_RAW_URL + "nhc_kjyw_zk_2015.pdf",
    "2025版三级公立医院绩效监测手册": BASE_RAW_URL + "nhc_jxjc_2025.pdf",
    "基药目录管理办法通知": BASE_RAW_URL + "nhc_jy_tz.pdf",
    "基药目录管理办法(通用版)": BASE_RAW_URL + "nhc_jy_glbf.pdf",
    "2026版基药目录管理办法": BASE_RAW_URL + "nhc_jy_2026.pdf",
    "2025年药事管理医疗质量控制指标": BASE_RAW_URL + "nhc_zk_2025.pdf",

    # 3. 国家医保局文件
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
st.markdown('<h1>🏥 政策直通车</h1>', unsafe_allow_html=True)

# L1: 国家 vs 地方
if st.session_state.step == 'L1':
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏛️ 国家级政策", use_container_width=True): nav_to('L2', l1="国家")
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button("📍 地方性政策", use_container_width=True): nav_to('L2', l1="地方")

# L2: 部门 / 省份
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回主页"): nav_to('L1')
    st.markdown(f"### 📂 当前选择：{st.session_state.l1}")
    opts = list(STRUCTURE[st.session_state.l1].keys())
    cols = st.columns(len(opts))
    for i, opt in enumerate(opts):
        with cols[i]:
            if st.button(opt, use_container_width=True): nav_to('L3', l2=opt)

# L3: 三级展示
elif st.session_state.step == 'L3':
    if st.button("⬅️ 返回上级"): nav_to('L2')
    st.markdown(f"### 🔍 {st.session_state.l2}")
    
    current_data = STRUCTURE[st.session_state.l1][st.session_state.l2]
    
    if isinstance(current_data, dict): # 国家级：进入四级子目录
        cols = st.columns(2)
        for i, (cat, files) in enumerate(current_data.items()):
            with cols[i % 2]:
                if st.button(f"📁 {cat}", use_container_width=True): nav_to('L4', l3=cat)
    else: # 地方级：直接展示文件卡片
        st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
        for f in current_data:
            url = LINKS.get(f, "#")
            st.markdown(f'<div class="simple-card"><div class="card-title">{f}</div><a href="{url}" target="_blank" style="text-decoration:none; color:#0066cc; font-weight:600; font-size:12px;">🔗 查看官方原文</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# L4: 国家级专用四级文件列表
elif st.session_state.step == 'L4':
    if st.button("⬅️ 返回子目录"): nav_to('L3')
    st.markdown(f"### 📄 {st.session_state.l3}")
    
    files = STRUCTURE["国家"][st.session_state.l2][st.session_state.l3]
    st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
    for f in files:
        url = LINKS.get(f, "#")
        st.markdown(f'<div class="simple-card"><div class="card-title">{f}</div><a href="{url}" target="_blank" style="text-decoration:none; color:#0066cc; font-weight:600; font-size:12px;">🔗 查看官方原文</a></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. 注脚
st.markdown(f"""<div class="footer-note">文件中<span class="text-green">绿色标识</span>为机会点，<span class="text-yellow">黄色标识</span>为风险点。<br>© 2026 政策直通车 | 数据来源：各官方公示文件</div>""", unsafe_allow_html=True)

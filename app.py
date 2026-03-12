import streamlit as st

# 1. 页面配置
st.set_page_config(
    page_title="政策直通车", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 🎨 医疗专业配色 & 极简字体 CSS ---
st.markdown("""
    <style>
    /* 全局背景：洁净白 */
    .stApp { background-color: #ffffff; }

    /* 字体大小严格控制 */
    h1 { font-size: 20px !important; font-weight: 700 !important; color: #003366; text-align: center; }
    h3 { font-size: 16px !important; font-weight: 600 !important; color: #004a99; }
    p, div, span { font-size: 13px !important; color: #333333; }

    /* 顶部标题：无背景框 */
    .clean-header {
        padding: 30px 0;
        text-align: center;
        margin-bottom: 20px;
    }

    /* 统一按钮样式：医学蓝 */
    .stButton>button {
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
        height: 50px;
        background-color: #f8fbff;
        border: 1px solid #d1e2f3;
        color: #003366;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #eef6ff;
        border-color: #004a99;
        color: #004a99;
    }

    /* 三级卡片布局 */
    .policy-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 10px;
    }
    
    .simple-card {
        background-color: #fcfdfe;
        padding: 20px;
        border: 1px solid #eef2f6;
        border-top: 3px solid #0056b3;
        border-radius: 6px;
        text-align: left;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .card-title { 
        font-size: 14px !important; 
        font-weight: 700 !important; 
        color: #003366; 
        margin-bottom: 12px;
        line-height: 1.4;
    }

    /* 注脚颜色修正 */
    .footer-note {
        text-align: center;
        padding: 30px;
        color: #888;
        font-size: 12px !important;
        margin-top: 60px;
        border-top: 1px solid #f0f0f0;
    }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #ffcc00; font-weight: bold; } /* 修正为黄色 */
    </style>
""", unsafe_allow_html=True)

# --- 2. 状态管理 ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1' not in st.session_state: st.session_state.l1 = None
if 'l2' not in st.session_state: st.session_state.l2 = None

def nav_to(step, l1=None, l2=None):
    st.session_state.step = step
    if l1: st.session_state.l1 = l1
    if l2: st.session_state.l2 = l2
    st.rerun()

# --- 3. 目录与真实链接数据 ---
# 简化后的三级目录标题
STRUCTURE = {
    "国家": {
        "国家卫健委": [
            "2012年抗菌药物临床应用管理办法", 
            "2015年抗菌药物应用评价指标及要求",
            "2025版公立医院绩效监测操作手册", 
            "国家基本药物目录管理办法通知", 
            "国家基本药物目录管理办法", 
            "2026年版基药目录管理办法",
            "2025年药事管理医疗质量控制指标", 
            "超品规备案", 
            "其他"
        ],
        "国家医保局": [
            "2025年版国家医保药品目录通知", 
            "做好谈判药品落地工作的通知", 
            "挂网药品价格风险预警标识通知", 
            "2026年医保基金监管工作通知",  
            "药品RWE综合价值评价指南征求意见", 
            "RWE国家可信评价点网络公约公告", 
            "支持创新药高质量发展若干措施", 
            "药品RWE综合价值评价系列指南汇总",
            "DRG/DIP", 
            "VBP"
        ]
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

# 对应的跳转链接
BASE_RAW_URL = "https://vicky-0831.github.io/policy/pdfs/"

LINKS = {
    # 地方政策链接
    "第二批DRG付费新药新技术除外支付工作通知": BASE_RAW_URL + "bj_drg.pdf",
    "集采药品接续采购公告（第1号）": BASE_RAW_URL + "gd_vbp_1.pdf",
    "集采药品接续采购公告（第2号）": BASE_RAW_URL + "gd_vbp_2.pdf",
    "集采药品接续采购公告（第3号）": BASE_RAW_URL + "gd_vbp_3.pdf",
    "集采药品接续采购公告（第4号）": BASE_RAW_URL + "gd_vbp_4.pdf",
    "第一批创新医药技术医保支付激励名单公示": BASE_RAW_URL + "zj_incentive.pdf",

    # 国家卫健委链接
    "2012年抗菌药物临床应用管理办法": BASE_RAW_URL + "nhc_kjyw_2012.pdf",
    "2015年抗菌药物应用评价指标及要求": BASE_RAW_URL + "nhc_kjyw_zk_2015.pdf",
    "2025版公立医院绩效监测操作手册": BASE_RAW_URL + "nhc_jxjc_2025.pdf",
    "国家基本药物目录管理办法通知": BASE_RAW_URL + "nhc_jy_tz.pdf",
    "国家基本药物目录管理办法": BASE_RAW_URL + "nhc_jy_glbf.pdf",
    "2026年版基药目录管理办法": BASE_RAW_URL + "nhc_jy_2026.pdf",
    "2025年药事管理医疗质量控制指标": BASE_RAW_URL + "nhc_zk_2025.pdf",

    # 国家医保局链接
    "2025年版国家医保药品目录通知": BASE_RAW_URL + "nhsa_ypml_2025.pdf",
    "做好谈判药品落地工作的通知": BASE_RAW_URL + "nhsa_tpyp_ld.pdf",
    "挂网药品价格风险预警标识通知": BASE_RAW_URL + "nhsa_fx_yj.pdf",
    "2026年医保基金监管工作通知": BASE_RAW_URL + "nhsa_jjjg_2026.pdf",
    "药品RWE综合价值评价指南征求意见": BASE_RAW_URL + "nhsa_rwe_yj.pdf",
    "RWE国家可信评价点网络公约公告": BASE_RAW_URL + "nhsa_rwe_kxd.pdf",
    "支持创新药高质量发展若干措施": BASE_RAW_URL + "nhsa_cxyp_cs.pdf",
    "药品RWE综合价值评价系列指南汇总": BASE_RAW_URL + "nhsa_rwe_hz.pdf"
}
# --- 4. 界面渲染 ---

# 顶部标题
st.markdown('<div class="clean-header"><h1>🏥 政策直通车</h1></div>', unsafe_allow_html=True)

# --- 一级页面：国家 vs 地方 (上下排列，颜色一致) ---
if st.session_state.step == 'L1':
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏛️ 国家级政策", use_container_width=True):
            nav_to('L2', l1="国家")
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button("📍 地方性政策", use_container_width=True):
            nav_to('L2', l1="地方")

# --- 二级页面：部门 / 省份 ---
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回首页"): nav_to('L1')
    st.markdown(f"### 📂 当前选择：{st.session_state.l1}")
    
    opts = list(STRUCTURE[st.session_state.l1].keys())
    # 动态列数，适应不同省份数量
    cols = st.columns(len(opts))
    for i, opt in enumerate(opts):
        with cols[i]:
            if st.button(opt, use_container_width=True):
                nav_to('L3', l2=opt)

# --- 三级页面：简化后的卡片 (无标题字样) ---
elif st.session_state.step == 'L3':
    if st.button("⬅️ 返回上级"): nav_to('L2')
    
    policies = STRUCTURE[st.session_state.l1][st.session_state.l2]
    st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
    for p in policies:
        url = LINKS.get(p, "#")
        st.markdown(f"""
            <div class="simple-card">
                <div class="card-title">{p}</div>
                <a href="{url}" target="_blank" style="text-decoration:none; color:#0066cc; font-weight:600; font-size:12px;">🔗 查看官方原文</a>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 注脚：颜色与内容修正 ---
st.markdown(f"""
    <div class="footer-note">
        文件中<span class="text-green">绿色标识</span>为机会点，
        <span class="text-yellow">黄色标识</span>为风险点。<br>
        © 2026 政策直通车 | 数据来源：各官方公示文件
    </div>
""", unsafe_allow_html=True)

import streamlit as st

# 1. 页面配置
st.set_page_config(
    page_title="政策机会点直通车", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 🎨 医学专业配色 & 精致字体 CSS ---
st.markdown("""
    <style>
    /* 全局背景：极淡灰蓝，专业感强 */
    .stApp { background-color: #f4f7f9; }

    /* 字体大小严格控制 */
    h1 { font-size: 20px !important; font-weight: 700 !important; color: #003366; margin-bottom: 10px !important; }
    h3 { font-size: 16px !important; font-weight: 600 !important; color: #004a99; margin-top: 15px !important; }
    p, div, span { font-size: 13px !important; color: #333333; }

    /* 顶部医学蓝 Banner */
    .medical-banner {
        background: linear-gradient(135deg, #004a99 0%, #0066cc 100%);
        padding: 20px;
        color: white;
        text-align: center;
        border-radius: 0 0 10px 10px;
        margin: -50px -50px 25px -50px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* 一级菜单：上下摆放的大按钮 */
    .l1-btn-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        max-width: 600px;
        margin: 40px auto;
    }

    /* 医疗卡片样式 */
    .policy-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 12px;
        margin-top: 10px;
    }
    .medical-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-top: 4px solid #004a99;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
        transition: transform 0.2s;
    }
    .medical-card:hover { transform: translateY(-3px); }
    
    .card-title { font-size: 11px !important; color: #888; font-weight: 600; margin-bottom: 5px; }
    .card-value { font-size: 15px !important; font-weight: 700 !important; color: #004a99; line-height: 1.3; }

    /* 机会点 & 风险点标识 */
    .opp-tag { color: #2d9d78; font-weight: bold; }
    .risk-tag { color: #d9534f; font-weight: bold; }
    
    /* 返回按钮样式 */
    .stButton>button {
        border-radius: 5px;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 状态管理 (用于跳转) ---
if 'step' not in st.session_state: st.session_state.step = 'L1'
if 'l1_selection' not in st.session_state: st.session_state.l1_selection = None
if 'l2_selection' not in st.session_state: st.session_state.l2_selection = None

def navigate_to(step, l1=None, l2=None):
    st.session_state.step = step
    if l1: st.session_state.l1_selection = l1
    if l2: st.session_state.l2_selection = l2
    st.rerun()

# --- 3. 目录数据 ---
STRUCTURE = {
    "国家": {
        "国家卫健委": ["抗菌药物管理办法", "绩效监测", "基药", "超品规备案", "医院管理质控", "其他"],
        "国家医保局": ["国谈落地", "红黄标", "基金监管", "DRG/DIP", "VBP", "其他"]
    },
    "地方": {
        "北京": ["DRG新药新技术除外支付"],
        "广东": ["集采药品协议期满接续采购"],
        "浙江": ["创新医药技术医保支付激励"]
    }
}

# --- 4. 界面逻辑 ---

# 顶部 Banner
st.markdown('<div class="medical-banner"><h1>🏥 政策直通车</h1></div>', unsafe_allow_html=True)

# --- 第一级：国家 vs 地方 (上下摆放) ---
if st.session_state.step == 'L1':
    st.markdown("<div style='text-align:center;'><h3>请选择政策维度</h3></div>", unsafe_allow_html=True)
    col_l1_1, col_l1_2, col_l1_3 = st.columns([1, 2, 1])
    with col_l1_2:
        if st.button("🏛️ 国家级政策维度", use_container_width=True, type="primary"):
            navigate_to('L2', l1="国家")
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.button("📍 地方性政策维度", use_container_width=True):
            navigate_to('L2', l1="地方")

# --- 第二级：部门 / 省份 ---
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回首页"): navigate_to('L1')
    st.title(f"📌 {st.session_state.l1_selection}维度分类")
    
    options = list(STRUCTURE[st.session_state.l1_selection].keys())
    cols = st.columns(len(options))
    for i, opt in enumerate(options):
        with cols[i]:
            if st.button(f"📂 {opt}", use_container_width=True):
                navigate_to('L3', l2=opt)

# --- 第三级：政策详情 (栅格卡片) ---
elif st.session_state.step == 'L3':
    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("⬅️ 返回"): navigate_to('L2')
    with col_title:
        st.title(f"🔍 {st.session_state.l2_selection} - 核心机会点")

    policies = STRUCTURE[st.session_state.l1_selection][st.session_state.l2_selection]
    
    # 模拟渲染栅格卡片
    st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
    for p in policies:
        # 提取文件中的真实机会点信息
        detail = "相关政策要求正在细化中..."
        if p == "DRG新药新技术除外支付":
            detail = "北京第二批除外支付名单发布，涵盖奥法妥木单抗等22种新药，2026年起实施 "
        elif p == "集采药品协议期满接续采购":
            detail = "广东牵头1-8批接续采购，原则上按需求量80%作为约定采购量 "
        elif p == "创新医药技术医保支付激励":
            detail = "浙江首批公示名单包含德曲妥珠单抗等25种创新药及支架法肠转流术 "
        elif p == "红黄标":
            detail = "重点关注绿色标识品种的挂网与临床准入优先权"
            
        st.markdown(f"""
            <div class="medical-card">
                <div class="card-title">{p}</div>
                <div class="card-value"><span class="opp-tag">●</span> {detail}</div>
                <div style="margin-top:10px; font-size:11px; color:#0066cc; cursor:pointer;">🔗 查看政策原文</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. 专业注脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
    <p style="font-size: 12px !important; color: #666;">
        <b>提示：</b>文件中<span class="opp-tag">绿色标识</span>为机会点，<span class="risk-tag">黄色标识</span>为风险点。
    </p>
    <p style="font-size: 11px !important; color: #999;">数据来源：国家及地方医保局、卫健委官方公示文件 | 更新日期：2026-03-11</p>
</div>
""", unsafe_allow_html=True)

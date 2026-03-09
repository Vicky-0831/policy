import streamlit as st

# 1. 页面配置
st.set_page_config(
    page_title="政策机会点看板", 
    layout="wide", 
    page_icon="🏥",
    initial_sidebar_state="collapsed"
)

# --- 🎨 极简门户 CSS ---
st.markdown("""
    <style>
    /* 隐藏顶部默认装饰 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 顶部蓝色 Banner */
    .portal-banner {
        background: linear-gradient(90deg, #005bac 0%, #0072ce 100%);
        padding: 30px;
        color: white;
        text-align: center;
        border-radius: 0 0 15px 15px;
        margin: -50px -50px 30px -50px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* 导航卡片样式 */
    .nav-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .nav-card:hover {
        transform: translateY(-5px);
        border-color: #005bac;
        box-shadow: 0 8px 15px rgba(0,91,172,0.1);
    }
    .nav-title {
        font-size: 20px;
        font-weight: 700;
        color: #333;
    }

    /* 三级机会点卡片 (绿色) */
    .opp-card {
        background-color: #f0fff4;
        border-left: 6px solid #28a745;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .opp-title {
        font-size: 16px;
        font-weight: 700;
        color: #155724;
    }
    
    /* 返回按钮 */
    .back-btn {
        color: #005bac;
        font-weight: 600;
        cursor: pointer;
        margin-bottom: 20px;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 状态管理 ---
if 'step' not in st.session_state:
    st.session_state.step = 'L1'  # L1: 国家/地方, L2: 部门/省份, L3: 政策列表
if 'l1_choice' not in st.session_state:
    st.session_state.l1_choice = None
if 'l2_choice' not in st.session_state:
    st.session_state.l2_choice = None

# --- 3. 目录数据定义 ---
STRUCTURE = {
    "国家": {
        "卫健委": ["抗菌药管理办法", "绩效监测", "基药目录管理办法", "质控指标"],
        "医保局": ["国谈", "红黄标", "基金监管", "其他政策"]
    },
    "地方": {
        "北京": ["DRG除外支付政策"],  # 
        "广东": ["VBP集采接续政策"],  # 
        "浙江": ["创新医药支付激励"]   # 
    }
}

# --- 4. 界面逻辑 ---

# 顶部 Banner
st.markdown('<div class="portal-banner"><h1>医保卫健政策机会点看板</h1><p>直击核心政策，抓取绿色机会</p></div>', unsafe_allow_html=True)

# 导航处理
def go_back():
    if st.session_state.step == 'L3':
        st.session_state.step = 'L2'
    elif st.session_state.step == 'L2':
        st.session_state.step = 'L1'
    st.rerun()

# --- 第一级：国家 vs 地方 ---
if st.session_state.step == 'L1':
    cols = st.columns(2)
    with cols[0]:
        if st.button("🏛️ 国家级政策", use_container_width=True, type="primary"):
            st.session_state.l1_choice = "国家"
            st.session_state.step = 'L2'
            st.rerun()
    with cols[1]:
        if st.button("📍 地方性政策", use_container_width=True, type="primary"):
            st.session_state.l1_choice = "地方"
            st.session_state.step = 'L2'
            st.rerun()

# --- 第二级：具体部门/省份 ---
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回主目录"):
        go_back()
    
    st.subheader(f"当前选择：{st.session_state.l1_choice}")
    options = list(STRUCTURE[st.session_state.l1_choice].keys())
    
    cols = st.columns(len(options))
    for idx, opt in enumerate(options):
        with cols[idx]:
            if st.button(opt, use_container_width=True, key=opt):
                st.session_state.l2_choice = opt
                st.session_state.step = 'L3'
                st.rerun()

# --- 第三级：具体政策列表 ---
elif st.session_state.step == 'L3':
    if st.button(f"⬅️ 返回{st.session_state.l1_choice}目录"):
        go_back()
    
    st.subheader(f"📌 {st.session_state.l2_choice} - 政策机会点")
    policies = STRUCTURE[st.session_state.l1_choice][st.session_state.l2_choice]
    
    for p in policies:
        with st.container():
            st.markdown(f"""
                <div class="opp-card">
                    <div class="opp-title">{p}</div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">
                        • 核心机会点提取中...<br/>
                        • 点击下方按钮查看官方原件
                    </div>
                </div>
            """, unsafe_allow_html=True)
            # 预留跳转按钮
            st.button(f"查看 {p} 原文", key=f"btn_{p}")

# --- 5. 页脚 ---
st.markdown("---")
st.caption("注：本看板仅展示“绿色”级别机会点。 [cite: 11, 64, 152, 184, 226, 255]")

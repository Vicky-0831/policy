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
    /* 隐藏默认组件 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 莫兰迪色值定义 */
    :root {
        --morandi-blue: #92a8d1;    /* 灰蓝色 - 顶栏 */
        --morandi-green: #b5c6b1;   /* 豆沙绿 - 机会点 */
        --morandi-bg: #f7f3f0;      /* 米灰色 - 背景 */
        --morandi-text: #5d5d5d;    /* 深灰色 - 文字 */
        --morandi-white: #ffffff;   /* 纯白 - 卡片 */
    }

    /* 页面背景 */
    .stApp {
        background-color: var(--morandi-bg);
    }

    /* 顶部 Banner - 莫兰迪灰蓝 */
    .portal-banner {
        background-color: var(--morandi-blue);
        padding: 40px;
        color: white;
        text-align: center;
        border-radius: 0 0 20px 20px;
        margin: -50px -50px 40px -50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .portal-banner h1 {
        font-weight: 300 !important;
        letter-spacing: 2px;
    }

    /* 导航按钮样式 */
    .stButton>button {
        background-color: var(--morandi-white);
        color: var(--morandi-text);
        border: 1px solid #dcdcdc;
        border-radius: 10px;
        padding: 15px;
        transition: all 0.3s;
        font-weight: 500;
    }
    .stButton>button:hover {
        border-color: var(--morandi-blue);
        color: var(--morandi-blue);
        background-color: #fafafa;
    }

    /* 三级机会点卡片 - 莫兰迪豆沙绿 */
    .opp-card {
        background-color: var(--morandi-white);
        border-left: 8px solid var(--morandi-green);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .opp-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--morandi-text);
        margin-bottom: 10px;
    }
    .opp-tag {
        display: inline-block;
        background-color: var(--morandi-green);
        color: white;
        padding: 2px 10px;
        border-radius: 5px;
        font-size: 12px;
        margin-bottom: 8px;
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
st.markdown('<div class="portal-banner"><h1>政策直通车</h1><p>……</p></div>', unsafe_allow_html=True)

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
        if st.button("🏛️ 国家", use_container_width=True, type="primary"):
            st.session_state.l1_choice = "国家"
            st.session_state.step = 'L2'
            st.rerun()
    with cols[1]:
        if st.button("📍 地方", use_container_width=True, type="primary"):
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
    
    st.subheader(f"📌 {st.session_state.l2_choice}")
    policies = STRUCTURE[st.session_state.l1_choice][st.session_state.l2_choice]
    
    for p in policies:
        with st.container():
            st.markdown(f"""
                <div class="opp-card">
                    <div class="opp-title">{p}</div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">
                        • 核心点提取...<br/>
                        • 点击下方按钮查看官方原件
                    </div>
                </div>
            """, unsafe_allow_html=True)
            # 预留跳转按钮
            st.button(f"查看 {p} 原文", key=f"btn_{p}")

# --- 5. 页脚 ---
st.markdown("---")
st.caption("注： [cite: 11, 64, 152, 184, 226, 255]")

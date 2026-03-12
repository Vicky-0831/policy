import streamlit as st

# 1. 页面配置
st.set_page_config(
    page_title="政策直通车", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 🎨 医疗极简配色 (洁净蓝白) & 字体适配 ---
st.markdown("""
    <style>
    /* 全局背景：极淡灰，专业感 */
    .stApp { background-color: #ffffff; }

    /* 字体大小严格控制 - 参考直通车 */
    h1 { font-size: 20px !important; font-weight: 700 !important; color: #003366; margin-bottom: 20px !important; text-align: center; }
    h3 { font-size: 16px !important; font-weight: 600 !important; color: #0056b3; margin-top: 10px !important; }
    p, div, span { font-size: 13px !important; color: #333333; }

    /* 顶部标题：去除背景框 */
    .clean-header {
        padding: 20px 0;
        text-align: center;
        border-bottom: 1px solid #eee;
        margin-bottom: 30px;
    }

    /* 一级/二级按钮：医学蓝风格 */
    .stButton>button {
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
        height: 45px;
        transition: 0.3s;
    }
    
    /* 三级政策列表：栅格布局 */
    .policy-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    
    /* 极简卡片：高对比度蓝白 */
    .simple-card {
        background-color: #f8fbff;
        padding: 15px;
        border: 1px solid #e1e8f0;
        border-radius: 6px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 80px;
    }
    .card-title-text { 
        font-size: 14px !important; 
        font-weight: 600 !important; 
        color: #003366; 
        margin-bottom: 8px;
    }

    /* 注脚颜色修正 */
    .footer-note {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 12px !important;
        margin-top: 50px;
        border-top: 1px solid #eee;
    }
    .text-green { color: #2d9d78; font-weight: bold; }
    .text-yellow { color: #f0ad4e; font-weight: bold; }
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

# 预设链接
LINKS = {
    "DRG新药新技术除外支付": "https://ybj.beijing.gov.cn/zwgk/2024zcwj/202512/t20251230_4378695.html",
    "集采药品协议期满接续采购": "https://hsa.gd.gov.cn/zwdt/snkb/content/post_4847124.html",
    "创新医药技术医保支付激励": "https://ybj.zj.gov.cn/art/2025/8/12/art_1229225636_5566097.html"
}

# --- 4. 界面渲染 ---

# 顶部标题 (无背景框)
st.markdown('<div class="clean-header"><h1>🏥 政策直通车</h1></div>', unsafe_allow_html=True)

# --- 一级页面：国家 vs 地方 (上下排列) ---
if st.session_state.step == 'L1':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🏛️ 国家级政策维度", use_container_width=True, type="primary"):
            nav_to('L2', l1="国家")
        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        if st.button("📍 地方性政策维度", use_container_width=True):
            nav_to('L2', l1="地方")

# --- 二级页面：部门 / 省份 (横向平铺) ---
elif st.session_state.step == 'L2':
    if st.button("⬅️ 返回主目录"): nav_to('L1')
    st.markdown(f"### 📂 当前选择：{st.session_state.l1}")
    
    opts = list(STRUCTURE[st.session_state.l1].keys())
    cols = st.columns(len(opts))
    for i, opt in enumerate(opts):
        with cols[i]:
            if st.button(opt, use_container_width=True, key=opt):
                nav_to('L3', l2=opt)

# --- 三级页面：纯净卡片展示 ---
elif st.session_state.step == 'L3':
    if st.button("⬅️ 返回"): nav_to('L2')
    # 删除了标题字样，直接展示内容
    
    policies = STRUCTURE[st.session_state.l1][st.session_state.l2]
    st.markdown('<div class="policy-grid">', unsafe_allow_html=True)
    for p in policies:
        # 获取对应的跳转链接
        url = LINKS.get(p, "#")
        st.markdown(f"""
            <div class="simple-card">
                <div class="card-title-text">{p}</div>
                <a href="{url}" target="_blank" style="text-decoration:none; color:#0056b3; font-size:12px;">🔗 查看官方原文</a>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 注脚：颜色修正 ---
st.markdown(f"""
    <div class="footer-note">
        文件中<span class="text-green">绿色标识</span>为机会点，
        <span class="text-yellow">黄色标识</span>为风险点。<br>
        © 2026 政策直通车 | 数据来源：各官方公示文件
    </div>
""", unsafe_allow_html=True)

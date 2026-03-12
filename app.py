import streamlit as st

# 1. 页面配置 (参考直通车：小间距、宽布局)
st.set_page_config(
    page_title="政策机会点看板", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 🎨 莫兰迪色系 + 精致小字体 CSS ---
st.markdown("""
    <style>
    /* 莫兰迪配色 */
    :root {
        --m-blue: #92a8d1;    /* 灰蓝 */
        --m-green: #b5c6b1;   /* 豆沙绿 */
        --m-bg: #f7f3f0;      /* 米灰背景 */
        --m-text: #5d5d5d;    /* 深灰文字 */
        --m-card-bg: #ffffff; 
    }

    .stApp { background-color: var(--m-bg); }

    /* 全站字体适配 */
    h1 { font-size: 20px !important; font-weight: 700 !important; color: var(--m-text); }
    h3 { font-size: 16px !important; font-weight: 600 !important; color: var(--m-text); }
    p, div, span { font-size: 13px !important; color: var(--m-text); }

    /* 顶部 Banner */
    .portal-banner {
        background-color: var(--m-blue);
        padding: 20px;
        color: white;
        text-align: center;
        border-radius: 0 0 15px 15px;
        margin: -50px -50px 25px -50px;
    }

    /* 政策栅格布局 (参考直通车) */
    #policy-grid {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 10px !important;
        margin-top: 10px;
    }
    @media (min-width: 900px) {
        #policy-grid { grid-template-columns: repeat(3, 1fr) !important; }
    }

    /* 莫兰迪机会点卡片 (Sage Green) */
    .custom-card {
        background-color: var(--m-card-bg);
        padding: 12px !important;
        border-radius: 8px;
        border-left: 5px solid var(--m-green) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        height: 100%;
    }
    .card-title {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #888;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .card-value {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: var(--m-text);
        line-height: 1.4;
    }
    
    /* 绿色机会点高亮 */
    .opp-green { color: #5a8d66; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 导航状态管理 ---
if 'l1' not in st.session_state: st.session_state.l1 = "国家"
if 'l2' not in st.session_state: st.session_state.l2 = "国家医保局"

# --- 3. 目录与内容定义 ---
STRUCTURE = {
    "国家": {
        "国家卫健委": ["抗菌药物管理办法", "绩效监测", "基药", "超品规备案", "医院管理质控", "其他"],
        "国家医保局": ["国谈落地", "红黄标", "基金监管", "DRG/DIP", "VBP", "其他"]
    },
    "地方": {
        "北京": ["DRG除外支付政策"],
        "广东": ["VBP集采接续政策"],
        "浙江": ["创新医药支付激励"]
    }
}

# --- 4. 界面逻辑 ---

# 顶部 Banner
st.markdown('<div class="portal-banner"><h1>医保卫健政策机会点看板</h1></div>', unsafe_allow_html=True)

# 一级选项：国家/地方 (上下排列)
st.markdown("### 🏷️ 维度选择")
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🏛️ 国家级政策", use_container_width=True, type="primary" if st.session_state.l1=="国家" else "secondary"):
        st.session_state.l1 = "国家"
        st.session_state.l2 = "国家卫健委"
        st.rerun()
with col_nav2:
    if st.button("📍 地方性政策", use_container_width=True, type="primary" if st.session_state.l1=="地方" else "secondary"):
        st.session_state.l1 = "地方"
        st.session_state.l2 = "北京"
        st.rerun()

st.markdown("---")

# 二级选项：横向切换
st.markdown(f"### 📂 {st.session_state.l1}维度分类")
l2_options = list(STRUCTURE[st.session_state.l1].keys())
l2_tabs = st.tabs([f" {opt}" for opt in l2_options])

for i, opt in enumerate(l2_options):
    with l2_tabs[i]:
        st.session_state.l2 = opt
        st.markdown(f"### 📌 {opt} - 核心机会点")
        
        # 三级内容：栅格卡片
        policies = STRUCTURE[st.session_state.l1][opt]
        
        html_grid = '<div id="policy-grid">'
        
        for p in policies:
            # 模拟匹配提取的机会点内容
            detail = "核心机会点提取中..."
            link_icon = "📄"
            
            # 填入已有文件信息
            if p == "DRG除外支付政策": 
                detail = "第二批除外支付名单(2026-2028)，包含22种新药 [cite: 11, 23, 37]"
            elif p == "VBP集采接续政策": 
                detail = "1-8批协议期满品种接续采购，需求量填报已完成 [cite: 68, 70]"
            elif p == "创新医药支付激励": 
                detail = "首批创新药支付激励名单，包含25种创新药品 [cite: 254, 274]"
            elif p == "DRG/DIP" and st.session_state.l1 == "国家":
                detail = "<span class='opp-green'>暂无国家层面除外政策更新</span>"

            html_grid += f"""
            <div class="custom-card">
                <div class="card-title">{p}</div>
                <div class="card-value">{detail}</div>
                <div style="margin-top:10px; font-size:11px; color:#92a8d1; cursor:pointer;">{link_icon} 查看原文</div>
            </div>
            """
        
        html_grid += '</div>'
        st.markdown(html_grid, unsafe_allow_html=True)

# 5. 注脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
    文件中<span style="color: #5a8d66; font-weight:bold;">绿色标识</span>为机会点，
    <span style="color: #b38b3d; font-weight:bold;">黄色标识</span>为风险点。<br>
    © 2026 政策机会点看板 | 数据基于官方公开文件
</div>
""", unsafe_allow_html=True)

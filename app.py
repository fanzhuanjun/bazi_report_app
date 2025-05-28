# app.py

import streamlit as st
from datetime import datetime
from bazi_report_generator import DeepSeekBaziReport # 导入你的类
# 移除了 plotly.express 和 pandas 的导入

# --- DeepSeek API Key 配置 (直接在此配置) ---
# 注意：直接在代码中硬编码API Key存在安全风险，尤其是在公开仓库或生产环境中。
# 推荐在实际部署时使用环境变量或Streamlit的st.secrets来管理API Key。
api_key = "sk-392daa9410c7429fa9be75e49049a4ec" # 根据用户要求直接硬编码

# --- Streamlit 页面配置 ---
st.set_page_config(
    page_title="🔮 DeepSeek 八字命理报告",
    page_icon="🔮",
    layout="wide", # 使用 "wide" 布局，让内容更宽裕
    initial_sidebar_state="auto"
)

# --- 主页面内容 ---
st.title("🔮 反转 八字命理报告")
st.markdown("欢迎来到反转专业八字命理学！请填写您的出生信息，即可获得详细报告。")

st.markdown("---")

# --- 用户输入表单 ---
st.subheader("🗓️ 请输入您的出生信息")

col1, col2, col3, col4, col5 = st.columns(5) # 调整列数以适应更多的输入

current_year = datetime.now().year

with col1:
    year = st.number_input("出生年份 (公历)", min_value=1900, max_value=current_year, value=1994, step=1)
with col2:
    month = st.number_input("出生月份 (公历)", min_value=1, max_value=12, value=9, step=1)
with col3:
    day = st.number_input("出生日期 (公历)", min_value=1, max_value=31, value=6, step=1)
with col4:
    hour = st.number_input("出生时辰 (24小时制, 0-23)", min_value=0, max_value=23, value=10, step=1)
with col5:
    gender = st.radio(
        "您的性别",
        ('男', '女'),
        horizontal=False # 垂直排列，与上面输入框对齐
    )

report_type = st.radio(
    "选择报告类型",
    ('免费版报告 (简要)', '付费版报告 (专业详细)'),
    horizontal=True,
    index=0 # 默认选中免费版
)

# --- 生成报告按钮 ---
if st.button("🚀 生成报告", type="primary"):
    if not api_key:
        st.error("DeepSeek API Key 未配置。请检查 `app.py` 文件中的配置。")
        st.stop()

    # 简单的数据验证
    try:
        input_date = datetime(year, month, day, hour)
    except ValueError:
        st.error("您输入的日期或时间无效，请检查！")
        st.stop()

    birth_data = {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour
    }

    try:
        bazi_generator = DeepSeekBaziReport(api_key)
        
        # 1. 计算八字干支
        bazi_info = bazi_generator.calculate_simple_bazi(
            birth_data["year"], 
            birth_data["month"], 
            birth_data["day"], 
            birth_data["hour"]
        )
        bazi_str = f"年柱:{bazi_info['year_gz']} | 月柱:{bazi_info['month_gz']} | 日柱:{bazi_info['day_gz']} | 时柱:{bazi_info['hour_gz']}"

        st.subheader("📝 八字信息") # 调整标题，移除“五行分析”字样
        st.write(f"**您的八字**: {bazi_str}")

        # 移除了本地计算和绘制五行饼状图的代码


        # 2. 生成 AI 报告
        with st.spinner("正在努力生成您的八字报告，这可能需要一些时间，请稍候..."):
            if report_type == '免费版报告 (简要)':
                report = bazi_generator.generate_free_report(bazi_str, gender)
            else:
                report = bazi_generator.generate_premium_report(bazi_str, gender)
        
        st.subheader(f"✨ 您的 {report_type} ✨")
        
        # --- 鲁棒性处理：移除AI可能添加的外部代码块 ---
        # 检查报告是否以代码块开始和结束
        if report.strip().startswith("```") and report.strip().endswith("```"):
            report_lines = report.strip().split('\n')
            if len(report_lines) >= 3:
                first_line = report_lines[0].strip()
                if first_line.startswith("```") and len(first_line) > 3: # e.g., ```markdown
                    report = '\n'.join(report_lines[1:-1]) # 移除首尾行
                else: # 可能是没有语言声明的通用代码块 ```
                    report = '\n'.join(report_lines[1:-1])
                st.warning("AI报告被包裹在代码块中，已自动移除。")
            else:
                st.warning("AI报告内容异常短，可能是一个空的或损坏的代码块。")
        # --- 鲁棒性处理结束 ---
        
        # Streamlit支持Markdown，LLM的输出如果包含Markdown格式会很好地渲染
        st.markdown(report, unsafe_allow_html=False) # 保持 unsafe_allow_html=False 为安全考虑
        st.success("报告生成完毕！")

    except Exception as e:
        st.error(f"生成报告时发生错误: {e}")
        st.info("请检查您的网络连接、DeepSeek API Key是否正确，以及输入信息是否符合要求。")

st.markdown("---")
st.info("免责声明：本报告仅供娱乐参考，不作为任何决策的依据。命理学并非科学，请理性看待。")
# app.py
import streamlit as st  # 这个 import 必须在最前面
from datetime import datetime
from bazi_report_generator import DeepSeekBaziReport
import pytz
import io
import re

# ！！！确保这是整个脚本的第一个 Streamlit 命令！！！
st.set_page_config(
    page_title="反转 专业八字命理学报告",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- DeepSeek API Key 配置 ---
api_key = "sk-392daa9410c7429fa9be75e49049a4ec" # 请替换为您的有效API Key

# --- Custom CSS for Beautification ---
custom_css = """
<style>
    /* General body styling (Streamlit handles most of this) */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #333;
    }

    /* Main title of the app */
    .app-main-title {
        color: #2c3e50; /* Dark blue-grey */
        text-align: center;
        font-size: 2.8em; /* Slightly larger */
        font-weight: bold;
        margin-bottom: 25px;
        padding-top: 10px;
    }

    /* Subheader for sections like "请填写您的出生信息" */
    .section-subheader {
        color: #34495e; /* Slightly lighter blue-grey */
        border-bottom: 3px solid #1abc9c; /* Teal accent, slightly thicker */
        padding-bottom: 12px;
        margin-top: 35px;
        margin-bottom: 25px;
        font-size: 2em; /* Slightly larger */
        font-weight: 600;
    }

    /* Bazi info display card */
    .bazi-info-card {
        background-color: #fdfefe; /* Very light, almost white */
        border: 1px solid #e5e8eb; /* Light border */
        border-left: 6px solid #3498db; /* Blue accent border */
        padding: 20px;
        margin-bottom: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    .bazi-info-card p {
        margin-bottom: 8px;
        font-size: 1.05em;
        line-height: 1.6;
    }
    .bazi-info-card strong {
        color: #2980b9; /* Blue for labels */
        font-weight: 600;
    }

    /* Report type title (e.g., "✨ 您的 免费版报告 (简要) ✨") */
    .report-type-title {
        color: #c0392b; /* Stronger Red for report type */
        font-size: 2.2em; /* Prominent */
        text-align: center;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        /* border-bottom: 2px solid #e67e22;  Orange accent */
    }

    /* Common styles for the LLM generated report content */
    .report-content {
        padding: 5px; /* Add a little padding around content area */
    }

    .report-content h2 { /* LLM Module Titles (##) */
        color: #2980b9; /* Professional Blue */
        font-size: 1.9em;
        font-weight: 600;
        margin-top: 35px;
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 2px solid #aed6f1; /* Lighter blue border */
    }

    .report-content h3 { /* LLM Section Titles (###) */
        color: #27ae60; /* Green */
        font-size: 1.6em;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .report-content h4 { /* LLM Sub-Section Titles (####) - if used */
        color: #8e44ad; /* Purple */
        font-size: 1.4em;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .report-content p {
        line-height: 1.8; /* Increased for readability */
        color: #424949; /* Darker grey for text */
        margin-bottom: 15px; /* More spacing */
        font-size: 1.05em;
    }

    .report-content strong, .report-content b {
        color: #d35400; /* Orange-red for emphasis in paragraphs */
        font-weight: bold;
    }

    .report-content em, .report-content i {
        color: #5D6D7E; /* Slightly muted for italics */
        font-style: italic;
    }

    .report-content ul, .report-content ol {
        margin-left: 5px; /* Adjusted for better alignment with common list styles */
        padding-left: 25px;
        list-style-position: outside;
    }

    .report-content li {
        margin-bottom: 10px;
        line-height: 1.7;
        font-size: 1.05em;
    }

    /* Span classes for LLM to use */
    .highlight-bazi {
        background-color: #e8f6f3; /* Very light teal */
        color: #117a65; /* Darker Teal */
        padding: 3px 7px; /* Slightly more padding */
        border-radius: 5px;
        font-weight: 500;
        border: 1px solid #a2d9ce; /* Light teal border */
        display: inline-block; /* Prevents awkward line breaks for short terms */
        line-height: 1.3; /* Ensure it doesn't expand line too much */
    }

    .positive-outcome {
        color: #229954; /* Darker Green */
        font-weight: bold;
        background-color: #e9f7ef; /* Very light green */
        padding: 2px 5px;
        border-radius: 4px;
        border-left: 3px solid #27ae60; /* Green accent */
    }

    .warning-text {
        color: #cb4335; /* Darker Red */
        font-weight: bold;
        background-color: #fdedec; /* Very light red */
        padding: 2px 5px;
        border-radius: 4px;
        border-left: 3px solid #e74c3c; /* Red accent */
    }

    .report-content blockquote {
        border-left: 5px solid #f39c12; /* Orange, thicker */
        padding: 12px 20px; /* More padding */
        margin: 20px 0; /* More vertical space */
        background-color: #fef5e7; /* Lighter yellow */
        color: #873600; /* Darker orange/brown for text */
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .report-content blockquote p {
        margin-bottom: 8px;
        line-height: 1.7;
        font-size: 1em; /* Slightly smaller if desired, or keep same */
    }
    .report-content blockquote p:last-child {
        margin-bottom: 0;
    }

    /* Disclaimer box */
    .disclaimer-box {
        background-color: #f4f6f6; /* Lighter grey */
        border: 1px solid #d5dbdb; /* Dashed border */
        padding: 18px;
        margin-top: 30px;
        border-radius: 6px;
        font-size: 0.95em;
        color: #566573; /* Muted grey */
        line-height: 1.6;
    }

    /* Style Streamlit Tabs for Premium Report */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.05em;
        font-weight: 500;
        color: #566573; /* Default tab color */
        border-radius: 4px;
        margin-right: 5px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #3498db; /* Active tab background */
        color: white !important; /* Active tab text color */
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px; /* Space between tabs and content */
    }

</style>
"""
# custom_css 的定义现在在 set_page_config 之后
st.markdown(custom_css, unsafe_allow_html=True) # CSS 注入在这里


# --- 初始化 Session State ---
if 'report_generated_successfully' not in st.session_state:
    st.session_state.report_generated_successfully = False
if 'bazi_info_for_display' not in st.session_state:
    st.session_state.bazi_info_for_display = {}
if 'free_report_content' not in st.session_state:
    st.session_state.free_report_content = ""
if 'premium_modules_content' not in st.session_state:
    st.session_state.premium_modules_content = {}

# 修改 user_inputs 的初始化，存储实际值或有意义的默认值
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = {
        "year": datetime.now().year - 28,
        "month": datetime.now().month,
        "day": datetime.now().day,
        "hour": 12,
        "gender": '男', 
        "report_type": '免费版报告 (简要)'
    }

# --- 主页面内容 ---
st.markdown("<h1 class='app-main-title'>🎲 反转实验室 专业八字命理报告</h1>", unsafe_allow_html=True)
st.markdown("欢迎来到反转专业的八字命理学！请填写您的出生信息，即可获得深度命理报告。")
st.markdown("---")

def clear_all_data_and_rerun():
    keys_to_delete = [
        'report_generated_successfully', 'bazi_info_for_display',
        'free_report_content', 'premium_modules_content'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.user_inputs = { 
        "year": datetime.now().year - 28, "month": datetime.now().month,
        "day": datetime.now().day, "hour": 12,
        "gender": '男', "report_type": '免费版报告 (简要)'
    }
    st.session_state.report_generated_successfully = False
    st.rerun()

if st.session_state.get('report_generated_successfully', False):
    st.info("当前已有一份生成的报告。您可以直接查看、下载，或选择“清除报告并重填”以开始新的分析。")
    if st.button("✨ 清除当前报告并重新填写", key="clear_report_button_top"):
        clear_all_data_and_rerun()

st.markdown("<h2 class='section-subheader'>🗓️ 请输入您的出生信息</h2>", unsafe_allow_html=True)


current_year = datetime.now().year
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.session_state.user_inputs['year'] = st.number_input(
        "出生年份 (公历)", min_value=1900, max_value=current_year,
        value=st.session_state.user_inputs['year'], step=1, key="year_input_field"
    )
with col2:
    st.session_state.user_inputs['month'] = st.number_input(
        "出生月份 (公历)", min_value=1, max_value=12,
        value=st.session_state.user_inputs['month'], step=1, key="month_input_field"
    )
with col3:
    st.session_state.user_inputs['day'] = st.number_input(
        "出生日期 (公历)", min_value=1, max_value=31,
        value=st.session_state.user_inputs['day'], step=1, key="day_input_field"
    )
with col4:
    st.session_state.user_inputs['hour'] = st.number_input(
        "出生时辰 (24小时制, 0-23)", min_value=0, max_value=23,
        value=st.session_state.user_inputs['hour'], step=1, key="hour_input_field"
    )
with col5:
    gender_options = ('男', '女')
    try:
        current_gender_index = gender_options.index(st.session_state.user_inputs['gender'])
    except ValueError: 
        current_gender_index = 0 
    
    st.session_state.user_inputs['gender'] = st.radio(
        "您的性别", gender_options,
        index=current_gender_index, 
        horizontal=True, key="gender_input_field" # Changed to horizontal for better layout
    )
selected_gender = st.session_state.user_inputs['gender']


report_type_options = ('免费版报告 (简要)', '付费版报告 (专业详细)')
try:
    current_report_type_index = report_type_options.index(st.session_state.user_inputs['report_type'])
except ValueError:
    current_report_type_index = 0

st.session_state.user_inputs['report_type'] = st.radio(
    "选择报告类型", report_type_options,
    horizontal=True,
    index=current_report_type_index,
    key="report_type_input_field"
)
selected_report_type = st.session_state.user_inputs['report_type']


# --- 生成报告按钮 ---
if st.button("🚀 生成报告", type="primary", disabled=st.session_state.get('report_generated_successfully', False), use_container_width=True):
    st.session_state.report_generated_successfully = False
    st.session_state.bazi_info_for_display = {}
    st.session_state.free_report_content = ""
    st.session_state.premium_modules_content = {}

    year = st.session_state.user_inputs['year']
    month = st.session_state.user_inputs['month']
    day = st.session_state.user_inputs['day']
    hour = st.session_state.user_inputs['hour']

    if not api_key or not api_key.startswith("sk-"):
        st.error("DeepSeek API Key 未配置或格式不正确。请检查 `api_key` 配置。")
        st.stop()

    try:
        if month == 2:
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            max_days = 29 if is_leap else 28
        elif month in [4, 6, 9, 11]:
            max_days = 30
        else:
            max_days = 31
        if not (1 <= day <= max_days):
            st.error(f"{year}年{month}月没有{day}日，请输入有效的日期！")
            st.stop()
        datetime(year, month, day, hour) # Validate datetime
    except ValueError:
        st.error("您输入的日期或时间无效，请检查！")
        st.stop()

    birth_data_for_calc = {"year": year, "month": month, "day": day, "hour": hour}

    try:
        bazi_engine = DeepSeekBaziReport(api_key)
        calculated_bazi_info = bazi_engine.calculate_simple_bazi(
            birth_data_for_calc["year"], birth_data_for_calc["month"],
            birth_data_for_calc["day"], birth_data_for_calc["hour"]
        )
        
        # Check for calculation errors
        if "计算错误" in calculated_bazi_info.values():
            st.error("八字计算时发生错误，请检查输入日期或稍后再试。")
            st.session_state.report_generated_successfully = False
            st.stop()

        bazi_string_representation = (
            f"年柱:{calculated_bazi_info['year_gz']} | "
            f"月柱:{calculated_bazi_info['month_gz']} | "
            f"日柱:{calculated_bazi_info['day_gz']} | "
            f"时柱:{calculated_bazi_info['hour_gz']}"
        )
        
        st.session_state.bazi_info_for_display = {
            "year": year, "month": month, "day": day, "hour": hour,
            "bazi_str": bazi_string_representation, 
            "gender": selected_gender, 
            "report_type": selected_report_type 
        }

        if selected_report_type == '免费版报告 (简要)':
            with st.spinner("正在努力生成您的免费八字报告，请稍候..."):
                generated_report_content = bazi_engine.generate_free_report(bazi_string_representation, selected_gender)
            
            if "API Error:" in generated_report_content or "Error calling DeepSeek API:" in generated_report_content:
                st.error(f"生成免费报告时遇到问题：{generated_report_content}")
                st.session_state.report_generated_successfully = False
            else:
                st.session_state.free_report_content = generated_report_content
                st.session_state.report_generated_successfully = True
        
        else: 
            generated_premium_modules = {}
            all_modules_generated_ok = True
            
            tab_titles = [
                "八字排盘与五行分析", "命格解码与人生特质", "事业财富与婚恋分析",
                "五行健康与养生建议", "大运流年运势推演"
            ]
            spinner_messages = { title: f"正在生成 {title.split('与')[0].split('和')[0]} 模块..." for title in tab_titles }
            
            generation_methods_map = {
                "八字排盘与五行分析": bazi_engine.generate_bazi_analysis_module,
                "命格解码与人生特质": bazi_engine.generate_mingge_decode_module,
                "事业财富与婚恋分析": bazi_engine.generate_career_love_module,
                "五行健康与养生建议": bazi_engine.generate_health_advice_module,
                "大运流年运势推演": bazi_engine.generate_fortune_flow_module
            }
            
            progress_bar = st.progress(0)
            total_modules = len(tab_titles)

            for i, title in enumerate(tab_titles):
                with st.spinner(spinner_messages[title]):
                    module_content_str = generation_methods_map[title](bazi_string_representation, selected_gender)
                    generated_premium_modules[title] = module_content_str
                    if "API Error:" in module_content_str or "Error calling DeepSeek API:" in module_content_str:
                        all_modules_generated_ok = False
                        st.error(f"生成 '{title}' 模块失败: {module_content_str}")
                progress_bar.progress((i + 1) / total_modules)
            
            if all_modules_generated_ok:
                st.session_state.premium_modules_content = generated_premium_modules
                st.session_state.report_generated_successfully = True
            else:
                st.warning("部分付费报告模块生成失败，请检查错误信息。")
                st.session_state.report_generated_successfully = False
            progress_bar.empty()


        if st.session_state.report_generated_successfully:
            st.success("报告生成完毕！您现在可以查看下方的报告内容并选择下载。")
            st.rerun() 
        
    except Exception as e:
        st.error(f"生成报告过程中发生意外错误: {e}")
        st.exception(e) 
        st.session_state.report_generated_successfully = False

# --- 显示已生成的报告 ---
if st.session_state.get('report_generated_successfully', False) and st.session_state.bazi_info_for_display:
    st.markdown("---")
    st.markdown("<h2 class='section-subheader'>📝 八字信息概览</h2>", unsafe_allow_html=True)
    bazi_display_data = st.session_state.bazi_info_for_display

    # Enhanced Bazi String Display
    bazi_str_parts = bazi_display_data['bazi_str'].split(" | ")
    styled_bazi_parts = []
    for part in bazi_str_parts:
        if ":" in part:
            label, value = part.split(":", 1)
            # Use regex to wrap each GanZhi pair individually if there are multiple, e.g. "甲子 乙丑"
            # For simplicity, assuming single GanZhi per pillar here
            value_styled = f"<span class='highlight-bazi'>{value.strip()}</span>"
            styled_bazi_parts.append(f"<strong>{label.strip()}</strong>: {value_styled}")
        else:
            styled_bazi_parts.append(part)
    
    styled_bazi_str_display = "  |  ".join(styled_bazi_parts)


    bazi_info_html = f"""
    <div class="bazi-info-card">
        <p><strong>公历生日</strong>: {bazi_display_data['year']}年 {bazi_display_data['month']}月 {bazi_display_data['day']}日 {bazi_display_data['hour']}时</p>
        <p>{styled_bazi_str_display}</p>
        <p><strong>性别</strong>: {bazi_display_data['gender']}</p>
    </div>
    """
    st.markdown(bazi_info_html, unsafe_allow_html=True)
    
    report_display_title_html = f"<h2 class='report-type-title'>✨ 您的 {bazi_display_data['report_type']} ✨</h2>"
    st.markdown(report_display_title_html, unsafe_allow_html=True)

    content_for_download = ""
    report_filename_part = "免费版" if bazi_display_data['report_type'] == '免费版报告 (简要)' else "付费版"
    
    # Header for download file should be clean Markdown
    download_file_header = f"""# 🎲 反转 专业八字命理报告

**公历生日**: {bazi_display_data['year']}年{bazi_display_data['month']}月{bazi_display_data['day']}日 {bazi_display_data['hour']}时
**您的八字**: {bazi_display_data['bazi_str']}
**性别**: {bazi_display_data['gender']}
**报告类型**: {bazi_display_data['report_type']}

---
"""
    download_file_footer = """
---
免责声明：本报告内容基于八字命理学理论，仅供参考，不构成任何决策的最终依据。命理学并非精密科学，请理性看待。
"""

    if bazi_display_data['report_type'] == '免费版报告 (简要)':
        report_content_to_show = st.session_state.free_report_content
        # The stripping of ``` is already done in _call_deepseek_api
        st.markdown(f"<div class='report-content'>{report_content_to_show}</div>", unsafe_allow_html=True)
        content_for_download = download_file_header + report_content_to_show + download_file_footer

    else: 
        modules_to_show = st.session_state.premium_modules_content
        tab_titles_ordered = [
            "八字排盘与五行分析", "命格解码与人生特质", "事业财富与婚恋分析",
            "五行健康与养生建议", "大运流年运势推演"
        ]
        tabs_display = st.tabs(tab_titles_ordered)
        
        premium_report_download_parts = [download_file_header]
        for i, title in enumerate(tab_titles_ordered):
            with tabs_display[i]:
                module_str_content = modules_to_show.get(title, "")
                if module_str_content and not ("API Error:" in module_str_content or "Error calling DeepSeek API:" in module_str_content):
                    # Wrap each tab's content in its own report-content div
                    st.markdown(f"<div class='report-content'>{module_str_content}</div>", unsafe_allow_html=True)
                    premium_report_download_parts.append(f"## {title}\n\n{module_str_content}\n\n---\n")
                elif "API Error:" in module_str_content or "Error calling DeepSeek API:" in module_str_content:
                    st.warning(f"抱歉，'{title}' 模块内容生成时出错，无法显示。")
                else:
                    st.info(f"抱歉，'{title}' 模块内容当前为空或未成功获取。")
        content_for_download = "".join(premium_report_download_parts).strip() + download_file_footer.strip()

    if content_for_download:
        current_utc_time = datetime.now(pytz.utc)
        timestamp_str = current_utc_time.strftime("%Y%m%d_%H%M%S_UTC")
        markdown_filename = f"八字命理报告_{timestamp_str}_{report_filename_part}.md"
        markdown_bytes = content_for_download.encode('utf-8')
        
        st.download_button(
            label="📥 下载完整报告 (Markdown格式)",
            data=markdown_bytes,
            file_name=markdown_filename,
            mime="text/markdown",
            key="download_report_file_button",
            use_container_width=True 
        )
    
    if st.button("🧹 清除当前报告并开始新的分析", key="clear_report_button_bottom", use_container_width=True):
        clear_all_data_and_rerun()

st.markdown("---")
st.markdown(
    "<div class='disclaimer-box'><strong>免责声明</strong>：本报告内容基于八字命理学理论，旨在提供参考与启发，并非预示确定的人生轨迹。命理学作为一种传统文化，其解读具有多重维度和不确定性，不应视为精密科学。个人命运的塑造离不开主观能动性与实际行动，请您结合自身情况理性看待报告内容，不宜作为重大人生决策的唯一依据。</div>",
    unsafe_allow_html=True
)

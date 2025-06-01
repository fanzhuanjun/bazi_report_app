# app.py

import streamlit as st
from datetime import datetime
from bazi_report_generator import DeepSeekBaziReport
import pytz 
import io

# --- DeepSeek API Key 配置 ---
api_key = "sk-392daa9410c7429fa9be75e49049a4ec" # 请替换为您的有效API Key

# --- Streamlit 页面配置 ---
st.set_page_config(
    page_title="🔮 DeepSeek 专业八字命理报告",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="auto"
)

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
        "gender": '男', # 直接存储选中的值
        "report_type": '免费版报告 (简要)' # 直接存储选中的值
    }

# --- 主页面内容 ---
st.title("🔮 DeepSeek 专业八字命理报告")
st.markdown("欢迎来到专业的八字命理学！请填写您的出生信息，即可获得详细报告。")
st.markdown("---")

def clear_all_data_and_rerun():
    keys_to_delete = [
        'report_generated_successfully', 'bazi_info_for_display',
        'free_report_content', 'premium_modules_content'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.user_inputs = { # 重置为默认值
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

st.subheader("🗓️ 请输入您的出生信息")

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
    # 获取当前存储的性别值在options中的索引，用于初始化radio
    try:
        current_gender_index = gender_options.index(st.session_state.user_inputs['gender'])
    except ValueError: # 如果存储的值不在options中（理论上不应发生，但做个保护）
        current_gender_index = 0 
    
    # st.radio 返回选中的值，我们直接存它
    st.session_state.user_inputs['gender'] = st.radio(
        "您的性别", gender_options,
        index=current_gender_index, # 使用计算出的索引来设置默认选中
        horizontal=False, key="gender_input_field"
    )
# 现在 selected_gender 直接就是session_state中存储的值
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
if st.button("🚀 生成报告", type="primary", disabled=st.session_state.get('report_generated_successfully', False)):
    st.session_state.report_generated_successfully = False
    st.session_state.bazi_info_for_display = {}
    st.session_state.free_report_content = ""
    st.session_state.premium_modules_content = {}

    year = st.session_state.user_inputs['year']
    month = st.session_state.user_inputs['month']
    day = st.session_state.user_inputs['day']
    hour = st.session_state.user_inputs['hour']
    # selected_gender 和 selected_report_type 已经从session_state中获取了正确的值

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
        datetime(year, month, day, hour)
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
        bazi_string_representation = (
            f"年柱:{calculated_bazi_info['year_gz']} | "
            f"月柱:{calculated_bazi_info['month_gz']} | "
            f"日柱:{calculated_bazi_info['day_gz']} | "
            f"时柱:{calculated_bazi_info['hour_gz']}"
        )
        
        st.session_state.bazi_info_for_display = {
            "year": year, "month": month, "day": day, "hour": hour,
            "bazi_str": bazi_string_representation, 
            "gender": selected_gender, # 使用已经获取的正确值
            "report_type": selected_report_type # 使用已经获取的正确值
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
            spinner_messages = { title: f"正在生成{title.split('与')[0]}..." for title in tab_titles }
            
            generation_methods_map = {
                "八字排盘与五行分析": bazi_engine.generate_bazi_analysis_module,
                "命格解码与人生特质": bazi_engine.generate_mingge_decode_module,
                "事业财富与婚恋分析": bazi_engine.generate_career_love_module,
                "五行健康与养生建议": bazi_engine.generate_health_advice_module,
                "大运流年运势推演": bazi_engine.generate_fortune_flow_module
            }

            for title in tab_titles:
                with st.spinner(spinner_messages[title]):
                    module_content_str = generation_methods_map[title](bazi_string_representation, selected_gender)
                    generated_premium_modules[title] = module_content_str
                    if "API Error:" in module_content_str or "Error calling DeepSeek API:" in module_content_str:
                        all_modules_generated_ok = False
                        st.error(f"生成 '{title}' 模块失败: {module_content_str}")
            
            if all_modules_generated_ok:
                st.session_state.premium_modules_content = generated_premium_modules
                st.session_state.report_generated_successfully = True
            else:
                st.warning("部分付费报告模块生成失败，请检查错误信息。")
                st.session_state.report_generated_successfully = False

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
    st.subheader("📝 八字信息概览")
    bazi_display_data = st.session_state.bazi_info_for_display
    st.write(f"**公历生日**: {bazi_display_data['year']}年 {bazi_display_data['month']}月 {bazi_display_data['day']}日 {bazi_display_data['hour']}时")
    st.write(f"**您的八字**: {bazi_display_data['bazi_str']}")
    st.write(f"**性别**: {bazi_display_data['gender']}") # 直接使用session_state中的值
    
    report_display_title = f"✨ 您的 {bazi_display_data['report_type']} ✨" # 直接使用session_state中的值
    st.subheader(report_display_title)

    content_for_download = ""
    report_filename_part = "免费版" if bazi_display_data['report_type'] == '免费版报告 (简要)' else "付费版"
    
    download_file_header = f"""# 🔮 DeepSeek 专业八字命理报告

**公历生日**: {bazi_display_data['year']}年{bazi_display_data['month']}月{bazi_display_data['day']}日 {bazi_display_data['hour']}时
**您的八字**: {bazi_display_data['bazi_str']}
**性别**: {bazi_display_data['gender']}
**报告类型**: {bazi_display_data['report_type']}

---
"""
    download_file_footer = """
---
免责声明：本报告内容基于命理学理论和AI模型生成，仅供娱乐参考，不构成任何决策的最终依据。命理学并非精密科学，请理性看待。
"""

    if bazi_display_data['report_type'] == '免费版报告 (简要)':
        report_content_to_show = st.session_state.free_report_content
        if report_content_to_show.strip().startswith("```") and report_content_to_show.strip().endswith("```"):
            lines = report_content_to_show.strip().split('\n')
            if len(lines) >= 3:
                first_line_content = lines[0].strip()
                if first_line_content.startswith("```") and (len(first_line_content) == 3 or first_line_content[3:].isalnum()):
                    report_content_to_show = '\n'.join(lines[1:-1]).strip()
        
        st.markdown(report_content_to_show, unsafe_allow_html=False)
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
                    st.markdown(module_str_content, unsafe_allow_html=False)
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
            key="download_report_file_button"
        )
    
    if st.button("🧹 清除当前报告并开始新的分析", key="clear_report_button_bottom"):
        clear_all_data_and_rerun()

st.markdown("---")
st.info("免责声明：本报告内容基于命理学理论和AI模型生成，仅供娱乐参考，不构成任何决策的最终依据。命理学并非精密科学，请理性看待。")
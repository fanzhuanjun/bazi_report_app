# app.py
import streamlit as st
from datetime import datetime
from bazi_report_generator import DeepSeekBaziReport # 假设这个是你最初的 bazi_report_generator.py
import pytz

# ！！！确保这是整个脚本的第一个 Streamlit 命令！！！
st.set_page_config(
    page_title="反转 专业八字命理学报告",
    page_icon="https://i.miji.bid/2025/06/02/066902e47e5172e4f1c67ac2c66cbeb5.png", # 可以用一个更相关的图标，例如 🔮 或 ✨
    layout="wide",
    initial_sidebar_state="expanded" # 确保侧边栏默认展开
)

# --- DeepSeek API Key 配置 ---
api_key = "sk-392daa9410c7429fa9be75e49049a4ec" # 请替换为您的有效API Key

# --- Custom CSS for Beautification (您原有的CSS，稍作调整以适应侧边栏) ---
custom_css = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #333;
        /* background-color: #f5f5f7; /* 可以为整个页面设置浅色背景 */
    }

    /* Main title of the app (in the main area) */
    .app-main-title {
        color: #2c3e50; 
        text-align: center;
        font-size: 2.6em; /* 稍微调整 */
        font-weight: bold;
        margin-bottom: 15px; /* 调整间距 */
        padding-top: 20px;
    }
    .app-subtitle { /* 主区域的副标题 */
        text-align: center;
        color: #555;
        font-size: 1.05em;
        margin-bottom: 30px; /* 调整间距 */
    }

    /* Sidebar title style */
    div[data-testid="stSidebarNavItems"] + div h2, /* 更精确地定位侧边栏内的标题 */
    [data-testid="stSidebar"] [data-testid="stHeading"] { /* Streamlit 1.18+ heading in sidebar */
        color: #2c3e50 !important;
        font-size: 1.6em !important; /* 侧边栏标题大小 */
        font-weight: 600 !important;
        padding-bottom: 10px;
        /* border-bottom: 2px solid #3498db; /* 侧边栏标题下划线颜色 */
        /* text-align: center; */ /* 如果希望居中 */
    }
    
    /* Style for Streamlit input labels in sidebar to match the image */
    [data-testid="stSidebar"] .st-emotion-cache-1qg0nbk p { /* This selector might change with Streamlit versions, inspect to confirm */
        color: #4a5568; /* Darker grey for labels */
        font-size: 0.95em; /* Slightly smaller labels */
    }
    [data-testid="stSidebar"] .stRadio > label { /* Radio button labels */
         font-size: 0.95em !important;
         color: #4a5568 !important;
    }


    /* Bazi info display card (in the main area) */
    .bazi-info-card {
        background-color: #fdfefe; 
        border: 1px solid #e5e8eb; 
        border-left: 5px solid #3498db; /* 左侧蓝色强调线 */
        padding: 20px;
        margin-top: 20px; /* 与上方元素的间距 */
        margin-bottom: 25px;
        border-radius: 8px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.06);
    }
    .bazi-info-card p {
        margin-bottom: 10px; /* 段落间距 */
        font-size: 1.05em;
        line-height: 1.65;
        color: #333;
    }
    .bazi-info-card strong { /* 卡片内标签，如“公历生日” */
        color: #2980b9; 
        font-weight: 600;
        margin-right: 5px;
    }
     .bazi-info-card .highlight-bazi { /* 八字干支高亮 */
        background-color: #e8f6f3;
        color: #117a65;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 500;
        border: 1px solid #a2d9ce;
        display: inline-block;
    }


    /* Report type title (in the main area) */
    .report-type-title {
        color: #c0392b; 
        font-size: 1.8em; /* 调整大小以适应主内容区 */
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 8px;
        /* text-align: center; /* 如果希望居中 */
    }

    /* LLM generated report content styles (in the main area) */
    .report-content {
        padding: 5px;
        margin-top: 10px; /* 确保与上方标题有间距 */
    }
    .report-content h2 { /* ## */
        color: #2980b9; 
        font-size: 1.7em;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #aed6f1; 
    }
    .report-content h3 { /* ### */
        color: #27ae60; 
        font-size: 1.5em;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 12px;
    }
    .report-content h4 { /* #### */
        color: #8e44ad; 
        font-size: 1.3em;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .report-content p {
        line-height: 1.75; 
        color: #34495e; 
        margin-bottom: 14px; 
        font-size: 1.05em;
    }
    .report-content strong, .report-content b {
        color: #d35400; 
        font-weight: bold !important; /* 确保所有strong都加粗 */
    }
    .report-content ul, .report-content ol {
        margin-left: 5px; 
        padding-left: 25px;
    }
    .report-content li {
        margin-bottom: 10px;
        line-height: 1.7;
        font-size: 1.05em;
    }
    .report-content blockquote {
        border-left: 5px solid #f39c12; 
        padding: 12px 20px; 
        margin: 20px 0; 
        background-color: #fef5e7; 
        color: #873600; 
        border-radius: 6px;
    }

    /* Disclaimer box (in the main area) */
    .disclaimer-box {
        background-color: #f0f2f6; /* 浅灰色背景 */
        border: 1px solid #d9d9d9; 
        padding: 20px;
        margin-top: 40px; /* 与上方内容的主要间距 */
        border-radius: 8px;
        font-size: 0.9em;
        color: #595959; 
        line-height: 1.6;
    }

    /* Tabs styling (in the main area) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f0f2f6; /* 标签栏背景色 */
        border-radius: 6px;
        padding: 5px;
        margin-bottom: 15px; /* 标签栏和内容的间距 */
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1em; /* 标签文字大小 */
        font-weight: 500;
        color: #595959; 
        border-radius: 4px;
        margin-right: 5px;
        padding: 8px 15px; /* 标签内边距 */
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #3498db; 
        color: white !important; 
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 10px; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 初始化 Session State ---
if 'report_generated_successfully' not in st.session_state:
    st.session_state.report_generated_successfully = False
if 'bazi_info_for_display' not in st.session_state:
    st.session_state.bazi_info_for_display = {}
if 'free_report_content' not in st.session_state:
    st.session_state.free_report_content = ""
if 'premium_modules_content' not in st.session_state:
    st.session_state.premium_modules_content = {}
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = {
        "year": datetime.now().year - 28, "month": datetime.now().month,
        "day": datetime.now().day, "hour": 12,
        "gender": '男', "report_type": '免费版报告 (简要)'
    }

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


# --- 侧边栏：输入信息 ---
with st.sidebar:
    # st.image("your_logo.png", width=100) # 如果您有logo可以放这里
    st.markdown("## 🗓️ 个人信息输入") # 使用Markdown标题以应用CSS
    st.markdown("---") # 分隔线

    if st.session_state.get('report_generated_successfully', False):
        # st.info("已有报告生成。若需重填，请先清除。") # 这个提示可以移到主区域
        if st.button("✨ 清除报告并重填", key="clear_report_button_sidebar", use_container_width=True):
            clear_all_data_and_rerun()
        st.markdown("---")

    current_year = datetime.now().year
    st.session_state.user_inputs['year'] = st.number_input(
        "出生年份 (公历)", min_value=1900, max_value=current_year,
        value=st.session_state.user_inputs['year'], step=1, key="year_input_sidebar"
    )
    st.session_state.user_inputs['month'] = st.number_input(
        "出生月份 (公历)", min_value=1, max_value=12,
        value=st.session_state.user_inputs['month'], step=1, key="month_input_sidebar"
    )
    st.session_state.user_inputs['day'] = st.number_input(
        "出生日期 (公历)", min_value=1, max_value=31,
        value=st.session_state.user_inputs['day'], step=1, key="day_input_sidebar"
    )
    st.session_state.user_inputs['hour'] = st.number_input(
        "出生时辰 (24小时制, 0-23)", min_value=0, max_value=23,
        value=st.session_state.user_inputs['hour'], step=1, key="hour_input_sidebar"
    )
    
    gender_options = ('男', '女')
    try:
        current_gender_index = gender_options.index(st.session_state.user_inputs['gender'])
    except ValueError:
        current_gender_index = 0
    st.session_state.user_inputs['gender'] = st.radio(
        "您的性别", gender_options, index=current_gender_index, key="gender_input_sidebar" # horizontal=False 默认垂直
    )
    
    report_type_options = ('免费版报告 (简要)', '付费版报告 (专业详细)')
    try:
        current_report_type_index = report_type_options.index(st.session_state.user_inputs['report_type'])
    except ValueError:
        current_report_type_index = 0
    st.session_state.user_inputs['report_type'] = st.radio(
        "选择报告类型", report_type_options, index=current_report_type_index, key="report_type_input_sidebar"
    )

    st.markdown("---") # 分隔线
    if st.button("🚀 生成报告", type="primary", disabled=st.session_state.get('report_generated_successfully', False), use_container_width=True, key="generate_report_sidebar"):
        # ... (生成报告的逻辑和之前版本一样，这里不再重复，确保它在按钮的 if 块内) ...
        # 清空旧数据
        st.session_state.report_generated_successfully = False
        st.session_state.bazi_info_for_display = {}
        st.session_state.free_report_content = ""
        st.session_state.premium_modules_content = {}

        year = st.session_state.user_inputs['year']
        month = st.session_state.user_inputs['month']
        day = st.session_state.user_inputs['day']
        hour = st.session_state.user_inputs['hour']
        selected_gender = st.session_state.user_inputs['gender']
        selected_report_type = st.session_state.user_inputs['report_type']

        if not api_key or not api_key.startswith("sk-"):
            st.error("DeepSeek API Key 未配置或格式不正确。") # 这个错误最好显示在主区域
            with st.spinner("错误"): # 临时占位，主区域会显示
                st.stop()


        try: # 日期有效性检查
            if month == 2:
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                max_days = 29 if is_leap else 28
            elif month in [4, 6, 9, 11]: max_days = 30
            else: max_days = 31
            if not (1 <= day <= max_days):
                st.error(f"{year}年{month}月没有{day}日！") # 主区域显示
                st.stop()
            datetime(year, month, day, hour)
        except ValueError:
            st.error("您输入的日期或时间无效！") # 主区域显示
            st.stop()

        bazi_engine = DeepSeekBaziReport(api_key)
        calculated_bazi_info = bazi_engine.calculate_simple_bazi(year, month, day, hour)
        
        if "计算错误" in calculated_bazi_info.values():
            st.error("八字计算时发生错误，请检查输入。") # 主区域显示
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
        
        main_area_status_placeholder = st.empty() # 用于在主区域显示 spinner 和 progress

        if selected_report_type == '免费版报告 (简要)':
            with main_area_status_placeholder.container(), st.spinner("正在努力生成您的免费八字报告，请稍候..."):
                 # 用 .container() 可以在 empty 内部放置多个元素，如果需要的话
                generated_report_content = bazi_engine.generate_free_report(bazi_string_representation, selected_gender)
            if "API Error:" in generated_report_content or "Error calling DeepSeek API:" in generated_report_content:
                st.error(f"生成免费报告时遇到问题：{generated_report_content}")
            else:
                st.session_state.free_report_content = generated_report_content
                st.session_state.report_generated_successfully = True
            main_area_status_placeholder.empty() # 清除spinner信息
        
        else: # 付费版报告 (专业详细)
            generated_premium_modules = {}
            all_modules_generated_ok = True
            tab_titles = ["八字排盘与五行分析", "命格解码与人生特质", "事业财富与婚恋分析", "五行健康与养生建议", "大运流年运势推演"]
            generation_methods_map = {
                "八字排盘与五行分析": bazi_engine.generate_bazi_analysis_module,
                "命格解码与人生特质": bazi_engine.generate_mingge_decode_module,
                "事业财富与婚恋分析": bazi_engine.generate_career_love_module,
                "五行健康与养生建议": bazi_engine.generate_health_advice_module,
                "大运流年运势推演": bazi_engine.generate_fortune_flow_module
            }
            total_modules = len(tab_titles)
            
            current_progress_bar = main_area_status_placeholder.progress(0) # 在主区域创建并显示进度条

            # 主区域的进度条
            # progress_bar_placeholder_main = st.empty()
            
            for i, title in enumerate(tab_titles):
                # Spinner 文本现在直接用 st.text 或 st.caption 更新，而不是嵌套在 spinner里
                # 或者，如果希望spinner和进度条同时显示，可以再用一个empty给spinner
                spinner_text_placeholder = st.empty() # 放在循环内，每次更新文本
                spinner_text_placeholder.text(f"⏳ 正在生成 {title.split('与')[0].split('和')[0]} 模块... ({i+1}/{total_modules})")
                
                # 模拟API调用，实际是LLM调用
                module_content_str = generation_methods_map[title](bazi_string_representation, selected_gender)
                generated_premium_modules[title] = module_content_str
                
                if "API Error:" in module_content_str or "Error calling DeepSeek API:" in module_content_str:
                    all_modules_generated_ok = False
                    st.error(f"生成 '{title}' 模块失败: {module_content_str}") 
                
                # --- 修正进度条逻辑 ---
                # 2. 在循环内更新进度条的值
                current_progress_bar.progress((i + 1) / total_modules)
                # --- 修正结束 ---
                spinner_text_placeholder.empty() # 清除本次循环的spinner文本

            main_area_status_placeholder.empty() # 清除进度条 (它会替换掉上面的progress bar)
            
            if all_modules_generated_ok:
                st.session_state.premium_modules_content = generated_premium_modules
                st.session_state.report_generated_successfully = True
            else:
                st.warning("部分付费报告模块生成失败，请检查错误信息。")

        if st.session_state.report_generated_successfully:
            st.rerun()





# --- 主页面内容 ---
st.markdown("<h1 class='app-main-title'>✨ 反转实验室 专业八字命理报告</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>探索传统智慧，洞悉人生奥秘。请输入您的信息以生成定制命理分析。</p>", unsafe_allow_html=True)

if st.session_state.get('report_generated_successfully', False):
    if 'bazi_info_for_display' in st.session_state and st.session_state.bazi_info_for_display:
        st.markdown("<h2 class='section-subheader' style='font-size: 1.6em; margin-top:10px;'>📝 八字信息概览</h2>", unsafe_allow_html=True)
        bazi_display_data = st.session_state.bazi_info_for_display

        bazi_str_parts = bazi_display_data['bazi_str'].split(" | ")
        styled_bazi_parts = []
        for part in bazi_str_parts:
            if ":" in part:
                label, value = part.split(":", 1)
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
        
        download_file_header = f"""# 🔮 反转 专业八字命理报告
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
            st.markdown(f"<div class='report-content'>{report_content_to_show}</div>", unsafe_allow_html=True)
            content_for_download = download_file_header + report_content_to_show + download_file_footer
        else: 
            modules_to_show = st.session_state.premium_modules_content
            tab_titles_ordered = ["八字排盘与五行分析", "命格解码与人生特质", "事业财富与婚恋分析", "五行健康与养生建议", "大运流年运势推演"]
            tabs_display = st.tabs(tab_titles_ordered)
            
            premium_report_download_parts = [download_file_header]
            for i, title in enumerate(tab_titles_ordered):
                with tabs_display[i]:
                    module_str_content = modules_to_show.get(title, "")
                    if module_str_content and not ("API Error:" in module_str_content or "Error calling DeepSeek API:" in module_str_content):
                        st.markdown(f"<div class='report-content'>{module_str_content}</div>", unsafe_allow_html=True)
                        premium_report_download_parts.append(f"## {title}\n\n{module_str_content}\n\n---\n")
                    elif "API Error:" in module_str_content or "Error calling DeepSeek API:" in module_str_content:
                        st.error(f"抱歉，'{title}' 模块内容生成时出错，无法显示。") # API错误显示在对应tab
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
                key="download_report_main_button", # 确保key唯一
                use_container_width=True 
            )
    else:
        st.info("⬅️ 请在左侧栏输入您的信息并点击“生成报告”以查看结果。")


# --- 页脚免责声明 (全局) ---
st.markdown("---")
st.markdown(
    "<div class='disclaimer-box'><strong>免责声明</strong>：本报告内容基于八字命理学理论，旨在提供参考与启发，并非预示确定的人生轨迹。命理学作为一种传统文化，其解读具有多重维度和不确定性，不应视为精密科学。个人命运的塑造离不开主观能动性与实际行动，请您结合自身情况理性看待报告内容，不宜作为重大人生决策的唯一依据。</div>",
    unsafe_allow_html=True
)

# app.py
import streamlit as st
from datetime import datetime, date, timedelta
from bazi_report_generator import DeepSeekBaziReport
import pytz
import asyncio

# ！！！确保这是整个脚本的第一个 Streamlit 命令！！！
st.set_page_config(
    page_title="反转 专业八字命理学报告",
    page_icon="https://i.miji.bid/2025/06/02/066902e47e5172e4f1c67ac2c66cbeb5.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DeepSeek API Key 配置 ---
api_key = "sk-392daa9410c7429fa9be75e49049a4ec" # 请替换为您的有效API Key

# --- Custom CSS for Beautification ---
custom_css = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #333;
    }
    .app-main-title {
        color: #2c3e50; 
        text-align: center;
        font-size: 2.6em;
        font-weight: bold;
        margin-bottom: 15px;
        padding-top: 20px;
    }
    .app-subtitle {
        text-align: center;
        color: #555;
        font-size: 1.05em;
        margin-bottom: 30px;
    }
    div[data-testid="stSidebarNavItems"] + div h2,
    [data-testid="stSidebar"] [data-testid="stHeading"] {
        color: #2c3e50 !important;
        font-size: 1.6em !important;
        font-weight: 600 !important;
        padding-bottom: 10px;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1qg0nbk p, 
    [data-testid="stSidebar"] label p, 
    [data-testid="stSidebar"] .st-emotion-cache-ue6h3e p 
    {
        color: #4a5568;
        font-size: 0.95em;
    }
    [data-testid="stSidebar"] .stRadio > label {
         font-size: 0.95em !important;
         color: #4a5568 !important;
    }
    .bazi-info-card {
        background-color: #fdfefe; 
        border: 1px solid #e5e8eb; 
        border-left: 5px solid #3498db;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 25px;
        border-radius: 8px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.06);
    }
    .bazi-info-card p {
        margin-bottom: 10px;
        font-size: 1.05em;
        line-height: 1.65;
        color: #333;
    }
    .bazi-info-card strong {
        color: #2980b9; 
        font-weight: 600;
        margin-right: 5px;
    }
     .bazi-info-card .highlight-bazi {
        background-color: #e8f6f3;
        color: #117a65;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 500;
        border: 1px solid #a2d9ce;
        display: inline-block;
    }
    .report-type-title {
        color: #c0392b; 
        font-size: 1.8em;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        padding-bottom: 8px;
    }
    .report-content { padding: 5px; margin-top: 10px; }
    .report-content h2 { color: #2980b9; font-size: 1.7em; font-weight: 600; margin-top: 30px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #aed6f1; }
    .report-content h3 { color: #27ae60; font-size: 1.5em; font-weight: 600; margin-top: 25px; margin-bottom: 12px; }
    .report-content h4 { color: #8e44ad; font-size: 1.3em; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }
    .report-content p { line-height: 1.75; color: #34495e; margin-bottom: 14px; font-size: 1.05em; }
    .report-content strong, .report-content b { color: #d35400; font-weight: bold !important; }
    .report-content ul, .report-content ol { margin-left: 5px; padding-left: 25px; }
    .report-content li { margin-bottom: 10px; line-height: 1.7; font-size: 1.05em; }
    .report-content blockquote { border-left: 5px solid #f39c12; padding: 12px 20px; margin: 20px 0; background-color: #fef5e7; color: #873600; border-radius: 6px; }
    .disclaimer-box { background-color: #f0f2f6; border: 1px solid #d9d9d9; padding: 20px; margin-top: 40px; border-radius: 8px; font-size: 0.9em; color: #595959; line-height: 1.6; }
    .stTabs [data-baseweb="tab-list"] { background-color: #f0f2f6; border-radius: 6px; padding: 5px; margin-bottom: 15px; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 1em; font-weight: 500; color: #595959; border-radius: 4px; margin-right: 5px; padding: 8px 15px; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { background-color: #3498db; color: white !important; font-weight: 600; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 10px; }

    /* Custom style for st.date_input to show placeholder with YYYY-MM-DD */
    div[data-testid="stDateInput"] input::placeholder {
        content: "YYYY-MM-DD";
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# Helper class for premium report generation
class PremiumReportGenerator:
    def __init__(self, bazi_engine, bazi_str, gender, tab_titles, generation_methods_map_async, age_info): # ADDED age_info
        self.bazi_engine = bazi_engine
        self.bazi_str = bazi_str
        self.gender = gender
        self.tab_titles = tab_titles
        self.generation_methods_map_async = generation_methods_map_async
        self.age_info = age_info # STORED age_info
        
        self.generated_modules = {}
        self.overall_success = True
        
        self.progress_bar_ui = None
        self.text_status_ui = None

    async def _generate_module_task(self, title):
        method_to_call = self.generation_methods_map_async[title]
        try:
            # The lambda functions in app.py are now responsible for passing the correct arguments,
            # including bazi_str, gender, and age_info consistently.
            content = await method_to_call(self.bazi_str, self.gender, self.age_info) 
            
            self.generated_modules[title] = content
            if "API Error:" in content or "Error calling DeepSeek API:" in content:
                self.overall_success = False
        except Exception as e:
            self.generated_modules[title] = f"生成模块 '{title}' 时发生意外错误: {str(e)}"
            self.overall_success = False
        return title

    async def run_all_concurrently(self, progress_bar_ui, text_status_ui):
        self.progress_bar_ui = progress_bar_ui
        self.text_status_ui = text_status_ui
        
        tasks = [self._generate_module_task(title) for title in self.tab_titles]
        
        num_completed = 0
        total_modules = len(self.tab_titles)
        
        # Initialize progress bar and text
        self.progress_bar_ui.progress(0)
        self.text_status_ui.text(f"⏳ 准备开始生成报告模块... (0/{total_modules})")

        for future in asyncio.as_completed(tasks):
            completed_task_title = await future 
            num_completed += 1
            
            short_display_title = completed_task_title.split('与')[0].split('和')[0]
            # Update text and progress bar
            self.text_status_ui.text(f"⏳ 正在生成 {short_display_title} 模块... ({num_completed}/{total_modules})")
            self.progress_bar_ui.progress(num_completed / total_modules)
            
        self.text_status_ui.text(f"✅ 所有报告模块生成完毕! ({total_modules}/{total_modules})") # Final status
        return self.generated_modules, self.overall_success


# --- 初始化 Session State ---
if 'report_generated_successfully' not in st.session_state:
    st.session_state.report_generated_successfully = False
if 'bazi_info_for_display' not in st.session_state:
    st.session_state.bazi_info_for_display = {}
if 'free_report_content' not in st.session_state:
    st.session_state.free_report_content = ""
if 'premium_modules_content' not in st.session_state:
    st.session_state.premium_modules_content = {}

# Default birth date calculation - robustly handle month/day for default
try:
    default_birth_date = date(datetime.now().year - 28, datetime.now().month, datetime.now().day)
except ValueError: # Handles cases like Feb 29 for non-leap year if current date is Feb 29
    default_birth_date = date(datetime.now().year - 28, datetime.now().month, 1)


if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = {
        "birth_date": default_birth_date,
        "hour": 12,
        "gender": '男',
        "report_type": '免费版报告 (简要)'
    }

def clear_all_data_and_rerun():
    keys_to_delete = [
        'report_generated_successfully', 'bazi_info_for_display',
        'free_report_content', 'premium_modules_content'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    current_year = datetime.now().year
    # Recalculate default_date_val robustly
    try:
        default_date_val = date(current_year - 28, datetime.now().month, datetime.now().day)
    except ValueError:
        default_date_val = date(current_year - 28, datetime.now().month, 1)


    st.session_state.user_inputs = {
        "birth_date": default_date_val,
        "hour": 12,
        "gender": '男',
        "report_type": '免费版报告 (简要)'
    }
    st.session_state.report_generated_successfully = False
    st.rerun()


# --- 侧边栏：输入信息 ---
with st.sidebar:
    st.markdown("## 🗓️ 个人信息输入")
    st.markdown("---")

    if st.session_state.get('report_generated_successfully', False):
        if st.button("✨ 清除报告并重填", key="clear_report_button_sidebar", use_container_width=True):
            clear_all_data_and_rerun()
        st.markdown("---")

    current_year = datetime.now().year
    min_date = date(1900, 1, 1)
    # Ensure max_date is valid, e.g. not beyond current date if current_year is selected
    max_date_dt = datetime(current_year, 12, 31)
    if datetime.now() < max_date_dt: # If current date is before Dec 31 of current year
        max_date = datetime.now().date()
    else:
        max_date = max_date_dt.date()

    
    if isinstance(st.session_state.user_inputs.get('birth_date'), str):
        try:
            st.session_state.user_inputs['birth_date'] = datetime.strptime(st.session_state.user_inputs['birth_date'], "%Y-%m-%d").date()
        except:
            st.session_state.user_inputs['birth_date'] = default_birth_date # Use module-level default
    elif not isinstance(st.session_state.user_inputs.get('birth_date'), date):
         st.session_state.user_inputs['birth_date'] = default_birth_date # Use module-level default

    # The format "YYYY/MM/DD" tells st.date_input how to display the date in the input box.
    # The calendar pop-up language is usually controlled by browser locale.
    st.session_state.user_inputs['birth_date'] = st.date_input(
        "出生日期 (公历)",
        value=st.session_state.user_inputs['birth_date'],
        min_value=min_date,
        max_value=max_date,
        key="birth_date_input_sidebar",
        format="YYYY-MM-DD" # Use YYYY-MM-DD for a more standard numeric display in the box
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
        "您的性别", gender_options, index=current_gender_index, key="gender_input_sidebar"
    )
    
    report_type_options = ('免费版报告 (简要)', '付费版报告 (专业详细)')
    try:
        current_report_type_index = report_type_options.index(st.session_state.user_inputs['report_type'])
    except ValueError:
        current_report_type_index = 0
    st.session_state.user_inputs['report_type'] = st.radio(
        "选择报告类型", report_type_options, index=current_report_type_index, key="report_type_input_sidebar"
    )

    st.markdown("---")
    if st.button("🚀 生成报告", type="primary", disabled=st.session_state.get('report_generated_successfully', False), use_container_width=True, key="generate_report_sidebar"):
        st.session_state.report_generated_successfully = False
        st.session_state.bazi_info_for_display = {}
        st.session_state.free_report_content = ""
        st.session_state.premium_modules_content = {}

        birth_date_obj = st.session_state.user_inputs['birth_date']
        year = birth_date_obj.year
        month = birth_date_obj.month # This will be an integer
        day = birth_date_obj.day
        hour = st.session_state.user_inputs['hour']
        selected_gender = st.session_state.user_inputs['gender']
        selected_report_type = st.session_state.user_inputs['report_type']

        # Calculate age_info_str here
        current_year_for_age = datetime.now().year
        age_val_for_display = current_year_for_age - year
        age_info_str = f"{age_val_for_display}岁" if age_val_for_display >= 0 and age_val_for_display <= 90 else "暂无"


        main_error_placeholder = st.empty()

        if not api_key or not api_key.startswith("sk-"):
            main_error_placeholder.error("DeepSeek API Key 未配置或格式不正确。请在代码中配置有效的API Key。")
            st.stop()

        try:
            datetime(year, month, day, hour)
        except ValueError:
            main_error_placeholder.error("您输入的日期或时间无效！")
            st.stop()

        bazi_engine = DeepSeekBaziReport(api_key)
        calculated_bazi_info = bazi_engine.calculate_simple_bazi(year, month, day, hour)
        
        if "计算错误" in calculated_bazi_info.values():
            main_error_placeholder.error("八字计算时发生错误，请检查输入或联系管理员。")
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
            "report_type": selected_report_type,
            "age_info": age_info_str # ADDED age_info_str to session state
        }
        
        # UI elements for status - create them in the main area
        status_container = st.empty() 

        if selected_report_type == '免费版报告 (简要)':
            with status_container, st.spinner("正在努力生成您的免费八字报告，请稍候..."): 
                # Free report prompt doesn't need age currently, but can be added if needed
                generated_report_content = bazi_engine.generate_free_report(bazi_string_representation, selected_gender)
            
            status_container.empty() 

            if "API Error:" in generated_report_content or "Error calling DeepSeek API:" in generated_report_content:
                main_error_placeholder.error(f"生成免费报告时遇到问题：{generated_report_content}")
            else:
                st.session_state.free_report_content = generated_report_content
                st.session_state.report_generated_successfully = True
        
        else: # 付费版报告 (专业详细)
            tab_titles = ["八字排盘与五行分析", "命格解码与人生特质", "事业财富与婚恋分析", "五行健康与养生建议", "大运流年运势推演"]
            
            generation_methods_map_async = {
                # All lambdas now accept bazi_str_arg, gender_arg, age_info_arg consistently
                "八字排盘与五行分析": lambda bazi_str_arg, gender_arg, age_info_arg: bazi_engine.generate_bazi_analysis_module_async(bazi_str_arg, gender_arg, age_info_arg),
                "命格解码与人生特质": lambda bazi_str_arg, gender_arg, age_info_arg: bazi_engine.generate_mingge_decode_module_async(bazi_str_arg, gender_arg, age_info_arg),
                "事业财富与婚恋分析": lambda bazi_str_arg, gender_arg, age_info_arg: bazi_engine.generate_career_love_module_async(bazi_str_arg, gender_arg, age_info_arg),
                "五行健康与养生建议": lambda bazi_str_arg, gender_arg, age_info_arg: bazi_engine.generate_health_advice_module_async(bazi_str_arg, gender_arg, age_info_arg),
                # IMPORTANT: For '大运流年运势推演', we pass additional birth details AND the age_info
                "大运流年运势推演": lambda bazi_str_arg, gender_arg, age_info_arg: bazi_engine.generate_fortune_flow_module_async(
                    bazi_str_arg, gender_arg,
                    st.session_state.bazi_info_for_display['year'],
                    st.session_state.bazi_info_for_display['month'],
                    st.session_state.bazi_info_for_display['day'],
                    st.session_state.bazi_info_for_display['hour'],
                    age_info_arg # ADDED age_info_arg here
                )
            }

            report_generator_instance = PremiumReportGenerator(
                bazi_engine, 
                bazi_string_representation, 
                selected_gender, 
                tab_titles, 
                generation_methods_map_async,
                age_info_str # PASSED age_info_str to PremiumReportGenerator
            )
            
            with status_container.container(): 
                progress_bar_element = st.progress(0)
                text_status_element = st.text("⏳ 准备开始生成报告模块...")


            _generated_modules_result = {}
            _overall_success_result = True

            try:
                _generated_modules_result, _overall_success_result = asyncio.run(
                    report_generator_instance.run_all_concurrently(progress_bar_element, text_status_element)
                )
            except Exception as e: 
                main_error_placeholder.error(f"异步生成报告时发生系统错误: {e}")
                _overall_success_result = False
            
            st.session_state.premium_modules_content = _generated_modules_result
            if _generated_modules_result: 
                st.session_state.report_generated_successfully = True 
            
            if not _overall_success_result:
                pass 


        if st.session_state.report_generated_successfully:
            main_error_placeholder.empty()
            status_container.empty() 
            st.rerun()

# --- 主页面内容 ---
st.markdown("<h1 class='app-main-title'>✨ 反转实验室 专业八字命理报告</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>探索传统智慧，洞悉人生奥秘。请输入您的信息并生成定制命理分析。</p>", unsafe_allow_html=True)

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

        birth_date_str = f"{bazi_display_data['year']}年 {bazi_display_data['month']}月 {bazi_display_data['day']}日 {bazi_display_data['hour']}时"
        # Display age_info if available
        age_display_str = f"<strong>当前年龄</strong>: {bazi_display_data.get('age_info', '未知')}" if 'age_info' in bazi_display_data else ""

        bazi_info_html = f"""
        <div class="bazi-info-card">
            <p><strong>公历生日</strong>: {birth_date_str}</p>
            <p>{styled_bazi_str_display}</p>
            <p><strong>性别</strong>: {bazi_display_data['gender']} {age_display_str}</p>
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
**当前年龄**: {bazi_display_data.get('age_info', '未知')}
**报告类型**: {bazi_display_data['report_type']}
---
"""
        download_file_footer = """
---
免责声明：本报告内容基于八字命理学理论，仅供参考，不构成任何决策的最终依据。命理学并非精密科学，请理性看待。
"""

        if bazi_display_data['report_type'] == '免费版报告 (简要)':
            report_content_to_show = st.session_state.free_report_content
            if "API Error:" in report_content_to_show or "Error calling DeepSeek API:" in report_content_to_show:
                st.error(f"免费报告生成失败：{report_content_to_show}")
                content_for_download = download_file_header + f"错误：{report_content_to_show}" + download_file_footer
            else:
                st.markdown(f"<div class='report-content'>{report_content_to_show}</div>", unsafe_allow_html=True)
                content_for_download = download_file_header + report_content_to_show + download_file_footer
        else: 
            modules_to_show = st.session_state.premium_modules_content
            tab_titles_ordered = ["八字排盘与五行分析", "命格解码与人生特质", "事业财富与婚恋分析", "五行健康与养生建议", "大运流年运势推演"]
            tabs_display = st.tabs(tab_titles_ordered)
            
            premium_report_download_parts = [download_file_header]
            all_modules_valid = True
            for i, title in enumerate(tab_titles_ordered):
                with tabs_display[i]:
                    module_str_content = modules_to_show.get(title, "此模块内容未能成功加载。")
                    is_error_content = "API Error:" in module_str_content or \
                                       "Error calling DeepSeek API:" in module_str_content or \
                                       ("生成模块" in module_str_content and "时发生" in module_str_content)

                    if is_error_content:
                        st.error(f"抱歉，'{title}' 模块内容生成时出错或未能加载：\n{module_str_content}")
                        premium_report_download_parts.append(f"## {title}\n\n错误：{module_str_content}\n\n---\n")
                        all_modules_valid = False
                    elif module_str_content == "此模块内容未能成功加载。":
                         st.info(f"'{title}' 模块内容当前为空或未成功获取。")
                         premium_report_download_parts.append(f"## {title}\n\n此模块内容未能成功加载。\n\n---\n")
                         all_modules_valid = False
                    else:
                        st.markdown(f"<div class='report-content'>{module_str_content}</div>", unsafe_allow_html=True)
                        premium_report_download_parts.append(f"## {title}\n\n{module_str_content}\n\n---\n")
            
            if not modules_to_show or not all_modules_valid: 
                 if not st.session_state.get("premium_generation_error_shown_globally", False):
                    st.warning("部分或全部付费报告模块未能成功生成，请检查各模块内容。如果问题持续，请重试或联系支持。")
                    st.session_state.premium_generation_error_shown_globally = True 
            else:
                if "premium_generation_error_shown_globally" in st.session_state:
                    del st.session_state.premium_generation_error_shown_globally


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
                key="download_report_main_button",
                use_container_width=True 
            )
    else:
        st.info("⬅️ 请在左侧栏输入您的信息并点击“生成报告”以查看结果。")

st.markdown("---")
st.markdown(
    "<div class='disclaimer-box'><strong>免责声明</strong>：本报告内容基于八字命理学理论，旨在提供参考与启发，并非预示确定的人生轨迹。命理学并非精密科学，请理性看待。个人命运的塑造离不开主观能动性与实际行动，请您结合自身情况理性看待报告内容，不宜作为重大人生决策的唯一依据。</div>",
    unsafe_allow_html=True
)

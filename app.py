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
api_key = "sk-537f71b3f5294a8696610aefa4a9423a" # 请替换为您的有效API Key

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
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Define report type to module mapping (Moved to global scope) ---
REPORT_MODULES_MAP = {
    "姻缘定制版": ["八字排盘与五行分析", "命格解码与人生特质", "婚恋情感分析", "五行健康与养生建议", "大运流年运势推演"],
    "事业财富版": ["八字排盘与五行分析", "命格解码与人生特质", "事业财富分析", "五行健康与养生建议", "大运流年运势推演"],
    "初级版": ["八字排盘与五行分析", "命格解码与人生特质", "五行健康与养生建议", "大运流年运势推演"],
    "完整版": ["八字排盘与五行分析", "命格解码与人生特质", "事业财富分析", "婚恋情感分析", "五行健康与养生建议", "大运流年运势推演"]
}

# Helper class for premium report generation
class PremiumReportGenerator:
    def __init__(self, bazi_engine, bazi_str, gender, report_type_modules_ordered, generation_methods_map_async, age_info):
        self.bazi_engine = bazi_engine
        self.bazi_str = bazi_str
        self.gender = gender
        # The specific ordered list of modules for the selected report type
        self.report_type_modules_ordered = report_type_modules_ordered 
        self.generation_methods_map_async = generation_methods_map_async
        self.age_info = age_info
        
        self.generated_modules = {}
        self.overall_success = True
        
        self.progress_bar_ui = None
        self.text_status_ui = None

    # Helper async function to run a module generation and return its title and content
    async def _generate_module_and_return_title(self, title: str, method_call, *args, **kwargs):
        try:
            content = await method_call(*args, **kwargs)
            # Check for API errors or specific error messages from the LLM responses
            if "API Error:" in content or "Error calling DeepSeek API:" in content or \
               ("生成模块" in content and "时发生" in content) or ("意外错误" in content):
                return title, content, False # Return content and indicate failure
            return title, content, True # Return content and indicate success
        except Exception as e:
            return title, f"生成模块 '{title}' 时发生意外错误: {str(e)}", False # Return error and indicate failure

    async def run_all_concurrently(self, progress_bar_ui, text_status_ui):
        self.progress_bar_ui = progress_bar_ui
        self.text_status_ui = text_status_ui
        
        total_modules = len(self.report_type_modules_ordered)
        core_bazi_summary = "" # Initialize core summary
        
        self.progress_bar_ui.progress(0)
        self.text_status_ui.text(f"⏳ 准备开始生成报告模块... (0/{total_modules})")

        # --- Phase 1: Generate the first module (always "八字排盘与五行分析") and extract core summary (sequential) ---
        # The user's new report types all start with "八字排盘与五行分析", so this remains valid.
        first_module_title = self.report_type_modules_ordered[0] # This should always be "八字排盘与五行分析"
        short_display_title_first = first_module_title.split('与')[0].split('和')[0]
        self.text_status_ui.text(f"⏳ 正在生成 {short_display_title_first} 模块 (基础分析)...")
        
        # Directly call the first module generation
        first_module_content = ""
        try:
            first_module_content_raw = await self.generation_methods_map_async[first_module_title](self.bazi_str, self.gender, self.age_info)
            
            if "API Error:" in first_module_content_raw or "Error calling DeepSeek API:" in first_module_content_raw or \
               ("生成模块" in first_module_content_raw and "意外错误" in first_module_content_raw):
                self.overall_success = False
                first_module_content = f"⚠️ 八字排盘与五行分析模块生成失败。错误信息: {first_module_content_raw}\n\n请重试。\n\n" + first_module_content_raw
                core_bazi_summary = "核心命理分析提取失败，后续模块可能不一致。原始八字排盘模块有错误。"
            else:
                first_module_content = first_module_content_raw
                self.text_status_ui.text(f"⏳ 正在提取核心命理摘要...")
                core_bazi_summary_raw = await self.bazi_engine._extract_core_bazi_summary(first_module_content_raw)
                
                if "API Error:" in core_bazi_summary_raw:
                    self.overall_success = False
                    st.warning(f"核心命理摘要提取失败: {core_bazi_summary_raw}. 后续模块可能缺乏一致性。")
                    core_bazi_summary = "未能成功提取核心命理摘要，后续分析可能不一致。"
                else:
                    core_bazi_summary = core_bazi_summary_raw
                st.session_state.debug_core_summary = core_bazi_summary # Store for potential debugging
        except Exception as e:
            self.overall_success = False
            first_module_content = f"生成模块 '{first_module_title}' 时发生意外错误: {str(e)}"
            core_bazi_summary = "核心命理分析提取失败，后续模块可能不一致。原始八字排盘模块有意外错误。"
        
        self.generated_modules[first_module_title] = first_module_content

        # After the first module (and summary extraction), update progress to show one module done
        num_completed = 1 
        self.progress_bar_ui.progress(num_completed / total_modules)
        self.text_status_ui.text(f"✅ 完成 {short_display_title_first} 模块. ({num_completed}/{total_modules})")

        # --- Phase 2: Generate remaining modules concurrently ---
        remaining_titles = self.report_type_modules_ordered[1:]
        tasks = []
        for title in remaining_titles:
            method_to_call = self.generation_methods_map_async[title]
            if title == "大运流年运势推演":
                task = asyncio.create_task(
                    self._generate_module_and_return_title(
                        title, # Pass title explicitly
                        method_to_call,
                        self.bazi_str, self.gender,
                        st.session_state.bazi_info_for_display['year'],
                        st.session_state.bazi_info_for_display['month'],
                        st.session_state.bazi_info_for_display['day'],
                        st.session_state.bazi_info_for_display['hour'],
                        self.age_info,
                        core_bazi_summary # Pass the core summary
                    )
                )
            else:
                task = asyncio.create_task(
                    self._generate_module_and_return_title(
                        title, # Pass title explicitly
                        method_to_call,
                        self.bazi_str, self.gender, self.age_info, core_bazi_summary
                    )
                )
            tasks.append(task)
        
        # Concurrently wait for the remaining tasks to complete
        for future in asyncio.as_completed(tasks):
            # Now, 'future' will directly yield (title, content, success_status) from _generate_module_and_return_title
            completed_task_title, content, module_success = await future
            
            self.generated_modules[completed_task_title] = content
            if not module_success:
                self.overall_success = False
            
            num_completed += 1
            short_display_title_current = completed_task_title.split('与')[0].split('和')[0]
            self.text_status_ui.text(f"⏳ 正在生成 {short_display_title_current} 模块... ({num_completed}/{total_modules})")
            self.progress_bar_ui.progress(num_completed / total_modules)
            
        self.text_status_ui.text(f"✅ 所有报告模块生成完毕! ({total_modules}/{total_modules})") # Final status
        return self.generated_modules, self.overall_success


# --- 初始化 Session State ---
if 'report_generated_successfully' not in st.session_state:
    st.session_state.report_generated_successfully = False
if 'bazi_info_for_display' not in st.session_state:
    st.session_state.bazi_info_for_display = {}
# Removed 'free_report_content' as it's no longer used
if 'premium_modules_content' not in st.session_state:
    st.session_state.premium_modules_content = {}
if 'debug_core_summary' not in st.session_state: 
    st.session_state.debug_core_summary = ""

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
        "report_type": '初级版' # Updated default report type
    }

def clear_all_data_and_rerun():
    keys_to_delete = [
        'report_generated_successfully', 'bazi_info_for_display',
        'premium_modules_content', 'debug_core_summary' 
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
        "report_type": '初级版' # Updated default report type
    }
    st.session_state.report_generated_successfully = False
    st.rerun()


# --- 侧边栏：保留清除按钮 ---
with st.sidebar:
    st.markdown("## ⚙️ 操作") 
    st.markdown("---")

    if st.session_state.get('report_generated_successfully', False):
        if st.button("✨ 清除报告并重填", key="clear_report_button_sidebar", use_container_width=True):
            clear_all_data_and_rerun()
        st.markdown("---")
    
    st.markdown("输入信息请在主页面上方完成。")


# --- 主页面内容 ---
st.markdown("<h1 class='app-main-title'>✨ 反转实验室 专业八字命理报告</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>探索传统智慧，洞悉人生奥秘。请输入您的信息并生成定制命理分析。</p>", unsafe_allow_html=True)

# --- START OF MOVED INPUT SECTION ---
st.markdown("---") 
st.markdown("### 🗓️ 请输入您的个人信息")

# Date and time related variables
current_year = datetime.now().year
min_date = date(1900, 1, 1)
max_date_dt = datetime(current_year, 12, 31)
if datetime.now() < max_date_dt:
    max_date = datetime.now().date()
else:
    max_date = max_date_dt.date()

# Ensure birth_date is a date object
if isinstance(st.session_state.user_inputs.get('birth_date'), str):
    try:
        st.session_state.user_inputs['birth_date'] = datetime.strptime(st.session_state.user_inputs['birth_date'], "%Y-%m-%d").date()
    except:
        st.session_state.user_inputs['birth_date'] = default_birth_date
elif not isinstance(st.session_state.user_inputs.get('birth_date'), date):
        st.session_state.user_inputs['birth_date'] = default_birth_date

col1, col2 = st.columns(2)

with col1:
    st.session_state.user_inputs['birth_date'] = st.date_input(
        "出生日期 (公历)",
        value=st.session_state.user_inputs['birth_date'],
        min_value=min_date,
        max_value=max_date,
        key="birth_date_input_main", 
        format="YYYY-MM-DD"
    )
    gender_options = ('男', '女')
    try:
        current_gender_index = gender_options.index(st.session_state.user_inputs['gender'])
    except ValueError:
        current_gender_index = 0
    st.session_state.user_inputs['gender'] = st.radio(
        "您的性别", gender_options, index=current_gender_index, key="gender_input_main", horizontal=True 
    )

with col2:
    st.session_state.user_inputs['hour'] = st.number_input(
        "出生时辰 (24小时制, 0-23)", min_value=0, max_value=23,
        value=st.session_state.user_inputs['hour'], step=1, key="hour_input_main" 
    )
    # Updated report type options
    report_type_options = ('姻缘定制版', '事业财富版', '初级版', '完整版')
    try:
        current_report_type_index = report_type_options.index(st.session_state.user_inputs['report_type'])
    except ValueError:
        current_report_type_index = 0
    st.session_state.user_inputs['report_type'] = st.radio(
        "选择报告类型", report_type_options, index=current_report_type_index, key="report_type_input_main" 
    )

# Placeholder for errors and status messages related to input and generation button
main_input_area_error_placeholder = st.empty() 
main_input_area_status_container = st.empty()

if st.button("🚀 生成报告", type="primary", disabled=st.session_state.get('report_generated_successfully', False), use_container_width=True, key="generate_report_main"): 
    st.session_state.report_generated_successfully = False
    st.session_state.bazi_info_for_display = {}
    # Removed clearing of free_report_content
    st.session_state.premium_modules_content = {}
    st.session_state.debug_core_summary = "" # Clear debug summary on new generation

    birth_date_obj = st.session_state.user_inputs['birth_date']
    year = birth_date_obj.year
    month = birth_date_obj.month
    day = birth_date_obj.day
    hour = st.session_state.user_inputs['hour']
    selected_gender = st.session_state.user_inputs['gender']
    selected_report_type = st.session_state.user_inputs['report_type']

    current_year_for_age = datetime.now().year
    age_val_for_display = current_year_for_age - year
    age_info_str = f"{age_val_for_display}岁" if age_val_for_display >= 0 and age_val_for_display <= 90 else "暂无"

    if not api_key or not api_key.startswith("sk-"):
        main_input_area_error_placeholder.error("DeepSeek API Key 未配置或格式不正确。请在代码中配置有效的API Key。")
        st.stop()

    try:
        datetime(year, month, day, hour)
    except ValueError:
        main_input_area_error_placeholder.error("您输入的日期或时间无效！")
        st.stop()

    bazi_engine = DeepSeekBaziReport(api_key)
    calculated_bazi_info = bazi_engine.calculate_simple_bazi(year, month, day, hour)
    
    if "计算错误" in calculated_bazi_info.values():
        main_input_area_error_placeholder.error("八字计算时发生错误，请检查输入或联系管理员。")
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
        "age_info": age_info_str
    }
    
    # Get the specific modules for the selected report type
    selected_modules_for_generation = REPORT_MODULES_MAP.get(selected_report_type, [])
    
    # Check if a valid report type was selected
    if not selected_modules_for_generation:
        main_input_area_error_placeholder.error(f"无效的报告类型：{selected_report_type}。请选择一个有效的报告类型。")
        st.session_state.report_generated_successfully = False
        st.stop()

    # Updated lambda functions to match the new method signatures in DeepSeekBaziReport
    generation_methods_map_async = {
        "八字排盘与五行分析": lambda bazi_str_arg, gender_arg, age_info_arg: \
                              bazi_engine.generate_bazi_analysis_module_async(bazi_str_arg, gender_arg, age_info_arg),
        "命格解码与人生特质": lambda bazi_str_arg, gender_arg, age_info_arg, core_summary_arg: \
                              bazi_engine.generate_mingge_decode_module_async(bazi_str_arg, gender_arg, age_info_arg, core_summary_arg),
        "事业财富分析": lambda bazi_str_arg, gender_arg, age_info_arg, core_summary_arg: \
                              bazi_engine.generate_career_wealth_module_async(bazi_str_arg, gender_arg, age_info_arg, core_summary_arg),
        "婚恋情感分析": lambda bazi_str_arg, gender_arg, age_info_arg, core_summary_arg: \
                              bazi_engine.generate_love_marriage_module_async(bazi_str_arg, gender_arg, age_info_arg, core_summary_arg),
        "五行健康与养生建议": lambda bazi_str_arg, gender_arg, age_info_arg, core_summary_arg: \
                              bazi_engine.generate_health_advice_module_async(bazi_str_arg, gender_arg, age_info_arg, core_summary_arg),
        "大运流年运势推演": lambda bazi_str_arg, gender_arg, year_arg, month_arg, day_arg, hour_arg, age_info_arg, core_summary_arg: \
                              bazi_engine.generate_fortune_flow_module_async(bazi_str_arg, gender_arg, year_arg, month_arg, day_arg, hour_arg, age_info_arg, core_summary_arg)
    }

    report_generator_instance = PremiumReportGenerator(
        bazi_engine, 
        bazi_string_representation, 
        selected_gender, 
        selected_modules_for_generation, # Pass the dynamic list of modules
        generation_methods_map_async,
        age_info_str
    )
    
    with main_input_area_status_container.container(): 
        progress_bar_element = st.progress(0)
        text_status_element = st.text("⏳ 准备开始生成报告模块...")

    _generated_modules_result = {}
    _overall_success_result = True

    try:
        _generated_modules_result, _overall_success_result = asyncio.run(
            report_generator_instance.run_all_concurrently(progress_bar_element, text_status_element)
        )
    except Exception as e: 
        main_input_area_error_placeholder.error(f"异步生成报告时发生系统错误: {e}")
        _overall_success_result = False
    
    st.session_state.premium_modules_content = _generated_modules_result
    if _generated_modules_result and _overall_success_result: 
        st.session_state.report_generated_successfully = True 
    
    if not _overall_success_result:
        pass 

    if st.session_state.report_generated_successfully:
        main_input_area_error_placeholder.empty()
        main_input_area_status_container.empty() 
        st.rerun()

st.markdown("---") 
# --- END OF MOVED INPUT SECTION ---


# --- 主页面报告显示区域 ---
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
        # Use selected_report_type directly for filename
        report_filename_part = bazi_display_data['report_type'] 
        
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
免责声明：本报告内容基于八字命理学理论，仅供参考，不构成任何决策的最终依据。命理学并非精密科学，请理性看待。个人命运的塑造离不开主观能动性与实际行动，请您结合自身情况理性看待报告内容，不宜作为重大人生决策的唯一依据。
"""
        # Debugging: show core summary for premium reports
        if st.session_state.debug_core_summary: # No longer tied to "付费版报告" specifically
            with st.expander("🔬 查看AI提取的核心命理摘要 (用于辅助一致性分析)"):
                st.info(st.session_state.debug_core_summary)

        # All reports now use the module-based display
        modules_to_show = st.session_state.premium_modules_content
        # Use the modules determined by the selected report type for tab display
        tabs_display = st.tabs(REPORT_MODULES_MAP[bazi_display_data['report_type']])
        
        premium_report_download_parts = [download_file_header]
        all_modules_valid = True
        for i, title in enumerate(REPORT_MODULES_MAP[bazi_display_data['report_type']]):
            with tabs_display[i]:
                module_str_content = modules_to_show.get(title, "此模块内容未能成功加载。")
                is_error_content = "API Error:" in module_str_content or \
                                   "Error calling DeepSeek API:" in module_str_content or \
                                   ("生成模块" in module_str_content and "时发生" in module_str_content) or \
                                   ("意外错误" in module_str_content) 

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
                st.warning("部分或全部报告模块未能成功生成，请检查各模块内容。如果问题持续，请重试或联系支持。")
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
        st.info("请在上方填写您的信息并点击“生成报告”以查看结果。") 

st.markdown("---")
st.markdown(
    "<div class='disclaimer-box'><strong>免责声明</strong>：本报告内容基于八字命理学理论，旨在提供参考与启发，并非预示确定的人生轨迹。命理学并非精密科学，请理性看待。个人命运的塑造离不开主观能动性与实际行动，请您结合自身情况理性看待报告内容，不宜作为重大人生决策的唯一依据。</div>",
    unsafe_allow_html=True
)

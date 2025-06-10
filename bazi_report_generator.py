# bazi_report_generator.py

import httpx
import json
from typing import Dict
import sxtwl
import asyncio
import math
import datetime

def get_next(year, month, day):
    """
    Returns the next day as a tuple (year, month, day)
    
    Parameters:
    year (int): The year
    month (int): The month (1-12)
    day (int): The day (1-31, depending on month)
    
    Returns:
    tuple: (next_year, next_month, next_day)
    """
    try:
        current_date = datetime.date(year, month, day)
        next_date = current_date + datetime.timedelta(days=1)
        return (next_date.year, next_date.month, next_date.day)
    except ValueError as e:
        raise ValueError("Invalid date input") from e



class DeepSeekBaziReport:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"

        # Inherited from paidayun.py and integrated as class attributes
        self.Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        self.ShX = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        self.numCn = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        self.jqmc = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏",
             "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑","白露", "秋分", "寒露", "霜降",
             "立冬", "小雪", "大雪"]
        self.ymc = [ "正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二" ]
        self.rmc = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
            "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
            "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十", "卅一"]
        self.XiZ = ['摩羯', '水瓶', '双鱼', '白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手']
        self.WeekCn = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

        # 12个"节" (节令) 的索引，对应 jqmc 列表 (jqIndex % 2 != 0)
        self.JIE_QI_INDICES = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23] # This is already correct based on %2 != 0

        self.gan_elements = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
        }
        self.zhi_elements = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
            "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
            "戌": "土", "亥": "水"
        }
        self.zhi_hidden_stems = { # Simplified, real Bazi needs more complex hidden stem logic
            "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
            "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
            "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
            "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
        }

    async def _call_deepseek_api_async(self, prompt: str, model: str = "deepseek-chat", temperature: float = 0.7) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        system_prompt_content = """你是一位精通中华传统八字命理学的资深专家。在生成报告时，请始终采用娓娓道来的叙述风格，确保语言流畅自然。对于每一个分析要点，都请用3到5句完整且连贯的句子组成一个流畅的小段落进行深入浅出的阐释，让不了解八字的用户也能轻松理解。
            """
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
                response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                if content.startswith("```markdown\n"):
                    content = content[len("```markdown\n"):]
                if content.startswith("```\n"):
                    content = content[len("```\n"):]
                if content.endswith("\n```"):
                    content = content[:-len("\n```")]
                return content
            else:
                return f"API Error: Unexpected response format - {json.dumps(result)}"
        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            try:
                error_json = json.loads(error_details)
                error_message = error_json.get("error", {}).get("message", "Unknown error detail")
            except json.JSONDecodeError:
                error_message = error_details
            return f"API Error: {e.response.status_code} - {error_message}"
        except httpx.RequestError as e: # Catch network-related errors
            return f"API Request Error: {str(e)}"
        except Exception as e:
            return f"Error calling DeepSeek API (async): {str(e)}"

    def _call_deepseek_api_sync(self, prompt: str, model: str = "deepseek-chat", temperature: float = 0.7) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        system_prompt_content = """你是一位精通中华传统八字命理学的资深专家。在生成报告时，请始终采用娓娓道来的叙述风格，确保语言流畅自然。同时要尽量做到客观，不要只输出好的方面，也要有坏的提醒。对于每一个分析要点，都请用3到5句完整且连贯的句子组成一个流畅的小段落进行深入浅出的阐释，让不了解八字的用户也能轻松理解。
            """
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 4000,
        }
        try:
            with httpx.Client(timeout=180.0) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
                response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                if content.startswith("```markdown\n"):
                    content = content[len("```markdown\n"):]
                if content.startswith("```\n"):
                    content = content[len("```\n"):]
                if content.endswith("\n```"):
                    content = content[:-len("\n```")]
                return content
            else:
                return f"API Error: Unexpected response format - {json.dumps(result)}"
        except httpx.HTTPStatusError as e:
            error_details = e.response.text
            try:
                error_json = json.loads(error_details)
                error_message = error_json.get("error", {}).get("message", error_details)
            except json.JSONDecodeError:
                error_message = error_details
            return f"API Error: {e.response.status_code} - {error_message}"
        except Exception as e:
            return f"Error calling DeepSeek API: {str(e)}"

    async def _extract_core_bazi_summary(self, bazi_analysis_content: str) -> str:
        """
        从“八字排盘与五行分析”模块的内容中提取核心命理判断，
        供后续模块作为上下文使用。
        """
        prompt = f"""
        以下是针对某个八字生成的“八字排盘与五行分析”报告内容。请你作为专业的八字命理师，
        从这段内容中提取并概括出以下核心信息：
        - 日主的强弱（是身强、身弱、从强、从弱等）
        - 八字中各五行的旺衰情况（哪个五行最旺，哪个最弱，是否有缺失）
        - 初步判定的喜用神是什么（如果有明确提到）
        - 命局中最显著的一两个十神及其对命主性格或运势的初步影响

        请将这些信息组织成一段简洁、准确的中文概括，作为对该八字核心命理特征的统一总结。
        这段总结将用于指导后续所有模块的分析，务必确保其准确性与一致性。
        示例格式：
        "此八字日主[日干]身[强/弱]，五行中[最旺五行]过旺，[最弱五行]偏弱，初步判断喜用神为[喜用神]。命局中[十神A]和[十神B]显著，预示命主..."
        
        请直接输出总结内容，不要包含任何额外说明或Markdown标题。

        原始报告内容：
        ```markdown
        {bazi_analysis_content}
        ```
        """
        # 使用较低的温度以确保总结的准确性和事实性
        summary = await self._call_deepseek_api_async(prompt, temperature=0.3)
        if "API Error:" in summary or "Error calling DeepSeek API:" in summary:
            print(f"Error extracting core summary: {summary}")
            return "核心命理分析提取失败，可能导致后续模块分析不一致。请检查API调用。"
        return summary


    def calculate_simple_bazi(self, year: int, month: int, day: int, hour: int) -> Dict[str, str]:
        try:
            day_obj = sxtwl.fromSolar(year, month, day)
            year_gz = day_obj.getYearGZ()
            month_gz = day_obj.getMonthGZ()
            
            # 时柱
            hour_gz = day_obj.getHourGZ(hour) # sxtwl uses 0-23 for hour directly for getHourGZ
            
            # 日柱
            day_gz_obj = day_obj.getDayGZ() # Get current day's GZ first
            if hour == 23:
                # If hour is 23, the day pillar actually belongs to the next day
                new_year, new_month, new_day = get_next(year, month, day)
                new_day_obj = sxtwl.fromSolar(new_year, new_month, new_day)
                day_gz_obj = new_day_obj.getDayGZ() # Update day_gz_obj to next day's GZ
            
            bazi_info = {
                "year_gz": self.Gan[year_gz.tg] + self.Zhi[year_gz.dz],
                "month_gz": self.Gan[month_gz.tg] + self.Zhi[month_gz.dz],
                "day_gz": self.Gan[day_gz_obj.tg] + self.Zhi[day_gz_obj.dz], # Corrected variable name
                "hour_gz": self.Gan[hour_gz.tg] + self.Zhi[hour_gz.dz]
            }
            return bazi_info
        except Exception as e:
            # More specific error logging
            print(f"Error in Bazi calculation (sxtwl): year={year}, month={month}, day={day}, hour={hour}. Error: {e}")
            # Return a clear error indicator
            return {
                "year_gz": "计算错误", "month_gz": "计算错误",
                "day_gz": "计算错误", "hour_gz": "计算错误"
            }

    # Removed generate_free_report

    # Premium modules will now be async and accept core_bazi_summary
    async def generate_bazi_analysis_module_async(self, bazi_str: str, gender: str, age_info: str) -> str:
        prompt = f"""
            ### 八字排盘与五行分析

            针对八字：{bazi_str}，性别：{gender}，年龄: {age_info}。
            
            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格。同时要尽量做到客观，不要只输出好的方面，也要有坏的提醒。对于以下列出的每一个主要分析点（如“1. 四柱干支”、“2. 五行力量分析”等）及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出，包括标题和必要的强调。

            首先，请用一个富有诗意的比喻，对这份八字的整体命运特征及一生进行3-4句话的艺术性概括。
            然后详细分析以下内容：

            1.  **四柱干支解读**：
                *   年柱: {bazi_str.split(' | ')[0].split(':')[1].strip()}，并用3-5句完整连贯的话，阐述其在整个命盘中的基础意义，例如它通常代表着命主的祖上根基、早年运程（通常指16岁前）以及时代大环境所赋予的初始印记等。
                *   月柱: {bazi_str.split(' | ')[1].split(':')[1].strip()}，并用3-5句完整连贯的话，阐述其关键作用，例如它深刻影响着命主的家庭环境、父母兄弟姐妹的关系、青少年时期的成长经历（通常指16-32岁），同时也是观察个人性格形成和事业发展潜力的重要窗口。
                *   日柱: {bazi_str.split(' | ')[2].split(':')[1].strip()} (其中日干是：{bazi_str.split(' | ')[2].split(':')[1].strip()[0]})，并用3-5句完整连贯的话，详细说明此日干作为命主（也称日元或自身）的核心特质、本性以及内在驱动力，同时日支（也称夫妻宫）也揭示了命主中年运势（通常指32-48岁）、婚姻观念及与伴侣互动模式的初步信息。
                *   时柱: {bazi_str.split(' | ')[3].split(':')[1].strip()}，并用3-5句完整连贯的话，阐述其所代表的晚年生活景象（通常指48岁后）、子女情况、个人深层追求、事业的最终成就或人生归宿等。

            2.  **五行力量透析**：
                *   请用3-5句完整连贯的话，详细说明此八字命局中金、木、水、火、土这五种元素各自的旺衰程度（例如，哪个五行力量最强，哪个相对较弱，是否有某个五行缺失）。
                *   接着，请用3-5句完整连贯的话，深入分析这些五行之间存在的相生（如木生火、火生土）与相克（如金克木、水克火）关系，是如何具体地影响整个命局的平衡状态与核心特质的，这些互动又怎样塑造了命主的整体运势走向。

            3.  **十神关系详察**：
                *   请首先列出此八字四柱地支中所藏匿的天干（包括本气、中气、余气），并根据日主（日干），清晰标示出命盘天干上透出的主要十神（十神判断要确保准确性）以及地支藏干在特定条件下可能引化出的十神。
                *   然后，请用3-5句完整连贯的话，挑选其中一至两个对命局影响最为显著的十神，阐述它们各自代表的人事物象（例如，正官可能代表上司、约束力或事业，食神可能代表才华、口福或晚辈），以及它们的存在如何影响命主的性格特点和人生际遇。

            4.  **喜用神初步研判**：
                *   请用3-5句完整连贯的话，综合考量日主的强弱旺衰（是身强还是身弱）以及命局中五行的整体平衡流通情况，初步判断出此命局最需要或最喜爱的五行（即喜用神）是什么。
                *   随后，请用3-5句完整连贯的话，简要阐述您做出此判断的主要依据和命理逻辑，例如，如果日主过强，可能需要克制或泄耗的五行为喜用，反之亦然。

            请以专业严谨但通俗易懂的方式展开内容，确保前后逻辑一致、分析深入，让零基础读者也能轻松理解。
            """
        return await self._call_deepseek_api_async(prompt)

    async def generate_mingge_decode_module_async(self, bazi_str: str, gender: str, age_info: str, core_bazi_summary: str) -> str:
        prompt = f"""
            ### 命格解码与人生特质
            
            针对八字：{bazi_str}，性别：{gender}，年龄: {age_info}。
            
            **核心命理基础：**
            {core_bazi_summary}
            
            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格，并且**务必严格遵循上述核心命理基础所确定的方向，确保本模块的所有分析与该基础信息保持高度一致性，避免任何矛盾之处。** 同时要尽量做到客观，不要只输出好的方面，也要有坏的提醒。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请详细分析以下内容：
            
            1.  **格局初步判断与解读**：
                *   请用3-5句完整连贯的话，尝试判断此八字可能属于的主要格局类型（例如扶抑格中的身旺/身弱、从格中的从强/从弱、专旺格、化气格等）。如果格局不够典型或者呈现多种可能性，也请如实指出，并说明判断的主要依据是什么。
                *   接着，请用3-5句完整连贯的话，阐释此（或此类）格局的基本含义，以及这种格局通常会对命主的人生层次、行事风格以及成就高低带来哪些方面的主要影响。

            2.  **性格特质深度描绘**：
                *   请用3-5句完整连贯的话，融合对日主强弱、十神组合特点以及五行旺衰情况的综合分析，生动地描绘出命主在性格上可能展现的主要优点，例如积极进取、温和善良或是富有创造力等。
                *   同样，请用3-5句完整连贯的话，客观地指出命主性格中可能存在的、需要留意的方面或潜在的缺点，例如可能比较固执、容易冲动或是内心较为敏感等。
                *   最后，请用3-5句完整连贯的话，具体描述命主在日常生活中，为人处世可能展现出的主要行为模式和与人交往的鲜明特点。

            3.  **人生主要优势与潜在挑战**：
                *   请用3-5句完整连贯的话，依据命局的整体组合与力量分布，分析命主在一生中可能更容易把握或拥有的主要优势和发展机遇，例如可能容易获得贵人相助、或者在某个特定领域更容易取得成功。
                *   同时，请用3-5句完整连贯的话，指出命主在人生旅途中可能需要面对和克服的主要挑战、困扰或人生课题，例如可能在人际关系、健康或是某个时期的财运方面需要特别注意。

            4.  **核心价值观与人生追求洞察**：
                *   请用3-5句完整连贯的话，基于命局所反映出的深层信息，尝试推断并阐述命主在内心深处可能秉持的核心价值观是什么，例如是更看重成就感、家庭和谐、精神自由还是物质保障。
                *   接着，请用3-5句完整连贯的话，进一步分析命主在人生中可能会努力追求的主要目标和生活理想是什么样的。

            
            请确保分析深刻、富有洞察力，且行文流畅易懂。
            """
        return await self._call_deepseek_api_async(prompt)

    # NEW: Split career and love into two separate modules
    async def generate_career_wealth_module_async(self, bazi_str: str, gender: str, age_info: str, core_bazi_summary: str) -> str:
        prompt = f"""
            ### 事业财富分析
            
            针对八字：{bazi_str}，性别：{gender}，年龄: {age_info}。
            
            **核心命理基础：**
            {core_bazi_summary}

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格，并且**务必严格遵循上述核心命理基础所确定的方向，确保本模块的所有分析与该基础信息保持高度一致性，避免任何矛盾之处。** 同时要尽量做到客观，不要只输出好的方面，也要有坏的提醒。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请详细分析事业财富：
            
            1.  **优势行业与职业方向指引**：
                *   请用3-5句完整连贯的话，根据此八字的五行喜用（即命局所喜的五行元素）以及显著的十神特性（例如，若食伤生财明显，可能适合创意或技艺求财；若官印相生，可能适合管理或学术领域），为命主建议一些相对更有利或更容易获得发展的行业领域。
                *   接着，请用3-5句完整连贯的话，进一步分析并指出命主较为适合的职业发展方向或岗位类型，例如是偏向技术研发、市场营销、教育文化、还是自主经营等，并简述理由。

            2.  **事业发展模式与机遇前瞻**：
                *   请用3-5句完整连贯的话，分析并阐述命主的命格更倾向于哪种事业发展模式，例如是更适合独立创业、勇闯新路，还是与人合伙经营、共同发展，亦或是在相对稳定的大型企事业单位中按部就班地晋升。
                *   同时，请用3-5句完整连贯的话，基于命局特点，预测命主在事业发展过程中可能会遇到的典型机遇（例如某个时期易得提拔）和需要留意的潜在阻碍或挑战（例如某个阶段易犯小人）。

            3.  **财富能量评估与求财之道**：
                *   请用3-5句完整连贯的话，评估命主天生的财富能量（例如正财运稳健还是偏财运突出，或者财库情况如何），并分析其在金钱观念和理财习惯上可能表现出的特点。
                *   随后，请用3-5句完整连贯的话，为命主提供一些符合其命格特性的求财建议和积累财富的策略方向，例如是宜稳健投资还是可适度冒险，是靠专业技能还是人脉资源等。

            4.  **事业贵人类型与提点**：
                *   请用3-5句完整连贯的话，分析在命主的事业发展道路上，最有可能遇到何种类型的贵人（例如，是年长的上司、同辈的朋友还是某个特定属相的人），这些贵人可能会在哪些方面给予重要的帮助或指点。
            
            请确保分析具体、实用，结论有据可循，文字亲切易懂。
            """
        return await self._call_deepseek_api_async(prompt)

    async def generate_love_marriage_module_async(self, bazi_str: str, gender: str, age_info: str, core_bazi_summary: str) -> str:
        prompt = f"""
            ### 婚恋情感分析
            
            针对八字：{bazi_str}，性别：{gender}，年龄: {age_info}。
            
            **核心命理基础：**
            {core_bazi_summary}

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格，并且**务必严格遵循上述核心命理基础所确定的方向，确保本模块的所有分析与该基础信息保持高度一致性，避免任何矛盾之处。** 同时要尽量做到客观，不要只输出好的方面，也要有坏的提醒。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请详细探索婚恋情感：
            
            1.  **婚恋观念剖析与择偶偏好**：
                *   请用3-5句完整连贯的话，深入分析命主在婚恋关系中可能持有的核心观念，例如是更向往浪漫激情、注重现实条件、渴望精神共鸣还是追求平淡安稳。
                *   接着，请用3-5句完整连贯的话，具体描述命主在选择伴侣时，内心深处可能会比较看重对方具备哪些条件或特质，例如外貌、才华、经济实力、性格相投或是家庭背景等。

            2.  **情感互动模式与沟通特点**：
                *   请用3-5句完整连贯的话，描绘命主在亲密关系中通常会展现出的行为特点和情感表达方式，例如是主动热情型、温和体贴型还是内敛含蓄型。
                *   同时，请用3-5句完整连贯的话，分析命主在情感关系中可能存在的优点（如忠诚、善解人意）以及需要特别注意的沟通问题或潜在的相处模式挑战。

            3.  **未来伴侣信息初探 (若命局信息较为明显)**：
                *   请用3-5句完整连贯的话，根据命盘中的夫妻宫（通常是日支）的状态以及代表配偶的星神（男命看财星，女命看官杀星）的旺衰喜忌等信息，初步推断未来伴侣可能具备的某些较为明显的特征（如大致的性格倾向、能力范围、外形感觉等），或可能的相识途径与缘分时机。 （若信息不明显，可说明难以具体判断）

            4.  **婚恋顺利度评估与经营建议**：
                *   请用3-5句完整连贯的话，综合评估命主婚恋过程的大致顺利程度，并指出在感情道路上可能遇到的典型情感波折、考验或需要经营的方面。
                *   最后，请用3-5句完整连贯的话，给出一些具有针对性的、有助于命主更好地经营情感关系、提升婚恋运的实用建议。
            
            请确保分析具体、实用，结论有据可循，文字亲切易懂。
            """
        return await self._call_deepseek_api_async(prompt)


    async def generate_health_advice_module_async(self, bazi_str: str, gender: str, age_info: str, core_bazi_summary: str) -> str:
        prompt = f"""
            ### 五行健康与养生建议
            
            针对八字：{bazi_str}，性别：{gender}，年龄: {age_info}。
            
            **核心命理基础：**
            {core_bazi_summary}

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格，并且**务必严格遵循上述核心命理基础所确定的方向，确保本模块的所有分析与该基础信息保持高度一致性，避免任何矛盾之处。** 对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请详细分析以下内容：
            
            1.  **五行对应脏腑健康状态分析**：
                *   请用3-5句完整连贯的话，根据此八字初步分析与各五行相对应的主要脏腑（例如金对应肺与大肠，木对应肝与胆，水对应肾与膀胱，火对应心与小肠，土对应脾与胃）潜在的健康状况或能量水平。
                *   接着，请用3-5句完整连贯的话，具体指出哪些脏腑的功能在本命局中可能表现得相对强健有力，而哪些脏腑又可能显得相对薄弱，或者更容易在特定条件下出现失衡或不适的问题。

            2.  **体质基本特点与易感病症提示**：
                *   请用3-5句完整连贯的话，综合八字五行的整体偏向（例如偏寒、偏热、偏燥、偏湿等），分析并阐述命主可能具有的基本体质特点。
                *   然后，请用3-5句完整连贯的话，根据命局中可能存在的五行过旺、过弱或严重失衡的情况，预测命主在生活中需要特别注意预防哪些类型的疾病倾向或常见的身体不适症状。

            3.  **个性化养生调理方案建议**：
                *   **饮食调养**: 请用3-5句完整连贯的话，针对命局的五行特点（例如，若某五行过弱则需补益，过旺则需疏泄），提出一些具体的饮食宜忌。例如，建议多食用哪些五行属性的食物来补益相应的脏腑，或者避免哪些食物以免加重失衡。
                *   **作息与运动**: 请用3-5句完整连贯的话，结合命主的能量特点和五行喜忌，为其推荐一些较为适合的作息规律（例如早睡早起，或根据季节调整）和运动方式（例如是适合瑜伽、太极等静态运动，还是跑步、游泳等动态运动，或是需要动静结合）。
                *   **情绪疏导与压力管理**: 请用3-5句完整连贯的话，结合命主的性格特质和潜在的情绪模式（例如易怒、易忧思等），提出一些有助于其保持身心平衡、有效疏导负面情绪和缓解生活压力的方法建议。

            4.  **有利方位选择与生活环境调整参考**：
                *   请用3-5句完整连贯的话，根据命局的五行喜用神，为命主在选择居住方位、工作学习方位时提供一些参考建议，指出哪些方向可能对其身心健康和整体能量状态更为有利。
                *   同时，请用3-5句完整连贯的话，简要提及在日常生活中，哪些颜色或环境布置元素（例如根据五行选择植物、装饰品等）可能对命主的健康运势起到积极的辅助作用。
            
            请确保建议具有针对性，并尽可能结合中医五行理论进行阐释，使其更具参考价值。
            """
        return await self._call_deepseek_api_async(prompt)

    async def generate_fortune_flow_module_async(self, bazi_str: str, gender: str, year: int, month: int, day: int, hour: int, age_info: str, core_bazi_summary: str) -> str:
        # Call the integrated _calculate_dayun method
        dayun_calc_result = self._calculate_dayun(year, month, day, hour, sex=gender)

        if not dayun_calc_result: # Handle error from paidayun calculation
            return f"生成大运列表失败：{bazi_str}"

        # Format the dayun_list into a string for the prompt
        dayun_list_str_for_prompt = ""
        for da_yun in dayun_calc_result['大运']:
            dayun_list_str_for_prompt += f"  {da_yun['大运柱']} (起运虚岁: {da_yun['起运虚岁']}岁, 年龄区间: {da_yun['年龄区间']})\n"

        # The '起运' info line for the prompt, formatted like the screenshot
        # e.g., 2029年02月11日(6.2) 起运
        dayun_start_info_line = dayun_calc_result['起运信息']['第二步大运开始的起运日期和精确虚岁']
        
        # Use the passed age_info directly in the prompt
        prompt = f"""
            ### 大运流年运势推演

            针对八字：{bazi_str}，性别：{gender}， 年龄: {age_info}。
            出生日期：{dayun_calc_result['出生日期']}
            {dayun_start_info_line}
            大运列表:
            {dayun_list_str_for_prompt}

            **核心命理基础：**
            {core_bazi_summary}

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格，注意采用与命主年龄相匹配的叙述。并且**务必严格遵循上述核心命理基础所确定的方向，确保本模块的所有分析与该基础信息保持高度一致性，避免任何矛盾之处。** 同时要尽量做到客观，不要只输出好的方面，也要有坏的提醒。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。

            请进行未来运势趋势分析：

            1.  **大运起排规则与起运岁数说明**：
                *   请用3-5句完整连贯的话，简要说明大运是如何根据出生月柱和性别（阳男阴女顺行，阴男阳女逆行）来起排的，以及每一步大运通常主管十年的运程。
                *   请结合上面提供的大运列表，指出命主从几岁开始进入第一步大运，并解释这个起运岁数是如何影响人生阶段划分的。

            2.  **未来1-2步大运趋势简析 (每步大运10年)**：
                *   对于命主即将进入或正在经历的第一步（或下一两步）大运，请列出其天干地支。然后，请用3-5句完整连贯的话，分析这组干支是如何与原命局发生作用的，例如它会增强或削弱原局中的哪些五行力量，或者引动哪些十神。
                *   接着，请用3-5句完整连贯的话，进一步阐述在这一步大运的十年期间，命主在事业发展、财富积累、感情生活、身体健康等主要人生方面，可能会经历怎样的总体吉凶趋势、生活重心变化或重要的发展机遇与挑战。 （若分析两步大运，请分别阐述）

            3.  **未来5年流年运势关注点提示**：
                *   请列出未来5年的流年干支。对于其中每一个流年，请用3-5句完整连贯的话，结合当前所处的大运环境，指出该年有哪些方面是命主需要特别关注的，要做到尽量具体和客观。例如，某一年可能特别有利于学业进步或事业拓展，某一年则需多加注意人际关系调和或财务管理，又或者某一年健康方面容易出现一些小状况等。请尽量给出具体的生活领域提示。

            4.  **人生运程趋吉避凶总括性建议**：
                *   请用3-5句完整连贯的话，基于对命局特点以及未来大运流年基本趋势的综合判断，为命主提供一些在人生不同运程起伏阶段，如何更好地把握发展机遇、规避潜在风险、以及调适心态的总体性指导原则或智慧锦囊。

            **声明**: 此处提供的分析是基于八字命理理论对未来运势所做的简要趋势性推演，主要用于提供一个宏观的参考框架。具体到每一年甚至每一月的详细运势，会受到更多细微因素的影响，且个人的主观努力和选择亦至关重要。因此，本内容仅供参考，不宜作为重大决策的唯一依据。
            """
        return await self._call_deepseek_api_async(prompt)

    # START OF PAIDAYUN.PY INTEGRATION
    # Helper functions become methods of the class
    def _gz_to_str(self, gz_obj):
        """将sxtwl.GZ对象转换为天干地支字符串"""
        return f"{self.Gan[gz_obj.tg]}{self.Zhi[gz_obj.dz]}"

    def _get_next_gz(self, gz_obj):
        """获取下一个天干地支（顺排）"""
        next_tg_idx = (gz_obj.tg + 1) % 10
        next_dz_idx = (gz_obj.dz + 1) % 12
        return sxtwl.GZ(next_tg_idx, next_dz_idx)

    def _get_prev_gz(self, gz_obj):
        """获取上一个天干地支（逆排）"""
        next_tg_idx = (gz_obj.tg - 1 + 10) % 10
        next_dz_idx = (gz_obj.dz - 1 + 12) % 12
        return sxtwl.GZ(next_tg_idx, next_dz_idx)

    # The main paidayun function logic, now a method '_calculate_dayun'
    def _calculate_dayun(self, year, month, day, hour, minute=0, second=0, sex="男"):
        """
        排大运函数

        Args:
            year (int): 出生年份 (公历)
            month (int): 出生月份 (公历)
            day (int): 出生日期 (公历)
            hour (int): 出生小时 (公历，24小时制)
            minute (int, optional): 出生分钟 (公历). Defaults to 0.
            second (int, optional): 出生秒钟 (公历). Defaults to 0.
            sex (str, optional): 性别 ('男'或'女'). Defaults to '男'.

        Returns:
            dict: 包含八字、起运信息和大运流年的字典。
                  如果输入无效，返回None。
        """
        if sex not in ["男", "女"]:
            print("错误：性别参数必须是 '男' 或 '女'。")
            return None

        try:
            # 1. 创建 sxtwl.Time 对象，用于获取精确的公历时间点
            birth_time_obj = sxtwl.Time(year, month, day, hour, minute, second)
            birth_jd = sxtwl.toJD(birth_time_obj) # 出生时的儒略日数

            # 2. 创建 sxtwl.Day 对象，用于获取八字四柱
            birth_day_obj = sxtwl.fromSolar(year, month, day)

            # 3. 获取八字四柱
            year_gz = birth_day_obj.getYearGZ() # 以立春为界
            month_gz = birth_day_obj.getMonthGZ()
            
            hour_gz = birth_day_obj.getHourGZ(hour)
            if hour == 23:
                new_year, new_month, new_day = get_next(year, month, day)
                new_day_obj = sxtwl.fromSolar(new_year, new_month, new_day)
                day_gz = new_day_obj.getDayGZ() # Changed to assign to day_gz directly
            else:
                day_gz = birth_day_obj.getDayGZ() # Changed to assign to day_gz directly
            
            bazi_pillars = {
                "年柱": self.Gan[year_gz.tg] + self.Zhi[year_gz.dz],
                "月柱": self.Gan[month_gz.tg] + self.Zhi[month_gz.dz],
                "日柱": self.Gan[day_gz.tg] + self.Zhi[day_gz.dz], # Corrected variable name from dTG to day_gz
                "时柱": self.Gan[hour_gz.tg] + self.Zhi[hour_gz.dz]
            }

            # 4. 确定排运方向 (阳男顺、阴女顺；阳女逆、阴男逆)
            year_stem_idx = year_gz.tg
            is_year_yang = (year_stem_idx % 2 == 0) # 甲丙戊庚壬为阳干 (0, 2, 4, 6, 8)

            direction_sign = 0 # 1 for 顺排, -1 for 逆排
            if (is_year_yang and sex == "男") or (not is_year_yang and sex == "女"):
                direction_sign = 1  # 阳男顺排, 阴女顺排
            else:
                direction_sign = -1 # 阳女逆排, 阴男逆排

            start_direction = "顺排" if direction_sign == 1 else "逆排"

            # 5. 查找起运节气
            jieqi_list_prev_year = sxtwl.getJieQiByYear(year - 1)
            jieqi_list_current_year = sxtwl.getJieQiByYear(year)
            jieqi_list_next_year = sxtwl.getJieQiByYear(year + 1)

            all_sorted_jieqi = sorted(
                jieqi_list_prev_year + jieqi_list_current_year + jieqi_list_next_year,
                key=lambda x: x.jd
            )
            
            # 过滤掉“中气”，只保留“节令” (jqIndex % 2 != 0)
            # sxtwl的节气索引约定：0: 冬至(气), 1: 小寒(节), 2: 大寒(气), 3: 立春(节), ...
            # 奇数索引对应的是“节”，例如1(小寒), 3(立春), 5(惊蛰)
            filtered_jieqi = [jq for jq in all_sorted_jieqi if jq.jqIndex % 2 != 0]

            target_jieqi_obj = None 
            
            idx_birth_jieqi_after = -1 
            for i, jq in enumerate(filtered_jieqi):
                if jq.jd > birth_jd:
                    idx_birth_jieqi_after = i
                    break
            
            # Error handling for edge cases where no jieqi is found after or before
            if direction_sign == 1: # 顺排：寻找出生时间后的第一个节令
                if idx_birth_jieqi_after == -1 or idx_birth_jieqi_after >= len(filtered_jieqi):
                    raise ValueError(f"顺排：未能找到出生时间 {birth_time_obj.toStr()} 之后的有效节令。请检查日期范围或节气数据。")
                target_jieqi_obj = filtered_jieqi[idx_birth_jieqi_after]
            else: # 逆排：寻找出生时间前的第一个节令
                if idx_birth_jieqi_after == 0: # birth_jd is before the first 'jie' in the list
                     raise ValueError(f"逆排：未能找到出生时间 {birth_time_obj.toStr()} 之前的有效节令（可能日期过早或数据不全）。")
                if idx_birth_jieqi_after == -1: # birth_jd is after all 'jie' in the list, so take the last one
                    target_jieqi_obj = filtered_jieqi[-1]
                else: # birth_jd is between filtered_jieqi[idx_birth_jieqi_after-1] and filtered_jieqi[idx_birth_jieqi_after]
                    target_jieqi_obj = filtered_jieqi[idx_birth_jieqi_after - 1]

            target_jieqi_jd = target_jieqi_obj.jd
            target_jieqi_time_obj = sxtwl.JD2DD(target_jieqi_jd) 

            # 6. 计算从出生到第二步大运开始时的精确天数和岁数
            day_difference_float = abs(target_jieqi_jd - birth_jd)
            day_difference_round_int = int(round(day_difference_float)) 

            # 计算第二步大运开始时的精确虚岁 (X.Y格式，用于起运信息)
            second_dayun_start_age_float = day_difference_float / 3
            second_dayun_start_age_decimal_display = round(second_dayun_start_age_float, 1)

            # 确定大运表格中显示的第二个十年期大运的起运年龄 (虚岁)
            # 如果计算出的精确年龄（X.Y）非常小（例如小于1），则第一个实际起运的大运通常显示为1岁起运。
            # 否则，从计算出的精确年龄向上取整作为起运年龄。
            start_age_for_second_decade_display = int(math.ceil(second_dayun_start_age_float))
            if start_age_for_second_decade_display == 0 and second_dayun_start_age_float == 0.0:
                start_age_for_second_decade_display = 1 # Edge case: if literally 0.0, it means it started at 1
            elif start_age_for_second_decade_display == 0 and second_dayun_start_age_float > 0.0: # like 0.1 to 0.999...
                start_age_for_second_decade_display = 1


            # 7. 排列大运
            dayun_list = []
            current_dayun_gz = month_gz 
            
            # 第一个大运的起运虚岁总是显示为1岁
            first_dayun_display_start_age = 1 

            # 生成第一步大运的信息
            first_dayun_pillar_str = self._gz_to_str(current_dayun_gz)
            # 第一步大运的年龄区间是 1岁 到 (第二步大运起始年龄 - 1)岁
            first_dayun_age_range_str = f"{first_dayun_display_start_age}~{max(first_dayun_display_start_age, start_age_for_second_decade_display - 1)}岁"
            
            dayun_list.append({
                "大运柱": first_dayun_pillar_str,
                "起运虚岁": first_dayun_display_start_age, 
                "年龄区间": first_dayun_age_range_str
            })

            # 准备下一个大运的干支（用于后续的10年大运）
            if direction_sign == 1: # 顺排
                current_dayun_gz = self._get_next_gz(current_dayun_gz)
            else: # 逆排
                current_dayun_gz = self._get_prev_gz(current_dayun_gz)
            
            # 从第二步大运开始，年龄按照 10年递增
            current_start_age_for_loop = start_age_for_second_decade_display 

            # 循环生成后续9步大运 (总共10步，第一步已处理)
            for i in range(9): 
                pillar_str = self._gz_to_str(current_dayun_gz)
                age_range_str = f"{current_start_age_for_loop}岁至{current_start_age_for_loop + 9}岁"
                
                dayun_list.append({
                    "大运柱": pillar_str,
                    "起运虚岁": current_start_age_for_loop, 
                    "年龄区间": age_range_str
                })

                # 准备下一个大运
                if direction_sign == 1: # 顺排
                    current_dayun_gz = self._get_next_gz(current_dayun_gz)
                else: # 逆排
                    current_dayun_gz = self._get_prev_gz(current_dayun_gz)
                
                current_start_age_for_loop += 10 # 每个大运管十年

            # This age_info is for internal calculation/return, the one from app.py takes precedence in prompt
            age = datetime.datetime.now().year - year
            age_info_internal = f"{age}岁" if age >=0 and age <= 90 else "暂无"

            return {
                "出生日期": f"{year}年{month}月{day}日 {hour:02d}:{minute:02d}:{second:02d} ({'男' if sex == '男' else '女'})",
                "年龄": age_info_internal, 
                "八字四柱": bazi_pillars,
                "起运信息": {
                    "排运方向": start_direction,
                    "从出生到第二步大运开始的精确天数": day_difference_round_int, 
                    "第二步大运开始的起运日期和精确虚岁": 
                        f"{int(target_jieqi_time_obj.Y)}年{int(target_jieqi_time_obj.M)}月{int(target_jieqi_time_obj.D)}日 {int(target_jieqi_time_obj.h):02d}:{int(target_jieqi_time_obj.m):02d}:{int(round(target_jieqi_time_obj.s)):02d} ({second_dayun_start_age_decimal_display:.1f}) 起运",
                    "第二步大运的起始虚岁 (表格顶部显示)": start_age_for_second_decade_display, 
                    "第二步大运开始的节气名称": self.jqmc[target_jieqi_obj.jqIndex],
                },
                "大运": dayun_list
            }

        except Exception as e:
            print(f"计算出错：{e}")
            return None

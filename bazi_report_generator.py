# bazi_report_generator.py

<<<<<<< HEAD
import httpx # Using httpx for HTTP requests, you can use 'requests' as well
import json
from typing import Dict

# You might have a more sophisticated Bazi calculation utility.
# For now, calculate_simple_bazi is a placeholder.
# If you have a real Bazi library (like sxtwlpy or a custom one), integrate it here.
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# Simplified Bazi calculation - placeholder, replace with accurate logic
def get_gan_zhi(year, val_offset_gan, val_offset_zhi):
    # This is an extremely naive placeholder and not astrologically correct.
    # Replace with a proper Bazi calculation library or algorithm.
    gan_idx = (year - val_offset_gan) % 10
    zhi_idx = (year - val_offset_zhi) % 12
    return f"{TIAN_GAN[gan_idx]}{DI_ZHI[zhi_idx]}"

class DeepSeekBaziReport:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1" # Official API endpoint

    def _call_deepseek_api(self, prompt: str, model: str = "deepseek-chat", temperature: float = 0.7) -> str:
=======
import requests
import json
from datetime import datetime
import sxtwl

class DeepSeekBaziReport:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 八字基础数据（用于本地计算）
        self.Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

        # 五行映射 (这些映射信息可以保留，因为AI可能需要它们进行分析，即使我们不本地计算)
        self.gan_elements = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"
        }
        self.zhi_elements = {
            "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土",
            "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金",
            "戌": "土", "亥": "水"
        }
        self.zhi_hidden_stems = {
            "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
            "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
            "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
            "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]
        }


    def calculate_simple_bazi(self, year, month, day, hour):
        """
        根据公历日期和时辰计算四柱八字。
        Args:
            year (int): 公历年份
            month (int): 公历月份
            day (int): 公历日期
            hour (int): 公历小时 (0-23)，用于计算时柱
        Returns:
            dict: 包含四柱干支的字典
        """
        try:
            day_obj = sxtwl.fromSolar(year, month, day) 

            yTG = day_obj.getYearGZ()
            mTG = day_obj.getMonthGZ()
            dTG = day_obj.getDayGZ()
            sTG = day_obj.getHourGZ(hour)
            
            bazi_info = {
                "year_gz": self.Gan[yTG.tg] + self.Zhi[yTG.dz],
                "month_gz": self.Gan[mTG.tg] + self.Zhi[mTG.dz],
                "day_gz": self.Gan[dTG.tg] + self.Zhi[dTG.dz],
                "hour_gz": self.Gan[sTG.tg] + self.Zhi[sTG.dz]
            }
            return bazi_info
        except Exception as e:
            raise ValueError(f"八字计算失败，请检查日期和时间输入: {e}")

    # 移除了 calculate_five_element_balance 方法，因为不再用于前端绘图。

    def call_deepseek_api(self, prompt, max_tokens=5000, model="deepseek-chat"):
        """调用 DeepSeek API 生成内容"""
>>>>>>> 936059c1e5039781dfa58c2493bc95dd7ca44050
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
<<<<<<< HEAD
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一位精通中华传统八字命理学的资深专家。在生成报告时，请始终采用娓娓道来的叙述风格，确保语言流畅自然，富有亲和力。对于每一个分析要点，都请用3到5句完整且连贯的句子组成一个小段落进行深入浅出的阐释，让不了解八字的用户也能轻松理解。请使用Markdown格式化输出，保持报告的专业性和结构清晰。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 4000, # Adjust as needed
        }
        try:
            with httpx.Client(timeout=180.0) as client: # Increased timeout
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
                response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                # Remove potential ```markdown ... ``` wrappers if LLM adds them
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

    def calculate_simple_bazi(self, year: int, month: int, day: int, hour: int) -> Dict[str, str]:
        # Placeholder: Replace with a robust Bazi calculation library (e.g., sxtwl, lunisolar)
        try:
            year_gz = get_gan_zhi(year, 4, 4) 
            month_gz = get_gan_zhi(month, 1, 1) 
            day_gz = get_gan_zhi(day, 1, 1) 
            hour_gz = get_gan_zhi(hour // 2, 1, 1) 

            return {
                "year_gz": year_gz,
                "month_gz": month_gz,
                "day_gz": day_gz,
                "hour_gz": hour_gz
            }
        except Exception as e:
            print(f"Error in placeholder Bazi calculation: {e}")
            return {
                "year_gz": "甲子", "month_gz": "丙寅",
                "day_gz": "丁卯", "hour_gz": "戊辰"
            }


    def generate_free_report(self, bazi_str: str, gender: str) -> str:
        prompt = f"""
            请根据以下八字信息和性别，生成一份简要的免费八字命理报告。报告内容应直接呈现，无需额外解释或标题。

            八字：{bazi_str}
            性别：{gender}

            报告应包含以下几点，每点用1-2句话概括：
            1.  **日主特性**: 简述日主（日干）的基本属性和特点。
            2.  **性格概要**: 根据八字组合，概括主要的性格特征。
            3.  **运势提醒**: 给出一条近期的或笼统的运势提醒。

            请直接输出这份包含三点的简要报告。
            """
        return self._call_deepseek_api(prompt, temperature=0.5)

    def generate_bazi_analysis_module(self, bazi_str: str, gender: str) -> str:
        prompt = f"""
            ### 八字排盘与五行分析

            针对八字：{bazi_str}，性别：{gender}。
            
            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格。对于以下列出的每一个主要分析点（如“1. 四柱干支”、“2. 五行力量分析”等）及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂、富有亲和力。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出，包括标题和必要的强调。

            请详细分析以下内容：

            1.  **四柱干支解读**：
                *   年柱: [请在此处填写实际年柱干支]，并用3-5句完整连贯的话，阐述其在整个命盘中的基础意义，例如它通常代表着命主的祖上根基、早年运程（通常指16岁前）以及时代大环境所赋予的初始印记等。
                *   月柱: [请在此处填写实际月柱干支]，并用3-5句完整连贯的话，阐述其关键作用，例如它深刻影响着命主的家庭环境、父母兄弟姐妹的关系、青少年时期的成长经历（通常指16-32岁），同时也是观察个人性格形成和事业发展潜力的重要窗口。
                *   日柱: [请在此处填写实际日柱干支] (其中日干是：[日干])，并用3-5句完整连贯的话，详细说明此日干作为命主（也称日元或自身）的核心特质、本性以及内在驱动力，同时日支（也称夫妻宫）也揭示了命主中年运势（通常指32-48岁）、婚姻观念及与伴侣互动模式的初步信息。
                *   时柱: [请在此处填写实际时柱干支]，并用3-5句完整连贯的话，阐述其所代表的晚年生活景象（通常指48岁后）、子女情况、个人深层追求、事业的最终成就或人生归宿等。

            2.  **五行力量透析**：
                *   请用3-5句完整连贯的话，详细说明此八字命局中金、木、水、火、土这五种元素各自的旺衰程度（例如，哪个五行力量最强，哪个相对较弱，是否有某个五行缺失）。
                *   接着，请用3-5句完整连贯的话，深入分析这些五行之间存在的相生（如木生火、火生土）与相克（如金克木、水克火）关系，是如何具体地影响整个命局的平衡状态与核心特质的，这些互动又怎样塑造了命主的整体运势走向。

            3.  **十神关系详察**：
                *   请首先列出此八字四柱地支中所藏匿的天干（包括本气、中气、余气），并根据日主（日干），清晰标示出命盘天干上透出的主要十神（如正官、偏财、食神、比肩等）以及地支藏干在特定条件下可能引化出的十神。
                *   然后，请用3-5句完整连贯的话，挑选其中一至两个对命局影响最为显著的十神，阐述它们各自代表的人事物象（例如，正官可能代表上司、约束力或事业，食神可能代表才华、口福或晚辈），以及它们的存在如何影响命主的性格特点和人生际遇。

            4.  **喜用神初步研判**：
                *   请用3-5句完整连贯的话，综合考量日主的强弱旺衰（是身强还是身弱）以及命局中五行的整体平衡流通情况，初步判断出此命局最需要或最喜爱的五行（即喜用神）是什么。
                *   随后，请用3-5句完整连贯的话，简要阐述您做出此判断的主要依据和命理逻辑，例如，如果日主过强，可能需要克制或泄耗的五行为喜用，反之亦然。

            请以专业严谨但通俗易懂的方式展开内容，确保逻辑清晰、分析深入，让零基础读者也能轻松理解。
            """
        return self._call_deepseek_api(prompt)

    def generate_mingge_decode_module(self, bazi_str: str, gender: str) -> str:
        prompt = f"""
            ### 命格解码与人生特质
            
            针对八字：{bazi_str}，性别：{gender}。

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂、富有亲和力。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请详细分析以下内容：
            
            1.  **格局初步判断与解读**：
                *   请用3-5句完整连贯的话，尝试判断此八字可能属于的主要格局类型（例如扶抑格中的身旺/身弱、从格中的从强/从弱、专旺格、化气格等）。如果格局不够典型或者呈现多种可能性，也请如实指出，并说明判断的主要依据是什么。
                *   接着，请用3-5句完整连贯的话，阐释此（或此类）格局的基本含义，以及这种格局通常会对命主的人生层次、行事风格以及成就高低带来哪些方面的主要影响。

            2.  **性格特质深度描绘**：
                *   请用3-5句完整连贯的话，融合对日主强弱、十神组合特点以及五行旺衰情况的综合分析，生动地描绘出命主在性格上可能展现的主要优点，例如积极进取、温和善良或是富有创造力等。
                *   同样，请用3-5句完整连贯的话，客观地指出命主性格中可能存在的、需要留意的方面或潜在的缺点，例如可能比较固执、容易冲动或是内心较为敏感等。
                *   再用3-5句完整连贯的话，分析并阐述命主基于其命格特质，可能拥有的独特天赋、潜在才能或特别擅长的领域，例如可能在艺术、技术、管理或沟通方面有过人之处。
                *   最后，请用3-5句完整连贯的话，具体描述命主在日常生活中，为人处世可能展现出的主要行为模式和与人交往的鲜明特点。

            3.  **人生主要优势与潜在挑战**：
                *   请用3-5句完整连贯的话，依据命局的整体组合与力量分布，分析命主在一生中可能更容易把握或拥有的主要优势和发展机遇，例如可能容易获得贵人相助、或者在某个特定领域更容易取得成功。
                *   同时，请用3-5句完整连贯的话，指出命主在人生旅途中可能需要面对和克服的主要挑战、困扰或人生课题，例如可能在人际关系、健康或是某个时期的财运方面需要特别注意。

            4.  **核心价值观与人生追求洞察**：
                *   请用3-5句完整连贯的话，基于命局所反映出的深层信息，尝试推断并阐述命主在内心深处可能秉持的核心价值观是什么，例如是更看重成就感、家庭和谐、精神自由还是物质保障。
                *   接着，请用3-5句完整连贯的话，进一步分析命主在人生中可能会努力追求的主要目标和生活理想是什么样的。

            5. **本模块核心内容总结**:
                *   请用3-5句完整连贯的话，对本模块（命格解码与人生特质）分析的关键内容和核心洞见进行一个简明扼要的总结，帮助读者回顾和把握重点。
            
            请确保分析深刻、富有洞察力，且行文流畅易懂。
            """
        return self._call_deepseek_api(prompt)

    def generate_career_love_module(self, bazi_str: str, gender: str) -> str:
        prompt = f"""
            ### 事业财富与婚恋分析
            
            针对八字：{bazi_str}，性别：{gender}。

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂、富有亲和力。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请分别详细分析事业财富和婚恋情感：
            
            **一、事业财富运程解析**
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

            **二、婚恋情感运程探索**
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
        return self._call_deepseek_api(prompt)

    def generate_health_advice_module(self, bazi_str: str, gender: str) -> str:
        prompt = f"""
            ### 五行健康与养生建议
            
            针对八字：{bazi_str}，性别：{gender}。

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂、富有亲和力。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。
            
            请详细分析以下内容：
            
            1.  **五行对应脏腑健康状态分析**：
                *   请用3-5句完整连贯的话，根据此八字中金、木、水、火、土五行的强弱分布、以及它们之间的生克制化关系，初步分析与各五行相对应的主要脏腑（例如金对应肺与大肠，木对应肝与胆，水对应肾与膀胱，火对应心与小肠，土对应脾与胃）潜在的健康状况或能量水平。
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
        return self._call_deepseek_api(prompt)

    def generate_fortune_flow_module(self, bazi_str: str, gender: str) -> str:
        prompt = f"""
            ### 大运流年运势推演 (简要趋势)

            针对八字：{bazi_str}，性别：{gender}。

            **重要提示：** 请您在撰写此模块时，采用娓娓道来的叙述风格。对于以下列出的每一个主要分析点及其内部的子项（若有），请不要只是简单罗列信息。而是针对每一项，都用3到5句完整且连贯的句子组成一个流畅的小段落来进行深入浅出的阐释。您的目标是让即使不熟悉八字命理的读者也能轻松理解各项分析的含义、逻辑及其对命主的影响。请保持专业的分析深度，同时确保语言通俗易懂、富有亲和力。请直接以这样的叙述方式填充各个要点，并使用Markdown格式化您的输出。

            请进行简要的未来运势趋势分析：

            1.  **大运起排规则与起运岁数说明**：
                *   请用3-5句完整连贯的话，简要说明大运是如何根据出生月柱和性别（阳男阴女顺行，阴男阳女逆行）来起排的，以及每一步大运通常主管十年的运程。
                *   如果可能（通常需要精确的节气信息，若无法精确计算，可说明是大致推断），请用3-5句完整连贯的话，指出命主大约从几岁开始进入第一步大运，并解释这个起运岁数是如何影响人生阶段划分的。

            2.  **未来1-2步大运趋势简析 (每步大运10年)**：
                *   对于命主即将进入或正在经历的第一步（或下一两步）大运，请列出其天干地支。然后，请用3-5句完整连贯的话，分析这组干支是如何与原命局发生作用的，例如它会增强或削弱原局中的哪些五行力量，或者引动哪些十神。
                *   接着，请用3-5句完整连贯的话，进一步阐述在这一步大运的十年期间，命主在事业发展、财富积累、感情生活、身体健康等主要人生方面，可能会经历怎样的总体吉凶趋势、生活重心变化或重要的发展机遇与挑战。 （若分析两步大运，请分别阐述）

            3.  **未来3-5年流年运势关注点提示**：
                *   请列出未来3到5年的流年干支。对于其中每一个流年，请用3-5句完整连贯的话，结合当前所处的大运环境，指出该年有哪些方面是命主需要特别关注的，例如，某一年可能特别有利于学业进步或事业拓展，某一年则需多加注意人际关系调和或财务管理，又或者某一年健康方面容易出现一些小状况等。请尽量给出具体的生活领域提示。

            4.  **人生运程趋吉避凶总括性建议**：
                *   请用3-5句完整连贯的话，基于对命局特点以及未来大运流年基本趋势的综合判断，为命主提供一些在人生不同运程起伏阶段，如何更好地把握发展机遇、规避潜在风险、以及调适心态的总体性指导原则或智慧锦囊。

            **声明**: 此处提供的分析是基于八字命理理论对未来运势所做的简要趋势性推演，主要用于提供一个宏观的参考框架。具体到每一年甚至每一月的详细运势，会受到更多细微因素的影响，且个人的主观努力和选择亦至关重要。因此，本内容仅供参考，不宜作为重大决策的唯一依据。
            """
        return self._call_deepseek_api(prompt)
=======
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=90) # 增加超时设置
            response.raise_for_status() # 检查HTTP请求是否成功
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception(f"API调用失败: 无效的API密钥或权限不足。请检查您的DeepSeek API密钥。")
            elif response.status_code == 400:
                 raise Exception(f"API调用失败: 请求参数参数错误。详细信息: {response.text}")
            elif response.status_code == 429:
                 raise Exception(f"API调用失败: 请求频率过高或超出配额。请稍后重试或检查您的DeepSeek账户。")
            else:
                raise Exception(f"API调用失败: HTTP错误 {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"API调用失败: 无法连接到DeepSeek API服务器。请检查您的网络连接。{e}")
        except requests.exceptions.Timeout:
            raise Exception("API调用超时。DeepSeek API响应时间过长。")
        except json.JSONDecodeError:
            raise Exception(f"API返回的不是有效的JSON格式: {response.text}")
        except KeyError:
            raise Exception(f"API返回的JSON结构不符合预期，可能没有'choices'或'message'字段。原始响应: {response.json()}")
        except Exception as e:
            raise Exception(f"调用DeepSeek API时发生未知错误: {e}")

    def generate_free_report(self, bazi_str, gender='男'):
        """生成免费版报告，仅接受八字字符串"""
        
        prompt = f"""
        请根据以下八字信息生成一份简明分析报告：
        八字：{gender}命:{bazi_str}

        要求：
        1. 八字排盘（显示天干地支）
        2. 五行分布（以文本形式描述金、木、水、火、土的占比和旺衰）
        3. 性格特点（简要分析）
        4. 命主五个好的预兆
        5. 命主两个不好的预兆
        6. 1-2条实用建议（如幸运颜色、数字等）
        
        语言通俗易懂，300字以内，保持中立客观。
        
        ---
        重要：请直接输出报告内容。严格使用标准的Markdown语法进行格式化，例如使用标题（#）、列表（- 或 *）、粗体（**）等。**请不要将整个报告内容包裹在任何代码块中 (即不要在报告开头和结尾使用三个反引号 \`\`\`)。** 报告中若无代码示例，则无需使用反引号。
        """
        return self.call_deepseek_api(prompt, max_tokens=700)

    def generate_premium_report(self, bazi_str, gender='男'):
        """生成付费版报告，仅接受八字字符串"""
        
        prompt = f"""
        你是一位拥有20年实战经验的命理学家，请基于「{gender}命:{bazi_str}」生成一份专业且易懂的八字命理报告。
        
        ▌报告要求
        1. 仅使用八字推导，严禁反推公历日期
        2. 总字数1800-2500字，分章节排版
        3. 所有结论需注明推导逻辑（如："因日主甲木生申月失令，故..."）
        4. 专业术语首现时附带白话解释（例：正官=约束力强的能量）
        
        ▌报告结构
        【核心排盘】 
        • 八字展示：{gender}命:{bazi_str}（含四柱干支、藏干、十神、纳音）
        • 五行旺衰分析：请描述金、木、水、火、土的旺衰状态和相互关系，以及对命局的影响。
        • 地支藏干分析：请以列表或表格形式描述地支所藏天干及其对命局的影响。
        
        【命局解码】
        ★ 格局评定：
        - 判定标准：需分析并说明命主格局
        - 富贵层次：分先天命局潜力（1-10分）+后天兑现条件
        - 关键矛盾：突出命局最大冲突点（如财坏印/官杀混杂）
        
        ★ 人生特质：
        - 性格三维度：①主星特质 ②五行显性 ③地支暗藏特质
        - 能力分析：描述政务/商业/技艺/学术/艺术等方面的潜力和倾向。
        - 思维模式：决策风格（理性/直觉）与风险偏好
        
        【专项预测】
        🔮 事业轨迹：
        - 黄金领域：根据用神+十神组合推荐3个适配行业
        - 财富周期：每十年财运曲线（需结合大运走势）
        - 风险预警：35/42/55岁等关键年龄节点提醒
        
        💞 婚恋指南：
        - 配偶三维画像：①十神特征 ②五行补益 ③地支合冲
        - 婚运时间窗：红鸾/天喜星动年份+流年触发条件
        - 相处禁忌：需避免的生肖/日柱组合
        
        【动态运势】
        📈 大运推演：
        - 当前大运：起止时间+干支（例：2020-2030 癸卯）
        - 未来十年：每两年为一个分析单元，标注吉神凶煞
        - 关键转折：换运前一年需特别注意事项
        
        ✨ 2025乙巳年：
        - 流年卦象：年柱与八字互动关系（刑冲破害合）
        - 月度指南：农历1/4/7/10月重点事项提醒
        - 太岁锦囊：建议佩戴/避开的五行元素
        
        ▌输出规范
        1. 每章节以🔍【学术依据】收尾，简析推导逻辑
        2. 关键结论前加⚠️（风险项）或✅（机遇项）标识
        3. 改运建议需包含：职业/方位/颜色/饰品/社交五类
        4. 文末统一标注："以上内容需结合现实情况灵活调整"
        
        请采用学者论文式的严谨表述，同时保持风水师接地气的建议风格。
        ---
        
        """
        # 重要：请直接输出报告内容。严格使用标准的Markdown语法进行格式化，特别是章节标题、列表、粗体等。**请不要将整个报告内容包裹在任何代码块中 (即不要在报告开头和结尾使用三个反引号 \`\`\`)。** 报告中若无代码示例，则无需使用反引号。
        return self.call_deepseek_api(prompt, max_tokens=5000, model="deepseek-chat")
>>>>>>> 936059c1e5039781dfa58c2493bc95dd7ca44050

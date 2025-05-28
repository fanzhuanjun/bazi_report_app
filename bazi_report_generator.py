# bazi_report_generator.py

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
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
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
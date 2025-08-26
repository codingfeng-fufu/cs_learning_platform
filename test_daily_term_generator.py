#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日名词生成器测试脚本
用于测试和优化每日名词系统的生成质量

使用方法:
python test_daily_term_generator.py
"""

import os
import sys
import json
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

# 配置
OPENAI_API_KEY = "your-openai-api-key-here"  # 请替换为你的API密钥
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# 计算机科学领域分类
CS_DOMAINS = {
    "algorithms": {
        "name": "算法与数据结构",
        "keywords": ["算法", "数据结构", "排序", "搜索", "图论", "动态规划", "贪心", "分治"],
        "difficulty_levels": ["入门", "中级", "高级"]
    },
    "programming": {
        "name": "编程语言",
        "keywords": ["Python", "Java", "C++", "JavaScript", "Go", "Rust", "编程范式", "语法"],
        "difficulty_levels": ["基础", "进阶", "专家"]
    },
    "systems": {
        "name": "系统与架构",
        "keywords": ["操作系统", "分布式系统", "微服务", "容器", "云计算", "架构设计"],
        "difficulty_levels": ["基础", "中级", "高级"]
    },
    "networks": {
        "name": "网络与安全",
        "keywords": ["网络协议", "网络安全", "加密", "防火墙", "VPN", "TCP/IP"],
        "difficulty_levels": ["基础", "中级", "高级"]
    },
    "databases": {
        "name": "数据库",
        "keywords": ["SQL", "NoSQL", "数据库设计", "索引", "事务", "分布式数据库"],
        "difficulty_levels": ["基础", "中级", "高级"]
    },
    "ai_ml": {
        "name": "人工智能与机器学习",
        "keywords": ["机器学习", "深度学习", "神经网络", "自然语言处理", "计算机视觉"],
        "difficulty_levels": ["入门", "中级", "高级"]
    },
    "web": {
        "name": "Web开发",
        "keywords": ["前端", "后端", "框架", "API", "响应式设计", "性能优化"],
        "difficulty_levels": ["基础", "中级", "高级"]
    },
    "mobile": {
        "name": "移动开发",
        "keywords": ["Android", "iOS", "React Native", "Flutter", "移动应用", "跨平台"],
        "difficulty_levels": ["基础", "中级", "高级"]
    }
}

class DailyTermGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def generate_term_prompt(self, domain: str, difficulty: str, date: str) -> str:
        """生成用于AI的提示词"""
        domain_info = CS_DOMAINS.get(domain, CS_DOMAINS["algorithms"])
        
        prompt = f"""
作为计算机科学教育专家，请为{date}生成一个{domain_info['name']}领域的每日名词。

要求：
1. 难度级别：{difficulty}
2. 领域：{domain_info['name']}
3. 相关关键词：{', '.join(domain_info['keywords'])}

请生成一个JSON格式的响应，包含以下字段：
{{
    "term": "专业术语名称（中文）",
    "english_term": "英文术语",
    "category": "{domain_info['name']}",
    "difficulty": "{difficulty}",
    "definition": "简洁准确的定义（100-150字）",
    "detailed_explanation": "详细解释，包含原理、用途、特点（300-500字）",
    "examples": [
        "实际应用例子1",
        "实际应用例子2",
        "实际应用例子3"
    ],
    "related_terms": [
        "相关术语1",
        "相关术语2", 
        "相关术语3"
    ],
    "learning_tips": "学习建议和记忆技巧（100-200字）",
    "practical_application": "实际应用场景描述（150-250字）",
    "common_misconceptions": "常见误解或注意事项（100-150字）",
    "further_reading": [
        "推荐资源1",
        "推荐资源2"
    ]
}}

注意事项：
- 术语应该具有教育价值和实用性
- 解释要准确、易懂，适合学习者理解
- 例子要具体、贴近实际应用
- 避免过于基础或过于冷门的术语
- 确保内容的准确性和时效性
"""
        return prompt
    
    def call_openai_api(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """调用OpenAI API"""
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的计算机科学教育专家，擅长解释复杂的技术概念。"
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                
                response = requests.post(
                    OPENAI_API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 尝试解析JSON
                    try:
                        # 清理可能的markdown格式
                        if content.startswith('```json'):
                            content = content.replace('```json', '').replace('```', '')
                        elif content.startswith('```'):
                            content = content.replace('```', '')
                        
                        return json.loads(content.strip())
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误 (尝试 {attempt + 1}): {e}")
                        print(f"原始内容: {content[:200]}...")
                        if attempt == max_retries - 1:
                            return None
                        continue
                        
                else:
                    print(f"API请求失败 (尝试 {attempt + 1}): {response.status_code}")
                    print(f"错误信息: {response.text}")
                    
            except Exception as e:
                print(f"请求异常 (尝试 {attempt + 1}): {e}")
                
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                
        return None
    
    def generate_daily_term(self, domain: str = None, difficulty: str = None) -> Optional[Dict]:
        """生成每日名词"""
        # 随机选择领域和难度（如果未指定）
        if not domain:
            domain = random.choice(list(CS_DOMAINS.keys()))
        if not difficulty:
            domain_info = CS_DOMAINS[domain]
            difficulty = random.choice(domain_info["difficulty_levels"])
            
        date_str = datetime.now().strftime("%Y年%m月%d日")
        
        print(f"正在生成 {date_str} 的每日名词...")
        print(f"领域: {CS_DOMAINS[domain]['name']}")
        print(f"难度: {difficulty}")
        print("-" * 50)
        
        prompt = self.generate_term_prompt(domain, difficulty, date_str)
        result = self.call_openai_api(prompt)
        
        if result:
            # 添加生成时间戳
            result['generated_at'] = datetime.now().isoformat()
            result['domain_key'] = domain
            
        return result
    
    def validate_term_quality(self, term_data: Dict) -> Tuple[bool, List[str]]:
        """验证生成的术语质量"""
        issues = []
        
        # 检查必需字段
        required_fields = [
            'term', 'english_term', 'category', 'difficulty',
            'definition', 'detailed_explanation', 'examples',
            'related_terms', 'learning_tips', 'practical_application'
        ]
        
        for field in required_fields:
            if field not in term_data or not term_data[field]:
                issues.append(f"缺少必需字段: {field}")
        
        # 检查内容长度
        if 'definition' in term_data:
            def_len = len(term_data['definition'])
            if def_len < 50:
                issues.append(f"定义过短: {def_len}字符")
            elif def_len > 300:
                issues.append(f"定义过长: {def_len}字符")
        
        if 'detailed_explanation' in term_data:
            exp_len = len(term_data['detailed_explanation'])
            if exp_len < 200:
                issues.append(f"详细解释过短: {exp_len}字符")
            elif exp_len > 800:
                issues.append(f"详细解释过长: {exp_len}字符")
        
        # 检查例子数量
        if 'examples' in term_data:
            if len(term_data['examples']) < 2:
                issues.append("例子数量不足")
            elif len(term_data['examples']) > 5:
                issues.append("例子数量过多")
        
        # 检查相关术语
        if 'related_terms' in term_data:
            if len(term_data['related_terms']) < 2:
                issues.append("相关术语数量不足")
        
        return len(issues) == 0, issues
    
    def batch_generate_terms(self, count: int = 5) -> List[Dict]:
        """批量生成术语用于测试"""
        results = []
        
        for i in range(count):
            print(f"\n=== 生成第 {i+1}/{count} 个术语 ===")
            
            # 随机选择不同的领域和难度
            domain = random.choice(list(CS_DOMAINS.keys()))
            domain_info = CS_DOMAINS[domain]
            difficulty = random.choice(domain_info["difficulty_levels"])
            
            term = self.generate_daily_term(domain, difficulty)
            
            if term:
                is_valid, issues = self.validate_term_quality(term)
                term['validation'] = {
                    'is_valid': is_valid,
                    'issues': issues
                }
                results.append(term)
                
                print(f"✅ 成功生成: {term.get('term', 'Unknown')}")
                if not is_valid:
                    print(f"⚠️  质量问题: {', '.join(issues)}")
            else:
                print("❌ 生成失败")
            
            # 避免API限制
            if i < count - 1:
                time.sleep(1)
        
        return results
    
    def save_results(self, results: List[Dict], filename: str = None):
        """保存结果到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"daily_terms_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 结果已保存到: {filename}")
        return filename

def print_term_summary(term: Dict):
    """打印术语摘要"""
    print(f"\n📚 术语: {term.get('term', 'N/A')}")
    print(f"🔤 英文: {term.get('english_term', 'N/A')}")
    print(f"📂 分类: {term.get('category', 'N/A')}")
    print(f"⭐ 难度: {term.get('difficulty', 'N/A')}")
    print(f"📝 定义: {term.get('definition', 'N/A')[:100]}...")
    
    if 'validation' in term:
        validation = term['validation']
        status = "✅ 通过" if validation['is_valid'] else "❌ 有问题"
        print(f"🔍 验证: {status}")
        if validation['issues']:
            print(f"⚠️  问题: {', '.join(validation['issues'])}")

def main():
    """主函数"""
    print("🚀 每日名词生成器测试脚本")
    print("=" * 50)
    
    # 检查API密钥
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("❌ 请先设置你的OpenAI API密钥")
        print("在脚本顶部修改 OPENAI_API_KEY 变量")
        return
    
    generator = DailyTermGenerator(OPENAI_API_KEY)
    
    while True:
        print("\n📋 选择操作:")
        print("1. 生成单个术语")
        print("2. 批量生成术语 (测试质量)")
        print("3. 指定领域生成")
        print("4. 查看领域列表")
        print("5. 退出")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            term = generator.generate_daily_term()
            if term:
                print_term_summary(term)
                
                save = input("\n💾 是否保存结果? (y/n): ").strip().lower()
                if save == 'y':
                    generator.save_results([term])
            
        elif choice == "2":
            count = input("生成数量 (默认5): ").strip()
            count = int(count) if count.isdigit() else 5
            
            results = generator.batch_generate_terms(count)
            
            print(f"\n📊 批量生成完成，共 {len(results)} 个术语")
            
            # 统计质量
            valid_count = sum(1 for r in results if r.get('validation', {}).get('is_valid', False))
            print(f"✅ 质量合格: {valid_count}/{len(results)}")
            
            # 显示摘要
            for i, term in enumerate(results, 1):
                print(f"\n--- 术语 {i} ---")
                print_term_summary(term)
            
            generator.save_results(results)
            
        elif choice == "3":
            print("\n📂 可用领域:")
            for key, info in CS_DOMAINS.items():
                print(f"{key}: {info['name']}")
            
            domain = input("\n请输入领域键名: ").strip()
            if domain in CS_DOMAINS:
                difficulty = input(f"请输入难度 {CS_DOMAINS[domain]['difficulty_levels']}: ").strip()
                if not difficulty:
                    difficulty = None
                
                term = generator.generate_daily_term(domain, difficulty)
                if term:
                    print_term_summary(term)
            else:
                print("❌ 无效的领域")
                
        elif choice == "4":
            print("\n📂 计算机科学领域列表:")
            for key, info in CS_DOMAINS.items():
                print(f"\n🔹 {key}: {info['name']}")
                print(f"   关键词: {', '.join(info['keywords'][:3])}...")
                print(f"   难度级别: {', '.join(info['difficulty_levels'])}")
                
        elif choice == "5":
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()

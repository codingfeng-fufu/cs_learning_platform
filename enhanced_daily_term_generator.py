#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版每日名词生成器
包含质量评估、批量生成、统计分析等高级功能

使用方法:
python enhanced_daily_term_generator.py
"""

import os
import sys
import json
import random
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
import time
import statistics
from pathlib import Path

# 导入配置
try:
    from config import *
except ImportError:
    print("❌ 找不到config.py文件，请确保配置文件存在")
    sys.exit(1)

class QualityAnalyzer:
    """质量分析器"""
    
    def __init__(self):
        self.quality_metrics = {
            'content_length': 0,
            'keyword_coverage': 0,
            'readability': 0,
            'completeness': 0,
            'accuracy': 0
        }
    
    def analyze_term(self, term_data: Dict) -> Dict[str, Any]:
        """分析术语质量"""
        analysis = {
            'overall_score': 0,
            'metrics': {},
            'issues': [],
            'suggestions': []
        }
        
        # 内容长度分析
        analysis['metrics']['content_length'] = self._analyze_content_length(term_data)
        
        # 完整性分析
        analysis['metrics']['completeness'] = self._analyze_completeness(term_data)
        
        # 关键词覆盖分析
        analysis['metrics']['keyword_coverage'] = self._analyze_keyword_coverage(term_data)
        
        # 可读性分析
        analysis['metrics']['readability'] = self._analyze_readability(term_data)
        
        # 计算总分
        scores = list(analysis['metrics'].values())
        analysis['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        # 生成建议
        analysis['suggestions'] = self._generate_suggestions(analysis['metrics'])
        
        return analysis
    
    def _analyze_content_length(self, term_data: Dict) -> float:
        """分析内容长度是否合适"""
        score = 0
        total_checks = 0
        
        # 检查定义长度
        if 'definition' in term_data:
            def_len = len(term_data['definition'])
            if QUALITY_CONFIG['min_definition_length'] <= def_len <= QUALITY_CONFIG['max_definition_length']:
                score += 1
            total_checks += 1
        
        # 检查详细解释长度
        if 'detailed_explanation' in term_data:
            exp_len = len(term_data['detailed_explanation'])
            if QUALITY_CONFIG['min_explanation_length'] <= exp_len <= QUALITY_CONFIG['max_explanation_length']:
                score += 1
            total_checks += 1
        
        return score / total_checks if total_checks > 0 else 0
    
    def _analyze_completeness(self, term_data: Dict) -> float:
        """分析内容完整性"""
        required_fields = [
            'term', 'english_term', 'category', 'difficulty',
            'definition', 'detailed_explanation', 'examples',
            'related_terms', 'learning_tips', 'practical_application'
        ]
        
        present_fields = sum(1 for field in required_fields if field in term_data and term_data[field])
        return present_fields / len(required_fields)
    
    def _analyze_keyword_coverage(self, term_data: Dict) -> float:
        """分析关键词覆盖度"""
        if 'category' not in term_data:
            return 0
        
        # 找到对应的领域
        domain_key = None
        for key, domain in CS_DOMAINS.items():
            if domain['name'] == term_data['category']:
                domain_key = key
                break
        
        if not domain_key:
            return 0.5  # 默认分数
        
        keywords = CS_DOMAINS[domain_key]['keywords']
        content = ' '.join([
            term_data.get('definition', ''),
            term_data.get('detailed_explanation', ''),
            ' '.join(term_data.get('examples', [])),
            ' '.join(term_data.get('related_terms', []))
        ]).lower()
        
        matched_keywords = sum(1 for keyword in keywords if keyword.lower() in content)
        return min(matched_keywords / len(keywords) * 2, 1.0)  # 最高1.0分
    
    def _analyze_readability(self, term_data: Dict) -> float:
        """分析可读性（简化版）"""
        score = 0
        checks = 0
        
        # 检查定义是否简洁明了
        if 'definition' in term_data:
            definition = term_data['definition']
            # 简单的可读性检查：句子长度、标点符号等
            sentences = definition.split('。')
            avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
            
            if 10 <= avg_sentence_length <= 50:  # 合理的句子长度
                score += 1
            checks += 1
        
        # 检查是否有具体例子
        if 'examples' in term_data and len(term_data['examples']) >= 2:
            score += 1
        checks += 1
        
        return score / checks if checks > 0 else 0
    
    def _generate_suggestions(self, metrics: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if metrics.get('content_length', 0) < 0.8:
            suggestions.append("建议调整内容长度，确保定义简洁、解释详细")
        
        if metrics.get('completeness', 0) < 0.9:
            suggestions.append("建议补充缺失的字段，确保信息完整")
        
        if metrics.get('keyword_coverage', 0) < 0.3:
            suggestions.append("建议增加相关领域关键词的使用")
        
        if metrics.get('readability', 0) < 0.7:
            suggestions.append("建议改善可读性，使用更清晰的表达和具体例子")
        
        return suggestions

class EnhancedDailyTermGenerator:
    """增强版每日名词生成器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.quality_analyzer = QualityAnalyzer()
        self.generation_history = []
        
        # 设置日志
        self._setup_logging()
        
        # 创建输出目录
        self.output_dir = Path(OUTPUT_CONFIG['save_directory'])
        self.output_dir.mkdir(exist_ok=True)
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def select_domain_intelligently(self, exclude_recent: bool = True) -> Tuple[str, str]:
        """智能选择领域和难度"""
        # 根据权重选择领域
        domains = list(CS_DOMAINS.keys())
        weights = [CS_DOMAINS[d]['weight'] for d in domains]
        
        # 如果需要排除最近使用的领域
        if exclude_recent and len(self.generation_history) > 0:
            recent_domains = [h.get('domain_key') for h in self.generation_history[-3:]]
            for i, domain in enumerate(domains):
                if domain in recent_domains:
                    weights[i] *= 0.3  # 降低最近使用过的领域权重
        
        # 加权随机选择
        domain = random.choices(domains, weights=weights)[0]
        
        # 选择难度
        domain_info = CS_DOMAINS[domain]
        difficulty = random.choice(domain_info['difficulty_levels'])
        
        return domain, difficulty
    
    def generate_term_with_template(self, domain: str, difficulty: str, template: str = "standard") -> Optional[Dict]:
        """使用模板生成术语"""
        if template not in TERM_GENERATION_TEMPLATES:
            template = "standard"
        
        template_config = TERM_GENERATION_TEMPLATES[template]
        domain_info = CS_DOMAINS[domain]
        
        # 构建提示词
        date_str = datetime.now().strftime("%Y年%m月%d日")
        keywords = ', '.join(random.sample(domain_info['keywords'], min(5, len(domain_info['keywords']))))
        
        user_prompt = template_config['user_prompt_template'].format(
            date=date_str,
            category=domain_info['name'],
            difficulty=difficulty,
            keywords=keywords
        )
        
        return self._call_api_with_retry(template_config['system_prompt'], user_prompt)
    
    def _call_api_with_retry(self, system_prompt: str, user_prompt: str) -> Optional[Dict]:
        """带重试的API调用"""
        for attempt in range(API_CONFIG['max_retries']):
            try:
                payload = {
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": API_CONFIG['max_tokens'],
                    "temperature": API_CONFIG['temperature'],
                    "top_p": API_CONFIG['top_p']
                }
                
                response = requests.post(
                    OPENAI_API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=API_CONFIG['timeout']
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 解析JSON
                    try:
                        # 清理格式
                        content = content.strip()
                        if content.startswith('```json'):
                            content = content[7:]
                        if content.endswith('```'):
                            content = content[:-3]
                        content = content.strip()
                        
                        parsed_data = json.loads(content)
                        
                        # 添加元数据
                        parsed_data['generated_at'] = datetime.now().isoformat()
                        parsed_data['api_model'] = OPENAI_MODEL
                        parsed_data['generation_attempt'] = attempt + 1
                        
                        return parsed_data
                        
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"JSON解析失败 (尝试 {attempt + 1}): {e}")
                        if attempt == API_CONFIG['max_retries'] - 1:
                            self.logger.error(f"原始内容: {content[:300]}...")
                        continue
                        
                else:
                    self.logger.warning(f"API请求失败 (尝试 {attempt + 1}): {response.status_code}")
                    
            except Exception as e:
                self.logger.warning(f"请求异常 (尝试 {attempt + 1}): {e}")
                
            if attempt < API_CONFIG['max_retries'] - 1:
                time.sleep(API_CONFIG['retry_delay'] ** attempt)
                
        return None
    
    def generate_and_analyze(self, domain: str = None, difficulty: str = None, template: str = "standard") -> Optional[Dict]:
        """生成并分析术语"""
        # 智能选择领域和难度
        if not domain or not difficulty:
            domain, difficulty = self.select_domain_intelligently()
        
        self.logger.info(f"生成术语: 领域={CS_DOMAINS[domain]['name']}, 难度={difficulty}, 模板={template}")
        
        # 生成术语
        term_data = self.generate_term_with_template(domain, difficulty, template)
        
        if term_data:
            # 添加领域信息
            term_data['domain_key'] = domain
            
            # 质量分析
            quality_analysis = self.quality_analyzer.analyze_term(term_data)
            term_data['quality_analysis'] = quality_analysis
            
            # 记录到历史
            self.generation_history.append(term_data)
            
            self.logger.info(f"生成成功: {term_data.get('term', 'Unknown')} (质量分数: {quality_analysis['overall_score']:.2f})")
            
            return term_data
        else:
            self.logger.error("生成失败")
            return None
    
    def batch_generate_with_analysis(self, count: int = 10, min_quality: float = 0.7) -> List[Dict]:
        """批量生成并筛选高质量术语"""
        results = []
        attempts = 0
        max_attempts = count * 3  # 最多尝试3倍数量
        
        self.logger.info(f"开始批量生成 {count} 个术语，最低质量要求: {min_quality}")
        
        while len(results) < count and attempts < max_attempts:
            attempts += 1
            
            # 选择模板
            template = random.choice(list(TERM_GENERATION_TEMPLATES.keys()))
            
            term = self.generate_and_analyze(template=template)
            
            if term:
                quality_score = term['quality_analysis']['overall_score']
                
                if quality_score >= min_quality:
                    results.append(term)
                    print(f"✅ 接受术语 {len(results)}/{count}: {term.get('term', 'Unknown')} (质量: {quality_score:.2f})")
                else:
                    print(f"❌ 拒绝术语: {term.get('term', 'Unknown')} (质量: {quality_score:.2f} < {min_quality})")
            
            # 避免API限制
            time.sleep(1)
        
        self.logger.info(f"批量生成完成: {len(results)}/{count} 个术语通过质量检查")
        return results
    
    def generate_statistics(self, terms: List[Dict]) -> Dict:
        """生成统计信息"""
        if not terms:
            return {}
        
        stats = {
            'total_count': len(terms),
            'quality_distribution': {},
            'domain_distribution': {},
            'difficulty_distribution': {},
            'average_quality': 0,
            'quality_metrics': {}
        }
        
        # 质量分布
        quality_scores = [t['quality_analysis']['overall_score'] for t in terms if 'quality_analysis' in t]
        if quality_scores:
            stats['average_quality'] = statistics.mean(quality_scores)
            stats['quality_distribution'] = {
                'excellent': sum(1 for s in quality_scores if s >= 0.9),
                'good': sum(1 for s in quality_scores if 0.7 <= s < 0.9),
                'fair': sum(1 for s in quality_scores if 0.5 <= s < 0.7),
                'poor': sum(1 for s in quality_scores if s < 0.5)
            }
        
        # 领域分布
        domains = [t.get('domain_key', 'unknown') for t in terms]
        stats['domain_distribution'] = dict(Counter(domains))
        
        # 难度分布
        difficulties = [t.get('difficulty', 'unknown') for t in terms]
        stats['difficulty_distribution'] = dict(Counter(difficulties))
        
        # 质量指标平均值
        metrics = ['content_length', 'completeness', 'keyword_coverage', 'readability']
        for metric in metrics:
            values = []
            for term in terms:
                if 'quality_analysis' in term and 'metrics' in term['quality_analysis']:
                    if metric in term['quality_analysis']['metrics']:
                        values.append(term['quality_analysis']['metrics'][metric])
            
            if values:
                stats['quality_metrics'][metric] = {
                    'average': statistics.mean(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return stats
    
    def save_results_with_analysis(self, terms: List[Dict], filename: str = None) -> str:
        """保存结果和分析"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = OUTPUT_CONFIG['filename_format'].format(timestamp=timestamp)
        
        filepath = self.output_dir / filename
        
        # 生成统计信息
        statistics_data = self.generate_statistics(terms)
        
        # 构建输出数据
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': '2.0',
                'total_terms': len(terms),
                'api_model': OPENAI_MODEL
            },
            'statistics': statistics_data,
            'terms': terms
        }
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            if OUTPUT_CONFIG['pretty_print']:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(output_data, f, ensure_ascii=False)
        
        self.logger.info(f"结果已保存到: {filepath}")
        return str(filepath)

def print_quality_report(term: Dict):
    """打印质量报告"""
    print(f"\n📚 术语: {term.get('term', 'N/A')}")
    print(f"🔤 英文: {term.get('english_term', 'N/A')}")
    print(f"📂 分类: {term.get('category', 'N/A')}")
    print(f"⭐ 难度: {term.get('difficulty', 'N/A')}")
    
    if 'quality_analysis' in term:
        qa = term['quality_analysis']
        print(f"🎯 质量分数: {qa['overall_score']:.2f}")
        
        print("📊 质量指标:")
        for metric, score in qa['metrics'].items():
            print(f"   {metric}: {score:.2f}")
        
        if qa['suggestions']:
            print("💡 改进建议:")
            for suggestion in qa['suggestions']:
                print(f"   • {suggestion}")

def main():
    """主函数"""
    print("🚀 增强版每日名词生成器")
    print("=" * 60)
    
    # 检查API密钥
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("❌ 请先设置OpenAI API密钥")
        print("方法1: 设置环境变量 OPENAI_API_KEY")
        print("方法2: 在config.py中修改 OPENAI_API_KEY")
        return
    
    generator = EnhancedDailyTermGenerator()
    
    while True:
        print("\n📋 选择操作:")
        print("1. 智能生成单个术语")
        print("2. 高质量批量生成")
        print("3. 指定参数生成")
        print("4. 查看生成历史")
        print("5. 质量分析报告")
        print("6. 领域配置信息")
        print("7. 退出")
        
        choice = input("\n请选择 (1-7): ").strip()
        
        if choice == "1":
            template = input("选择模板 (standard/beginner_friendly/advanced, 默认standard): ").strip()
            if not template:
                template = "standard"
            
            term = generator.generate_and_analyze(template=template)
            if term:
                print_quality_report(term)
                
                save = input("\n💾 是否保存结果? (y/n): ").strip().lower()
                if save == 'y':
                    generator.save_results_with_analysis([term])
        
        elif choice == "2":
            count = input("生成数量 (默认10): ").strip()
            count = int(count) if count.isdigit() else 10
            
            min_quality = input("最低质量要求 (0.0-1.0, 默认0.7): ").strip()
            try:
                min_quality = float(min_quality) if min_quality else 0.7
            except ValueError:
                min_quality = 0.7
            
            print(f"\n🔄 开始批量生成 {count} 个高质量术语...")
            results = generator.batch_generate_with_analysis(count, min_quality)
            
            if results:
                print(f"\n📊 生成完成，共 {len(results)} 个术语")
                
                # 显示统计
                stats = generator.generate_statistics(results)
                print(f"平均质量分数: {stats.get('average_quality', 0):.2f}")
                
                filename = generator.save_results_with_analysis(results)
                print(f"📁 结果已保存到: {filename}")
        
        elif choice == "3":
            print("\n📂 可用领域:")
            for key, info in CS_DOMAINS.items():
                print(f"{key}: {info['name']}")
            
            domain = input("\n请输入领域键名: ").strip()
            if domain not in CS_DOMAINS:
                print("❌ 无效的领域")
                continue
            
            difficulty = input(f"请输入难度 {CS_DOMAINS[domain]['difficulty_levels']}: ").strip()
            template = input("选择模板 (standard/beginner_friendly/advanced): ").strip()
            
            if not template:
                template = "standard"
            
            term = generator.generate_and_analyze(domain, difficulty, template)
            if term:
                print_quality_report(term)
        
        elif choice == "4":
            if generator.generation_history:
                print(f"\n📜 生成历史 (最近{len(generator.generation_history)}个):")
                for i, term in enumerate(generator.generation_history[-10:], 1):
                    quality = term.get('quality_analysis', {}).get('overall_score', 0)
                    print(f"{i}. {term.get('term', 'Unknown')} - 质量: {quality:.2f}")
            else:
                print("\n📜 暂无生成历史")
        
        elif choice == "5":
            if generator.generation_history:
                stats = generator.generate_statistics(generator.generation_history)
                print("\n📊 质量分析报告:")
                print(f"总术语数: {stats['total_count']}")
                print(f"平均质量: {stats.get('average_quality', 0):.2f}")
                
                if 'quality_distribution' in stats:
                    print("\n质量分布:")
                    for level, count in stats['quality_distribution'].items():
                        print(f"  {level}: {count}")
                
                if 'domain_distribution' in stats:
                    print("\n领域分布:")
                    for domain, count in stats['domain_distribution'].items():
                        domain_name = CS_DOMAINS.get(domain, {}).get('name', domain)
                        print(f"  {domain_name}: {count}")
            else:
                print("\n📊 暂无数据可分析")
        
        elif choice == "6":
            print("\n📂 领域配置信息:")
            for key, info in CS_DOMAINS.items():
                print(f"\n🔹 {key}: {info['name']}")
                print(f"   权重: {info['weight']}")
                print(f"   难度级别: {', '.join(info['difficulty_levels'])}")
                print(f"   关键词数量: {len(info['keywords'])}")
        
        elif choice == "7":
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()

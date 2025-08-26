#!/usr/bin/env python
"""
性能测试脚本 - 测试优化前后的性能差异
"""

import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor
import sys

def test_page_performance(url, num_requests=10):
    """测试页面性能"""
    print(f"🔍 测试页面: {url}")
    
    response_times = []
    success_count = 0
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
            
            if response.status_code == 200:
                success_count += 1
                
            print(f"  请求 {i+1}: {response_time:.2f}ms - {response.status_code}")
            
        except Exception as e:
            print(f"  请求 {i+1}: 失败 - {e}")
    
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"📊 统计结果:")
        print(f"  平均响应时间: {avg_time:.2f}ms")
        print(f"  最快响应时间: {min_time:.2f}ms")
        print(f"  最慢响应时间: {max_time:.2f}ms")
        print(f"  成功率: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
        
        return {
            'url': url,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'success_rate': success_count/num_requests
        }
    
    return None

def test_concurrent_performance(url, num_concurrent=5, num_requests=20):
    """测试并发性能"""
    print(f"\n🚀 并发测试: {url} ({num_concurrent}个并发)")
    
    def single_request():
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            return (end_time - start_time) * 1000, response.status_code
        except Exception as e:
            return None, str(e)
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [executor.submit(single_request) for _ in range(num_requests)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    
    response_times = [r[0] for r in results if r[0] is not None]
    success_count = len(response_times)
    
    if response_times:
        avg_time = statistics.mean(response_times)
        print(f"📊 并发测试结果:")
        print(f"  总耗时: {total_time:.2f}ms")
        print(f"  平均响应时间: {avg_time:.2f}ms")
        print(f"  成功率: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
        print(f"  吞吐量: {success_count/(total_time/1000):.2f} 请求/秒")
        
        return {
            'total_time': total_time,
            'avg_time': avg_time,
            'success_rate': success_count/num_requests,
            'throughput': success_count/(total_time/1000)
        }
    
    return None

def main():
    """主函数"""
    print("🚀 性能测试开始...")
    print("=" * 60)
    
    # 测试的页面
    base_url = "http://127.0.0.1:8000"
    test_pages = [
        f"{base_url}/",
        f"{base_url}/daily-term/",
        f"{base_url}/universe/",
        f"{base_url}/about/",
    ]
    
    results = []
    
    # 单个请求性能测试
    print("\n📊 单个请求性能测试:")
    print("-" * 40)
    
    for url in test_pages:
        result = test_page_performance(url, num_requests=5)
        if result:
            results.append(result)
        print()
    
    # 并发性能测试
    print("\n🚀 并发性能测试:")
    print("-" * 40)
    
    concurrent_results = []
    for url in test_pages[:2]:  # 只测试主要页面
        result = test_concurrent_performance(url, num_concurrent=3, num_requests=10)
        if result:
            concurrent_results.append(result)
        print()
    
    # 性能评估
    print("\n📋 性能评估:")
    print("-" * 40)
    
    if results:
        overall_avg = statistics.mean([r['avg_time'] for r in results])
        print(f"整体平均响应时间: {overall_avg:.2f}ms")
        
        # 性能等级评估
        if overall_avg < 200:
            grade = "优秀 🌟"
        elif overall_avg < 500:
            grade = "良好 👍"
        elif overall_avg < 1000:
            grade = "一般 😐"
        else:
            grade = "需要优化 ⚠️"
        
        print(f"性能等级: {grade}")
        
        # 详细分析
        print(f"\n📈 详细分析:")
        for result in results:
            page_name = result['url'].split('/')[-2] or 'index'
            print(f"  {page_name}: {result['avg_time']:.2f}ms")
    
    # 优化建议
    print(f"\n💡 优化建议:")
    if results:
        slow_pages = [r for r in results if r['avg_time'] > 500]
        if slow_pages:
            print("  以下页面响应较慢，建议优化:")
            for page in slow_pages:
                page_name = page['url'].split('/')[-2] or 'index'
                print(f"    - {page_name}: {page['avg_time']:.2f}ms")
        else:
            print("  ✅ 所有页面响应时间都在可接受范围内")
    
    print(f"\n🔧 已应用的优化:")
    print("  ✅ 数据库查询缓存")
    print("  ✅ 模板文件压缩")
    print("  ✅ 性能监控中间件")
    print("  ✅ 缓存控制头")
    
    print(f"\n📋 进一步优化建议:")
    print("  1. 启用Redis缓存")
    print("  2. 使用CDN加速静态资源")
    print("  3. 数据库索引优化")
    print("  4. 图片懒加载")
    print("  5. 启用HTTP/2")
    
    print("\n" + "=" * 60)
    print("🔍 性能测试完成")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏸️  测试已中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

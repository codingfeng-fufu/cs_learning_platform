#!/usr/bin/env python
"""
内存优化脚本
"""

import gc
import os
import sys
import psutil
from django.core.cache import cache
from django.core.management import execute_from_command_line

def get_memory_usage():
    """获取当前内存使用情况"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    system_memory = psutil.virtual_memory()
    
    return {
        'process_mb': memory_info.rss / 1024 / 1024,
        'system_percent': system_memory.percent,
        'system_available_mb': system_memory.available / 1024 / 1024
    }

def optimize_memory():
    """执行内存优化"""
    print("🧠 开始内存优化...")
    
    initial_memory = get_memory_usage()
    print(f"初始内存使用: {initial_memory['process_mb']:.1f}MB")
    print(f"系统内存使用: {initial_memory['system_percent']:.1f}%")
    
    # 1. 清理缓存
    print("🧹 清理应用缓存...")
    cache.clear()
    
    # 2. 强制垃圾回收
    print("♻️  执行垃圾回收...")
    collected = gc.collect()
    print(f"回收了 {collected} 个对象")
    
    # 3. 清理Python缓存
    print("🗑️  清理Python缓存...")
    if hasattr(sys, '_clear_type_cache'):
        sys._clear_type_cache()
    
    # 4. 清理Django缓存
    print("🔄 重置Django缓存...")
    from django.core.management import call_command
    try:
        call_command('clear_cache')
    except:
        pass  # 如果命令不存在就跳过
    
    # 5. 检查优化效果
    final_memory = get_memory_usage()
    memory_saved = initial_memory['process_mb'] - final_memory['process_mb']
    
    print(f"\n📊 优化结果:")
    print(f"进程内存: {initial_memory['process_mb']:.1f}MB → {final_memory['process_mb']:.1f}MB")
    print(f"节省内存: {memory_saved:.1f}MB")
    print(f"系统内存: {initial_memory['system_percent']:.1f}% → {final_memory['system_percent']:.1f}%")
    
    if memory_saved > 0:
        print("✅ 内存优化成功")
    else:
        print("⚠️  内存使用未明显减少")
    
    return final_memory

def check_memory_leaks():
    """检查潜在的内存泄漏"""
    print("\n🔍 检查内存泄漏...")
    
    # 检查大对象
    import gc
    large_objects = []
    
    for obj in gc.get_objects():
        try:
            size = sys.getsizeof(obj)
            if size > 1024 * 1024:  # 大于1MB的对象
                large_objects.append((type(obj).__name__, size))
        except:
            continue
    
    if large_objects:
        print("发现大对象:")
        for obj_type, size in sorted(large_objects, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {obj_type}: {size / 1024 / 1024:.1f}MB")
    else:
        print("✅ 未发现异常大对象")

def optimize_django_settings():
    """优化Django设置以减少内存使用"""
    print("\n⚙️  优化Django设置...")
    
    optimizations = [
        "# 内存优化设置",
        "CONN_MAX_AGE = 0  # 禁用持久连接",
        "DATABASES['default']['CONN_MAX_AGE'] = 0",
        "",
        "# 限制缓存大小",
        "CACHES['default']['OPTIONS']['MAX_ENTRIES'] = 1000",
        "",
        "# 禁用不必要的中间件",
        "# 在生产环境中可以注释掉调试相关的中间件",
        "",
        "# 限制文件上传大小",
        "FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB",
        "DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5MB",
    ]
    
    print("建议的内存优化设置:")
    for line in optimizations:
        print(f"  {line}")

def main():
    """主函数"""
    print("🚀 Django应用内存优化工具")
    print("=" * 50)
    
    # 检查当前内存状态
    current_memory = get_memory_usage()
    
    if current_memory['system_percent'] > 90:
        print("⚠️  系统内存使用率过高，建议立即优化")
    elif current_memory['system_percent'] > 80:
        print("⚠️  系统内存使用率较高，建议优化")
    else:
        print("✅ 系统内存使用率正常")
    
    # 执行优化
    optimize_memory()
    
    # 检查内存泄漏
    check_memory_leaks()
    
    # 提供优化建议
    optimize_django_settings()
    
    print("\n💡 额外建议:")
    print("1. 重启Django服务器以释放内存")
    print("2. 考虑增加系统内存")
    print("3. 使用专业的WSGI服务器（如Gunicorn）")
    print("4. 启用内存监控和告警")
    print("5. 定期重启应用服务")
    
    print("\n" + "=" * 50)
    print("🧠 内存优化完成")

if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs_learning_platform.settings')
    
    import django
    django.setup()
    
    main()

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models
import json
import logging

from .algorithms.single_linklist import SingleLinkedList
from .models import KnowledgePoint, DailyTerm
from .search_service import SearchService
from .algorithms.hamming_code import HammingCode
from .algorithms.crc_check import CRCChecker
from .services.daily_term_service import DailyTermService

logger = logging.getLogger(__name__)


def get_cs_universe_knowledge_points():
    """获取CS Universe中的知识点数据，与cs_universe.html中的数据保持一致"""
    cs_courses = [
        {
            'name': '数据结构',
            'category': 'algorithm',
            'icon': '🧠',
            'planets': [
                {
                    'name': '链表',
                    'satellites': ['单链表', '双链表', '循环链表', '静态链表']
                },
                {
                    'name': '栈',
                    'satellites': ['顺序栈', '链式栈', '栈——括号匹配', '栈——表达式求值', '栈——卡特兰数', '栈——函数调用', '栈——递归']
                },
                {
                    'name': '队列',
                    'satellites': ['顺序队列', '循环队列', '链队列', '双端队列', '队列——缓冲区', '广度优先搜索']
                },
                {
                    'name': '矩阵',
                    'satellites': ['对称矩阵', '三角矩阵', '稀疏矩阵——三元组表示法', '稀疏矩阵——十字链表法', '广义表', 'KMP模式匹配']
                },
                {
                    'name': '树与二叉树',
                    'satellites': ['树与二叉树的性质', 'BST', 'AVL', '二叉树——顺序存储', '二叉树——链式存储', '二叉树——四序遍历', '线索二叉树', '树、森林与二叉树的转换', '树和森林的遍历', '哈夫曼树', '并查集']
                },
                {
                    'name': '图',
                    'satellites': ['图的存储结构', '图的遍历——DFS', '图的遍历——BFS', '最小生成树——Prim算法', '最小生成树——Kruskal算法', '最短路径——Dijkstra算法', '最短路径——Floyd', '最短路径——A*', '关键路径']
                },
                {
                    'name': '查找',
                    'satellites': ['二分查找', '分块查找', 'BST', 'AVL', '红黑树', 'B树', 'B+树', 'hash表']
                },
                {
                    'name': '排序',
                    'satellites': ['八大排序', '外部排序']
                }
            ]
        },
        {
            'name': '算法设计',
            'category': 'algorithm',
            'icon': '🧠',
            'planets': [
                {
                    'name': '分治算法',
                    'satellites': ['二分搜索', '归并排序', '快速排序', '最大子数组']
                },
                {
                    'name': '动态规划',
                    'satellites': ['背包问题', '最长公共子序列', '最长递增子序列', '编辑距离', '状态转移']
                },
                {
                    'name': '贪心算法',
                    'satellites': ['活动选择', '背包贪心', '哈夫曼编码', '最小生成树']
                },
                {
                    'name': '回溯算法',
                    'satellites': ['N皇后问题', '数独求解', '子集生成', '排列组合']
                },
                {
                    'name': '图论算法',
                    'satellites': ['深度优先搜索', '广度优先搜索', 'Dijkstra算法', 'Floyd算法', 'Kruskal算法', 'Prim算法']
                },
                {
                    'name': '字符串算法',
                    'satellites': ['KMP模式匹配', 'Rabin-Karp算法', '后缀数组', 'AC自动机']
                },
                {
                    'name': '数值算法',
                    'satellites': ['快速幂', '欧几里得算法', '扩展欧几里得', '素数筛选']
                }
            ]
        },
        {
            'name': '计算机网络',
            'category': 'network',
            'icon': '🌐',
            'planets': [
                {
                    'name': '物理层',
                    'satellites': ['数据通信的基础知识', '传输介质', '信道复用', '物理层设备']
                },
                {
                    'name': '数据链路层',
                    'satellites': ['组帧', '差错控制——检错码', '差错控制——纠错编码', '流量控制', '可靠传输机制', '滑动窗口机制', '停等协议', 'GBN协议', 'SR协议', 'ppp协议', 'MAC子层', 'CSMA/CD协议', 'CSMA/CA协议', '网桥', '生成树协议', '以太网交换机', 'WLAN', '令牌环网', '自适应树', 'ALOHA', '位图协议', '二进制倒计数', 'VLAN', '经典以太网']
                },
                {
                    'name': '网络层',
                    'satellites': ['虚电路和数据包服务', '路由与转发', '拥塞控制', 'DV路由算法', '链路状态路由算法', '层次路由', 'IPv4——分组', 'IPv4——地址', 'IPv4——NAT', 'IPv4——子网划分与子网掩码', 'CIDR', 'ARP', 'DHCP', 'ICMP', 'IP数据包的格式', 'RIP', 'OSPF', 'BGP', 'IPv6', 'IP组播', '移动IP', 'VPN']
                },
                {
                    'name': '传输层',
                    'satellites': ['UDP数据包', 'UDP校验', 'TCP报文段', 'TCP的流量控制', 'TCP的可靠传输', 'TCP拥塞控制', 'TCP连接的建立和释放', '套接字']
                },
                {
                    'name': '应用层',
                    'satellites': ['DNS', 'FTP', 'TELNET', 'WWW', 'HTTP', 'MIME', 'SMTP', 'POP3', 'DHCP', 'SNMP']
                },
                {
                    'name': '网络安全',
                    'satellites': ['计算机网络面临的安全性威胁', '安全的计算机网络', '对称密钥密码', 'DES', 'AES', '公钥密码体制', 'RSA', '数字签名', 'MD5', 'SHA-1', '密钥分配']
                }
            ]
        },
        {
            'name': '操作系统',
            'category': 'system',
            'icon': '💻',
            'planets': [
                {
                    'name': '进程管理',
                    'satellites': ['进程创建', '进程调度', '进程同步', '进程通信', '死锁处理']
                },
                {
                    'name': '线程管理',
                    'satellites': ['线程创建', '线程同步', '线程池', '多线程编程']
                },
                {
                    'name': '内存管理',
                    'satellites': ['内存分配', '虚拟内存', '分页机制', '分段机制', '页面置换', 'TLB管理']
                },
                {
                    'name': '文件系统',
                    'satellites': ['文件分配', '目录结构', '磁盘调度', 'RAID技术', '文件权限', '日志文件']
                },
                {
                    'name': '设备管理',
                    'satellites': ['I/O管理', '中断处理', 'DMA技术', '设备驱动', '缓冲技术']
                },
                {
                    'name': '系统调用',
                    'satellites': ['系统调用接口', '内核态', '用户态', '权限管理', '系统服务']
                }
            ]
        },
        {
            'name': '数据库系统',
            'category': 'database',
            'icon': '🗄️',
            'planets': [
                {
                    'name': '关系模型',
                    'satellites': ['关系代数', '元组演算', 'ER模型', '关系规范化', '函数依赖']
                },
                {
                    'name': 'SQL语言',
                    'satellites': ['DDL语句', 'DML语句', 'DCL语句', '查询优化', '视图操作']
                },
                {
                    'name': '事务管理',
                    'satellites': ['ACID性质', '并发控制', '锁机制', '死锁处理', '恢复技术']
                },
                {
                    'name': '索引技术',
                    'satellites': ['B+树索引', '哈希索引', '位图索引', '全文索引', '索引优化']
                },
                {
                    'name': '查询处理',
                    'satellites': ['查询优化', '执行计划', '连接算法', '选择算法', '统计信息']
                },
                {
                    'name': '分布式数据库',
                    'satellites': ['数据分片', '分布式事务', '一致性协议', 'CAP理论', 'NoSQL数据库']
                }
            ]
        },
        {
            'name': '软件工程',
            'category': 'ai',
            'icon': '🤖',
            'planets': [
                {
                    'name': '需求工程',
                    'satellites': ['需求分析', '需求建模', '用例分析', '需求验证', '需求管理']
                },
                {
                    'name': '系统设计',
                    'satellites': ['架构设计', '详细设计', '接口设计', '数据库设计', '用户界面设计']
                },
                {
                    'name': '软件测试',
                    'satellites': ['单元测试', '集成测试', '系统测试', '验收测试', '性能测试', '安全测试']
                },
                {
                    'name': '项目管理',
                    'satellites': ['敏捷开发', 'Scrum方法', '看板方法', '风险管理', '质量管理']
                },
                {
                    'name': '版本控制',
                    'satellites': ['Git管理', '分支策略', '合并冲突', '代码审查', '持续集成']
                },
                {
                    'name': '设计模式',
                    'satellites': ['创建型模式', '结构型模式', '行为型模式', '架构模式', '设计原则']
                }
            ]
        }
    ]

    # 转换为知识点列表
    knowledge_points = []
    for course in cs_courses:
        for planet in course['planets']:
            for satellite in planet['satellites']:
                # 检查是否已实现 - 更新为实际完善的页面
                implemented_mapping = {
                    # 原有的算法页面
                    '单链表': 'single-linklist',
                    '图的遍历——DFS': 'graph_dfs',
                    '差错控制——检错码': 'crc-check',
                    '差错控制——纠错编码': 'hamming-code',

                    # 数据结构类 (1个)
                    '树与二叉树的性质': 'tree-binary-tree-properties',

                    # 计算机网络类 (2个)
                    '物理层设备': 'topic-fe62a26c',
                    'PPP协议': 'ppp-c146f0f8',

                    # 信息安全类 (3个)
                    '数字签名': 'topic-95da6a4c',
                    'MD5算法': 'md5-7f138a09',
                    'SHA-1算法': 'sha1-c7df38de',

                    # 软件工程类 (5个)
                    '需求分析': 'topic-195af93f',
                    '敏捷开发': 'topic-889270ca',
                    '单元测试': 'topic-93b824b5',
                    'Git管理': 'git-51617d4b',
                    '架构模式': 'topic-3b64cdeb',

                    # 操作系统类 (4个)
                    '进程调度': 'topic-8dd1b7f3',
                    '虚拟内存': 'topic-84429675',
                    '进程同步': 'topic-c120f910',
                    '磁盘调度': 'topic-a56767df'
                }

                is_implemented = satellite in implemented_mapping
                if is_implemented:
                    slug = implemented_mapping[satellite]
                else:
                    # 生成安全的英文slug
                    import re
                    import hashlib

                    # 创建一个中文到英文的映射表
                    chinese_to_english = {
                        '双链表': 'double-linked-list',
                        '循环链表': 'circular-linked-list',
                        '静态链表': 'static-linked-list',
                        '顺序栈': 'sequential-stack',
                        '链式栈': 'linked-stack',
                        '括号匹配': 'bracket-matching',
                        '表达式求值': 'expression-evaluation',
                        '卡特兰数': 'catalan-number',
                        '函数调用': 'function-call',
                        '递归': 'recursion',
                        '顺序队列': 'sequential-queue',
                        '循环队列': 'circular-queue',
                        '链队列': 'linked-queue',
                        '双端队列': 'deque',
                        '缓冲区': 'buffer',
                        '广度优先搜索': 'breadth-first-search',
                        '对称矩阵': 'symmetric-matrix',
                        '三角矩阵': 'triangular-matrix',
                        '稀疏矩阵': 'sparse-matrix',
                        '三元组表示法': 'triplet-representation',
                        '十字链表法': 'cross-linked-list',
                        '广义表': 'generalized-list',
                        '模式匹配': 'pattern-matching',
                        '树与二叉树的性质': 'tree-binary-tree-properties',
                        '顺序存储': 'sequential-storage',
                        '链式存储': 'linked-storage',
                        '四序遍历': 'four-order-traversal',
                        '线索二叉树': 'threaded-binary-tree',
                        '森林与二叉树的转换': 'forest-binary-tree-conversion',
                        '树和森林的遍历': 'tree-forest-traversal',
                        '哈夫曼树': 'huffman-tree',
                        '并查集': 'union-find',
                        '图的存储结构': 'graph-storage-structure',
                        '最小生成树': 'minimum-spanning-tree',
                        '最短路径': 'shortest-path',
                        '关键路径': 'critical-path',
                        '二分查找': 'binary-search',
                        '分块查找': 'block-search',
                        '红黑树': 'red-black-tree',
                        '哈希表': 'hash-table',
                        '八大排序': 'eight-sorting-algorithms',
                        '外部排序': 'external-sorting'
                    }

                    # 如果有预定义的英文名称，使用它
                    if satellite in chinese_to_english:
                        slug = chinese_to_english[satellite]
                    else:
                        # 否则生成一个基于内容的唯一slug
                        # 使用MD5哈希的前8位作为唯一标识
                        hash_obj = hashlib.md5(satellite.encode('utf-8'))
                        hash_hex = hash_obj.hexdigest()[:8]

                        # 尝试提取英文字符
                        english_part = re.sub(r'[^a-zA-Z0-9]', '', satellite.lower())
                        if english_part and len(english_part) >= 2:
                            slug = f"{english_part}-{hash_hex}"
                        else:
                            slug = f"topic-{hash_hex}"

                    # 确保slug符合URL规范
                    slug = re.sub(r'[^a-zA-Z0-9_-]', '', slug).strip('-')

                # 设置正确的分类标识
                category_mapping = {
                    '数据结构': 'data-structure',
                    '算法设计': 'algorithm',
                    '计算机网络': 'network',
                    '操作系统': 'system',
                    '数据库系统': 'database',
                    '软件工程': 'software',
                    '信息安全': 'security'
                }

                knowledge_points.append({
                    'title': satellite,
                    'slug': slug,
                    'description': f'{course["name"]} - {planet["name"]}中的{satellite}',
                    'category': category_mapping.get(course['name'], course['category']),
                    'category_display': course['name'],
                    'difficulty': 'intermediate',
                    'icon': course['icon'],
                    'is_implemented': is_implemented,
                    'order': 0
                })

    return knowledge_points


def index(request):
    """主页 - 知识点卡片展示"""
    from django.core.cache import cache

    # 缓存今日名词（1小时）
    today_term = cache.get('today_term')
    if not today_term:
        from .services.daily_term_service import DailyTermService
        service = DailyTermService()
        today_term = service.get_today_term()
        if today_term:
            cache.set('today_term', today_term, 3600)  # 缓存1小时

    # 获取搜索参数
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    # 缓存知识点数据（30分钟）
    cache_key = f'knowledge_points_{search_query}_{category_filter}'
    all_knowledge_points = cache.get(cache_key)

    if not all_knowledge_points:
        all_knowledge_points = get_cs_universe_knowledge_points()
        cache.set(cache_key, all_knowledge_points, 1800)  # 缓存30分钟

    # 搜索过滤
    if search_query:
        all_knowledge_points = [
            point for point in all_knowledge_points
            if search_query.lower() in point['title'].lower() or
               search_query.lower() in point['description'].lower()
        ]

    # 分类过滤
    if category_filter:
        all_knowledge_points = [
            point for point in all_knowledge_points
            if point['category'] == category_filter
        ]

    # 按分类分组知识点
    categories = {}
    for point in all_knowledge_points:
        category_name = point['category_display']
        if category_name not in categories:
            categories[category_name] = []
        categories[category_name].append(point)

    # 获取统计信息
    total_points = len(all_knowledge_points)
    implemented_count = len([p for p in all_knowledge_points if p['is_implemented']])

    context = {
        'categories': categories,
        'total_points': total_points,
        'implemented_count': implemented_count,
        'search_query': search_query,
        'category_filter': category_filter,
        'today_term': today_term,
        'current_date': timezone.now().date(),
    }
    return render(request, 'knowledge_app/index.html', context)


def knowledge_detail(request, slug):
    """知识点详情页"""
    # 首先尝试从数据库获取知识点
    try:
        from users.models import KnowledgePoint as UserKnowledgePoint
        knowledge_point = UserKnowledgePoint.objects.get(slug=slug, is_active=True)
    except UserKnowledgePoint.DoesNotExist:
        # 如果数据库中没有，从CS Universe数据中查找
        all_knowledge_points = get_cs_universe_knowledge_points()
        knowledge_point = None

        for point in all_knowledge_points:
            if point['slug'] == slug:
                # 创建一个类似模型对象的字典
                knowledge_point = type('KnowledgePoint', (), {
                    'title': point['title'],
                    'slug': point['slug'],
                    'description': point['description'],
                    'category': point['category'],
                    'category_display': point['category_display'],
                    'difficulty': point['difficulty'],
                    'icon': point['icon'],
                    'is_implemented': point['is_implemented'],
                    'order': point['order']
                })()
                break

        if not knowledge_point:
            raise Http404("知识点不存在")

    # 如果用户已登录，记录学习进度
    user_progress = None
    if request.user.is_authenticated:
        from users.progress_service import ProgressService
        from users.models import UserKnowledgeProgress

        # 开始学习会话
        session = ProgressService.start_study_session(request.user, slug)

        # 获取用户在此知识点的进度
        try:
            user_progress = UserKnowledgeProgress.objects.get(
                user=request.user,
                knowledge_point__slug=slug
            )
        except UserKnowledgeProgress.DoesNotExist:
            user_progress = None

    # 检查是否有专门的模板文件，否则使用通用模板
    import os
    from django.conf import settings

    specific_template = f'knowledge_app/{slug}.html'
    generic_template = 'knowledge_app/knowledge_detail.html'

    # 检查特定模板是否存在
    template_path = os.path.join(settings.BASE_DIR, 'templates', specific_template)
    if os.path.exists(template_path):
        template = specific_template
    else:
        template = generic_template

    context = {
        'knowledge_point': knowledge_point,
        'user_progress': user_progress,
        'session_id': session.id if request.user.is_authenticated and session else None,
    }
    return render(request, template, context)


def search(request):
    """搜索页面"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    implemented = request.GET.get('implemented', '')
    sort_by = request.GET.get('sort', 'relevance')
    page = request.GET.get('page', 1)

    results = []
    total_results = 0
    search_time = 0

    if query:
        import time
        start_time = time.time()

        # 构建过滤器
        filters = {}
        if category:
            filters['category'] = category
        if difficulty:
            filters['difficulty'] = difficulty
        if implemented:
            filters['implemented'] = implemented.lower() == 'true'

        # 执行搜索
        all_results = SearchService.search_knowledge_points(
            query=query,
            filters=filters,
            sort_by=sort_by,
            limit=100  # 获取更多结果用于分页
        )

        total_results = len(all_results)
        search_time = round((time.time() - start_time) * 1000, 2)

        # 分页
        paginator = Paginator(all_results, 10)  # 每页10个结果
        try:
            results = paginator.page(page)
        except:
            results = paginator.page(1)

    # 获取搜索相关数据
    popular_searches = SearchService.get_popular_searches(limit=8)
    search_filters = SearchService.get_search_filters()
    user_history = SearchService.get_user_search_history(request.user, limit=5)

    context = {
        'query': query,
        'results': results,
        'total_results': total_results,
        'search_time': search_time,
        'popular_searches': popular_searches,
        'search_filters': search_filters,
        'user_history': user_history,
        'current_filters': {
            'category': category,
            'difficulty': difficulty,
            'implemented': implemented,
            'sort': sort_by,
        }
    }

    return render(request, 'knowledge_app/search.html', context)


@require_http_methods(["GET"])
def search_suggestions(request):
    """搜索建议API"""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 1:
        return JsonResponse({'suggestions': []})

    suggestions = SearchService.get_search_suggestions(query, limit=8)

    return JsonResponse({'suggestions': suggestions})


@require_http_methods(["GET"])
def search_api(request):
    """搜索API"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))

    if not query:
        return JsonResponse({'results': [], 'total': 0})

    results = SearchService.search_knowledge_points(query, limit=limit)

    return JsonResponse({
        'results': results,
        'total': len(results),
        'query': query
    })


@require_http_methods(["POST"])
def clear_search_history(request):
    """清除搜索历史"""
    if request.user.is_authenticated:
        success = SearchService.clear_user_search_history(request.user)
        return JsonResponse({'success': success})

    return JsonResponse({'success': False, 'error': '用户未登录'})


# ========== 海明码相关API ==========

@csrf_exempt
@require_http_methods(["POST"])
def hamming_encode_api(request):
    """海明码编码API"""
    try:
        data = json.loads(request.body)
        data_bits = data.get('data_bits', '').strip()

        # 输入验证
        if not data_bits:
            return JsonResponse({
                'success': False,
                'error': '请输入要编码的数据'
            })

        if not all(bit in '01' for bit in data_bits):
            return JsonResponse({
                'success': False,
                'error': '数据只能包含0和1'
            })

        if len(data_bits) > 16:
            return JsonResponse({
                'success': False,
                'error': '数据长度不能超过16位'
            })

        # 执行编码
        hc = HammingCode()
        result, steps = hc.encode(data_bits)

        if result is None:
            return JsonResponse({
                'success': False,
                'error': '编码失败，请检查输入数据'
            })

        logger.info(f"海明码编码成功: {data_bits} -> {result}")

        return JsonResponse({
            'success': True,
            'result': result,
            'steps': steps,
            'input_length': len(data_bits),
            'output_length': len(result)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"海明码编码API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def hamming_decode_api(request):
    """海明码解码API"""
    try:
        data = json.loads(request.body)
        hamming_bits = data.get('hamming_bits', '').strip()

        # 输入验证
        if not hamming_bits:
            return JsonResponse({
                'success': False,
                'error': '请输入要解码的海明码'
            })

        if not all(bit in '01' for bit in hamming_bits):
            return JsonResponse({
                'success': False,
                'error': '海明码只能包含0和1'
            })

        if len(hamming_bits) > 32:
            return JsonResponse({
                'success': False,
                'error': '海明码长度不能超过32位'
            })

        # 执行解码
        hc = HammingCode()
        result, has_error, steps = hc.decode(hamming_bits)

        if result is None:
            return JsonResponse({
                'success': False,
                'error': '解码失败，请检查输入的海明码格式'
            })

        logger.info(f"海明码解码成功: {hamming_bits} -> {result}, 有错误: {has_error}")

        return JsonResponse({
            'success': True,
            'result': result,
            'has_error': has_error,
            'steps': steps,
            'input_length': len(hamming_bits),
            'output_length': len(result)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"海明码解码API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


# ========== CRC相关API ==========

@csrf_exempt
@require_http_methods(["POST"])
def crc_calculate_api(request):
    """CRC计算API"""
    try:
        data = json.loads(request.body)
        data_bits = data.get('data_bits', '').strip()
        polynomial = data.get('polynomial', '1011').strip()

        # 输入验证
        if not data_bits:
            return JsonResponse({
                'success': False,
                'error': '请输入要计算CRC的数据'
            })

        if not polynomial:
            return JsonResponse({
                'success': False,
                'error': '请输入生成多项式'
            })

        if not all(bit in '01' for bit in data_bits):
            return JsonResponse({
                'success': False,
                'error': '数据只能包含0和1'
            })

        if not all(bit in '01' for bit in polynomial):
            return JsonResponse({
                'success': False,
                'error': '生成多项式只能包含0和1'
            })

        if len(data_bits) > 20:
            return JsonResponse({
                'success': False,
                'error': '数据长度不能超过20位'
            })

        if len(polynomial) < 2 or len(polynomial) > 10:
            return JsonResponse({
                'success': False,
                'error': '生成多项式长度应在2-10位之间'
            })

        # 执行CRC计算
        crc = CRCChecker(polynomial)
        result, steps = crc.calculate_crc(data_bits)

        if result is None:
            return JsonResponse({
                'success': False,
                'error': 'CRC计算失败'
            })

        logger.info(f"CRC计算成功: {data_bits} + {polynomial} -> {result}")

        return JsonResponse({
            'success': True,
            'result': result,
            'steps': steps,
            'complete_data': data_bits + result,
            'crc_length': len(result)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"CRC计算API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def crc_verify_api(request):
    """CRC验证API"""
    try:
        data = json.loads(request.body)
        data_with_crc = data.get('data_with_crc', '').strip()
        polynomial = data.get('polynomial', '1011').strip()

        # 输入验证
        if not data_with_crc:
            return JsonResponse({
                'success': False,
                'error': '请输入要验证的数据（含CRC）'
            })

        if not polynomial:
            return JsonResponse({
                'success': False,
                'error': '请输入生成多项式'
            })

        if not all(bit in '01' for bit in data_with_crc):
            return JsonResponse({
                'success': False,
                'error': '数据只能包含0和1'
            })

        if not all(bit in '01' for bit in polynomial):
            return JsonResponse({
                'success': False,
                'error': '生成多项式只能包含0和1'
            })

        crc_length = len(polynomial) - 1
        if len(data_with_crc) <= crc_length:
            return JsonResponse({
                'success': False,
                'error': f'数据长度必须大于{crc_length}位'
            })

        # 执行CRC验证
        crc = CRCChecker(polynomial)
        is_valid, steps = crc.verify_crc(data_with_crc)

        logger.info(f"CRC验证完成: {data_with_crc} + {polynomial} -> {'有效' if is_valid else '无效'}")

        return JsonResponse({
            'success': True,
            'is_valid': is_valid,
            'steps': steps,
            'data_length': len(data_with_crc),
            'crc_length': crc_length
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"CRC验证API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


# ========== 单链表相关API ==========

# 全局变量存储用户的链表状态（实际项目中应该使用session或数据库）
user_lists = {}


def get_user_list(session_key):
    """获取用户的链表实例"""
    if session_key not in user_lists:
        user_lists[session_key] = SingleLinkedList()
    return user_lists[session_key]


# 修复后的视图API函数
# 请将这些函数添加到您的 views.py 中，或者更新现有的函数

@csrf_exempt
@require_http_methods(["POST"])
def linked_list_add_api(request):
    """单链表添加操作API - 修复版"""
    try:
        data = json.loads(request.body)
        add_type = data.get('add_type', '').strip()
        value = data.get('value')
        position = data.get('position')

        # 输入验证
        if add_type not in ['head', 'tail', 'position']:
            return JsonResponse({
                'success': False,
                'error': '无效的添加类型'
            })

        if value is None:
            return JsonResponse({
                'success': False,
                'error': '请输入节点值'
            })

        # 验证数值范围
        try:
            value = int(value)
            if value < -999 or value > 999:
                return JsonResponse({
                    'success': False,
                    'error': '节点值必须在-999到999之间'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': '节点值必须是数字'
            })

        # 获取用户的链表实例
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        linked_list = get_user_list(session_key)

        # 执行添加操作
        if add_type == 'head':
            success, steps = linked_list.add_head(value)
        elif add_type == 'tail':
            success, steps = linked_list.add_tail(value)
        elif add_type == 'position':
            if position is None:
                return JsonResponse({
                    'success': False,
                    'error': '请输入插入位置'
                })

            try:
                position = int(position)
                if position < 0:
                    return JsonResponse({
                        'success': False,
                        'error': '位置不能为负数'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': '位置必须是非负整数'
                })

            success, steps = linked_list.add_at_position(position, value)

        if not success:
            return JsonResponse({
                'success': False,
                'error': '添加操作失败',
                'steps': steps
            })

        logger.info(f"单链表添加成功: {add_type} 添加 {value}")

        # 获取步骤的动画数据
        animation_steps = linked_list.get_steps_with_animation_data()

        return JsonResponse({
            'success': True,
            'list_state': linked_list.to_list(),
            'list_info': linked_list.get_info(),
            'steps': steps,  # 字符串数组格式的步骤
            'animation_data': [
                {
                    'description': step.get('description', str(step)),
                    'type': step.get('type', 'info'),
                    'highlight_nodes': step.get('highlight_nodes', []),
                    'highlight_pointers': step.get('highlight_pointers', [])
                } for step in animation_steps
            ]
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"单链表添加API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def linked_list_delete_api(request):
    """单链表删除操作API - 修复版"""
    try:
        data = json.loads(request.body)
        delete_type = data.get('delete_type', '').strip()
        value = data.get('value')
        position = data.get('position')

        # 输入验证
        if delete_type not in ['value', 'position', 'head', 'tail']:
            return JsonResponse({
                'success': False,
                'error': '无效的删除类型'
            })

        # 获取用户的链表实例
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        linked_list = get_user_list(session_key)

        # 检查链表是否为空
        if linked_list.is_empty():
            return JsonResponse({
                'success': False,
                'error': '链表为空，无法删除'
            })

        # 执行删除操作
        if delete_type == 'head':
            success, deleted_value, steps = linked_list.delete_head()
        elif delete_type == 'tail':
            success, deleted_value, steps = linked_list.delete_tail()
        elif delete_type == 'value':
            if value is None:
                return JsonResponse({
                    'success': False,
                    'error': '请输入要删除的值'
                })

            try:
                value = int(value)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': '要删除的值必须是数字'
                })

            success, deleted_position, steps = linked_list.delete_by_value(value)
            deleted_value = value if success else None
        elif delete_type == 'position':
            if position is None:
                return JsonResponse({
                    'success': False,
                    'error': '请输入要删除的位置'
                })

            try:
                position = int(position)
                if position < 0:
                    return JsonResponse({
                        'success': False,
                        'error': '位置不能为负数'
                    })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': '位置必须是非负整数'
                })

            success, deleted_value, steps = linked_list.delete_at_position(position)

        if not success:
            return JsonResponse({
                'success': False,
                'error': '删除操作失败',
                'steps': steps
            })

        logger.info(f"单链表删除成功: {delete_type} 删除 {deleted_value}")

        # 获取步骤的动画数据
        animation_steps = linked_list.get_steps_with_animation_data()

        return JsonResponse({
            'success': True,
            'list_state': linked_list.to_list(),
            'list_info': linked_list.get_info(),
            'steps': steps,  # 字符串数组格式的步骤
            'deleted_value': deleted_value,
            'animation_data': [
                {
                    'description': step.get('description', str(step)),
                    'type': step.get('type', 'info'),
                    'highlight_nodes': step.get('highlight_nodes', []),
                    'highlight_pointers': step.get('highlight_pointers', [])
                } for step in animation_steps
            ]
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"单链表删除API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def linked_list_insert_api(request):
    """单链表插入操作API - 修复版"""
    try:
        data = json.loads(request.body)
        insert_type = data.get('insert_type', '').strip()
        target_value = data.get('target_value')
        new_value = data.get('new_value')

        # 输入验证
        if insert_type not in ['before', 'after']:
            return JsonResponse({
                'success': False,
                'error': '无效的插入类型'
            })

        if target_value is None:
            return JsonResponse({
                'success': False,
                'error': '请输入目标节点值'
            })

        if new_value is None:
            return JsonResponse({
                'success': False,
                'error': '请输入新节点值'
            })

        # 验证数值范围
        try:
            target_value = int(target_value)
            new_value = int(new_value)
            if target_value < -999 or target_value > 999 or new_value < -999 or new_value > 999:
                return JsonResponse({
                    'success': False,
                    'error': '节点值必须在-999到999之间'
                })
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': '节点值必须是数字'
            })

        # 获取用户的链表实例
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        linked_list = get_user_list(session_key)

        # 执行插入操作
        if insert_type == 'before':
            success, steps = linked_list.insert_before_value(target_value, new_value)
        else:  # after
            success, steps = linked_list.insert_after_value(target_value, new_value)

        if not success:
            return JsonResponse({
                'success': False,
                'error': '插入操作失败',
                'steps': steps
            })

        logger.info(f"单链表插入成功: 在 {target_value} {insert_type} 插入 {new_value}")

        # 获取步骤的动画数据
        animation_steps = linked_list.get_steps_with_animation_data()

        return JsonResponse({
            'success': True,
            'list_state': linked_list.to_list(),
            'list_info': linked_list.get_info(),
            'steps': steps,  # 字符串数组格式的步骤
            'animation_data': [
                {
                    'description': step.get('description', str(step)),
                    'type': step.get('type', 'info'),
                    'highlight_nodes': step.get('highlight_nodes', []),
                    'highlight_pointers': step.get('highlight_pointers', [])
                } for step in animation_steps
            ]
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"单链表插入API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def linked_list_search_api(request):
    """单链表查找操作API - 修复版"""
    try:
        data = json.loads(request.body)
        search_value = data.get('search_value')

        if search_value is None:
            return JsonResponse({
                'success': False,
                'error': '请输入要查找的值'
            })

        # 验证数值
        try:
            search_value = int(search_value)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': '查找值必须是数字'
            })

        # 获取用户的链表实例
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        linked_list = get_user_list(session_key)

        # 执行查找操作
        found, position, steps = linked_list.search_value(search_value)

        logger.info(f"单链表查找: 值 {search_value} {'找到' if found else '未找到'}")

        # 获取步骤的动画数据
        animation_steps = linked_list.get_steps_with_animation_data()

        return JsonResponse({
            'success': True,
            'found': found,
            'position': position,
            'search_value': search_value,
            'list_state': linked_list.to_list(),
            'list_info': linked_list.get_info(),
            'steps': steps,  # 字符串数组格式的步骤
            'animation_data': [
                {
                    'description': step.get('description', str(step)),
                    'type': step.get('type', 'info'),
                    'highlight_nodes': step.get('highlight_nodes', []),
                    'highlight_pointers': step.get('highlight_pointers', [])
                } for step in animation_steps
            ]
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        logger.error(f"单链表查找API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def linked_list_clear_api(request):
    """单链表清空操作API"""
    try:
        # 获取用户的链表实例
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # 重新创建一个空链表
        user_lists[session_key] = SingleLinkedList()

        logger.info(f"单链表清空成功")

        return JsonResponse({
            'success': True,
            'list_state': [],
            'list_info': {
                'length': 0,
                'is_empty': True,
                'head_value': None,
                'tail_value': None,
                'as_list': [],
                'display': 'Empty List'
            }
        })

    except Exception as e:
        logger.error(f"单链表清空API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
def linked_list_status_api(request):
    """获取单链表状态API"""
    try:
        # 获取用户的链表实例
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        linked_list = get_user_list(session_key)

        return JsonResponse({
            'success': True,
            'list_state': linked_list.to_list(),
            'list_info': linked_list.get_info()
        })

    except Exception as e:
        logger.error(f"获取单链表状态API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


def cs_universe(request):
    return render(request,'knowledge_app/cs_universe_css3d.html')

def get_graph_dfs(request):
    return render(request,'knowledge_app/graph_dfs.html')

# ========== 大分类概览页面 ==========

def data_structures(request):
    """数据结构概览页面"""
    context = {
        'page_title': '数据结构',
        'page_icon': '🏗️',
        'page_description': '掌握数据的组织、存储和操作方式，构建高效算法的基石',
        'breadcrumb_category': '计算机科学',
    }
    return render(request, 'knowledge_app/data-structures.html', context)

def algorithm_design(request):
    """算法设计概览页面"""
    context = {
        'page_title': '算法设计',
        'page_icon': '🧠',
        'page_description': '掌握问题求解的系统方法，设计高效优雅的算法解决方案',
        'breadcrumb_category': '计算机科学',
    }
    return render(request, 'knowledge_app/algorithm-design.html', context)

def computer_networks(request):
    """计算机网络概览页面"""
    context = {
        'page_title': '计算机网络',
        'page_icon': '🌐',
        'page_description': '理解网络通信原理，掌握现代互联网的基础架构和协议体系',
        'breadcrumb_category': '计算机科学',
    }
    return render(request, 'knowledge_app/computer-networks.html', context)

def operating_systems(request):
    """操作系统概览页面"""
    context = {
        'page_title': '操作系统',
        'page_icon': '💻',
        'page_description': '深入理解计算机系统的核心，掌握进程、内存、文件系统等关键概念',
        'breadcrumb_category': '计算机科学',
    }
    return render(request, 'knowledge_app/operating-systems.html', context)

def database_systems(request):
    """数据库系统概览页面"""
    context = {
        'page_title': '数据库系统',
        'page_icon': '🗄️',
        'page_description': '掌握数据存储与管理的核心技术，从关系型到NoSQL数据库',
        'breadcrumb_category': '计算机科学',
    }
    return render(request, 'knowledge_app/database-systems.html', context)

def software_engineering(request):
    """软件工程概览页面"""
    context = {
        'page_title': '软件工程',
        'page_icon': '🛠️',
        'page_description': '学习软件开发的工程化方法，提升项目管理和团队协作能力',
        'breadcrumb_category': '计算机科学',
    }
    return render(request, 'knowledge_app/software-engineering.html', context)

# ========== 行星页面（子分类概览） ==========

def linked_list(request):
    """链表概览页面"""
    return render(request, 'knowledge_app/linked-list.html')

def double_linked_list(request):
    """双向链表概览页面"""
    return render(request, 'knowledge_app/double-linked-list.html')

def circular_linked_list(request):
    """循环链表概览页面"""
    return render(request, 'knowledge_app/circular-linked-list.html')

def stack(request):
    """栈概览页面"""
    return render(request, 'knowledge_app/stack.html')

def queue(request):
    """队列概览页面"""
    return render(request, 'knowledge_app/queue.html')

def divide_conquer(request):
    """分治算法概览页面"""
    return render(request, 'knowledge_app/divide-conquer.html')

def dynamic_programming(request):
    """动态规划概览页面"""
    return render(request, 'knowledge_app/dynamic-programming.html')

def physical_layer(request):
    """物理层概览页面"""
    return render(request, 'knowledge_app/physical-layer.html')

def data_link_layer(request):
    """数据链路层概览页面"""
    return render(request, 'knowledge_app/data-link-layer.html')

def matrix(request):
    """矩阵概览页面"""
    return render(request, 'knowledge_app/matrix.html')

def tree_binary_tree(request):
    """树与二叉树概览页面"""
    return render(request, 'knowledge_app/tree-binary-tree.html')

def graph(request):
    """图概览页面"""
    return render(request, 'knowledge_app/graph.html')

# 搜索功能已在上面实现，这里删除重复的函数

def sorting(request):
    """排序概览页面"""
    return render(request, 'knowledge_app/sorting.html')

def greedy_algorithm(request):
    """贪心算法概览页面"""
    return render(request, 'knowledge_app/greedy-algorithm.html')

def backtracking(request):
    """回溯算法概览页面"""
    return render(request, 'knowledge_app/backtracking.html')

def graph_algorithms(request):
    """图论算法概览页面"""
    return render(request, 'knowledge_app/graph-algorithms.html')

def string_algorithms(request):
    """字符串算法概览页面"""
    return render(request, 'knowledge_app/string-algorithms.html')

def numerical_algorithms(request):
    """数值算法概览页面"""
    return render(request, 'knowledge_app/numerical-algorithms.html')

def network_layer(request):
    """网络层概览页面"""
    return render(request, 'knowledge_app/network-layer.html')

def transport_layer(request):
    """传输层概览页面"""
    return render(request, 'knowledge_app/transport-layer.html')

def application_layer(request):
    """应用层概览页面"""
    return render(request, 'knowledge_app/application-layer.html')

def network_security(request):
    """网络安全概览页面"""
    return render(request, 'knowledge_app/network-security.html')

def process_management(request):
    """进程管理概览页面"""
    return render(request, 'knowledge_app/process-management.html')

def thread_management(request):
    """线程管理概览页面"""
    return render(request, 'knowledge_app/thread-management.html')

def memory_management(request):
    """内存管理概览页面"""
    return render(request, 'knowledge_app/memory-management.html')

def file_system(request):
    """文件系统概览页面"""
    return render(request, 'knowledge_app/file-system.html')

def device_management(request):
    """设备管理概览页面"""
    return render(request, 'knowledge_app/device-management.html')

def system_calls(request):
    """系统调用概览页面"""
    return render(request, 'knowledge_app/system-calls.html')

def relational_model(request):
    """关系模型概览页面"""
    return render(request, 'knowledge_app/relational-model.html')

def sql_language(request):
    """SQL语言概览页面"""
    return render(request, 'knowledge_app/sql-language.html')

def transaction_management(request):
    """事务管理概览页面"""
    return render(request, 'knowledge_app/transaction-management.html')

def indexing(request):
    """索引技术概览页面"""
    return render(request, 'knowledge_app/indexing.html')

def query_processing(request):
    """查询处理概览页面"""
    return render(request, 'knowledge_app/query-processing.html')

def distributed_database(request):
    """分布式数据库概览页面"""
    return render(request, 'knowledge_app/distributed-database.html')

def requirements_engineering(request):
    """需求工程概览页面"""
    return render(request, 'knowledge_app/requirements-engineering.html')

def system_design(request):
    """系统设计概览页面"""
    return render(request, 'knowledge_app/system-design.html')

def software_testing(request):
    """软件测试概览页面"""
    return render(request, 'knowledge_app/software-testing.html')

def project_management(request):
    """项目管理概览页面"""
    return render(request, 'knowledge_app/project-management.html')

def version_control(request):
    """版本控制概览页面"""
    return render(request, 'knowledge_app/version-control.html')

def design_patterns(request):
    """设计模式概览页面"""
    return render(request, 'knowledge_app/design-patterns.html')


# ==================== 每日名词相关视图 ====================

def daily_term(request):
    """每日名词主页"""
    service = DailyTermService()

    # 获取今日名词
    today_term = service.get_today_term()

    # 如果没有今日名词，尝试生成一个
    if not today_term:
        try:
            today_term = service.generate_daily_term()
        except Exception as e:
            logger.error(f"Failed to generate daily term: {e}")

    # 获取历史名词
    history_terms = service.get_term_history(7)

    # 增加浏览次数
    if today_term:
        today_term.increment_view_count()

    context = {
        'today_term': today_term,
        'history_terms': history_terms,
        'current_date': timezone.now().date(),
    }

    return render(request, 'knowledge_app/daily_term.html', context)


def daily_term_detail(request, term_id):
    """名词详情页面"""
    term = get_object_or_404(DailyTerm, id=term_id)

    # 增加浏览次数
    term.increment_view_count()

    # 获取相关名词（同分类或相似难度）
    related_terms = DailyTerm.objects.filter(
        status='active'
    ).exclude(id=term.id)

    # 优先显示同分类的
    if term.category:
        related_terms = related_terms.filter(category=term.category)

    related_terms = related_terms.order_by('-display_date')[:5]

    context = {
        'term': term,
        'related_terms': related_terms,
    }

    return render(request, 'knowledge_app/daily_term_detail.html', context)


@require_http_methods(["GET"])
def export_daily_term_pdf(request, term_id):
    """导出每日名词PDF"""
    term = get_object_or_404(DailyTerm, id=term_id)

    import logging
    logger = logging.getLogger(__name__)

    try:
        import io
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib import colors
        from django.conf import settings
        from django.utils import timezone

        logger.info(f"开始导出每日名词PDF: {term.term} (ID: {term_id})")

        # 注册中文字体
        try:
            import platform
            if platform.system() == 'Windows':
                font_paths = [
                    'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
                    'C:/Windows/Fonts/simhei.ttf',  # 黑体
                    'C:/Windows/Fonts/simsun.ttc',  # 宋体
                ]
            else:
                font_paths = [
                    '/System/Library/Fonts/PingFang.ttc',  # Mac
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                ]

            chinese_font_registered = False
            for font_path in font_paths:
                try:
                    import os
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        chinese_font_registered = True
                        break
                except:
                    continue

            if not chinese_font_registered:
                chinese_font_name = 'Helvetica'
            else:
                chinese_font_name = 'ChineseFont'

        except Exception as e:
            logger.warning(f"字体注册失败，使用默认字体: {e}")
            chinese_font_name = 'Helvetica'

        # 创建PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # 获取样式并创建中文样式
        styles = getSampleStyleSheet()

        # 创建支持中文的样式
        title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font_name,
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1,  # 居中
        )

        heading_style = ParagraphStyle(
            'ChineseHeading',
            parent=styles['Heading2'],
            fontName=chinese_font_name,
            fontSize=16,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.HexColor('#34495e'),
        )

        normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=12,
            spaceAfter=8,
            leading=18,
            textColor=colors.HexColor('#2c3e50'),
        )

        meta_style = ParagraphStyle(
            'ChineseMeta',
            parent=styles['Normal'],
            fontName=chinese_font_name,
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#7f8c8d'),
        )

        story = []

        # 标题
        story.append(Paragraph(f"📚 每日名词解释卡片", title_style))
        story.append(Spacer(1, 20))

        # 名词标题
        story.append(Paragraph(f"🔤 {term.term}", heading_style))
        story.append(Spacer(1, 10))

        # 元信息表格
        meta_data = [
            ['📅 日期', term.display_date.strftime('%Y年%m月%d日')],
            ['🏷️ 分类', term.category or '未分类'],
            ['📊 难度', term.get_difficulty_level_display()],
            ['👀 浏览量', f"{term.view_count} 次"],
            ['👍 点赞数', f"{term.like_count} 个"],
        ]

        meta_table = Table(meta_data, colWidths=[4*cm, 8*cm])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), chinese_font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(meta_table)
        story.append(Spacer(1, 20))

        # 详细解释
        story.append(Paragraph("📖 详细解释", heading_style))
        story.append(Paragraph(term.explanation, normal_style))
        story.append(Spacer(1, 15))

        # 扩展信息
        if term.extended_info:
            if term.extended_info.get('examples'):
                story.append(Paragraph("💡 实例", heading_style))
                for example in term.extended_info['examples']:
                    story.append(Paragraph(f"• {example}", normal_style))
                story.append(Spacer(1, 10))

            if term.extended_info.get('related_concepts'):
                story.append(Paragraph("🔗 相关概念", heading_style))
                for concept in term.extended_info['related_concepts']:
                    story.append(Paragraph(f"• {concept}", normal_style))
                story.append(Spacer(1, 10))

            if term.extended_info.get('applications'):
                story.append(Paragraph("🚀 应用场景", heading_style))
                for application in term.extended_info['applications']:
                    story.append(Paragraph(f"• {application}", normal_style))
                story.append(Spacer(1, 10))

        # 页脚信息
        story.append(Spacer(1, 30))
        footer_text = f"生成时间: {timezone.now().strftime('%Y年%m月%d日 %H:%M:%S')} | 计算机科学学习平台"
        story.append(Paragraph(footer_text, meta_style))

        # 构建PDF
        doc.build(story)
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()

        logger.info("每日名词PDF内容生成成功")

        # 生成文件名
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        import re
        safe_term = re.sub(r'[<>:"/\\|?*]', '', term.term)[:30]
        if not safe_term.strip():
            safe_term = '每日名词'
        filename = f"{safe_term}_名词卡片_{timestamp}.pdf"

        # 创建响应
        response = HttpResponse(pdf_content, content_type='application/pdf')
        # 设置文件名，支持中文文件名
        from urllib.parse import quote
        ascii_filename = f"DailyTerm_{term.id}_{timestamp}.pdf"
        encoded_filename = quote(filename.encode('utf-8'))
        response['Content-Disposition'] = f'inline; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'

        logger.info(f"每日名词PDF导出成功: {filename}")
        return response

    except Exception as e:
        import traceback
        logger.error(f"每日名词PDF导出失败: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        messages.error(request, f'PDF导出失败：{str(e)}')
        return redirect('knowledge_app:daily_term_detail', term_id=term_id)


def daily_term_history(request):
    """名词历史页面"""
    # 获取筛选参数
    category = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    search = request.GET.get('search', '')

    # 构建查询
    terms = DailyTerm.objects.filter(status='active')

    if category:
        terms = terms.filter(category=category)

    if difficulty:
        terms = terms.filter(difficulty_level=difficulty)

    if search:
        terms = terms.filter(
            models.Q(term__icontains=search) |
            models.Q(explanation__icontains=search)
        )

    # 分页
    paginator = Paginator(terms.order_by('-display_date'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 获取分类和难度选项
    categories = DailyTerm.objects.filter(status='active').values_list(
        'category', flat=True
    ).distinct()

    difficulties = DailyTerm.objects.filter(status='active').values_list(
        'difficulty_level', flat=True
    ).distinct()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'difficulties': difficulties,
        'current_category': category,
        'current_difficulty': difficulty,
        'current_search': search,
    }

    return render(request, 'knowledge_app/daily_term_history.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def daily_term_like(request, term_id):
    """点赞名词"""
    try:
        term = get_object_or_404(DailyTerm, id=term_id)
        term.increment_like_count()

        return JsonResponse({
            'success': True,
            'like_count': term.like_count,
            'message': '点赞成功！'
        })
    except Exception as e:
        logger.error(f"Failed to like term {term_id}: {e}")
        return JsonResponse({
            'success': False,
            'message': '点赞失败，请稍后重试'
        })


def daily_term_api(request):
    """每日名词API接口"""
    service = DailyTermService()
    today_term = service.get_today_term()

    if not today_term:
        return JsonResponse({
            'success': False,
            'message': '今日名词暂未生成'
        })

    return JsonResponse({
        'success': True,
        'data': {
            'id': today_term.id,
            'term': today_term.term,
            'explanation': today_term.explanation,
            'category': today_term.category,
            'difficulty': today_term.get_difficulty_level_display(),
            'display_date': today_term.display_date.isoformat(),
            'view_count': today_term.view_count,
            'like_count': today_term.like_count,
        }
    })


# ==================== 练习生成器相关视图 ====================

@csrf_exempt
@require_http_methods(["POST"])
def generate_exercises(request):
    """生成练习题API"""
    try:
        data = json.loads(request.body)
        knowledge_point = data.get('knowledge_point')
        difficulty = data.get('difficulty', 'medium')
        count = data.get('count', 5)

        if not knowledge_point:
            return JsonResponse({
                'success': False,
                'message': '缺少知识点参数'
            })

        # 检查用户是否登录
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': '请先登录'
            })

        from .services.exercise_generator_service import ExerciseGeneratorService
        service = ExerciseGeneratorService()

        # 生成练习会话
        session = service.generate_exercise_session(
            user=request.user,
            knowledge_point=knowledge_point,
            difficulty=difficulty,
            count=count
        )

        if session:
            return JsonResponse({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'knowledge_point': session.knowledge_point,
                    'total_questions': session.total_questions,
                    'exercises': session.exercises,
                    'started_at': session.started_at.isoformat()
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '生成练习题失败，请稍后重试'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f"Generate exercises error: {e}")
        return JsonResponse({
            'success': False,
            'message': '服务器内部错误'
        })


@csrf_exempt
@require_http_methods(["POST"])
def submit_exercise_answers(request):
    """提交练习答案API"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        answers = data.get('answers', [])

        if not session_id:
            return JsonResponse({
                'success': False,
                'message': '缺少会话ID'
            })

        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': '请先登录'
            })

        from .services.exercise_generator_service import ExerciseGeneratorService
        service = ExerciseGeneratorService()

        # 提交答案
        session = service.submit_answers(session_id, answers)

        if session:
            return JsonResponse({
                'success': True,
                'data': {
                    'session_id': session.id,
                    'score': session.score,
                    'accuracy_rate': session.get_accuracy_rate(),
                    'correct_count': session.correct_count,
                    'total_questions': session.total_questions,
                    'time_spent': session.time_spent
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '提交答案失败'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f"Submit exercise answers error: {e}")
        return JsonResponse({
            'success': False,
            'message': '服务器内部错误'
        })


@require_http_methods(["GET"])
def get_exercise_report(request, session_id):
    """获取练习报告API"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': '请先登录'
            })

        from .services.exercise_generator_service import ExerciseGeneratorService
        service = ExerciseGeneratorService()

        # 获取报告
        report = service.get_session_report(session_id)

        if report:
            return JsonResponse({
                'success': True,
                'data': report
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '未找到练习报告'
            })

    except Exception as e:
        logger.error(f"Get exercise report error: {e}")
        return JsonResponse({
            'success': False,
            'message': '服务器内部错误'
        })


def test_exercise(request):
    """测试练习生成器页面"""
    return render(request, 'knowledge_app/test_exercise.html')


# ==================== 关于页面和成就系统 ====================

def about(request):
    """关于页面"""
    # 获取一些统计数据
    from .models import KnowledgePoint
    from .personal_quiz_models import QuizLibrary, QuizQuestion, QuizSession
    from django.contrib.auth import get_user_model

    User = get_user_model()

    stats = {
        'knowledge_points': KnowledgePoint.objects.filter(is_active=True).count(),
        'quiz_libraries': QuizLibrary.objects.count(),
        'quiz_questions': QuizQuestion.objects.count(),
        'quiz_sessions': QuizSession.objects.count(),
        'registered_users': User.objects.count(),
    }

    # 获取最新更新信息
    latest_updates = [
        {
            'version': 'v1.0.0',
            'date': '2025-08-03',
            'features': [
                '🎓 上线每日名词功能，帮助初学者每天学习一个新概念',
                '🌌 发布CS宇宙知识图谱，可视化展示知识结构',
                '📝 推出新手友好的练习题库，从基础开始循序渐进',
                '🤖 集成AI学习助手，为初学者提供个性化指导',
                '🏆 建立成就系统，激励初学者持续学习',
                '📱 响应式设计，支持手机和电脑学习'
            ]
        }
    ]

    context = {
        'stats': stats,
        'latest_updates': latest_updates,
    }

    return render(request, 'knowledge_app/about.html', context)


def debug_universe(request):
    """Universe调试页面"""
    from django.http import HttpResponse
    try:
        with open('debug_universe.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("调试文件未找到", content_type='text/plain')


# ==================== 新增知识点页面视图 ====================

def backtracking_page(request):
    """回溯算法页面"""
    return render(request, 'knowledge_app/backtracking.html')


def linked_list_page(request):
    """单链表页面"""
    return render(request, 'knowledge_app/linked_list.html')


def binary_search_page(request):
    """二分查找页面"""
    return render(request, 'knowledge_app/binary_search.html')


def quick_sort_page(request):
    """快速排序页面"""
    return render(request, 'knowledge_app/quick_sort.html')


def hash_table_page(request):
    """哈希表页面"""
    return render(request, 'knowledge_app/hash_table.html')


def binary_search_tree_page(request):
    """二叉搜索树页面"""
    return render(request, 'knowledge_app/binary_search_tree.html')


def achievements(request):
    """成就列表页面"""
    # 这里可以添加成就系统的逻辑
    # 目前先返回一个基本的成就列表

    achievements_data = [
        {
            'id': 1,
            'name': '初学者',
            'description': '完成第一道练习题',
            'icon': '🌱',
            'category': 'practice',
            'points': 10,
            'unlocked': True if request.user.is_authenticated else False,
            'progress': 100 if request.user.is_authenticated else 0,
            'unlock_date': '2025-08-01' if request.user.is_authenticated else None,
        },
        {
            'id': 2,
            'name': '勤奋学习者',
            'description': '连续7天访问平台',
            'icon': '📚',
            'category': 'engagement',
            'points': 50,
            'unlocked': False,
            'progress': 60,
            'unlock_date': None,
        },
        {
            'id': 3,
            'name': '知识探索者',
            'description': '浏览50个不同的知识点',
            'icon': '🔍',
            'category': 'exploration',
            'points': 100,
            'unlocked': False,
            'progress': 30,
            'unlock_date': None,
        },
        {
            'id': 4,
            'name': '练习达人',
            'description': '完成100道练习题',
            'icon': '💪',
            'category': 'practice',
            'points': 200,
            'unlocked': False,
            'progress': 15,
            'unlock_date': None,
        },
        {
            'id': 5,
            'name': '完美主义者',
            'description': '连续答对20道题',
            'icon': '🎯',
            'category': 'accuracy',
            'points': 150,
            'unlocked': False,
            'progress': 0,
            'unlock_date': None,
        },
        {
            'id': 6,
            'name': 'CS大师',
            'description': '在所有分类中都获得80%以上正确率',
            'icon': '👑',
            'category': 'mastery',
            'points': 500,
            'unlocked': False,
            'progress': 5,
            'unlock_date': None,
        }
    ]

    # 按类别分组
    categories = {
        'practice': {'name': '练习成就', 'icon': '📝', 'achievements': []},
        'engagement': {'name': '参与成就', 'icon': '🔥', 'achievements': []},
        'exploration': {'name': '探索成就', 'icon': '🌟', 'achievements': []},
        'accuracy': {'name': '精准成就', 'icon': '🎯', 'achievements': []},
        'mastery': {'name': '大师成就', 'icon': '👑', 'achievements': []},
    }

    for achievement in achievements_data:
        category = achievement['category']
        if category in categories:
            categories[category]['achievements'].append(achievement)

    # 计算总体统计
    total_achievements = len(achievements_data)
    unlocked_achievements = len([a for a in achievements_data if a['unlocked']])
    total_points = sum(a['points'] for a in achievements_data if a['unlocked'])

    context = {
        'categories': categories,
        'total_achievements': total_achievements,
        'unlocked_achievements': unlocked_achievements,
        'total_points': total_points,
        'completion_rate': round((unlocked_achievements / total_achievements) * 100, 1) if total_achievements > 0 else 0,
    }

    return render(request, 'knowledge_app/achievements.html', context)


def achievement_detail(request, achievement_id):
    """成就详情页面"""
    # 模拟成就数据（实际应该从数据库获取）
    achievements_data = {
        1: {
            'id': 1,
            'name': '初学者',
            'description': '完成第一道练习题',
            'detailed_description': '欢迎来到计算机科学学习平台！完成第一道练习题是您学习旅程的重要第一步。这个成就标志着您已经开始了实践学习的过程。',
            'icon': '🌱',
            'category': 'practice',
            'points': 10,
            'unlocked': True if request.user.is_authenticated else False,
            'progress': 100 if request.user.is_authenticated else 0,
            'unlock_date': '2025-08-01' if request.user.is_authenticated else None,
            'requirements': [
                '注册账户',
                '选择任意一道练习题',
                '提交答案（无论对错）'
            ],
            'tips': [
                '不要害怕犯错，错误是学习的一部分',
                '仔细阅读题目，理解题意后再作答',
                '可以使用提示功能帮助理解'
            ],
            'related_achievements': [2, 4],
            'difficulty': 'easy',
            'rarity': 'common'
        },
        2: {
            'id': 2,
            'name': '勤奋学习者',
            'description': '连续7天访问平台',
            'detailed_description': '持续学习是掌握计算机科学知识的关键。连续7天访问平台展现了您对学习的坚持和热情。保持这种学习习惯，您将在知识的道路上走得更远。',
            'icon': '📚',
            'category': 'engagement',
            'points': 50,
            'unlocked': False,
            'progress': 60,
            'unlock_date': None,
            'requirements': [
                '连续7天登录平台',
                '每天至少浏览一个知识点或完成一道题'
            ],
            'tips': [
                '设置每日学习提醒',
                '制定合理的学习计划',
                '即使很忙也要保持每天的学习习惯'
            ],
            'related_achievements': [3, 6],
            'difficulty': 'medium',
            'rarity': 'uncommon'
        },
        # 可以继续添加其他成就的详细信息
    }

    achievement = achievements_data.get(achievement_id)
    if not achievement:
        from django.http import Http404
        raise Http404("成就不存在")

    # 获取相关成就
    related_achievements = []
    for related_id in achievement.get('related_achievements', []):
        if related_id in achievements_data:
            related_achievements.append(achievements_data[related_id])

    context = {
        'achievement': achievement,
        'related_achievements': related_achievements,
    }

    return render(request, 'knowledge_app/achievement_detail.html', context)


def feedback_survey(request):
    """反馈问卷页面"""
    return render(request, 'knowledge_app/feedback_survey.html')


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["POST"])
def submit_feedback_survey(request):
    """提交反馈问卷"""
    try:
        import json
        import logging
        from django.http import JsonResponse
        from django.utils import timezone

        # 获取问卷数据
        data = json.loads(request.body)

        # 这里可以保存到数据库或发送邮件
        # 目前先简单记录到日志
        logger = logging.getLogger(__name__)

        feedback_info = {
            'timestamp': timezone.now().isoformat(),
            'user_type': data.get('userType'),
            'experience_rating': data.get('experienceRating'),
            'most_useful_feature': data.get('mostUsefulFeature'),
            'improvement_suggestions': data.get('improvementSuggestions'),
            'new_features': data.get('newFeatures'),
            'difficulty_rating': data.get('difficultyRating'),
            'recommendation_rating': data.get('recommendationRating'),
            'additional_comments': data.get('additionalComments'),
            'contact_email': data.get('contactEmail', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
        }

        logger.info(f"收到用户反馈: {feedback_info}")

        # 可以在这里添加邮件发送功能
        # send_feedback_email(feedback_info)

        return JsonResponse({
            'success': True,
            'message': '感谢您的反馈！您的意见对我们非常重要。'
        })

    except Exception as e:
        logger.error(f"处理反馈问卷时出错: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '提交失败，请稍后重试或直接发送邮件给我们。'
        })


def test_chatbot(request):
    """测试GLM聊天机器人页面"""
    return render(request, 'knowledge_app/test_chatbot.html')


def test_themes(request):
    """测试主题系统页面"""
    return render(request, 'knowledge_app/test_themes.html')


# ==================== GLM聊天机器人相关视图 ====================

@csrf_exempt
@require_http_methods(["POST"])
def chat_about_term(request):
    """与GLM聊天机器人讨论名词"""
    try:
        data = json.loads(request.body)
        term = data.get('term')
        term_explanation = data.get('explanation')
        user_question = data.get('question')
        theme = data.get('theme', 'friendly')  # 获取主题参数

        if not all([term, term_explanation, user_question]):
            return JsonResponse({
                'success': False,
                'error': '缺少必要参数'
            })

        from .services.glm_chatbot_service import GLMChatbotService
        service = GLMChatbotService()

        # 检查服务是否可用
        if not service.is_available():
            return JsonResponse({
                'success': False,
                'error': 'GLM聊天服务暂时不可用，请检查API配置'
            })

        # 获取用户ID（如果已登录）
        user_id = request.user.id if request.user.is_authenticated else None

        # 询问AI（传递主题参数）
        result = service.ask_about_term(term, term_explanation, user_question, user_id, theme)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f"Chat about term error: {e}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        })


@require_http_methods(["GET"])
def get_suggested_questions(request):
    """获取推荐问题"""
    try:
        term = request.GET.get('term')
        term_explanation = request.GET.get('explanation')

        if not all([term, term_explanation]):
            return JsonResponse({
                'success': False,
                'error': '缺少必要参数'
            })

        from .services.glm_chatbot_service import GLMChatbotService
        service = GLMChatbotService()

        # 获取推荐问题
        result = service.get_suggested_questions(term, term_explanation)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Get suggested questions error: {e}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        })


@require_http_methods(["GET"])
def chatbot_status(request):
    """获取聊天机器人状态"""
    try:
        from .services.glm_chatbot_service import GLMChatbotService
        service = GLMChatbotService()

        status = service.get_service_status()

        return JsonResponse({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"Get chatbot status error: {e}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        })


# ==================== 主题管理相关视图 ====================

@require_http_methods(["GET"])
def get_chatbot_themes(request):
    """获取所有聊天机器人主题"""
    try:
        from .services.glm_chatbot_service import GLMChatbotService
        service = GLMChatbotService()

        themes = service.get_all_themes()
        current_theme = service.get_current_theme()

        return JsonResponse({
            'success': True,
            'themes': themes,
            'current_theme': service.current_theme,
            'current_theme_info': current_theme
        })

    except Exception as e:
        logger.error(f"Get chatbot themes error: {e}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        })


@csrf_exempt
@require_http_methods(["POST"])
def set_chatbot_theme(request):
    """设置聊天机器人主题"""
    try:
        data = json.loads(request.body)
        theme_key = data.get('theme')

        if not theme_key:
            return JsonResponse({
                'success': False,
                'error': '缺少主题参数'
            })

        from .services.glm_chatbot_service import GLMChatbotService
        service = GLMChatbotService()

        success = service.set_theme(theme_key)

        if success:
            # 可以在这里保存用户的主题偏好到数据库
            if request.user.is_authenticated:
                # TODO: 保存用户主题偏好
                pass

            return JsonResponse({
                'success': True,
                'theme': theme_key,
                'theme_info': service.get_current_theme()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '无效的主题'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f"Set chatbot theme error: {e}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        })


def theme_showcase(request):
    """主题展示页面"""
    return render(request, 'knowledge_app/theme_showcase.html')


# ==================== 知识图谱相关视图 ====================

def knowledge_graph(request):
    """知识图谱主页面"""
    from .services.knowledge_graph_service import KnowledgeGraphService
    from .services.prerequisite_service import PrerequisiteService
    from .knowledge_graph_models import ConceptNode
    from django.db.models import Count

    service = KnowledgeGraphService()
    prereq_service = PrerequisiteService()

    # 获取分类统计
    categories = ConceptNode.objects.filter(is_active=True).values('category').annotate(
        count=Count('id')
    ).order_by('-count')

    # 获取推荐
    recommendations = service.get_learning_recommendations(request.user, limit=6)

    # 构建前置知识图
    prereq_service.build_prerequisite_graph()

    context = {
        'categories': categories,
        'recommendations': recommendations,
    }

    return render(request, 'knowledge_app/knowledge_graph.html', context)



def prerequisite_graph(request):
    """前置关系图谱页面"""
    return render(request, 'knowledge_app/prerequisite_graph.html')


@require_http_methods(["GET"])
def api_graph_data(request):
    """获取图谱数据API"""
    try:
        from .services.knowledge_graph_service import KnowledgeGraphService

        service = KnowledgeGraphService()

        # 获取参数
        category = request.GET.get('category')
        max_nodes = int(request.GET.get('max_nodes', 50))
        layout = request.GET.get('layout', 'force_directed')

        # 获取图谱数据
        graph_data = service.get_graph_data(
            category=category,
            max_nodes=max_nodes,
            layout=layout
        )

        return JsonResponse({
            'success': True,
            'data': graph_data
        })

    except Exception as e:
        logger.error(f"Get graph data error: {e}")
        return JsonResponse({
            'success': False,
            'error': '获取图谱数据失败'
        })


@require_http_methods(["GET"])
def api_concept_details(request, concept_id):
    """获取概念详情API"""
    try:
        from .services.knowledge_graph_service import KnowledgeGraphService

        service = KnowledgeGraphService()

        # 获取概念详情
        details = service.get_concept_details(concept_id, request.user)

        if not details:
            return JsonResponse({
                'success': False,
                'error': '概念不存在'
            })

        # 更新查看统计
        service.update_concept_stats(concept_id, 'view')

        return JsonResponse({
            'success': True,
            'data': details
        })

    except Exception as e:
        logger.error(f"Get concept details error: {e}")
        return JsonResponse({
            'success': False,
            'error': '获取概念详情失败'
        })


@csrf_exempt
@require_http_methods(["POST"])
def api_record_learning(request):
    """记录学习行为API"""
    try:
        data = json.loads(request.body)
        concept_id = data.get('concept_id')
        study_time = data.get('study_time', 0)

        if not concept_id:
            return JsonResponse({
                'success': False,
                'error': '缺少概念ID'
            })

        from .services.knowledge_graph_service import KnowledgeGraphService
        service = KnowledgeGraphService()

        # 记录学习行为
        progress = service.record_user_learning(
            request.user,
            concept_id,
            study_time
        )

        if progress is None:
            return JsonResponse({
                'success': False,
                'error': '记录学习行为失败'
            })

        return JsonResponse({
            'success': True,
            'data': progress
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '请求数据格式错误'
        })
    except Exception as e:
        logger.error(f"Record learning error: {e}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        })


@require_http_methods(["GET"])
def api_learning_recommendations(request):
    """获取学习推荐API"""
    try:
        from .services.knowledge_graph_service import KnowledgeGraphService

        service = KnowledgeGraphService()
        limit = int(request.GET.get('limit', 10))

        recommendations = service.get_learning_recommendations(request.user, limit)

        return JsonResponse({
            'success': True,
            'data': recommendations
        })

    except Exception as e:
        logger.error(f"Get recommendations error: {e}")
        return JsonResponse({
            'success': False,
            'error': '获取推荐失败'
        })


def kruskal_algorithm(request):
    """Kruskal算法页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 Kruskal算法页面")

    context = {
        'title': '最小生成树——Kruskal算法',
        'description': '数据结构 - 图的最小生成树算法可视化演示与代码实现'
    }

    return render(request, 'knowledge_app/kruskal.html', context)


def prim_algorithm(request):
    """Prim算法页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 Prim算法页面")

    context = {
        'title': '最小生成树——Prim算法',
        'description': '数据结构 - 图的最小生成树算法可视化演示与代码实现'
    }

    return render(request, 'knowledge_app/prim.html', context)


def stack_interactive(request):
    """栈交互式演示页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 栈交互式演示页面")

    context = {
        'title': '栈 - 交互式演示',
        'description': '数据结构 - 后进先出(LIFO)的线性数据结构可视化演示与应用'
    }

    return render(request, 'knowledge_app/stack_interactive.html', context)


def queue_interactive(request):
    """队列交互式演示页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 队列交互式演示页面")

    context = {
        'title': '队列 - 交互式演示',
        'description': '数据结构 - 先进先出(FIFO)的线性数据结构可视化演示与应用'
    }

    return render(request, 'knowledge_app/queue_interactive.html', context)


def binary_tree_interactive(request):
    """二叉树交互式演示页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 二叉树交互式演示页面")

    context = {
        'title': '二叉树 - 交互式演示',
        'description': '数据结构 - 树形结构的基础，支持高效的查找、插入和删除操作'
    }

    return render(request, 'knowledge_app/binary_tree_interactive.html', context)


def sorting_interactive(request):
    """排序算法交互式演示页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 排序算法交互式演示页面")

    context = {
        'title': '排序算法 - 交互式演示',
        'description': '算法基础 - 多种经典排序算法的可视化演示与性能对比'
    }

    return render(request, 'knowledge_app/sorting_interactive.html', context)


def avl_tree(request):
    """AVL树可视化系统页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 AVL树可视化系统页面")

    context = {
        'title': 'AVL树可视化系统',
        'description': '数据结构 - 自平衡二叉搜索树，通过旋转操作保持树的平衡性'
    }

    return render(request, 'knowledge_app/avl-0e3587fa.html', context)


def red_black_tree(request):
    """红黑树可视化系统页面"""
    logger.info(f"用户 {request.user.username if request.user.is_authenticated else 'Anonymous'} 访问 红黑树可视化系统页面")

    context = {
        'page_title': '红黑树',
        'page_icon': '🔴',
        'breadcrumb_category': '数据结构',
        'page_description': '自平衡二叉搜索树 - 高效稳定的数据结构，广泛应用于现代编程语言和系统中',
    }

    return render(request, 'knowledge_app/red-black-tree.html', context)


# ==================== 练习题管理相关视图 ====================

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .exercise_models import Exercise
import csv
from io import StringIO

@staff_member_required
def exercise_preview(request, exercise_id):
    """练习题预览"""
    exercise = get_object_or_404(Exercise, id=exercise_id)

    context = {
        'exercise': exercise,
        'is_preview': True,
    }

    return render(request, 'admin/exercise_preview.html', context)


@staff_member_required
def exercise_test(request, exercise_id):
    """练习题测试答题"""
    exercise = get_object_or_404(Exercise, id=exercise_id)

    context = {
        'exercise': exercise,
        'is_test': True,
    }

    return render(request, 'admin/exercise_test.html', context)


@staff_member_required
def exercise_templates(request):
    """练习题模板管理"""
    templates = [
        {
            'name': '单选题模板',
            'type': 'single_choice',
            'icon': '🔘',
            'description': '适用于只有一个正确答案的题目',
            'example': '数组的时间复杂度是？',
            'template': {
                'title': '示例单选题',
                'question_text': '以下哪个是正确的描述？',
                'options': {
                    'A': '选项A的内容',
                    'B': '选项B的内容',
                    'C': '选项C的内容',
                    'D': '选项D的内容'
                },
                'correct_answer': 'A',
                'explanation': '这里填写详细的答案解析...',
                'hints': [
                    '考虑基本概念的定义',
                    '想想实际应用场景',
                    '参考教材中的相关内容'
                ]
            }
        },
        {
            'name': '多选题模板',
            'type': 'multiple_choice',
            'icon': '☑️',
            'description': '适用于有多个正确答案的题目',
            'example': '以下哪些是排序算法？',
            'template': {
                'title': '示例多选题',
                'question_text': '以下哪些选项是正确的？（多选）',
                'options': {
                    'A': '选项A的内容',
                    'B': '选项B的内容',
                    'C': '选项C的内容',
                    'D': '选项D的内容'
                },
                'correct_answer': 'A,C',
                'explanation': '这里填写详细的答案解析...',
                'hints': [
                    '仔细分析每个选项',
                    '可能有多个正确答案',
                    '排除明显错误的选项'
                ]
            }
        },
        {
            'name': '判断题模板',
            'type': 'true_false',
            'icon': '✅',
            'description': '适用于对错判断类题目',
            'example': '栈是先进先出的数据结构',
            'template': {
                'title': '示例判断题',
                'question_text': '请判断以下说法是否正确：',
                'correct_answer': 'true',
                'explanation': '这里填写详细的答案解析...',
                'hints': [
                    '回忆基本概念',
                    '考虑特殊情况',
                    '参考定义和性质'
                ]
            }
        },
        {
            'name': '填空题模板',
            'type': 'fill_blank',
            'icon': '📝',
            'description': '适用于需要填写答案的题目',
            'example': '二分查找的时间复杂度是____',
            'template': {
                'title': '示例填空题',
                'question_text': '请在空白处填入正确答案：____',
                'correct_answer': '正确答案',
                'explanation': '这里填写详细的答案解析...',
                'hints': [
                    '考虑相关公式',
                    '注意答案格式',
                    '检查单位和符号'
                ]
            }
        },
        {
            'name': '简答题模板',
            'type': 'short_answer',
            'icon': '📄',
            'description': '适用于需要详细回答的题目',
            'example': '请解释快速排序的原理',
            'template': {
                'title': '示例简答题',
                'question_text': '请详细回答以下问题：',
                'correct_answer': '参考答案内容...',
                'explanation': '这里填写详细的答案解析...',
                'hints': [
                    '从基本概念开始',
                    '举例说明',
                    '总结要点'
                ]
            }
        },
        {
            'name': '编程题模板',
            'type': 'coding',
            'icon': '💻',
            'description': '适用于代码编写类题目',
            'example': '实现二分查找算法',
            'template': {
                'title': '示例编程题',
                'question_text': '请编写代码实现以下功能：',
                'correct_answer': '// 参考代码\nfunction example() {\n    // 实现逻辑\n}',
                'explanation': '这里填写详细的代码解析...',
                'hints': [
                    '分析算法思路',
                    '考虑边界条件',
                    '优化时间复杂度'
                ]
            }
        }
    ]

    context = {
        'templates': templates,
    }

    return render(request, 'admin/exercise_templates.html', context)


@staff_member_required
def exercise_import(request):
    """练习题批量导入"""
    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']

            try:
                # 读取CSV文件
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(StringIO(decoded_file))

                imported_count = 0
                errors = []

                for row_num, row in enumerate(csv_data, start=2):
                    try:
                        # 验证必填字段
                        required_fields = ['title', 'question_text', 'correct_answer', 'category', 'difficulty', 'question_type']
                        for field in required_fields:
                            if not row.get(field, '').strip():
                                errors.append(f'第{row_num}行：{field}字段不能为空')
                                continue

                        # 获取或创建分类和难度
                        from .exercise_models import ExerciseCategory, ExerciseDifficulty

                        category, _ = ExerciseCategory.objects.get_or_create(
                            name=row['category'],
                            defaults={'slug': row['category'].lower().replace(' ', '-')}
                        )

                        difficulty, _ = ExerciseDifficulty.objects.get_or_create(
                            name=row['difficulty'],
                            defaults={'level': 1}
                        )

                        # 处理选项（如果是选择题）
                        options = {}
                        if row['question_type'] in ['single_choice', 'multiple_choice']:
                            for key in ['A', 'B', 'C', 'D', 'E', 'F']:
                                option_value = row.get(f'option_{key}', '').strip()
                                if option_value:
                                    options[key] = option_value

                        # 处理提示
                        hints = []
                        for i in range(1, 6):  # 最多5个提示
                            hint = row.get(f'hint_{i}', '').strip()
                            if hint:
                                hints.append(hint)

                        # 创建练习题
                        exercise = Exercise.objects.create(
                            title=row['title'].strip(),
                            slug=row.get('slug', '').strip() or row['title'].lower().replace(' ', '-'),
                            category=category,
                            difficulty=difficulty,
                            question_type=row['question_type'].strip(),
                            question_text=row['question_text'].strip(),
                            options=options,
                            correct_answer=row['correct_answer'].strip(),
                            explanation=row.get('explanation', '').strip(),
                            hints=hints,
                            tags=row.get('tags', '').strip(),
                            time_limit=int(row.get('time_limit', 0) or 0),
                            is_active=row.get('is_active', 'true').lower() == 'true',
                            is_featured=row.get('is_featured', 'false').lower() == 'true'
                        )

                        imported_count += 1

                    except Exception as e:
                        errors.append(f'第{row_num}行：{str(e)}')

                # 返回结果
                context = {
                    'imported_count': imported_count,
                    'errors': errors,
                    'success': imported_count > 0
                }

                return render(request, 'admin/exercise_import_result.html', context)

            except Exception as e:
                context = {
                    'error': f'文件处理错误：{str(e)}'
                }
                return render(request, 'admin/exercise_import.html', context)

    # 生成CSV模板
    sample_data = [
        {
            'title': '示例单选题',
            'slug': 'example-single-choice',
            'category': '数据结构',
            'difficulty': '初级',
            'question_type': 'single_choice',
            'question_text': '以下哪个是正确的描述？',
            'option_A': '选项A的内容',
            'option_B': '选项B的内容',
            'option_C': '选项C的内容',
            'option_D': '选项D的内容',
            'correct_answer': 'A',
            'explanation': '这里填写详细的答案解析',
            'hint_1': '考虑基本概念',
            'hint_2': '想想实际应用',
            'hint_3': '参考教材内容',
            'tags': '数组,基础,概念',
            'time_limit': '300',
            'is_active': 'true',
            'is_featured': 'false'
        }
    ]

    context = {
        'sample_data': sample_data,
    }

    return render(request, 'admin/exercise_import.html', context)


@staff_member_required
def exercise_export(request):
    """练习题批量导出"""
    # 获取查询参数
    category_id = request.GET.get('category')
    difficulty_id = request.GET.get('difficulty')
    question_type = request.GET.get('question_type')

    # 构建查询
    exercises = Exercise.objects.all()

    if category_id:
        exercises = exercises.filter(category_id=category_id)
    if difficulty_id:
        exercises = exercises.filter(difficulty_id=difficulty_id)
    if question_type:
        exercises = exercises.filter(question_type=question_type)

    # 创建CSV响应
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="exercises_export.csv"'

    # 添加BOM以支持Excel中文显示
    response.write('\ufeff')

    writer = csv.writer(response)

    # 写入表头
    headers = [
        'title', 'slug', 'category', 'difficulty', 'question_type',
        'question_text', 'option_A', 'option_B', 'option_C', 'option_D',
        'option_E', 'option_F', 'correct_answer', 'explanation',
        'hint_1', 'hint_2', 'hint_3', 'hint_4', 'hint_5',
        'tags', 'time_limit', 'is_active', 'is_featured'
    ]
    writer.writerow(headers)

    # 写入数据
    for exercise in exercises:
        row = [
            exercise.title,
            exercise.slug,
            exercise.category.name,
            exercise.difficulty.name,
            exercise.question_type,
            exercise.question_text,
        ]

        # 添加选项
        options = exercise.options or {}
        for key in ['A', 'B', 'C', 'D', 'E', 'F']:
            row.append(options.get(key, ''))

        row.extend([
            exercise.correct_answer,
            exercise.explanation,
        ])

        # 添加提示
        hints = exercise.hints or []
        for i in range(5):
            row.append(hints[i] if i < len(hints) else '')

        row.extend([
            exercise.tags,
            exercise.time_limit,
            exercise.is_active,
            exercise.is_featured
        ])

        writer.writerow(row)

    return response







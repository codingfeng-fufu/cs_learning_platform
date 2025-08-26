from django.urls import path, include
from . import views
from . import personal_quiz_views
from . import share_views

app_name = 'knowledge_app'

urlpatterns = [
    # 主页和详情页
    path('', views.index, name='index'),

    # 特殊算法页面（需要在通用路由之前）
    path('learn/kruskal/', views.kruskal_algorithm, name='kruskal'),
    path('learn/prim/', views.prim_algorithm, name='prim'),

    # 新增的知识点页面
    path('backtracking/', views.backtracking_page, name='backtracking'),
    path('linked-list/', views.linked_list_page, name='linked_list_page'),
    path('binary-search/', views.binary_search_page, name='binary_search'),
    path('quick-sort/', views.quick_sort_page, name='quick_sort'),
    path('hash-table/', views.hash_table_page, name='hash_table'),
    path('binary-search-tree/', views.binary_search_tree_page, name='binary_search_tree'),

    # 通用知识点详情页
    path('learn/<slug:slug>/', views.knowledge_detail, name='detail'),

    # CS Universe页面
    path('universe/', views.cs_universe, name='cs_universe'),
    path('graph_dfs/',views.get_graph_dfs,name='graph_dfs'),

    # 搜索功能
    path('search/', views.search, name='search'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/search/', views.search_api, name='search_api'),



    # 大分类概览页面
    path('category/data-structures/', views.data_structures, name='data_structures'),
    path('category/algorithm-design/', views.algorithm_design, name='algorithm_design'),
    path('category/computer-networks/', views.computer_networks, name='computer_networks'),
    path('category/operating-systems/', views.operating_systems, name='operating_systems'),
    path('category/database-systems/', views.database_systems, name='database_systems'),
    path('category/software-engineering/', views.software_engineering, name='software_engineering'),

    # 行星页面（子分类概览）
    path('planet/linked-list/', views.linked_list, name='linked_list'),
    path('planet/double-linked-list/', views.double_linked_list, name='double_linked_list'),
    path('planet/circular-linked-list/', views.circular_linked_list, name='circular_linked_list'),
    path('planet/stack/', views.stack, name='stack'),
    path('planet/queue/', views.queue, name='queue'),
    path('planet/divide-conquer/', views.divide_conquer, name='divide_conquer'),
    path('planet/dynamic-programming/', views.dynamic_programming, name='dynamic_programming'),
    path('planet/physical-layer/', views.physical_layer, name='physical_layer'),
    path('planet/data-link-layer/', views.data_link_layer, name='data_link_layer'),
    path('planet/matrix/', views.matrix, name='matrix'),
    path('planet/tree-binary-tree/', views.tree_binary_tree, name='tree_binary_tree'),
    path('planet/graph/', views.graph, name='graph'),
    path('planet/search/', views.search, name='search'),
    path('planet/sorting/', views.sorting, name='sorting'),
    path('planet/greedy-algorithm/', views.greedy_algorithm, name='greedy_algorithm'),
    path('planet/backtracking/', views.backtracking, name='backtracking'),
    path('planet/graph-algorithms/', views.graph_algorithms, name='graph_algorithms'),
    path('planet/string-algorithms/', views.string_algorithms, name='string_algorithms'),
    path('planet/numerical-algorithms/', views.numerical_algorithms, name='numerical_algorithms'),
    path('planet/network-layer/', views.network_layer, name='network_layer'),
    path('planet/transport-layer/', views.transport_layer, name='transport_layer'),
    path('planet/application-layer/', views.application_layer, name='application_layer'),
    path('planet/network-security/', views.network_security, name='network_security'),
    path('planet/process-management/', views.process_management, name='process_management'),
    path('planet/thread-management/', views.thread_management, name='thread_management'),
    path('planet/memory-management/', views.memory_management, name='memory_management'),
    path('planet/file-system/', views.file_system, name='file_system'),
    path('planet/device-management/', views.device_management, name='device_management'),
    path('planet/system-calls/', views.system_calls, name='system_calls'),
    path('planet/relational-model/', views.relational_model, name='relational_model'),
    path('planet/sql-language/', views.sql_language, name='sql_language'),
    path('planet/transaction-management/', views.transaction_management, name='transaction_management'),
    path('planet/indexing/', views.indexing, name='indexing'),
    path('planet/query-processing/', views.query_processing, name='query_processing'),
    path('planet/distributed-database/', views.distributed_database, name='distributed_database'),
    path('planet/requirements-engineering/', views.requirements_engineering, name='requirements_engineering'),
    path('planet/system-design/', views.system_design, name='system_design'),
    path('planet/software-testing/', views.software_testing, name='software_testing'),
    path('planet/project-management/', views.project_management, name='project_management'),
    path('planet/version-control/', views.version_control, name='version_control'),
    path('planet/design-patterns/', views.design_patterns, name='design_patterns'),

    # 海明码API接口
    path('api/hamming/encode/', views.hamming_encode_api, name='hamming_encode'),
    path('api/hamming/decode/', views.hamming_decode_api, name='hamming_decode'),

    # CRC API接口
    path('api/crc/calculate/', views.crc_calculate_api, name='crc_calculate'),
    path('api/crc/verify/', views.crc_verify_api, name='crc_verify'),

    # Single LinkList API接口
    path('api/linkedlist/add/', views.linked_list_add_api, name='linked_list_add'),
    path('api/linkedlist/delete/', views.linked_list_delete_api, name='linked_list_delete'),
    path('api/linkedlist/clear/', views.linked_list_clear_api, name='linked_list_clear'),
    path('api/linkedlist/status/', views.linked_list_status_api, name='linked_list_status'),
    path('api/linkedlist/insert/', views.linked_list_insert_api, name='linked_list_insert'),
    path('api/linkedlist/search/', views.linked_list_search_api, name='linked_list_search'),

    # 每日名词相关
    path('daily-term/', views.daily_term, name='daily_term'),
    path('daily-term/<int:term_id>/', views.daily_term_detail, name='daily_term_detail'),
    path('daily-term/<int:term_id>/export-pdf/', views.export_daily_term_pdf, name='export_daily_term_pdf'),
    path('daily-term/history/', views.daily_term_history, name='daily_term_history'),
    path('api/daily-term/like/<int:term_id>/', views.daily_term_like, name='daily_term_like'),
    path('api/daily-term/', views.daily_term_api, name='daily_term_api'),

    # 关于页面和成就系统
    path('about/', views.about, name='about'),
    path('debug-universe/', views.debug_universe, name='debug_universe'),
    path('achievements/', views.achievements, name='achievements'),
    path('achievements/<int:achievement_id>/', views.achievement_detail, name='achievement_detail'),

    # 反馈问卷
    path('feedback-survey/', views.feedback_survey, name='feedback_survey'),
    path('api/feedback-survey/', views.submit_feedback_survey, name='submit_feedback_survey'),

    # 练习生成器相关
    path('api/exercises/generate/', views.generate_exercises, name='generate_exercises'),
    path('api/exercises/submit/', views.submit_exercise_answers, name='submit_exercise_answers'),
    path('api/exercises/report/<int:session_id>/', views.get_exercise_report, name='get_exercise_report'),
    path('test-exercise/', views.test_exercise, name='test_exercise'),

    # GLM聊天机器人相关
    path('api/chatbot/ask/', views.chat_about_term, name='chat_about_term'),
    path('api/chatbot/questions/', views.get_suggested_questions, name='get_suggested_questions'),
    path('api/chatbot/status/', views.chatbot_status, name='chatbot_status'),
    path('test-chatbot/', views.test_chatbot, name='test_chatbot'),

    # 主题管理相关
    path('api/themes/chatbot/', views.get_chatbot_themes, name='get_chatbot_themes'),
    path('api/themes/chatbot/set/', views.set_chatbot_theme, name='set_chatbot_theme'),
    path('test-themes/', views.test_themes, name='test_themes'),
    path('themes/', views.theme_showcase, name='theme_showcase'),

    # 知识图谱相关
    path('knowledge-graph/', views.knowledge_graph, name='knowledge_graph'),
    path('prerequisite-graph/', views.prerequisite_graph, name='prerequisite_graph'),
    path('api/graph/data/', views.api_graph_data, name='api_graph_data'),
    path('api/graph/concept/<int:concept_id>/', views.api_concept_details, name='api_concept_details'),
    path('api/graph/record-learning/', views.api_record_learning, name='api_record_learning'),
    path('api/graph/recommendations/', views.api_learning_recommendations, name='api_learning_recommendations'),

    # 练习题管理相关
    path('exercise-admin/preview/<int:exercise_id>/', views.exercise_preview, name='exercise_preview'),
    path('exercise-admin/test/<int:exercise_id>/', views.exercise_test, name='exercise_test'),
    path('exercise-admin/import/', views.exercise_import, name='exercise_import'),
    path('exercise-admin/export/', views.exercise_export, name='exercise_export'),
    path('exercise-admin/templates/', views.exercise_templates, name='exercise_templates'),



    # 数据结构可视化
    path('avl-tree/', views.avl_tree, name='avl_tree'),
    path('red-black-tree/', views.red_black_tree, name='red_black_tree'),

    # 个人题库系统
    path('quiz/', personal_quiz_views.quiz_dashboard, name='quiz_dashboard'),
    path('quiz/libraries/', personal_quiz_views.library_list, name='quiz_library_list'),
    path('quiz/libraries/create/', personal_quiz_views.create_library, name='quiz_create_library'),
    path('quiz/libraries/<int:library_id>/', personal_quiz_views.library_detail, name='quiz_library_detail'),
    path('quiz/libraries/<int:library_id>/questions/create/', personal_quiz_views.create_question, name='quiz_create_question'),
    path('quiz/libraries/<int:library_id>/start/', personal_quiz_views.start_quiz, name='quiz_start'),

    # 练习功能
    path('quiz/session/<int:session_id>/', personal_quiz_views.quiz_session, name='quiz_session'),
    path('quiz/session/<int:session_id>/submit/', personal_quiz_views.submit_answer, name='quiz_submit_answer'),
    path('quiz/session/<int:session_id>/result/', personal_quiz_views.quiz_result, name='quiz_result'),

    # 错题功能
    path('quiz/wrong-answers/', personal_quiz_views.wrong_answers, name='quiz_wrong_answers'),
    path('quiz/wrong-answers/<int:wrong_answer_id>/', personal_quiz_views.wrong_answer_detail, name='quiz_wrong_answer_detail'),
    path('quiz/wrong-answers/<int:wrong_answer_id>/mastered/', personal_quiz_views.mark_mastered, name='quiz_mark_mastered'),
    path('quiz/wrong-answers/<int:wrong_answer_id>/analyze/', personal_quiz_views.analyze_wrong_answer, name='quiz_analyze_wrong_answer'),
    path('quiz/wrong-answers/practice/', personal_quiz_views.practice_wrong_answers, name='quiz_practice_wrong_answers'),

    # 统计功能
    path('quiz/statistics/', personal_quiz_views.study_statistics, name='quiz_statistics'),

    # AI分析功能
    path('quiz/session/<int:session_id>/ai-analysis/', personal_quiz_views.analyze_session_performance, name='quiz_analyze_session'),

    # PDF导出功能
    path('quiz/libraries/<int:library_id>/export-pdf/', personal_quiz_views.export_library_pdf, name='quiz_export_library_pdf'),
    path('quiz/wrong-answers/export-pdf/', personal_quiz_views.export_wrong_answers_pdf, name='quiz_export_wrong_answers_pdf'),

    # PDF测试功能
    path('quiz/test-pdf/', personal_quiz_views.test_pdf_generation, name='quiz_test_pdf'),

    # 题库分享功能
    path('quiz/libraries/<int:library_id>/share/', share_views.share_library, name='share_library'),
    path('quiz/libraries/<int:library_id>/shares/', share_views.library_shares, name='library_shares'),
    path('quiz/shares/received/', share_views.received_shares, name='received_shares'),
    path('quiz/shares/public/', share_views.public_libraries, name='public_libraries'),
    path('quiz/shared/<str:share_code>/', share_views.shared_library_detail, name='shared_library_detail'),
    path('quiz/shares/<int:share_id>/copy/', share_views.copy_shared_library, name='copy_shared_library'),
    path('quiz/shares/<int:share_id>/toggle/', share_views.toggle_share_status, name='toggle_share_status'),
    path('quiz/shares/<int:share_id>/delete/', share_views.delete_share, name='delete_share'),
]
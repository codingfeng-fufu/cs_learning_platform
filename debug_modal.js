// 调试模态框功能的JavaScript代码

// 测试函数是否存在
console.log('=== 调试模态框功能 ===');

// 检查必要的DOM元素
function checkModalElements() {
    const elements = [
        'knowledgeModal',
        'modalTitle', 
        'modalDescription',
        'modalCategory',
        'modalDifficulty',
        'modalIcon',
        'modalFeatures',
        'modalPrimaryBtn'
    ];
    
    console.log('检查模态框元素:');
    elements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`${id}: ${element ? '✓ 存在' : '✗ 缺失'}`);
    });
}

// 测试showDailyTermDetail函数
function testShowDailyTermDetail() {
    console.log('测试 showDailyTermDetail 函数...');
    
    if (typeof showDailyTermDetail === 'function') {
        console.log('✓ showDailyTermDetail 函数存在');
        
        // 测试调用
        try {
            showDailyTermDetail('27', '支持向量机', '这是一个测试解释', '数据结构', 'beginner');
            console.log('✓ 函数调用成功');
        } catch (error) {
            console.error('✗ 函数调用失败:', error);
        }
    } else {
        console.error('✗ showDailyTermDetail 函数不存在');
    }
}

// 测试辅助函数
function testHelperFunctions() {
    console.log('测试辅助函数...');
    
    const functions = ['getCategoryDisplayName', 'getDifficultyDisplayName', 'closeKnowledgeModal'];
    
    functions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✓ ${funcName} 函数存在`);
        } else {
            console.error(`✗ ${funcName} 函数不存在`);
        }
    });
}

// 页面加载完成后执行测试
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始调试...');
    checkModalElements();
    testHelperFunctions();
    testShowDailyTermDetail();
});

// 手动测试函数
window.debugModal = function() {
    console.log('手动调试模态框...');
    checkModalElements();
    testHelperFunctions();
    testShowDailyTermDetail();
};

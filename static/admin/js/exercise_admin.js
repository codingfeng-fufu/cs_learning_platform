// 练习题管理后台JavaScript

// 全局变量
let previewUpdateTimer = null;

// 初始化编辑器
function initializeExerciseEditor() {
    console.log('初始化练习题编辑器...');
    
    // 初始化JSON编辑器
    initializeJSONEditors();
    
    // 绑定表单变化事件
    bindFormEvents();
    
    // 初始化题目类型变化监听
    bindQuestionTypeChange();
    
    // 添加帮助提示
    addHelpHints();
}

// 初始化JSON编辑器
function initializeJSONEditors() {
    // 为选项字段添加帮助
    const optionsField = document.querySelector('.options-widget');
    if (optionsField) {
        addJSONEditorHelp(optionsField, 'options');
    }
    
    // 为提示字段添加帮助
    const hintsField = document.querySelector('.hints-widget');
    if (hintsField) {
        addJSONEditorHelp(hintsField, 'hints');
    }
}

// 添加JSON编辑器帮助
function addJSONEditorHelp(field, type) {
    const helpDiv = document.createElement('div');
    helpDiv.className = 'json-editor-hint';
    
    if (type === 'options') {
        helpDiv.innerHTML = `
            <strong>选项格式示例：</strong><br>
            单选题/多选题：<code>{"A": "选项A内容", "B": "选项B内容", "C": "选项C内容", "D": "选项D内容"}</code><br>
            其他题型：留空或 <code>{}</code>
        `;
    } else if (type === 'hints') {
        helpDiv.innerHTML = `
            <strong>提示格式示例：</strong><br>
            <code>["第一个提示：引导思考方向", "第二个提示：提供关键信息", "第三个提示：接近答案"]</code><br>
            无提示时：<code>[]</code>
        `;
    }
    
    field.parentNode.insertBefore(helpDiv, field);
    
    // 添加格式验证
    field.addEventListener('blur', function() {
        validateJSON(field, type);
    });
}

// JSON格式验证
function validateJSON(field, type) {
    const value = field.value.trim();
    if (!value) {
        clearValidationError(field);
        return;
    }
    
    try {
        const parsed = JSON.parse(value);
        
        if (type === 'options') {
            if (typeof parsed !== 'object' || Array.isArray(parsed)) {
                showValidationError(field, '选项必须是对象格式，如：{"A": "选项内容"}');
                return;
            }
        } else if (type === 'hints') {
            if (!Array.isArray(parsed)) {
                showValidationError(field, '提示必须是数组格式，如：["提示1", "提示2"]');
                return;
            }
        }
        
        clearValidationError(field);
        
        // 格式化显示
        field.value = JSON.stringify(parsed, null, 2);
        
    } catch (e) {
        showValidationError(field, 'JSON格式错误：' + e.message);
    }
}

// 显示验证错误
function showValidationError(field, message) {
    clearValidationError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'json-validation-error';
    errorDiv.style.cssText = `
        color: #dc3545;
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        padding: 8px 12px;
        margin-top: 5px;
        font-size: 0.875em;
    `;
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#dc3545';
}

// 清除验证错误
function clearValidationError(field) {
    const existingError = field.parentNode.querySelector('.json-validation-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '';
}

// 绑定表单事件
function bindFormEvents() {
    // 监听所有输入字段的变化
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', schedulePreviewUpdate);
        input.addEventListener('change', schedulePreviewUpdate);
    });
}

// 绑定题目类型变化事件
function bindQuestionTypeChange() {
    const questionTypeField = document.querySelector('#id_question_type');
    if (questionTypeField) {
        questionTypeField.addEventListener('change', function() {
            const questionType = this.value;
            updateFieldsBasedOnType(questionType);
            schedulePreviewUpdate();
        });
        
        // 初始化时也调用一次
        updateFieldsBasedOnType(questionTypeField.value);
    }
}

// 添加帮助提示
function addHelpHints() {
    // 为题目类型字段添加变化监听
    const questionTypeField = document.querySelector('#id_question_type');
    if (questionTypeField) {
        // 初始化时调用一次
        updateFieldsBasedOnType(questionTypeField.value);
    }
}

// 根据题目类型更新字段显示
function updateFieldsBasedOnType(questionType) {
    const optionsField = document.querySelector('.options-widget');
    const optionsRow = optionsField ? optionsField.closest('.form-row') : null;
    
    if (optionsRow) {
        if (['single_choice', 'multiple_choice'].includes(questionType)) {
            optionsRow.style.display = 'block';
            optionsField.required = true;
        } else {
            optionsRow.style.display = 'none';
            optionsField.required = false;
            optionsField.value = '{}';
        }
    }
    
    // 更新正确答案字段的帮助文本
    updateAnswerHelp(questionType);
}

// 更新答案帮助文本
function updateAnswerHelp(questionType) {
    const answerField = document.querySelector('#id_correct_answer');
    if (!answerField) return;
    
    let helpText = '';
    switch (questionType) {
        case 'single_choice':
            helpText = '输入正确选项的字母，如：A';
            break;
        case 'multiple_choice':
            helpText = '输入多个正确选项，用逗号分隔，如：A,C,D';
            break;
        case 'true_false':
            helpText = '输入 true 或 false';
            break;
        case 'fill_blank':
            helpText = '输入标准答案文本';
            break;
        case 'short_answer':
            helpText = '输入参考答案';
            break;
        case 'coding':
            helpText = '输入标准代码';
            break;
    }
    
    // 更新或创建帮助文本
    let helpElement = answerField.parentNode.querySelector('.answer-help');
    if (!helpElement) {
        helpElement = document.createElement('div');
        helpElement.className = 'answer-help help';
        answerField.parentNode.appendChild(helpElement);
    }
    helpElement.textContent = helpText;
}

// 计划预览更新（防抖）
function schedulePreviewUpdate() {
    if (previewUpdateTimer) {
        clearTimeout(previewUpdateTimer);
    }
    previewUpdateTimer = setTimeout(updatePreview, 500);
}

// 更新预览内容
function updatePreview() {
    const previewContent = document.getElementById('preview-content');
    if (!previewContent) return;
    
    const title = document.querySelector('#id_title')?.value || '';
    const questionText = document.querySelector('#id_question_text')?.value || '';
    const questionType = document.querySelector('#id_question_type')?.value || '';
    const correctAnswer = document.querySelector('#id_correct_answer')?.value || '';
    
    if (!title && !questionText) {
        previewContent.innerHTML = '<div class="preview-placeholder"><p>填写题目内容后，这里会显示实时预览</p></div>';
        return;
    }
    
    const html = generatePreviewHTML(title, questionText, questionType, correctAnswer);
    previewContent.innerHTML = html;
}

// 生成预览HTML
function generatePreviewHTML(title, questionText, questionType, correctAnswer) {
    const typeNames = {
        'single_choice': '单选题',
        'multiple_choice': '多选题',
        'true_false': '判断题',
        'fill_blank': '填空题',
        'short_answer': '简答题',
        'coding': '编程题'
    };
    
    return `
        <div class="preview-exercise">
            <div class="preview-header">
                <h4>${title || '题目标题'}</h4>
                <span class="question-type-badge">${typeNames[questionType] || '未知类型'}</span>
            </div>
            <div class="preview-question">
                ${questionText || '题目内容...'}
            </div>
            ${correctAnswer ? `<div class="preview-answer"><strong>参考答案：</strong>${correctAnswer}</div>` : ''}
        </div>
    `;
}

// 切换预览面板
function togglePreview() {
    const panel = document.getElementById('preview-panel');
    if (panel) {
        panel.classList.toggle('active');
        if (panel.classList.contains('active')) {
            updatePreview();
        }
    }
}

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟初始化，确保Django admin的JavaScript已加载
    setTimeout(initializeExerciseEditor, 500);
});

// 模板相关函数
function startCreating() {
    const wizard = document.getElementById('welcome-wizard');
    const content = document.getElementById('exercise-content');
    if (wizard) wizard.style.display = 'none';
    if (content) content.style.display = 'block';
    initializeExerciseEditor();
}

function loadTemplate() {
    const selector = document.getElementById('template-selector');
    if (selector) selector.style.display = 'block';
}

function hideTemplateSelector() {
    const selector = document.getElementById('template-selector');
    if (selector) selector.style.display = 'none';
}

function applyTemplate(templateType) {
    const questionTypeField = document.querySelector('#id_question_type');
    if (questionTypeField) {
        questionTypeField.value = templateType;
        updateFieldsBasedOnType(templateType);
    }
    hideTemplateSelector();
    startCreating();
}

function showQuickHelp() {
    alert('快速帮助：\n\n1. 选择合适的题目类型\n2. 填写清晰的题目标题\n3. 编写题目内容\n4. 设置正确答案\n5. 添加解析和提示\n\n如需更多帮助，请参考使用指南。');
}

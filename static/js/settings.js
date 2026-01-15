// 设置页面JavaScript逻辑

// DOM元素
const elements = {
    feishuEnabled: document.getElementById('feishu-enabled'),
    feishuChatId: document.getElementById('feishu-chat-id'),
    switchStatus: document.getElementById('switch-status'),
    btnSave: document.getElementById('btn-save'),
    btnReset: document.getElementById('btn-reset'),
    btnTestFeishu: document.getElementById('btn-test-feishu'),
    statusMessage: document.getElementById('status-message'),
    testMessage: document.getElementById('test-message')
};

// 原始设置（用于重置）
let originalSettings = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    loadSettings();
    setupEventListeners();
});

// 设置事件监听
function setupEventListeners() {
    elements.feishuEnabled.addEventListener('change', onSwitchChange);
    elements.btnSave.addEventListener('click', saveSettings);
    elements.btnReset.addEventListener('click', resetSettings);
    elements.btnTestFeishu.addEventListener('click', testFeishu);
}

// 开关状态改变
function onSwitchChange() {
    const enabled = elements.feishuEnabled.checked;
    elements.switchStatus.textContent = enabled ? '开启' : '关闭';
}

// 加载设置
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (data.success) {
            const settings = data.settings;
            
            // 保存原始设置
            originalSettings = { ...settings };
            
            // 应用设置到界面
            elements.feishuEnabled.checked = settings.feishu_nok_send_enabled || false;
            elements.feishuChatId.value = settings.feishu_chat_id || '';
            
            // 更新开关状态文本
            onSwitchChange();
        } else {
            showMessage('加载设置失败: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('加载设置失败:', error);
        showMessage('加载设置失败', 'error');
    }
}

// 保存设置
async function saveSettings() {
    const settings = {
        feishu_nok_send_enabled: elements.feishuEnabled.checked,
        feishu_chat_id: elements.feishuChatId.value.trim()
    };
    
    // 验证
    if (settings.feishu_nok_send_enabled && !settings.feishu_chat_id) {
        showMessage('启用飞书发送时，请填写飞书群ID', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('设置已保存', 'success');
            // 更新原始设置
            originalSettings = { ...settings };
        } else {
            showMessage('保存失败: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('保存设置失败:', error);
        showMessage('保存设置失败', 'error');
    }
}

// 重置设置
function resetSettings() {
    if (!originalSettings) {
        return;
    }
    
    elements.feishuEnabled.checked = originalSettings.feishu_nok_send_enabled || false;
    elements.feishuChatId.value = originalSettings.feishu_chat_id || '';
    
    onSwitchChange();
    showMessage('已重置为上次保存的设置', 'success');
}

// 显示消息
function showMessage(message, type = 'success', element = null, duration = 3000) {
    const targetElement = element || elements.statusMessage;
    targetElement.textContent = message;
    targetElement.className = 'status-message ' + type + ' show';
    
    setTimeout(() => {
        targetElement.classList.remove('show');
    }, duration);
}

// 测试飞书消息发送
async function testFeishu() {
    const chatId = elements.feishuChatId.value.trim();
    
    // 验证
    if (!chatId) {
        showMessage('请先填写飞书群ID', 'error', elements.testMessage);
        return;
    }
    
    // 禁用按钮，防止重复点击
    elements.btnTestFeishu.disabled = true;
    elements.btnTestFeishu.textContent = '测试中...';
    
    try {
        const response = await fetch('/api/feishu/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: chatId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('测试成功！已向飞书群发送测试消息', 'success', elements.testMessage, 10000);
        } else {
            showMessage('测试失败: ' + data.error, 'error', elements.testMessage, 10000);
        }
    } catch (error) {
        console.error('测试飞书失败:', error);
        showMessage('测试失败: ' + error.message, 'error', elements.testMessage, 10000);
    } finally {
        // 恢复按钮状态
        elements.btnTestFeishu.disabled = false;
        elements.btnTestFeishu.textContent = '测试飞书连接';
    }
}

// 主题切换功能
function initializeTheme() {
    // 从localStorage读取保存的主题
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    
    // 创建主题切换按钮
    createThemeToggle();
}

function createThemeToggle() {
    // 检查是否已存在主题切换按钮
    if (document.getElementById('theme-toggle')) {
        return;
    }
    
    const toggle = document.createElement('button');
    toggle.id = 'theme-toggle';
    toggle.className = 'theme-toggle';
    toggle.innerHTML = '<span class="theme-toggle-icon">🌙</span><span class="theme-toggle-text">深色</span>';
    toggle.title = '切换主题';
    toggle.onclick = toggleTheme;
    
    document.body.appendChild(toggle);
    updateThemeToggleText();
}

function toggleTheme() {
    const currentTheme = document.body.classList.contains('theme-light') ? 'light' : 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
    if (theme === 'light') {
        document.body.classList.add('theme-light');
    } else {
        document.body.classList.remove('theme-light');
    }
    updateThemeToggleText();
}

function updateThemeToggleText() {
    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
        const isLight = document.body.classList.contains('theme-light');
        const icon = toggle.querySelector('.theme-toggle-icon');
        const text = toggle.querySelector('.theme-toggle-text');
        if (icon) icon.textContent = isLight ? '☀️' : '🌙';
        if (text) text.textContent = isLight ? '浅色' : '深色';
    }
}

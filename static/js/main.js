// 主页面JavaScript逻辑

// 全局状态
const IMAGE_FIT_MODE_STORAGE_KEY = 'imageFitMode';
const DEFAULT_IMAGE_FIT_MODE = 'fit-window';
const IMAGE_FIT_MODES = new Set(['fit-window', 'prioritize-height']);

const state = {
    currentFolder: null,
    currentIndex: 0,
    totalImages: 0,
    imageList: [],
    rotate: false,
    showBbox: true,
    imageFitMode: DEFAULT_IMAGE_FIT_MODE,
    preloadedImage: null,  // 预加载的图片缓存
    preloadedIndex: -1,    // 预加载的图片索引
    preloadedImageName: null,  // 预加载的图片文件名
    loading: false,
    // 飞书设置
    feishuSettings: {
        nok_send_enabled: false,
        chat_id: ''
    }
};

// DOM元素
const elements = {
    folderSelect: document.getElementById('folder-select'),
    mainImage: document.getElementById('main-image'),
    imageName: document.getElementById('image-name'),
    loading: document.getElementById('loading'),
    noImage: document.getElementById('no-image'),
    imageArea: document.querySelector('.image-area'),
    totalCount: document.getElementById('total-count'),
    currentIndex: document.getElementById('current-index'),
    modifyTime: document.getElementById('modify-time'),
    imageSize: document.getElementById('image-size'),
    progressBar: document.getElementById('progress-bar'),
    rotateToggle: document.getElementById('rotate-toggle'),
    bboxToggle: document.getElementById('bbox-toggle'),
    userIp: document.getElementById('user-ip'),
    btnFirst: document.getElementById('btn-first'),
    btnPrev: document.getElementById('btn-prev'),
    btnOk: document.getElementById('btn-ok'),
    btnNok: document.getElementById('btn-nok'),
    btnNext: document.getElementById('btn-next'),
    btnLast: document.getElementById('btn-last'),
    btnUndo: document.getElementById('btn-undo'),
    undoCount: document.getElementById('undo-count'),
    imageFitButtons: document.querySelectorAll('#image-fit-mode-controls .display-mode-btn'),
    notification: document.getElementById('notification')
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    initializeImageFitMode();
    initializeApp();
    setupEventListeners();
    setupKeyboardShortcuts();
});

// 初始化应用
async function initializeApp() {
    await loadUser();
    await loadFeishuSettings();
    await loadFolders();
    await loadGlobalState();
    checkUndoAvailable();
}

// 加载飞书设置
async function loadFeishuSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (data.success && data.settings) {
            state.feishuSettings.nok_send_enabled = data.settings.feishu_nok_send_enabled || false;
            state.feishuSettings.chat_id = data.settings.feishu_chat_id || '';
        }
    } catch (error) {
        console.error('加载飞书设置失败:', error);
    }
}

// 设置事件监听
function setupEventListeners() {
    elements.folderSelect.addEventListener('change', onFolderChange);
    elements.rotateToggle.addEventListener('change', onRotateToggle);
    elements.bboxToggle.addEventListener('change', onBboxToggle);
    elements.imageFitButtons.forEach(button => button.addEventListener('click', onImageFitModeChange));
    elements.btnFirst.addEventListener('click', () => navigate('first'));
    elements.btnPrev.addEventListener('click', () => navigate('prev'));
    elements.btnOk.addEventListener('click', () => classifyImage('ok'));
    elements.btnNok.addEventListener('click', () => classifyImage('nok'));
    elements.btnNext.addEventListener('click', () => navigate('next'));
    elements.btnLast.addEventListener('click', () => navigate('last'));
    elements.btnUndo.addEventListener('click', undoLastOperation);
}

// 设置键盘快捷键
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // 如果焦点在输入框，不处理快捷键
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        switch(e.key.toLowerCase()) {
            case 'arrowleft':
            case 'a':
                navigate('prev');
                e.preventDefault();
                break;
            case 'arrowright':
            case 'd':
                navigate('next');
                e.preventDefault();
                break;
            case 'home':
                navigate('first');
                e.preventDefault();
                break;
            case 'end':
                navigate('last');
                e.preventDefault();
                break;
            case 'enter':
            case '1':
                classifyImage('ok');
                e.preventDefault();
                break;
            case ' ':
            case '2':
                classifyImage('nok');
                e.preventDefault();
                break;
            case 'u':
                if (!e.ctrlKey) {
                    undoLastOperation();
                }
                e.preventDefault();
                break;
            case 'z':
                if (e.ctrlKey) {
                    undoLastOperation();
                    e.preventDefault();
                }
                break;
            case 'r':
                elements.rotateToggle.checked = !elements.rotateToggle.checked;
                onRotateToggle();
                e.preventDefault();
                break;
            case 'b':
                elements.bboxToggle.checked = !elements.bboxToggle.checked;
                onBboxToggle();
                e.preventDefault();
                break;
        }
    });
}

// 加载用户信息
async function loadUser() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();
        
        if (data.success) {
            elements.userIp.textContent = data.user.ip;
        }
    } catch (error) {
        console.error('加载用户信息失败:', error);
    }
}

// 加载文件夹列表
async function loadFolders() {
    try {
        const response = await fetch('/api/folders');
        const data = await response.json();
        
        if (data.success) {
            const currentSelectedFolder = elements.folderSelect.value;
            elements.folderSelect.innerHTML = '';
            
            if (data.folders.length === 0) {
                elements.folderSelect.innerHTML = '<option value="">无可用文件夹</option>';
                return;
            }
            
            data.folders.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder.name;
                option.textContent = `${folder.name} (${folder.pending_count})`;
                elements.folderSelect.appendChild(option);
            });
            
            // 恢复之前选择的文件夹
            if (currentSelectedFolder) {
                elements.folderSelect.value = currentSelectedFolder;
                state.currentFolder = currentSelectedFolder;
            } else if (data.folders.length > 0) {
                // 选择第一个文件夹
                state.currentFolder = data.folders[0].name;
                elements.folderSelect.value = state.currentFolder;
            }
            
            // 如果当前文件夹存在，加载图片
            if (state.currentFolder) {
                await loadImages();
            }
        }
    } catch (error) {
        console.error('加载文件夹列表失败:', error);
        showNotification('加载文件夹失败', 'error');
    }
}

// 更新文件夹选择下拉框中指定文件夹的显示数量
async function updateFolderDisplayCount(folderName) {
    if (!folderName) return;
    
    try {
        const response = await fetch('/api/folders');
        const data = await response.json();
        
        if (data.success) {
            const folder = data.folders.find(f => f.name === folderName);
            if (folder) {
                // 更新下拉框中对应选项的显示文本
                const option = elements.folderSelect.querySelector(`option[value="${folderName}"]`);
                if (option) {
                    option.textContent = `${folder.name} (${folder.pending_count})`;
                }
            }
        }
    } catch (error) {
        console.error('更新文件夹显示失败:', error);
    }
}

// 文件夹改变事件
async function onFolderChange() {
    state.currentFolder = elements.folderSelect.value;
    state.currentIndex = 0;
    await loadImages();
}

// 加载图片列表
async function loadImages() {
    if (!state.currentFolder) return;
    
    try {
        const response = await fetch(`/api/images?folder=${encodeURIComponent(state.currentFolder)}`);
        const data = await response.json();
        
        if (data.success) {
            state.imageList = data.images;
            state.totalImages = data.count;
            state.currentIndex = 0;
            
            updateInfo();
            await loadCurrentImage();
            await updateGlobalState();
        }
    } catch (error) {
        console.error('加载图片列表失败:', error);
        showNotification('加载图片列表失败', 'error');
    }
}

// 加载当前图片
async function loadCurrentImage() {
    if (state.loading) return;
    
    if (state.totalImages === 0) {
        showNoImage();
        return;
    }
    
    if (state.currentIndex < 0 || state.currentIndex >= state.totalImages) {
        return;
    }
    
    // 检查是否有预加载的图片
    if (state.preloadedImage && state.preloadedIndex === state.currentIndex) {
        // 使用预加载时保存的文件名，而不是从前端列表获取
        displayImage(state.preloadedImage, state.preloadedImageName);
        updateInfo();
        // 预加载下一张
        preloadNextImage();
        return;
    }
    
    state.loading = true;
    showLoading();
    
    try {
        const response = await fetch(
            `/api/image?folder=${encodeURIComponent(state.currentFolder)}&index=${state.currentIndex}&rotate=${state.rotate ? 1 : 0}&bbox=${state.showBbox ? 1 : 0}`
        );
        const data = await response.json();
        
        if (data.success) {
            // 使用后端返回的文件名，确保与实际显示的图片匹配
            displayImage(data.image, data.name);
            updateImageInfo(data);
            // 预加载下一张
            preloadNextImage();
        } else {
            showNotification('加载图片失败: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('加载图片失败:', error);
        showNotification('加载图片失败', 'error');
    } finally {
        state.loading = false;
    }
}

// 预加载下一张图片
async function preloadNextImage() {
    const nextIndex = state.currentIndex + 1;
    
    if (nextIndex >= state.totalImages) {
        return;  // 已经是最后一张
    }
    
    try {
        const response = await fetch(
            `/api/image?folder=${encodeURIComponent(state.currentFolder)}&index=${nextIndex}&rotate=${state.rotate ? 1 : 0}&bbox=${state.showBbox ? 1 : 0}`
        );
        const data = await response.json();
        
        if (data.success) {
            state.preloadedImage = data.image;
            state.preloadedIndex = nextIndex;
            state.preloadedImageName = data.name;  // 保存预加载图片的文件名
            console.log(`已预加载图片 ${nextIndex + 1}/${state.totalImages}`);
        }
    } catch (error) {
        console.error('预加载图片失败:', error);
    }
}

// 显示图片
function displayImage(base64Data, imageName) {
    elements.mainImage.src = 'data:image/jpeg;base64,' + base64Data;
    elements.mainImage.classList.add('visible');
    elements.imageName.textContent = imageName || '';
    elements.imageName.classList.add('visible');
    elements.loading.classList.remove('visible');
    elements.noImage.classList.remove('visible');
}

// 显示加载中
function showLoading() {
    elements.mainImage.classList.remove('visible');
    elements.imageName.classList.remove('visible');
    elements.loading.classList.add('visible');
    elements.noImage.classList.remove('visible');
}

// 显示无图片
function showNoImage() {
    elements.mainImage.classList.remove('visible');
    elements.imageName.classList.remove('visible');
    elements.loading.classList.remove('visible');
    elements.noImage.classList.add('visible');
}

// 更新信息显示
function updateInfo() {
    elements.totalCount.textContent = state.totalImages;
    elements.currentIndex.textContent = state.totalImages > 0 ? state.currentIndex + 1 : 0;
    
    const progress = state.totalImages > 0 ? ((state.currentIndex + 1) / state.totalImages) * 100 : 0;
    elements.progressBar.style.width = progress + '%';
    
    // 更新按钮状态
    elements.btnFirst.disabled = state.currentIndex === 0 || state.totalImages === 0;
    elements.btnPrev.disabled = state.currentIndex === 0 || state.totalImages === 0;
    elements.btnNext.disabled = state.currentIndex >= state.totalImages - 1 || state.totalImages === 0;
    elements.btnLast.disabled = state.currentIndex >= state.totalImages - 1 || state.totalImages === 0;
    elements.btnOk.disabled = state.totalImages === 0;
    elements.btnNok.disabled = state.totalImages === 0;
}

// 更新图片信息
function updateImageInfo(data) {
    if (data.modify_time) {
        elements.modifyTime.textContent = data.modify_time;
    }
    
    if (data.info) {
        const width = data.info.display_width || data.info.width;
        const height = data.info.display_height || data.info.height;
        elements.imageSize.textContent = `${width} x ${height}`;
    }
}

// 导航
async function navigate(direction) {
    if (state.totalImages === 0) return;
    
    switch(direction) {
        case 'first':
            state.currentIndex = 0;
            break;
        case 'prev':
            if (state.currentIndex > 0) {
                state.currentIndex--;
            }
            break;
        case 'next':
            if (state.currentIndex < state.totalImages - 1) {
                state.currentIndex++;
            }
            break;
        case 'last':
            state.currentIndex = state.totalImages - 1;
            break;
    }
    
    updateInfo();
    await loadCurrentImage();
    await updateGlobalState();
}

// 分类图片
async function classifyImage(category) {
    if (state.totalImages === 0 || state.currentIndex >= state.totalImages) {
        return;
    }
    
    const imageName = state.imageList[state.currentIndex];
    
    // 如果是NOK分类且飞书发送功能开启，先弹出确认框
    let shouldSendFeishu = false;
    if (category === 'nok' && state.feishuSettings.nok_send_enabled && state.feishuSettings.chat_id) {
        shouldSendFeishu = confirm('是否发送此图片到飞书群？');
    }
    
    try {
        // 执行分类操作
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                folder: state.currentFolder,
                image_name: imageName,
                category: category
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 根据分类类型决定通知颜色：NOK显示红色，OK显示绿色
            const notificationType = data.category === 'nok' ? 'error' : 'success';
            showNotification(data.message, notificationType);
            
            // 如果用户确认发送到飞书，执行发送操作
            if (shouldSendFeishu) {
                await sendToFeishu(state.currentFolder, imageName, state.feishuSettings.chat_id);
            }
            
            // 从列表中移除该图片
            state.imageList.splice(state.currentIndex, 1);
            state.totalImages--;
            
            // 调整索引
            if (state.currentIndex >= state.totalImages && state.totalImages > 0) {
                state.currentIndex = state.totalImages - 1;
            }
            
            // 检查预加载缓存是否仍然有效
            // 如果预加载的是下一张图片（当前索引+1），移除当前图片后，预加载的图片索引会变成当前索引
            // 所以需要更新预加载索引，使其匹配新的索引
            if (state.preloadedImage && state.preloadedIndex === state.currentIndex + 1) {
                // 预加载的图片正好是下一张要显示的，更新索引以匹配新的位置
                state.preloadedIndex = state.currentIndex;
            } else {
                // 预加载的图片不是下一张，清空缓存
                state.preloadedImage = null;
                state.preloadedIndex = -1;
                state.preloadedImageName = null;
            }
            
            updateInfo();
            await loadCurrentImage();
            await checkUndoAvailable();
            await updateGlobalState();
            // 更新文件夹选择下拉框中的图片数量显示
            await updateFolderDisplayCount(state.currentFolder);
        } else {
            showNotification('操作失败: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('操作失败: ' + error.message, 'error');
    }
}

// 发送图片到飞书群
async function sendToFeishu(folder, imageName, chatId) {
    try {
        const response = await fetch('/api/feishu/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                folder: folder,
                image_name: imageName,
                chat_id: chatId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('已发送到飞书群', 'success');
        } else {
            showNotification('发送飞书消息失败: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('发送飞书消息失败:', error);
        showNotification('发送飞书消息失败', 'error');
    }
}

// 检查撤回可用性
async function checkUndoAvailable() {
    try {
        const response = await fetch('/api/undo/available');
        const data = await response.json();
        
        if (data.success) {
            elements.btnUndo.disabled = !data.available;
            if (data.count > 0) {
                elements.undoCount.textContent = `(${data.count})`;
            } else {
                elements.undoCount.textContent = '';
            }
        }
    } catch (error) {
        console.error('检查撤回状态失败:', error);
    }
}

// 撤回操作
async function undoLastOperation() {
    if (elements.btnUndo.disabled) return;
    
    try {
        const response = await fetch('/api/undo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'info');
            
            // 重新加载当前文件夹的图片列表
            await loadImages();
            await checkUndoAvailable();
            // 更新文件夹选择下拉框中的图片数量显示
            await updateFolderDisplayCount(state.currentFolder);
        } else {
            showNotification('撤回失败: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('撤回失败: ' + error.message, 'error');
    }
}

// 旋转切换
function onRotateToggle() {
    state.rotate = elements.rotateToggle.checked;
    loadCurrentImage();
}

// 边界框切换
function onBboxToggle() {
    state.showBbox = elements.bboxToggle.checked;
    loadCurrentImage();
}

// 加载全局状态
function initializeImageFitMode() {
    const savedMode = localStorage.getItem(IMAGE_FIT_MODE_STORAGE_KEY) || DEFAULT_IMAGE_FIT_MODE;
    applyImageFitMode(savedMode);
}

function onImageFitModeChange(event) {
    const mode = event.currentTarget.dataset.imageFitMode || DEFAULT_IMAGE_FIT_MODE;
    applyImageFitMode(mode);
    localStorage.setItem(IMAGE_FIT_MODE_STORAGE_KEY, mode);
}

function applyImageFitMode(mode) {
    const normalizedMode = IMAGE_FIT_MODES.has(mode) ? mode : DEFAULT_IMAGE_FIT_MODE;
    state.imageFitMode = normalizedMode;

    if (elements.imageArea) {
        elements.imageArea.dataset.imageFitMode = normalizedMode;
    }

    elements.imageFitButtons.forEach(button => {
        const isActive = button.dataset.imageFitMode === normalizedMode;
        button.classList.toggle('is-active', isActive);
        button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
}

async function loadGlobalState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        
        if (data.success && data.state.current_folder) {
            state.currentFolder = data.state.current_folder;
            state.currentIndex = data.state.current_index || 0;
            
            // 更新文件夹选择
            elements.folderSelect.value = state.currentFolder;
            
            await loadImages();
        }
    } catch (error) {
        console.error('加载全局状态失败:', error);
    }
}

// 更新全局状态
async function updateGlobalState() {
    try {
        await fetch('/api/state', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                current_folder: state.currentFolder,
                current_index: state.currentIndex
            })
        });
    } catch (error) {
        console.error('更新全局状态失败:', error);
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    elements.notification.textContent = message;
    elements.notification.className = 'notification ' + type + ' show';
    
    setTimeout(() => {
        elements.notification.classList.remove('show');
    }, 3000);
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
    
    const themeHost = document.querySelector('.container') || document.body;
    themeHost.appendChild(toggle);
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


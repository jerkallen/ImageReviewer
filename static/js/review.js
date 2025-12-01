// 结果确认页面JavaScript

// 全局状态
const state = {
    currentFolder: null,
    currentCategory: 'ok',
    imageList: [],
    currentPage: 0,
    imagesPerPage: 12,
    totalPages: 0
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    initializePage();
});

// 初始化页面
async function initializePage() {
    await loadFolders();
    updateUI();
}

// 加载文件夹列表
async function loadFolders() {
    try {
        const response = await fetch('/api/folders');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('folder-select');
            select.innerHTML = '<option value="">选择项目文件夹...</option>';
            
            data.folders.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder.name;
                option.textContent = `${folder.name} (OK: ${folder.ok_count}, NOK: ${folder.nok_count})`;
                select.appendChild(option);
            });
            
            // 监听文件夹选择
            select.addEventListener('change', onFolderChange);
            
            // 如果有文件夹，选择第一个
            if (data.folders.length > 0) {
                state.currentFolder = data.folders[0].name;
                select.value = state.currentFolder;
                await loadImages();
            }
        }
    } catch (error) {
        console.error('加载文件夹列表失败:', error);
    }
}

// 文件夹切换
async function onFolderChange() {
    const select = document.getElementById('folder-select');
    state.currentFolder = select.value;
    state.currentPage = 0;
    
    if (state.currentFolder) {
        await loadImages();
    }
}

// 切换分类
async function switchCategory(category) {
    state.currentCategory = category;
    state.currentPage = 0;
    
    // 更新标签样式
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        if (tab.textContent.includes('OK') && category === 'ok') {
            tab.classList.add('active');
        } else if (tab.textContent.includes('NOK') && category === 'nok') {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    await loadImages();
}

// 加载图片列表
async function loadImages() {
    if (!state.currentFolder) {
        return;
    }
    
    try {
        const response = await fetch(
            `/api/review/images?folder=${encodeURIComponent(state.currentFolder)}&category=${state.currentCategory}`
        );
        const data = await response.json();
        
        if (data.success) {
            state.imageList = data.images;
            state.totalPages = Math.ceil(state.imageList.length / state.imagesPerPage);
            
            updateUI();
            renderThumbnails();
        }
    } catch (error) {
        console.error('加载图片列表失败:', error);
        showError('加载失败');
    }
}

// 渲染缩略图
async function renderThumbnails() {
    const container = document.getElementById('thumbnails-container');
    
    if (state.imageList.length === 0) {
        container.innerHTML = '<div class="no-images">该分类下暂无图片</div>';
        return;
    }
    
    container.innerHTML = '<div class="loading-message">加载缩略图中...</div>';
    
    const startIndex = state.currentPage * state.imagesPerPage;
    const endIndex = Math.min(startIndex + state.imagesPerPage, state.imageList.length);
    const pageImages = state.imageList.slice(startIndex, endIndex);
    
    container.innerHTML = '';
    
    // 并行加载缩略图
    const thumbnailPromises = pageImages.map(async (imageName, idx) => {
        const globalIndex = startIndex + idx;
        return await createThumbnailElement(imageName, globalIndex);
    });
    
    const thumbnails = await Promise.all(thumbnailPromises);
    thumbnails.forEach(thumb => container.appendChild(thumb));
}

// 创建缩略图元素
async function createThumbnailElement(imageName, index) {
    const div = document.createElement('div');
    div.className = 'thumbnail-item';
    
    try {
        const response = await fetch(
            `/api/review/image?folder=${encodeURIComponent(state.currentFolder)}&category=${state.currentCategory}&index=${index}&thumbnail=1`
        );
        const data = await response.json();
        
        if (data.success) {
            div.innerHTML = `
                <img class="thumbnail-image" src="data:image/jpeg;base64,${data.image}" alt="${imageName}">
                <div class="thumbnail-info">
                    <div class="thumbnail-name" title="${imageName}">${imageName}</div>
                </div>
            `;
            
            div.onclick = () => viewImage(index);
        } else {
            div.innerHTML = `
                <div class="thumbnail-image"></div>
                <div class="thumbnail-info">
                    <div class="thumbnail-name">${imageName}</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载缩略图失败:', error);
        div.innerHTML = `
            <div class="thumbnail-image"></div>
            <div class="thumbnail-info">
                <div class="thumbnail-name">${imageName}</div>
            </div>
        `;
    }
    
    return div;
}

// 查看图片
async function viewImage(index) {
    try {
        const response = await fetch(
            `/api/review/image?folder=${encodeURIComponent(state.currentFolder)}&category=${state.currentCategory}&index=${index}&thumbnail=0`
        );
        const data = await response.json();
        
        if (data.success) {
            const modal = document.getElementById('modal');
            const modalImage = document.getElementById('modal-image');
            const modalInfo = document.getElementById('modal-info');
            
            modalImage.src = 'data:image/jpeg;base64,' + data.image;
            modalInfo.textContent = `${data.name} (${index + 1} / ${state.imageList.length})`;
            
            modal.classList.add('show');
        }
    } catch (error) {
        console.error('加载图片失败:', error);
        alert('加载图片失败');
    }
}

// 关闭模态框
function closeModal(event) {
    const modal = document.getElementById('modal');
    
    // 如果点击的是模态框背景或关闭按钮，关闭模态框
    if (!event || event.target === modal || event.target.classList.contains('modal-close')) {
        modal.classList.remove('show');
    }
}

// 上一页
function prevPage() {
    if (state.currentPage > 0) {
        state.currentPage--;
        updateUI();
        renderThumbnails();
        window.scrollTo(0, 0);
    }
}

// 下一页
function nextPage() {
    if (state.currentPage < state.totalPages - 1) {
        state.currentPage++;
        updateUI();
        renderThumbnails();
        window.scrollTo(0, 0);
    }
}

// 更新UI
function updateUI() {
    // 更新图片数量
    const countElem = document.getElementById('image-count');
    const categoryName = state.currentCategory === 'ok' ? 'OK' : 'NOK';
    countElem.textContent = `${categoryName}文件夹: ${state.imageList.length} 张图片`;
    
    // 更新分页信息
    const pageInfo = document.getElementById('page-info');
    if (state.totalPages > 0) {
        pageInfo.textContent = `第 ${state.currentPage + 1} / ${state.totalPages} 页`;
    } else {
        pageInfo.textContent = '- / -';
    }
    
    // 更新按钮状态
    document.getElementById('btn-prev-page').disabled = state.currentPage === 0;
    document.getElementById('btn-next-page').disabled = state.currentPage >= state.totalPages - 1 || state.totalPages === 0;
}

// 显示错误
function showError(message) {
    const container = document.getElementById('thumbnails-container');
    container.innerHTML = `<div class="no-images">${message}</div>`;
}

// 键盘导航
document.addEventListener('keydown', (e) => {
    const modal = document.getElementById('modal');
    
    if (modal.classList.contains('show')) {
        if (e.key === 'Escape') {
            closeModal();
        }
    }
});

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


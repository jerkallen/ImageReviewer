// 操作历史页面JavaScript

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializePage();
});

// 初始化页面
async function initializePage() {
    setDefaultDates();
    await loadUsers();
    await loadStats();
    await loadOperations();
}

// 设置默认日期（最近7天）
function setDefaultDates() {
    const today = new Date();
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    
    document.getElementById('filter-end-date').valueAsDate = today;
    document.getElementById('filter-start-date').valueAsDate = weekAgo;
}

// 加载用户列表
async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('filter-user');
            select.innerHTML = '<option value="">全部用户</option>';
            
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.ip;
                option.textContent = user.ip;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载用户列表失败:', error);
    }
}

// 加载统计信息
async function loadStats() {
    try {
        const response = await fetch('/api/operations/stats?days=7');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            
            document.getElementById('stat-today').textContent = stats.today_count || 0;
            document.getElementById('stat-total').textContent = stats.total || 0;
            document.getElementById('stat-ok').textContent = stats.by_type.classify_ok || 0;
            document.getElementById('stat-nok').textContent = stats.by_type.classify_nok || 0;
        }
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

// 加载操作记录
async function loadOperations() {
    const startDate = document.getElementById('filter-start-date').value;
    const endDate = document.getElementById('filter-end-date').value;
    const userIp = document.getElementById('filter-user').value;
    const opType = document.getElementById('filter-type').value;
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (userIp) params.append('user_ip', userIp);
    if (opType) params.append('operation_type', opType);
    params.append('limit', '100');
    
    try {
        const response = await fetch(`/api/operations?${params.toString()}`);
        const data = await response.json();
        
        if (data.success) {
            renderTable(data.operations);
        }
    } catch (error) {
        console.error('加载操作记录失败:', error);
        const tbody = document.getElementById('history-tbody');
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">加载失败</td></tr>';
    }
}

// 渲染表格
function renderTable(operations) {
    const tbody = document.getElementById('history-tbody');
    
    if (operations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">暂无记录</td></tr>';
        return;
    }
    
    tbody.innerHTML = operations.map(op => {
        const opTypeClass = getOpTypeClass(op.operation_type);
        const opTypeName = getOpTypeName(op.operation_type);
        const timestamp = formatTimestamp(op.timestamp);
        
        return `
            <tr>
                <td>${timestamp}</td>
                <td>${op.user_ip}</td>
                <td><span class="op-type ${opTypeClass}">${opTypeName}</span></td>
                <td>${op.image_name}</td>
                <td>${getShortPath(op.source_folder)}</td>
                <td>${op.target_folder ? getShortPath(op.target_folder) : '-'}</td>
            </tr>
        `;
    }).join('');
}

// 获取操作类型CSS类
function getOpTypeClass(opType) {
    if (opType === 'classify_ok') return 'ok';
    if (opType === 'classify_nok') return 'nok';
    if (opType === 'undo') return 'undo';
    return '';
}

// 获取操作类型名称
function getOpTypeName(opType) {
    if (opType === 'classify_ok') return 'OK';
    if (opType === 'classify_nok') return 'NOK';
    if (opType === 'undo') return '撤回';
    return opType;
}

// 格式化时间戳
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 获取短路径（仅显示最后两级）
function getShortPath(path) {
    const parts = path.split(/[/\\]/);
    if (parts.length > 2) {
        return parts.slice(-2).join('/');
    }
    return path;
}

// 应用筛选
function applyFilters() {
    loadOperations();
}

// 重置筛选
function resetFilters() {
    setDefaultDates();
    document.getElementById('filter-user').value = '';
    document.getElementById('filter-type').value = '';
    loadOperations();
}

// 导出CSV
async function exportToCSV() {
    const startDate = document.getElementById('filter-start-date').value;
    const endDate = document.getElementById('filter-end-date').value;
    const userIp = document.getElementById('filter-user').value;
    const opType = document.getElementById('filter-type').value;
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (userIp) params.append('user_ip', userIp);
    if (opType) params.append('operation_type', opType);
    params.append('limit', '1000');  // 导出时获取更多数据
    
    try {
        const response = await fetch(`/api/operations?${params.toString()}`);
        const data = await response.json();
        
        if (data.success) {
            const csv = generateCSV(data.operations);
            downloadCSV(csv, 'operations_history.csv');
        }
    } catch (error) {
        console.error('导出CSV失败:', error);
        alert('导出失败：' + error.message);
    }
}

// 生成CSV内容
function generateCSV(operations) {
    const headers = ['时间', '用户IP', '操作类型', '图片名称', '源文件夹', '目标文件夹'];
    const rows = operations.map(op => [
        formatTimestamp(op.timestamp),
        op.user_ip,
        getOpTypeName(op.operation_type),
        op.image_name,
        op.source_folder,
        op.target_folder || ''
    ]);
    
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    // 添加UTF-8 BOM以确保Excel正确识别中文
    return '\uFEFF' + csvContent;
}

// 下载CSV文件
function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


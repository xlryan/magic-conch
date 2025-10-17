/**
 * 神奇海螺·烂尾博物馆 - 前端逻辑
 */

// 全局状态
let allEntries = [];

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    loadEntries();
});

/**
 * 加载所有条目
 */
async function loadEntries() {
    try {
        const response = await fetch('/api/entries');
        if (!response.ok) {
            throw new Error('Failed to load entries');
        }

        allEntries = await response.json();
        renderEntries();
        renderLeaderboard();
    } catch (error) {
        console.error('Error loading entries:', error);
        document.getElementById('entries-list').innerHTML = `
            <div class="loading" style="color: #ff6b35;">
                加载失败，请刷新页面重试
            </div>
        `;
        document.getElementById('leaderboard').innerHTML = `
            <div class="loading" style="color: #ff6b35;">
                加载失败
            </div>
        `;
    }
}

/**
 * 渲染项目列表
 */
function renderEntries() {
    const container = document.getElementById('entries-list');

    if (allEntries.length === 0) {
        container.innerHTML = '<div class="loading">暂无项目</div>';
        return;
    }

    container.innerHTML = allEntries.map(entry => `
        <div class="entry-card" data-entry-id="${entry.id}">
            <div class="entry-header">
                <div>
                    <h3 class="entry-title">${escapeHtml(entry.title)}</h3>
                    <div class="entry-owner">👤 ${escapeHtml(entry.owner)}</div>
                </div>
                <div class="entry-score">${entry.score}</div>
            </div>

            <p class="entry-summary">${escapeHtml(entry.summary)}</p>

            <div class="entry-meta">
                <span>🗓️ 最后活跃：${entry.last_commit}</span>
                <span>⏱️ 停更：${entry.days_stale} 天</span>
                <span>👥 投票：${entry.votes}</span>
            </div>

            <div class="entry-actions">
                <button
                    class="btn btn-vote"
                    onclick="vote('${entry.id}')"
                    id="vote-btn-${entry.id}"
                >
                    踩一脚 👟
                </button>
                <a
                    href="${escapeHtml(entry.repo_url)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn btn-link"
                >
                    查看项目 🔗
                </a>
            </div>
        </div>
    `).join('');
}

/**
 * 渲染排行榜（仅显示前 10）
 */
function renderLeaderboard() {
    const container = document.getElementById('leaderboard');

    if (allEntries.length === 0) {
        container.innerHTML = '<div class="loading">暂无数据</div>';
        return;
    }

    // 取前 10 名
    const top10 = allEntries.slice(0, 10);

    container.innerHTML = top10.map((entry, index) => `
        <div class="leaderboard-item">
            <div class="leaderboard-rank">${index + 1}</div>
            <div class="leaderboard-info">
                <div class="leaderboard-title">${escapeHtml(entry.title)}</div>
                <div class="leaderboard-meta">
                    ${escapeHtml(entry.owner)} · ${entry.votes} 票 · 停更 ${entry.days_stale} 天
                </div>
            </div>
            <div class="leaderboard-score">${entry.score}</div>
        </div>
    `).join('');
}

/**
 * 投票功能
 * @param {string} entryId - 条目 ID
 */
async function vote(entryId) {
    const button = document.getElementById(`vote-btn-${entryId}`);

    // 禁用按钮（防抖）
    button.disabled = true;
    button.textContent = '提交中...';

    try {
        const response = await fetch('/api/vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ entry_id: entryId })
        });

        const result = await response.json();

        if (result.ok) {
            // 投票成功，重新加载数据
            await loadEntries();
            showToast('投票成功！', 'success');
        } else {
            // 投票失败（如已投票）
            showToast(result.error || '投票失败', 'error');
            button.disabled = false;
            button.textContent = '踩一脚 👟';
        }
    } catch (error) {
        console.error('Vote error:', error);
        showToast('网络错误，请稍后重试', 'error');
        button.disabled = false;
        button.textContent = '踩一脚 👟';
    }

    // 2 秒后恢复按钮（如果没有成功投票）
    setTimeout(() => {
        if (button.disabled) {
            button.disabled = false;
            button.textContent = '踩一脚 👟';
        }
    }, 2000);
}

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型（success/error）
 */
function showToast(message, type = 'info') {
    // 创建 toast 元素
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background-color: ${type === 'success' ? '#4caf50' : '#ff6b35'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;

    // 添加到页面
    document.body.appendChild(toast);

    // 3 秒后移除
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

/**
 * HTML 转义（防 XSS）
 * @param {string} text - 待转义的文本
 * @returns {string} 转义后的文本
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 添加 CSS 动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

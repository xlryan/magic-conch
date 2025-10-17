/**
 * 神奇海螺·烂尾博物馆 - 前端交互逻辑
 * 版本 2.0 - 支持用户提交、点赞、审核
 */

// ==================== 全局状态 ====================
let allEntries = [];
let userTags = [];

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    initTagInput();
    initSubmitForm();
    loadEntries();
});

// ==================== 标签输入功能 ====================
function initTagInput() {
    const tagInput = document.getElementById('tag-input');
    const tagsDisplay = document.getElementById('tags-display');

    tagInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tag = tagInput.value.trim().toLowerCase();

            if (tag && userTags.length < 10) {
                if (!userTags.includes(tag)) {
                    userTags.push(tag);
                    renderTags();
                    tagInput.value = '';
                } else {
                    showToast('该标签已存在', 'info');
                }
            } else if (userTags.length >= 10) {
                showToast('最多添加 10 个标签', 'warning');
            }
        }
    });
}

function renderTags() {
    const tagsDisplay = document.getElementById('tags-display');
    tagsDisplay.innerHTML = userTags.map(tag => `
        <span class="tag">
            ${escapeHtml(tag)}
            <span class="tag-remove" onclick="removeTag('${escapeHtml(tag)}')">✕</span>
        </span>
    `).join('');
}

function removeTag(tag) {
    userTags = userTags.filter(t => t !== tag);
    renderTags();
}

// ==================== 提交表单 ====================
function initSubmitForm() {
    const form = document.getElementById('submit-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitEntry();
    });
}

async function submitEntry() {
    const submitBtn = document.getElementById('submit-btn');
    const originalText = submitBtn.textContent;

    // 禁用按钮
    submitBtn.disabled = true;
    submitBtn.textContent = '提交中...';

    try {
        const formData = {
            title: document.getElementById('title').value.trim(),
            owner: document.getElementById('owner').value.trim(),
            repo_url: document.getElementById('repo_url').value.trim(),
            last_commit: document.getElementById('last_commit').value,
            summary: document.getElementById('summary').value.trim(),
            tags: userTags.length > 0 ? userTags : null
        };

        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.ok) {
            showToast('✨ 提交成功！等待管理员审核后即可展示', 'success');
            // 重置表单
            document.getElementById('submit-form').reset();
            userTags = [];
            renderTags();
            // 滚动到顶部
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            showToast(result.error || '提交失败，请稍后重试', 'error');
        }
    } catch (error) {
        console.error('Submit error:', error);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// ==================== 加载条目 ====================
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
            <div class="loading" style="color: var(--color-danger);">
                ❌ 加载失败，请刷新页面重试
            </div>
        `;
        document.getElementById('leaderboard').innerHTML = `
            <div class="loading" style="color: var(--color-danger);">
                ❌ 加载失败
            </div>
        `;
    }
}

// ==================== 渲染条目列表 ====================
function renderEntries() {
    const container = document.getElementById('entries-list');

    if (allEntries.length === 0) {
        container.innerHTML = `
            <div class="card text-center">
                <p style="color: var(--color-text-muted); font-size: var(--text-lg);">
                    暂无已批准的项目，快来提交第一个吧！
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = allEntries.map(entry => createEntryCard(entry)).join('');
}

function createEntryCard(entry) {
    const tags = entry.tags ? entry.tags.split(',').map(t => t.trim()).filter(t => t) : [];

    return `
        <article class="entry-card fade-in">
            <div class="entry-header">
                <div class="entry-info">
                    <h3 class="entry-title">${escapeHtml(entry.title)}</h3>
                    <div class="entry-owner">👤 ${escapeHtml(entry.owner)}</div>
                </div>
                <div class="entry-score-badge">
                    <div class="entry-score-value">${entry.score}</div>
                    <div class="entry-score-label">烂尾指数</div>
                </div>
            </div>

            <p class="entry-summary">${escapeHtml(entry.summary)}</p>

            <div class="entry-meta">
                <div class="meta-item">
                    📅 最后活跃：<strong>${entry.last_commit}</strong>
                </div>
                <div class="meta-item">
                    ⏱️ 停更：<strong>${entry.days_stale}</strong> 天
                </div>
            </div>

            ${tags.length > 0 ? `
                <div class="entry-tags">
                    ${tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}

            <div class="entry-actions">
                <button
                    class="btn btn-primary"
                    onclick="vote('${entry.id}')"
                    id="vote-btn-${entry.id}"
                >
                    👟 踩一脚
                </button>

                <button
                    class="btn btn-secondary"
                    onclick="toggleLike('${entry.id}')"
                    id="like-btn-${entry.id}"
                >
                    ❤️ 点赞
                </button>

                <a
                    href="${escapeHtml(entry.repo_url)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn btn-ghost"
                >
                    🔗 查看项目
                </a>

                <div class="stats-group">
                    <div class="stat-item">
                        <span>👟</span>
                        <span class="stat-value" id="vote-count-${entry.id}">${entry.votes}</span>
                    </div>
                    <div class="stat-item">
                        <span>❤️</span>
                        <span class="stat-value" id="like-count-${entry.id}">${entry.likes}</span>
                    </div>
                </div>
            </div>
        </article>
    `;
}

// ==================== 投票功能（踩一脚）====================
async function vote(entryId) {
    const button = document.getElementById(`vote-btn-${entryId}`);
    const originalText = button.textContent;

    // 禁用按钮
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
            // 更新投票数
            const voteCountEl = document.getElementById(`vote-count-${entryId}`);
            if (voteCountEl) {
                voteCountEl.textContent = result.data.votes;
            }

            // 重新加载数据以更新分数和排行榜
            await loadEntries();

            showToast('👟 踩一脚成功！', 'success');
        } else {
            showToast(result.error || '投票失败', 'error');
        }
    } catch (error) {
        console.error('Vote error:', error);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        // 恢复按钮（2秒冷却）
        setTimeout(() => {
            button.disabled = false;
            button.textContent = originalText;
        }, 2000);
    }
}

// ==================== 点赞功能 ====================
async function toggleLike(entryId) {
    const button = document.getElementById(`like-btn-${entryId}`);
    const originalText = button.textContent;

    // 禁用按钮
    button.disabled = true;
    button.textContent = '处理中...';

    try {
        const response = await fetch('/api/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ entry_id: entryId })
        });

        const result = await response.json();

        if (result.ok) {
            // 更新点赞数
            const likeCountEl = document.getElementById(`like-count-${entryId}`);
            if (likeCountEl) {
                likeCountEl.textContent = result.data.likes;
            }

            // 更新按钮状态
            if (result.data.action === 'liked') {
                button.textContent = '💖 已点赞';
                showToast('❤️ 点赞成功！', 'success');
            } else {
                button.textContent = '❤️ 点赞';
                showToast('已取消点赞', 'info');
            }
        } else {
            showToast(result.error || '操作失败', 'error');
        }
    } catch (error) {
        console.error('Like error:', error);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        // 恢复按钮
        setTimeout(() => {
            button.disabled = false;
            if (button.textContent === '处理中...') {
                button.textContent = originalText;
            }
        }, 1000);
    }
}

// ==================== 渲染排行榜 ====================
function renderLeaderboard() {
    const container = document.getElementById('leaderboard');

    if (allEntries.length === 0) {
        container.innerHTML = `
            <div class="loading" style="color: var(--color-text-muted);">
                暂无数据
            </div>
        `;
        return;
    }

    // 取前 10 名
    const top10 = allEntries.slice(0, 10);

    container.innerHTML = top10.map((entry, index) => `
        <div class="leaderboard-item" onclick="scrollToEntry('${entry.id}')">
            <div class="leaderboard-rank">${index + 1}</div>
            <div class="leaderboard-info">
                <div class="leaderboard-title">${escapeHtml(entry.title)}</div>
                <div class="leaderboard-meta">
                    ${escapeHtml(entry.owner)} · 👟 ${entry.votes} · ❤️ ${entry.likes} · ⏱️ ${entry.days_stale}天
                </div>
            </div>
            <div class="leaderboard-score">${entry.score}</div>
        </div>
    `).join('');
}

function scrollToEntry(entryId) {
    const entryCard = document.querySelector(`[data-entry-id="${entryId}"]`);
    if (entryCard) {
        entryCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // 高亮效果
        entryCard.style.boxShadow = '0 0 30px rgba(244, 162, 97, 0.5)';
        setTimeout(() => {
            entryCard.style.boxShadow = '';
        }, 2000);
    }
}

// ==================== Toast 通知 ====================
function showToast(message, type = 'info') {
    // 创建 toast 元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.animation = 'slideInRight var(--transition-base) ease-out';

    // 添加到页面
    document.body.appendChild(toast);

    // 3 秒后移除
    setTimeout(() => {
        toast.style.animation = 'slideOutRight var(--transition-base) ease-in';
        setTimeout(() => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        }, 250);
    }, 3000);
}

// ==================== 工具函数 ====================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== 键盘快捷键 ====================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: 聚焦到提交表单
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('title').focus();
        document.getElementById('submit-section').scrollIntoView({ behavior: 'smooth' });
    }
});

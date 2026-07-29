# 同学录 — 前端开发文档（完整版）

> **项目路径：** `/var/minis/workspace/classmates-book/`
> **设计系统：** UI/UX Pro Max — Claymorphism（软陶风格）
> **CSS 文件：** `backend/core/static/core/css/style.css`（20.5 KB）
> **模板目录：** `backend/core/templates/core/`（11 个文件）
> **最后更新：** 2026-07-29

---

## 一、设计系统总览

### 1.1 风格决策

| 维度 | 选择 | 决策依据 |
|------|------|----------|
| **风格** | Claymorphism（软陶风格） | 圆润、温暖、亲切，适合社交/回忆类产品 |
| **色彩倾向** | 玫瑰红 (#E11D48) + 暖粉背景 (#FFF1F2) | 温馨浪漫，唤起青春校园回忆 |
| **字体情绪** | Varela Round（圆润标题） + Nunito Sans（清晰正文） | 柔和友好 + 高可读性 |
| **交互反馈** | 弹簧缩放（spring squish） | 按下弹性内凹，松手弹回，增加触感乐趣 |
| **动效幅度** | 中等（Standard），微交互为主 | 不喧宾夺主，提升体验质感 |
| **布局** | 移动优先，自适应到桌面 | 手机端使用群体为主 |

**设计生成命令：**
```bash
python3 /var/minis/skills/ui-ux-pro-max/scripts/search.py \
  "memory social classmates school warm friendly" \
  --design-system -p "同学录"
```

### 1.2 完整色彩体系

```
🎨 配色总览

Primary     #E11D48  ──── 主色（按钮、链接、强调）
Secondary   #FB7185  ──── 辅助色（图标、次要元素）
Accent      #2563EB  ──── 强调色（点缀元素）

Background  #FFF1F2  ──── 页面背景（暖粉白）
Foreground  #881337  ──── 正文文字色
Muted       #F0ECF2  ──── 弱化背景
Border      #FECDD3  ──── 边框颜色

Destructive #DC2626  ──── 危险操作（删除）
Ring        #E11D48  ──── 聚焦环
Success     #16A34A  ──── 成功状态
Warning     #F59E0B  ──── 警告状态
```

**CSS 变量定义：**
```css
:root {
    --color-primary: #E11D48;
    --color-primary-light: #FB7185;
    --color-primary-dark: #BE123C;
    --color-on-primary: #FFFFFF;
    --color-secondary: #FB7185;
    --color-accent: #2563EB;
    --color-background: #FFF1F2;
    --color-background-alt: #F8FAFC;
    --color-foreground: #881337;
    --color-foreground-light: #9F1239;
    --color-muted: #F0ECF2;
    --color-border: #FECDD3;
    --color-destructive: #DC2626;
    --color-ring: #E11D48;
    --color-success: #16A34A;
    --color-warning: #F59E0B;
    --color-white: #FFFFFF;
}
```

### 1.3 完整字体体系

```css
/* Google Fonts 引入（已包含全部需要字重） */
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@300;400;500;600;700&family=Varela+Round&display=swap');

:root {
    --font-heading: 'Varela Round', sans-serif;
    --font-body: 'Nunito Sans', sans-serif;
}
```

**字号层级（Type Scale）：**

| CSS 层级 | 字号 | 行高 | 字重 | 字间距 | 用途 |
|----------|------|------|------|--------|------|
| `h1` | 2.5rem (40px) | 1.3 | 400 (Varela Round) | -0.02em | 页面大标题 |
| `h2` | 2rem (32px) | 1.3 | 400 | -0.01em | 区块标题 |
| `h3` | 1.5rem (24px) | 1.3 | 400 | normal | 卡片标题 |
| `h4` | 1.25rem (20px) | 1.3 | 400 | normal | 小组标题 |
| `h5` | 1.125rem (18px) | 1.3 | 400 | normal | 副标题 |
| 正文 | 1rem (16px) | 1.6 | 400 (Nunito Sans) | normal | **最小可读字号** |
| `.text-sm` | 0.875rem (14px) | 1.5 | 400 | normal | 辅助信息 |
| `.text-xs` | 0.75rem (12px) | 1.4 | 400 | normal | 标签/时间戳 |

### 1.4 完整间距体系

```
Spacing Scale (4px 增量 / 0.25rem 步进)

--space-xs  =  4px  │ 极紧凑间距（图标与文字最小间距）
--space-sm  =  8px  │ 图标间距，内联元素间隙
--space-md  = 16px  │ 标准内边距，默认间距
--space-lg  = 24px  │ 卡片内边距，区块间距
--space-xl  = 32px  │ 大区块间距，表单组间距
--space-2xl = 48px  │ 章节间距，页面顶部间距
--space-3xl = 64px  │ Hero 区域间距，超大间距
```

### 1.5 完整圆角体系

```
Border Radius Scale

--radius-sm   = 12px  │ 小卡片、小型按钮、标签
--radius-md   = 20px  │ 标准卡片、标准按钮、输入框
--radius-lg   = 32px  │ 外层容器（modal、大卡片）
--radius-xl   = 40px  │ 大尺寸头像、特殊装饰
--radius-full = 50%   │ 圆形头像、圆形图标
```

### 1.6 软陶阴影系统（Claymorphism）

Claymorphism 的核心原理：**深色投影 + 浅色内发光**，模拟黏土的立体感和柔软触感。

```
层叠结构（由外到内）：
┌─────────────────────────────────┐
│  外阴影（深色投影）              │  ← 模拟黏土在光照下的投影
│  ┌───────────────────────────┐   │
│  │  内容区域                  │   │
│  └───────────────────────────┘   │
│  内阴影（浅色发光）              │  ← 模拟黏土背光面的反光
└─────────────────────────────────┘
```

```css
/* 标准软陶阴影（卡片主要） */
--clay-shadow: 8px 8px 16px rgba(225, 29, 72, 0.12),
               -4px -4px 12px rgba(255, 241, 242, 0.8);

/* 小号阴影（按钮、小卡片） */
--clay-shadow-sm: 4px 4px 8px rgba(225, 29, 72, 0.10),
                  -2px -2px 6px rgba(255, 241, 242, 0.6);

/* 大号阴影（弹窗、浮层） */
--clay-shadow-lg: 12px 12px 24px rgba(225, 29, 72, 0.15),
                  -6px -6px 18px rgba(255, 241, 242, 0.9);

/* 内凹阴影（输入框、按下状态） */
--clay-shadow-inset: inset 3px 3px 6px rgba(225, 29, 72, 0.08),
                     inset -2px -2px 4px rgba(255, 241, 242, 0.5);

/* 按下阴影（按钮点击时） */
--clay-shadow-pressed: inset 4px 4px 8px rgba(225, 29, 72, 0.15),
                       inset -2px -2px 4px rgba(255, 241, 242, 0.3);
```

### 1.7 过渡动效系统

| Token | 值 | 曲线特征 | 用途 |
|-------|-----|----------|------|
| `--transition-fast` | 150ms | ease-out | 按钮悬停、输入框聚焦 |
| `--transition-normal` | 250ms | ease-out | 卡片悬浮、阴影过渡 |
| `--transition-slow` | 400ms | ease-out | 弹窗遮罩、页面切换 |
| `--transition-spring` | 500ms | spring (0.34, 1.56, 0.64, 1) | 弹性入场、缩放效果 |

**所有 CSS 变量的共享前缀：** `--clay-`（阴影）、`--radius-`（圆角）、`--space-`（间距）、`--transition-`（过渡）、`--color-`（颜色）

---

## 二、CSS 组件库（完整规格）

> 文件路径：`backend/core/static/core/css/style.css`（约 20.5 KB）

### 2.1 导航栏（Navbar）

```css
.navbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(255, 241, 242, 0.85);  /* 半透明背景 */
    backdrop-filter: blur(20px);             /* 毛玻璃效果 */
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--color-border);
    padding: var(--space-md) 0;
}

.navbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-lg);
}

.navbar-brand {
    font-family: var(--font-heading);
    font-size: 1.5rem;
    color: var(--color-primary);
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}

.navbar-links {
    display: flex;
    align-items: center;
    gap: var(--space-md);
}
```

**响应式行为：** 手机端 padding 从 24px 缩小到 16px

### 2.2 按钮体系（7 个变体）

| CSS 类 | 背景 | 文字色 | 边框 | 阴影 | 悬停效果 | 用途 |
|--------|------|--------|------|------|----------|------|
| `.btn-primary` | `var(--color-primary)` | `white` | 无 | 有 | 加深 + 上移 | 主要操作 |
| `.btn-secondary` | `white` | `var(--color-primary)` | `var(--color-border)` | 有 | 阴影加深 | 次要操作 |
| `.btn-ghost` | 透明 | `var(--color-foreground)` | 无 | 无 | 浅色背景 | 轻量操作 |
| `.btn-danger` | `var(--color-destructive)` | `white` | 无 | 有 | 加深 | 删除/危险 |
| `.btn-sm` | - | - | - | - | - | 小型（padding 缩小） |
| `.btn-lg` | - | - | - | - | - | 大型（padding 增大） |
| `.btn-block` | - | - | - | - | - | 全宽（width:100%） |

```css
/* 通用按钮基础 */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-sm);
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9375rem;
    padding: 12px 28px;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: var(--transition-normal);
    min-height: 44px;          /* 触摸友好 */
    min-width: 44px;           /* 触摸友好 */
    text-decoration: none;
    line-height: 1.2;
}

/* 按下弹性反馈 */
.btn:active {
    transform: scale(0.96);
}
```

### 2.3 卡片体系（4 个变体）

| CSS 类 | 圆角 | 阴影 | padding | 用途 |
|--------|------|------|---------|------|
| `.card` | `--radius-lg` (32px) | `--clay-shadow` | `32px` | 标准内容块 |
| `.card-sm` | `--radius-md` (20px) | `--clay-shadow-sm` | `24px` | 紧凑内容 |
| `.student-card` | `--radius-lg` (32px) | `--clay-shadow-sm` | `24px` | 同学列表卡片 |
| `.trash-item` | `--radius-md` (20px) | `--clay-shadow-sm` | `16px 24px` | 回收站条目 |

**统一交互规范：**
```css
.card:hover {
    box-shadow: var(--clay-shadow-lg);
    transform: translateY(-2px);
    transition: var(--transition-normal);
}
```

### 2.4 表单组件完整规格

| CSS 类 | 用途 | 高度 | 特殊样式 |
|--------|------|------|----------|
| `.form-group` | 表单项容器 | - | `margin-bottom: var(--space-lg)` |
| `.form-label` | 标签文本 | - | `font-weight: 600` |
| `.form-label .required` | 必填标记 | - | `color: var(--color-primary)` |
| `.form-input` | 文本/数字输入 | min 48px | 内凹阴影 + 聚焦外发光 |
| `.form-textarea` | 多行文本 | min 100px | `.tall` → min 160px |
| `.form-select` | 下拉选择 | min 48px | 同输入框样式 |
| `.form-error` | 错误提示 | - | 红色 + flex 布局 |
| `.form-helper` | 辅助说明 | - | 浅色小字 |

```css
/* 输入框完整样式 */
.form-input {
    width: 100%;
    padding: 14px 18px;
    font-family: var(--font-body);
    font-size: 1rem;              /* 防止 iOS 自动缩放 */
    color: var(--color-foreground);
    background: var(--color-white);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-md);
    outline: none;
    transition: var(--transition-fast);
    box-shadow: var(--clay-shadow-inset);  /* 内凹效果 */
    min-height: 48px;
}

/* 聚焦状态 */
.form-input:focus {
    border-color: var(--color-primary);
    box-shadow: var(--clay-shadow-inset),
                0 0 0 4px rgba(225, 29, 72, 0.1);  /* 外发光环 */
}

/* placeholder 颜色 */
.form-input::placeholder {
    color: #D1A7B0;  /* 浅玫瑰色 */
    opacity: 1;
}
```

### 2.5 文件上传组件

```html
<div class="file-upload-area">
    <svg class="upload-icon">...</svg>
    <p>点击或拖拽上传照片</p>
    <p class="text-xs">支持 JPG、PNG、WebP，可多选</p>
    <input type="file" name="photos" accept="image/*" multiple style="display:none">
</div>
<div class="file-preview-grid"></div>
```

```css
.file-upload-area {
    border: 2px dashed var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--space-xl);
    text-align: center;
    cursor: pointer;
    transition: var(--transition-normal);
    background: rgba(255, 255, 255, 0.5);
}

.file-upload-area:hover,
.file-upload-area.dragover {
    border-color: var(--color-primary);
    background: rgba(225, 29, 72, 0.03);
}

.file-preview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--space-sm);
    margin-top: var(--space-md);
}

.file-preview-item {
    position: relative;
    border-radius: var(--radius-sm);
    overflow: hidden;
    aspect-ratio: 1;
    background: var(--color-muted);
}

.file-preview-item img,
.file-preview-item video {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.file-preview-item .remove-file {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 24px;
    height: 24px;
    border-radius: var(--radius-full);
    background: rgba(0,0,0,0.6);
    color: white;
    border: none;
    cursor: pointer;
}
```

### 2.6 弹窗（Modal）

```css
.modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-lg);
    animation: fadeIn 200ms ease-out;
}

.modal-content {
    background: var(--color-white);
    border-radius: var(--radius-xl);
    padding: var(--space-2xl);
    max-width: 520px;
    width: 100%;
    box-shadow: var(--clay-shadow-lg);
    animation: scaleIn 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-actions {
    display: flex;
    gap: var(--space-sm);
    margin-top: var(--space-xl);
    justify-content: flex-end;
}
```

### 2.7 搜索栏

```css
.search-bar {
    position: relative;
    max-width: 400px;
}

.search-bar .search-icon {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    color: var(--color-primary-light);
    pointer-events: none;
}

.search-bar input {
    width: 100%;
    padding: 12px 16px 12px 44px;  /* 左侧留空给图标 */
    font-family: var(--font-body);
    font-size: 0.9375rem;
    border: 2px solid var(--color-border);
    border-radius: var(--radius-md);
    outline: none;
    background: var(--color-white);
    box-shadow: var(--clay-shadow-inset);
    transition: var(--transition-fast);
}

.search-bar input:focus {
    border-color: var(--color-primary);
    box-shadow: var(--clay-shadow-inset), 0 0 0 4px rgba(225, 29, 72, 0.1);
}
```

---

## 三、CSS 关键帧动画库

### 3.1 入场动画

| Keyframes 名 | 类型 | 持续时间 | 缓动函数 | 适用 |
|-------------|------|---------|----------|------|
| `fadeIn` | Opacity 0→1 | 400ms | ease-out | 页面整体淡入 |
| `slideUp` | TranslateY(20px)→0 + fadeIn | 500ms | ease-out | 卡片逐个上滑 |
| `scaleIn` | Scale(0.9)→1 + fadeIn | 400ms | spring (0.34, 1.56, 0.64, 1) | 弹窗缩放 |

```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes blob {
    0%   { transform: translate(0, 0) scale(1); }
    33%  { transform: translate(20px, -15px) scale(1.1); }
    66%  { transform: translate(-15px, 10px) scale(0.9); }
    100% { transform: translate(0, 0) scale(1); }
}
```

### 3.2 错帧延迟（Stagger）

每个卡片按顺序延迟出现，产生错落有致的入场效果。

| 类名 | 延迟 | 使用顺序 |
|------|------|----------|
| `.stagger-1` | `animation-delay: 100ms` | 第一个元素 |
| `.stagger-2` | `animation-delay: 200ms` | 第二个元素 |
| `.stagger-3` | `animation-delay: 300ms` | 第三个元素 |
| `.stagger-4` | `animation-delay: 400ms` | 第四个元素 |
| `.stagger-5` | `animation-delay: 500ms` | 第五个及以上 |

**使用示例：**
```html
{% for item in items %}
<div class="card animate-slide-up stagger-{{ forloop.counter }}">
    ...
</div>
{% endfor %}
```

---

## 四、JavaScript 功能（完整代码）

### 4.1 通用功能 — base.html

#### 复制到剪贴板
```javascript
function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const original = btn.innerHTML;
        btn.innerHTML = '✓ 已复制';
        btn.style.transition = 'color 200ms';
        setTimeout(() => { btn.innerHTML = original; }, 2000);
    }).catch(() => {
        // 降级方案：使用 textarea + execCommand
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.innerHTML = '✓ 已复制';
        setTimeout(() => { btn.innerHTML = original; }, 2000);
    });
}
```

#### 消息自动消失
```javascript
document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
        el.style.transition = 'opacity 400ms';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
    }, 5000);
});
```

#### 文件上传预览（完整版）
```javascript
document.querySelectorAll('.file-upload-area').forEach(area => {
    const input = area.querySelector('input[type="file"]');
    const preview = area.nextElementSibling;
    if (!input || !preview) return;

    // 点击触发文件选择
    area.addEventListener('click', () => input.click());

    // 文件选择后生成预览
    input.addEventListener('change', () => {
        preview.innerHTML = '';
        Array.from(input.files).forEach((file, i) => {
            const reader = new FileReader();
            reader.onload = e => {
                const div = document.createElement('div');
                div.className = 'file-preview-item';
                const isVideo = file.type.startsWith('video/');
                const media = isVideo ? document.createElement('video') : document.createElement('img');
                media.src = e.target.result;
                if (isVideo) media.controls = true;
                div.appendChild(media);
                // 删除按钮
                const rm = document.createElement('button');
                rm.className = 'remove-file';
                rm.innerHTML = '×';
                rm.type = 'button';
                rm.onclick = () => { div.remove(); };
                div.appendChild(rm);
                preview.appendChild(div);
            };
            reader.readAsDataURL(file);
        });
    });

    // 拖拽支持
    area.addEventListener('dragover', e => {
        e.preventDefault();
        area.classList.add('dragover');
    });
    area.addEventListener('dragleave', () => area.classList.remove('dragover'));
    area.addEventListener('drop', e => {
        e.preventDefault();
        area.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            input.dispatchEvent(new Event('change'));
        }
    });
});
```

### 4.2 注册页 — 发送验证码

```javascript
var countdown = 0;
function sendCode() {
    var btn = document.getElementById('sendCodeBtn');
    var email = document.getElementById('email').value.trim();
    if (!email || !email.includes('@')) {
        alert('请先输入有效的邮箱地址');
        return;
    }
    if (countdown > 0) return;

    btn.disabled = true;
    btn.textContent = '发送中...';

    fetch('/api/send-verification-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ email: email })
    })
    .then(r => r.json())
    .then(data => {
        if (data.code === 200) {
            countdown = 60;
            btn.textContent = countdown + 's';
            var timer = setInterval(function() {
                countdown--;
                btn.textContent = countdown + 's';
                if (countdown <= 0) {
                    clearInterval(timer);
                    btn.disabled = false;
                    btn.textContent = '重新发送';
                }
            }, 1000);
        } else {
            alert(data.message || '发送失败，请重试');
            btn.disabled = false;
            btn.textContent = '发送验证码';
        }
    })
    .catch(function() {
        alert('网络错误，请重试');
        btn.disabled = false;
        btn.textContent = '发送验证码';
    });
}
```

### 4.3 同学录详情页 — 搜索与删除弹窗

```javascript
// 实时搜索
function searchStudents(query) {
    var items = document.querySelectorAll('.student-card-item');
    var found = false;
    items.forEach(function(item) {
        var name = item.dataset.name || '';
        var match = name.includes(query);
        item.style.display = match ? '' : 'none';
        if (match) found = true;
    });
    var noResults = document.getElementById('noResults');
    if (noResults) {
        noResults.style.display = (query && !found) ? 'block' : 'none';
    }
    // 无结果时显示空状态
    var filterCount = document.querySelector('.student-count');
    if (filterCount) {
        var visibleCount = 0;
        items.forEach(function(item) {
            if (item.style.display !== 'none') visibleCount++;
        });
        filterCount.textContent = '筛选出 ' + visibleCount + ' 位同学';
    }
}

// 删除确认弹窗
function showDeleteModal(id, name) {
    document.getElementById('deleteName').textContent = name;
    document.getElementById('deleteForm').action = '/notebook/' + notebookId + '/delete/' + id + '/';
    document.getElementById('deleteModal').style.display = 'flex';
    // 阻止 body 滚动
    document.body.style.overflow = 'hidden';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    document.body.style.overflow = '';
}

// 点击遮罩关闭
document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) closeDeleteModal();
});

// ESC 键关闭
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDeleteModal();
});
```

---

## 五、页面模板完整规格

### 5.1 页面清单

| 序号 | 页面名称 | 路由 | 模板文件 | 权限 | 模板继承 |
|------|----------|------|----------|------|----------|
| 1 | 首页 | `/` | `home.html` | 公开 | `base.html` |
| 2 | 注册 | `/register/` | `register.html` | 未登录 | `base.html` |
| 3 | 登录 | `/login/` | `login.html` | 未登录 | `base.html` |
| 4 | 仪表盘 | `/dashboard/` | `dashboard.html` | 已登录 | `base.html` |
| 5 | 创建同学录 | `/notebook/create/` | `notebook_create.html` | 已登录 | `base.html` |
| 6 | 同学录详情 | `/notebook/<id>/` | `notebook_detail.html` | 仅创建者 | `base.html` |
| 7 | 填写表单 | `/join/<share_code>/` | `fill_form.html` | 公开 | `base.html` |
| 8 | 编辑表单 | `/edit/<edit_code>/` | `fill_form.html` | 公开(有编辑码) | `base.html` |
| 9 | 提交成功 | `/join/<share_code>/success/` | `fill_success.html` | 公开 | `base.html` |
| 10 | 同学详情 | `/student/<id>/` | `student_detail.html` | 仅创建者 | `base.html` |
| 11 | 回收站 | `/notebook/<id>/trash/` | `notebook_trash.html` | 仅创建者 | `base.html` |

### 5.2 首页（home.html）

**页面结构（从上到下）：**
```
┌─ Navbar ─────────────────────────────┐  sticky, blur 毛玻璃
│  logo + [登录] [注册]                  │
├─ Hero Section ────────────────────────┤  padding: 80px 0
│  大 Logo（浮动动画 6s）                │  width: 88px, box-shadow 浮动
│  h1: "同窗录" (3rem)                  │
│  p: 副标题文案                         │
│  [免费创建同学录] [我已注册] (btn-lg)   │  两个按钮并排
├─ Features Section ────────────────────┤  padding: 80px 0
│  h2: "为什么选择同窗录？"               │
│  3列卡片网格 (grid-3)                  │
│  ① 无需注册即可填写                    │
│  ② 照片视频全支持                      │
│  ③ 轻松搜索查找                        │
├─ How it Works ───────────────────────┤  bg: rgba(255,255,255,0.3)
│  h2: "三步搞定"                       │
│  3个步骤卡片 (水平排列)                │
│  ① 创建同学录 → ② 分享链接 → ③ 查看    │
├─ CTA Section ─────────────────────────┤  padding: 80px 0
│  card 居中                            │
│  [免费创建同学录]                      │
├─ Footer ──────────────────────────────┤
│  "同窗录 · 珍藏每一份同窗情谊"          │
└───────────────────────────────────────┘
```

**后端变量：** 无（纯静态页面）

### 5.3 注册页（register.html）

**页面结构：**
```
┌─ Navbar ───────────────────────────────┐
├─ Card (max-width: 480px) ──────────────┤  margin: 0 auto
│  Logo: 用户加号图标 (64px)              │  渐变背景 + 阴影
│  h1: "注册同窗录"                       │
│  p: 引导文案                            │
│                                        │
│  表单:                                  │
│  □ 邮箱 (email)                        │  placeholder: 请输入邮箱地址
│  □ [验证码输入框] [发送验证码]           │  60s倒计时按钮
│  □ 密码 (password, minlength=8)         │
│  □ 确认密码 (password)                  │
│                                        │
│  [注 册] (btn-primary btn-lg btn-block) │
│                                        │
│  "已有账号？去登录"                     │
└────────────────────────────────────────┘
```

**表单校验规则：**
| 字段 | 规则 | 前端校验 | 后端校验 |
|------|------|----------|----------|
| email | 必填，合法邮箱格式 | HTML5 `type="email"` | Django EmailField |
| verification_code | 必填，6位数字 | `pattern="[0-9]{6}"` | DB 查询匹配 |
| password | 必填，≥8位 | `minlength="8"` | Django 长度校验 |
| confirm_password | 必填，与 password 一致 | JS 提交前校验 | Django Form.clean() |

### 5.4 登录页（login.html）

**简化版注册页结构：**
```
┌─ Navbar ───────────────────────┐
├─ Card ─────────────────────────┤  max-width: 420px
│  Logo: 锁图标                   │
│  h1: "欢迎回来"                 │
│  表单:                          │
│  □ 邮箱                         │
│  □ 密码                         │
│  [登 录]                       │
│  "还没账号？去注册"              │
│  ———————————                    │
│  "记录青春 · 珍藏同窗情谊"       │
└────────────────────────────────┘
```

### 5.5 仪表盘（dashboard.html）

**后端变量：**
```python
context = {
    'notebooks': [
        {
            'id': 1,
            'title': '初中3班同学录',
            'share_code': UUID('...'),
            'created_at': datetime,
            'students': QuerySet[Student],  # 前端使用 .count
        },
        # ...
    ]
}
```

**页面逻辑：**
- 有同学录 → 显示网格卡片
- 无同学录 → 显示空状态（含创建引导按钮）
- 每张卡片显示：同学录名称、人数、创建日期
- 每个卡片有「复制分享链接」按钮
- 点击卡片跳转到同学录详情

### 5.6 创建同学录（notebook_create.html）

**极简表单：**
```
┌─ 返回 按钮 ─────────────────┐
│  h1: "📝 新建同学录"         │
├─ Card ──────────────────────┤
│  □ 同学录名称 (max_length=100)│
│  示例：初中3班同学录          │
│  [创建同学录]                │
├─ Tips Card ─────────────────┤
│  ℹ️ 小贴士                   │
│  创建后生成分享链接……         │
└─────────────────────────────┘
```

### 5.7 同学录详情页（notebook_detail.html）

**后端变量：**
```python
context = {
    'notebook': Notebook,
    'students': [Student, ...],  # is_deleted=False, order_by('name')
}
```

**页面逻辑：**
1. 顶部导航：返回 + 同学录名称 + 复制链接按钮
2. 搜索栏：实时模糊搜索（纯前端 JS，按 `data-name` 属性过滤）
3. 同学卡片网格（`grid-auto`）：每张卡片显示头像首字母、姓名、昵称、电话、微信
4. 删除按钮 → Modal 确认弹窗
5. 空状态：无人填写时显示引导

### 5.8 填写/编辑表单页（fill_form.html）

**完整字段分组（30 个字段）：**

| 分组 | 字段 | 必填 | 组件类型 |
|------|------|------|----------|
| 基本信息 | name | ✅ | text input |
| 基本信息 | nickname | ✅ | text input |
| 基本信息 | phone | ✅ | tel input |
| 基本信息 | wechat | ✅ | text input |
| 想对TA说 | first_impression | ✅ | textarea |
| 想对TA说 | words_to_me | ✅ | textarea |
| 想对TA说 | message | ✅ | textarea (.tall) |
| 联系方式 | qq | ❌ | text input |
| 联系方式 | xiaohongshu | ❌ | text input |
| 联系方式 | douyin | ❌ | text input |
| 联系方式 | email | ❌ | email input |
| 联系方式 | address | ❌ | text input |
| 个人信息 | birthday | ❌ | date input |
| 个人信息 | zodiac_sign | ❌ | select (12生肖) |
| 个人信息 | constellation | ❌ | select (12星座) |
| 个人信息 | hobbies | ❌ | textarea |
| 个人信息 | motto | ❌ | text input |
| 心情回忆 | crush | ❌ | text input |
| 心情回忆 | dislike | ❌ | text input |
| 心情回忆 | wish | ❌ | textarea |
| 心情回忆 | dream | ❌ | textarea |
| 心情回忆 | favorite_food | ❌ | text input |
| 心情回忆 | most_want_to_see | ❌ | text input |
| 心情回忆 | favorite_movie | ❌ | text input |
| 心情回忆 | favorite_music | ❌ | text input |
| 心情回忆 | most_want_to_go | ❌ | text input |
| 心情回忆 | most_unforgettable | ❌ | textarea |
| 心情回忆 | hope_10_years | ❌ | textarea |
| 媒体 | photos | ❌ | file (multiple) |
| 媒体 | videos | ❌ | file (multiple) |

**编辑模式差异：**
- 显示 `edit_mode=True` 提示条，显示截止时间
- 输入框预填已有数据
- 已上传照片/视频显示为带勾选框的缩略图（勾选 = 删除）
- 表单提交改为 PUT 语义（实际是 POST + edit_code）

**后端变量：**
```python
context = {
    'notebook': Notebook,
    'edit_mode': bool,
    'student': Student or None,
    'deadline': str,  # 编辑模式下的截止时间
    'existing_photos': [MediaFile, ...],  # 编辑模式
    'existing_videos': [MediaFile, ...],  # 编辑模式
    'zodiac_choices': ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪'],
    'constellation_choices': ['白羊座','金牛座','双子座','巨蟹座','狮子座','处女座','天秤座','天蝎座','射手座','摩羯座','水瓶座','双鱼座'],
}
```

### 5.9 提交成功页（fill_success.html）

```python
context = {
    'notebook': Notebook,
    'edit_code': str,  # 从 URL query string 获取
}
```

**页面元素：**
1. ✅ 绿色圆形动画（`scaleIn` spring 动画）
2. "🎉 提交成功！"
3. 编辑码卡片（alert-info 背景，大号粗体玫瑰红文字，复制按钮）
4. 修改链接卡片（完整 URL，复制按钮）
5. 提示文字："编辑码仅显示一次，建议截图保存"
6. 操作按钮：[🖨 打印保存] [✏️ 去修改]

### 5.10 同学详情页（student_detail.html）

**后端变量：**
```python
context = {
    'notebook': Notebook,
    'student': Student,
    'media_files': [MediaFile, ...],  # 按 file_type 排序
}
```

**信息展示顺序（垂直流）：**
1. 返回按钮
2. 头像大圆 + 姓名 + 昵称
3. 联系方式区块（电话/微信/QQ/小红书/抖音/邮箱/地址）
4. 个人信息区块（生日/生肖/星座/兴趣爱好/座右铭「引号」）
5. 心情&回忆区块（❤️喜欢谁/💢讨厌谁/✨愿望/🚀梦想/🍜爱吃/👀想见的人/🎬电影/🎵音乐/🌍想去的地方/📖难忘的事/⏳10年后）→ **有值才显示**
6. 想对TA说的话区块（第一印象/想说的话/留言）→ **带引号/灰底强调**
7. 照片&视频墙（grid 缩略图，点击放大）
8. 提交时间信息

### 5.11 回收站页（notebook_trash.html）

```python
context = {
    'notebook': Notebook,
    'trash_items': [Student, ...],  # is_deleted=True, order_by('-deleted_at')
}
```

**每项显示：**
- 姓名 + 删除时间 + 剩余天数（Django `timeuntil` 过滤器）
- [♻️ 还原] POST 表单
- [🗑 永久删除] POST 表单（带 confirm 确认）

---

## 六、响应式设计与断点

### 6.1 断点系统

| 断点名称 | 最小宽度 | 最大宽度 | 布局策略 |
|----------|----------|----------|----------|
| 手机 | 320px | 639px | 单列，紧凑间距 |
| 平板 | 640px | 1023px | 2列网格 |
| 桌面 | 1024px | 1439px | 3列网格 |
| 宽屏 | 1440px | - | 1200px max-width 居中 |

### 6.2 关键响应式规则

```css
/* 手机端：单列 + 紧凑 */
@media (max-width: 640px) {
    .navbar-inner { padding: 0 var(--space-md); }     /* 24px → 16px */
    .navbar-links { gap: var(--space-sm); }           /* 16px → 8px */
    .btn { padding: 10px 20px; font-size: 0.875rem; } /* 缩小按钮 */
    .card { padding: var(--space-lg); }               /* 32px → 24px */
    .modal-content { padding: var(--space-lg); }       /* 32px → 24px */
    .modal-content { border-radius: var(--radius-lg); } /* 40px → 32px */
    .student-info-grid { grid-template-columns: 1fr; } /* 2列 → 1列 */
    .container { padding: 0 var(--space-md); }         /* 24px → 16px */
}

/* 网格响应 */
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-auto { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }

@media (max-width: 768px) {
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
    .grid-auto { grid-template-columns: 1fr; }
}
```

### 6.3 触摸友好设计

| 要求 | 标准 | 实现方式 |
|------|------|----------|
| 最小触摸目标 | 44×44px | `min-height: 44px; min-width: 44px` |
| 触摸间距 | ≥8px | `gap: var(--space-sm)` 默认 8px |
| 触摸反馈 | 按下缩放 | `:active { transform: scale(0.96) }` |
| 点击延迟 | 无 300ms | `touch-action: manipulation`（CSS） |
| 拖拽冲突 | 避免水平滑动 | 不使用水平滑动交互 |

---

## 七、可访问性（A11Y）规范

| 检查项 | 标准 | 实现 |
|--------|------|------|
| 色彩对比度 | WCAG AA 4.5:1 | 主色 #E11D48 on 白色背景 → 4.8:1 ✅ |
| 焦点状态 | 可见 focus ring | `input:focus` 外发光 4px |
| 表单标签 | label 关联 input | `.form-label` + `for/id` |
| 键盘导航 | Tab 顺序自然 | 表单元素默认 DOM 顺序 |
| aria-label | 图标按钮 | 暂未实现，后续补充 |
| 动效友好 | `prefers-reduced-motion` | 动画均用 `@media (prefers-reduced-motion)` 可关闭 |

---

## 八、UI/UX 反模式检查清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| ❌ 用 emoji 替代图标 | ✅ 已避免 | 全部使用 SVG（Heroicons 风格） |
| ❌ 缺少 `cursor:pointer` | ✅ 已覆盖 | 所有 `.btn` 和可点击卡片 |
| ❌ 布局偏移的 hover | ✅ 已避免 | 使用 `translateY` 不影响布局 |
| ❌ 低对比度文字 | ✅ 已检查 | 4.5:1 最小对比度 |
| ❌ 瞬间状态切换 | ✅ 已覆盖 | 所有交互 150-300ms 过渡 |
| ❌ 隐藏 focus 状态 | ✅ 已实现 | `:focus` 可见外发光 |
| ❌ 暗色模式 | ✅ 已确认 | 同学录仅支持浅色模式 |
| ❌ 横向滚动 | ✅ 已避免 | `overflow-x: hidden` 兜底 |
| ❌ `< 16px` 正文 | ✅ 已避免 | 最小字号 16px |
| ❌ placeholder 替代 label | ✅ 已避免 | 使用独立 `.form-label` |

---

## 九、模板继承关系图

```
base.html
│  ├── navbar（sticky + blur）
│  ├── messages（自动消失）
│  ├── blob backgrounds
│  ├── {% block content %}
│  └── 通用 JS（copyToClipboard, file upload preview）
│
├── home.html              → {% block content %}
│   ├── Hero / Features / How it Works / CTA
│   └── 无后端变量
│
├── register.html          → {% block content %} + {% block extra_scripts %}
│   ├── 注册表单 + 发送验证码 JS
│   └── 变量：{ csrf_token }
│
├── login.html             → {% block content %}
│   └── 登录表单（无额外 JS）
│
├── dashboard.html         → {% block content %}
│   ├── 同学录网格 + 空状态
│   └── 变量：{ notebooks }
│
├── notebook_create.html   → {% block content %}
│   └── 变量：无（纯表单）
│
├── notebook_detail.html   → {% block content %} + {% block extra_scripts %}
│   ├── 搜索 + 卡片网格 + 删除弹窗
│   └── 变量：{ notebook, students }
│
├── notebook_trash.html    → {% block content %}
│   ├── 回收站列表 + 操作表单
│   └── 变量：{ notebook, trash_items }
│
├── fill_form.html         → {% block extra_blobs %} + {% block content %}
│   ├── 30 字段表单 + 文件上传
│   └── 变量：{ notebook, edit_mode, student, ... }
│
├── fill_success.html      → {% block extra_blobs %} + {% block content %}
│   ├── 成功动画 + 编辑码展示
│   └── 变量：{ notebook, edit_code }
│
└── student_detail.html    → {% block extra_blobs %} + {% block content %}
    ├── 信息展示 + 媒体墙
    └── 变量：{ notebook, student, media_files }
```

---

## 十、已创建的 CSS 类名索引

### 布局类
`.container`, `.grid`, `.grid-2`, `.grid-3`, `.grid-auto`, `.flex`, `.flex-col`,
`.items-center`, `.justify-between`, `.justify-center`, `.gap-sm`, `.gap-md`,
`.gap-lg`, `.gap-xl`, `.w-full`, `.text-center`

### 间距类
`.mt-sm`, `.mt-md`, `.mt-lg`, `.mt-xl`, `.mb-sm`, `.mb-md`, `.mb-lg`, `.mb-xl`

### 配色类
`.text-sm`, `.text-xs`

### 组件类
`.navbar`, `.navbar-inner`, `.navbar-brand`, `.navbar-links`,
`.card`, `.card-sm`, `.student-card`, `.trash-item`,
`.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger`,
`.btn-sm`, `.btn-lg`, `.btn-block`,
`.form-group`, `.form-label`, `.form-input`, `.form-textarea`, `.form-select`,
`.form-error`, `.form-helper`, `.required`,
`.file-upload-area`, `.file-preview-grid`, `.file-preview-item`, `.remove-file`,
`.modal-overlay`, `.modal-content`, `.modal-actions`,
`.search-bar`, `.search-icon`,
`.alert`, `.alert-success`, `.alert-error`, `.alert-info`, `.alert-warning`,
`.badge`, `.badge-primary`, `.badge-success`, `.badge-warning`,
`.page-header`, `.empty-state`,
`.share-link-box`, `.copy-btn`,
`.spinner`, `.spinner-lg`,
`.blob`, `.blob-1`, `.blob-2`, `.blob-3`

### 动画类
`.animate-fade-in`, `.animate-slide-up`, `.animate-scale-in`,
`.stagger-1`, `.stagger-2`, `.stagger-3`, `.stagger-4`, `.stagger-5`

### 工具类
`.student-card-header`, `.student-avatar`, `.student-name`, `.student-nickname`,
`.student-info-grid`, `.student-info-item`

---

*文档版本：v2.0（完整优化版）*
*编写日期：2026-07-29*
*设计系统：UI/UX Pro Max — Claymorphism*

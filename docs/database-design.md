# 同学录 — 数据库设计文档（完整版）

> **数据库：** PostgreSQL 16（字符编码：UTF-8）
> **ORM 框架：** Django ORM
> **项目路径：** `/var/minis/workspace/classmates-book/`
> **最后更新：** 2026-07-29

---

## 一、实体关系总览

### 1.1 ER 图（文字版）

```
┌──────────────────┐           ┌──────────────────┐           ┌─────────────────────────┐
│     core_user    │           │  core_notebook   │           │     core_student        │
├──────────────────┤           ├──────────────────┤           ├─────────────────────────┤
│ PK│ id (BIGINT)  │◄──────────┤ PK│ id (BIGINT)  │◄──────────┤ PK│ id (BIGINT)          │
│   │ email (UNIQUE)│  1:N    │   │ title (VARCHAR)│  1:N     │   │ name (VARCHAR) NOT NULL│
│   │ password     │ 创建多本  │   │ share_code (UUID)│ 存放多条 │   │ + 6 个必填字段         │
│   │ username     │           │   │ owner_id (FK)  │           │   │ + 20 个选填字段        │
│   │ date_joined  │           │   │ created_at     │           │   │ + 编辑码/时间戳/软删除  │
│   │ ...          │           │   │ updated_at     │           │   │ notebook_id (FK)       │
└──────────────────┘           └──────────────────┘           └───────────┬─────────────┘
                                                                          │1
                                                                          │
                                                                          │N (可上传多张照片和多个视频)
                                                                          │
                                                               ┌──────────┴──────────────┐
                                                               │     core_mediafile       │
                                                               ├─────────────────────────┤
                                                               │ PK│ id (BIGINT)          │
                                                               │   │ file (VARCHAR 255)    │
                                                               │   │ file_type (photo/video)│
                                                               │   │ student_id (FK)       │
                                                               │   │ uploaded_at           │
                                                               │   │ file_size             │
                                                               └─────────────────────────┘

┌─────────────────────────────────────┐
│       core_verificationcode         │  ← 独立表，不与其他表关联
├─────────────────────────────────────┤
│ PK│ id (BIGINT)                     │
│   │ email (VARCHAR 254)             │
│   │ code (VARCHAR 6)                │
│   │ created_at (TIMESTAMPTZ)        │
│   │ expires_at (TIMESTAMPTZ)        │
│   │ is_used (BOOLEAN)               │
└─────────────────────────────────────┘
```

### 1.2 关系矩阵

| 主表 | 从表 | 关系类型 | 外键字段 | 级联策略 | 业务含义 |
|------|------|----------|----------|----------|----------|
| `core_user` | `core_notebook` | 一对多 (1:N) | `owner_id` | CASCADE | 一个用户创建多本同学录 |
| `core_notebook` | `core_student` | 一对多 (1:N) | `notebook_id` | CASCADE | 一本同学录包含多名同学 |
| `core_student` | `core_mediafile` | 一对多 (1:N) | `student_id` | CASCADE | 一名同学上传多份媒体文件 |

### 1.3 数据库命名规范

| 规则 | 示例 |
|------|------|
| 表名：`core_<模型名>`（小写蛇形） | `core_notebook`, `core_student` |
| 主键：`id` | `id BIGSERIAL PRIMARY KEY` |
| 外键：`<关联表>_id` | `owner_id`, `notebook_id` |
| 索引：`ix_<表名>_<字段>` | `ix_core_student_name` |
| 唯一约束：`UNIQUE (<字段>)` | `UNIQUE (email)`, `UNIQUE (share_code)` |

---

## 二、表结构详细设计

### 2.1 `core_user` — 用户表

**用途：** 存储注册用户信息，基于 Django `AbstractUser` 扩展。

**字段定义：**

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| `id` | `BIGSERIAL` | - | `PK` | 自动递增 | 主键 |
| `password` | `VARCHAR` | 128 | `NOT NULL` | - | PBKDF2 加密 |
| `last_login` | `TIMESTAMPTZ` | - | `NULLABLE` | `NULL` | 最后登录时间 |
| `is_superuser` | `BOOLEAN` | - | `NOT NULL` | `FALSE` | 超级管理员（预留） |
| `username` | `VARCHAR` | 150 | `NOT NULL, UNIQUE` | - | 注册时复用 email 值 |
| `first_name` | `VARCHAR` | 150 | `NULLABLE` | `NULL` | 名（预留） |
| `last_name` | `VARCHAR` | 150 | `NULLABLE` | `NULL` | 姓（预留） |
| `email` | `VARCHAR` | 254 | `NOT NULL, UNIQUE` | - | **登录凭证** |
| `is_staff` | `BOOLEAN` | - | `NOT NULL` | `FALSE` | 可登录 admin |
| `is_active` | `BOOLEAN` | - | `NOT NULL` | `TRUE` | 账户激活状态 |
| `date_joined` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 注册时间 |

**索引：**
```sql
PRIMARY KEY (id)
UNIQUE (username)
UNIQUE (email)
CREATE INDEX ix_core_user_email ON core_user(email);
```

**Django 模型（`core/models.py`）：**
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='邮箱')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
```

**说明：**
- Django 的 `AbstractUser` 自动创建 Django 所需的多对多关联表（`core_user_groups`、`core_user_user_permissions` 等）
- `username` 字段 Django 要求必填，注册时直接填入 `email` 值
- 登录使用 `email` 字段 + 自定义 `EmailAuthBackend`

---

### 2.2 `core_notebook` — 同学录表

**用途：** 存储用户创建的每一本同学录，每本同学录有唯一的分享标识。

**字段定义：**

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| `id` | `BIGSERIAL` | - | `PK` | 自动递增 | 主键 |
| `owner_id` | `BIGINT` | - | `NOT NULL, FK → core_user(id)` | - | **创建者外键** |
| `title` | `VARCHAR` | 100 | `NOT NULL` | - | 同学录名称 |
| `share_code` | `UUID` | - | `NOT NULL, UNIQUE` | `gen_random_uuid()` | **分享链接唯一标识** |
| `created_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 创建时间 |
| `updated_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 最后修改时间 |

**索引：**
```sql
PRIMARY KEY (id)
UNIQUE (share_code)
CREATE INDEX ix_core_notebook_owner   ON core_notebook(owner_id);
CREATE INDEX ix_core_notebook_created ON core_notebook(created_at DESC);
```

**外键：**
```sql
CONSTRAINT fk_notebook_owner
  FOREIGN KEY (owner_id) REFERENCES core_user(id)
  ON DELETE CASCADE
```

**DDL（完整）：**
```sql
CREATE TABLE core_notebook (
    id          BIGSERIAL       PRIMARY KEY,
    owner_id    BIGINT          NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    title       VARCHAR(100)    NOT NULL,
    share_code  UUID            NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX ix_core_notebook_owner   ON core_notebook(owner_id);
CREATE INDEX ix_core_notebook_created ON core_notebook(created_at DESC);
```

**Django 模型：**
```python
class Notebook(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notebooks', verbose_name='创建者')
    title = models.CharField(max_length=100, verbose_name='同学录名称')
    share_code = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, verbose_name='分享标识')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '同学录'
        verbose_name_plural = '同学录'
        ordering = ['-created_at']
```

**字段值示例：**
```
id: 3
owner_id: 1
title: '初中3班同学录'
share_code: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
created_at: '2026-07-29 10:30:00+08'
updated_at: '2026-07-29 10:30:00+08'
```

---

### 2.3 `core_student` — 同学信息表（核心表 ⭐）

**用途：** 存放每位同学填写的完整信息，是本系统的核心数据表。包含 7 个必填字段 + 20 个选填字段 + 元数据字段。

**元数据字段：**

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| `id` | `BIGSERIAL` | - | `PK` | 自动递增 | 主键 |
| `notebook_id` | `BIGINT` | - | `NOT NULL, FK → core_notebook(id)` | - | **所属同学录** |
| `edit_code` | `VARCHAR` | 64 | `UNIQUE, NULLABLE` | `NULL` | **编辑码**（提交后生成） |
| `created_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 首次提交时间 |
| `updated_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 最后修改时间 |
| `edit_deadline` | `TIMESTAMPTZ` | - | `NULLABLE` | `NULL` | 编辑截止时间 = `created_at + 3天` |
| `is_deleted` | `BOOLEAN` | - | `NOT NULL` | `FALSE` | **软删除标记** |
| `deleted_at` | `TIMESTAMPTZ` | - | `NULLABLE` | `NULL` | 软删除时间 |
| `restore_deadline` | `TIMESTAMPTZ` | - | `NULLABLE` | `NULL` | 还原截止时间 = `deleted_at + 10天` |

**必填字段（7 个）：**

| 字段名 | 数据类型 | 长度 | 约束 | 说明 |
|--------|----------|------|------|------|
| `name` | `VARCHAR` | 50 | `NOT NULL` | 真实姓名 |
| `nickname` | `VARCHAR` | 50 | `NOT NULL` | 昵称 |
| `phone` | `VARCHAR` | 20 | `NOT NULL` | 手机号码 |
| `wechat` | `VARCHAR` | 50 | `NOT NULL` | 微信号 |
| `first_impression` | `TEXT` | - | `NOT NULL` | 对我的第一印象（不限字数） |
| `words_to_me` | `TEXT` | - | `NOT NULL` | 想对我说的话（不限字数） |
| `message` | `TEXT` | - | `NOT NULL` | 留言（不限字数） |

**选填字段 — 联系方式（5 个）：**

| 字段名 | 数据类型 | 长度 | 约束 | 说明 |
|--------|----------|------|------|------|
| `qq` | `VARCHAR` | 20 | `NULLABLE` | QQ 号 |
| `xiaohongshu` | `VARCHAR` | 100 | `NULLABLE` | 小红书号 |
| `douyin` | `VARCHAR` | 100 | `NULLABLE` | 抖音号 |
| `email` | `VARCHAR` | 254 | `NULLABLE` | 邮箱地址（非注册用） |
| `address` | `TEXT` | - | `NULLABLE` | 现居地址 |

**选填字段 — 个人信息（15 个）：**

| 字段名 | 数据类型 | 长度 | 约束 | 说明 |
|--------|----------|------|------|------|
| `birthday` | `DATE` | - | `NULLABLE` | 生日 |
| `zodiac_sign` | `VARCHAR` | 10 | `NULLABLE` | 生肖 |
| `constellation` | `VARCHAR` | 10 | `NULLABLE` | 星座 |
| `hobbies` | `TEXT` | - | `NULLABLE` | 兴趣爱好 |
| `motto` | `TEXT` | - | `NULLABLE` | 座右铭 |
| `crush` | `TEXT` | - | `NULLABLE` | 学生时代喜欢过谁 |
| `dislike` | `TEXT` | - | `NULLABLE` | 讨厌过谁 |
| `wish` | `TEXT` | - | `NULLABLE` | 愿望 |
| `dream` | `TEXT` | - | `NULLABLE` | 梦想 |
| `favorite_food` | `TEXT` | - | `NULLABLE` | 喜欢吃什么 |
| `most_want_to_see` | `TEXT` | - | `NULLABLE` | 最想见的人 |
| `favorite_movie` | `TEXT` | - | `NULLABLE` | 喜欢看的电影 |
| `favorite_music` | `TEXT` | - | `NULLABLE` | 喜欢听的歌 |
| `most_want_to_go` | `TEXT` | - | `NULLABLE` | 最想去的地方 |
| `most_unforgettable` | `TEXT` | - | `NULLABLE` | 最难忘的事 |
| `hope_10_years` | `TEXT` | - | `NULLABLE` | 希望 10 年后的我们 |

**索引策略（7 个索引）：**

| 索引名 | 类型 | 字段 | 用途 |
|--------|------|------|------|
| `PRIMARY KEY` | B-tree | `id` | 主键查找 |
| `UNIQUE` | B-tree | `edit_code` | 编辑码查询（仅非 NULL 时生效） |
| `ix_core_student_notebook` | B-tree | `notebook_id` | 按同学录查询所有学生 |
| `ix_core_student_name` | B-tree | `name` | 按名字搜索 |
| `ix_core_student_notebook_name` | 联合 B-tree | `(notebook_id, name)` | **在同学录内按名字搜索** |
| `ix_core_student_notebook_active` | **部分索引** | `notebook_id WHERE is_deleted=FALSE` | 正常列表查询（不含回收站） |
| `ix_core_student_notebook_trash` | **部分索引** | `notebook_id WHERE is_deleted=TRUE` | 回收站查询 |
| `ix_core_student_restore_deadline` | **部分索引** | `restore_deadline WHERE is_deleted=TRUE` | 定时清理过期记录 |

> **部分索引（Partial Index）说明：** PostgreSQL 支持 `WHERE` 子句过滤索引，只索引符合条件的行，显著减少索引体积，提高写入性能。

**DDL（完整）：**
```sql
CREATE TABLE core_student (
    id                  BIGSERIAL       PRIMARY KEY,
    notebook_id         BIGINT          NOT NULL REFERENCES core_notebook(id) ON DELETE CASCADE,
    edit_code           VARCHAR(64)     UNIQUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    edit_deadline       TIMESTAMPTZ,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ,
    restore_deadline    TIMESTAMPTZ,

    -- 必填字段
    name                VARCHAR(50)     NOT NULL,
    nickname            VARCHAR(50)     NOT NULL,
    phone               VARCHAR(20)     NOT NULL,
    wechat              VARCHAR(50)     NOT NULL,
    first_impression    TEXT            NOT NULL,
    words_to_me         TEXT            NOT NULL,
    message             TEXT            NOT NULL,

    -- 选填字段
    birthday            DATE,
    zodiac_sign         VARCHAR(10),
    constellation       VARCHAR(10),
    qq                  VARCHAR(20),
    xiaohongshu         VARCHAR(100),
    douyin              VARCHAR(100),
    email               VARCHAR(254),
    address             TEXT,
    hobbies             TEXT,
    motto               TEXT,
    crush               TEXT,
    dislike             TEXT,
    wish                TEXT,
    dream               TEXT,
    favorite_food       TEXT,
    most_want_to_see    TEXT,
    favorite_movie      TEXT,
    favorite_music      TEXT,
    most_want_to_go     TEXT,
    most_unforgettable  TEXT,
    hope_10_years       TEXT
);

-- 索引
CREATE INDEX ix_core_student_notebook           ON core_student(notebook_id);
CREATE INDEX ix_core_student_name               ON core_student(name);
CREATE INDEX ix_core_student_notebook_name      ON core_student(notebook_id, name);
CREATE INDEX ix_core_student_notebook_active    ON core_student(notebook_id) WHERE is_deleted = FALSE;
CREATE INDEX ix_core_student_notebook_trash     ON core_student(notebook_id) WHERE is_deleted = TRUE;
CREATE INDEX ix_core_student_restore_deadline   ON core_student(restore_deadline) WHERE is_deleted = TRUE;
```

**Django 模型：**
```python
class Student(models.Model):
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='students')
    edit_code = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edit_deadline = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    restore_deadline = models.DateTimeField(null=True, blank=True)

    # 必填字段（7个）
    name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    wechat = models.CharField(max_length=50)
    first_impression = models.TextField()
    words_to_me = models.TextField()
    message = models.TextField()

    # 选填字段（20个）
    birthday = models.DateField(null=True, blank=True)
    zodiac_sign = models.CharField(max_length=10, null=True, blank=True)
    constellation = models.CharField(max_length=10, null=True, blank=True)
    qq = models.CharField(max_length=20, null=True, blank=True)
    xiaohongshu = models.CharField(max_length=100, null=True, blank=True)
    douyin = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    motto = models.TextField(null=True, blank=True)
    crush = models.TextField(null=True, blank=True)
    dislike = models.TextField(null=True, blank=True)
    wish = models.TextField(null=True, blank=True)
    dream = models.TextField(null=True, blank=True)
    favorite_food = models.TextField(null=True, blank=True)
    most_want_to_see = models.TextField(null=True, blank=True)
    favorite_movie = models.TextField(null=True, blank=True)
    favorite_music = models.TextField(null=True, blank=True)
    most_want_to_go = models.TextField(null=True, blank=True)
    most_unforgettable = models.TextField(null=True, blank=True)
    hope_10_years = models.TextField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['notebook', 'name']),
        ]

    def generate_edit_code(self):
        import secrets
        from django.utils import timezone
        from datetime import timedelta
        self.edit_code = secrets.token_urlsafe(16)
        self.edit_deadline = timezone.now() + timedelta(days=3)
        return self.edit_code

    def soft_delete(self):
        from django.utils import timezone
        from datetime import timedelta
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.restore_deadline = timezone.now() + timedelta(days=10)
        self.save(update_fields=['is_deleted', 'deleted_at', 'restore_deadline'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.restore_deadline = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'restore_deadline'])

    def can_edit(self):
        from django.utils import timezone
        if not self.edit_deadline:
            return False
        return timezone.now() <= self.edit_deadline
```

---

### 2.4 `core_mediafile` — 媒体文件表

**用途：** 存储同学上传的照片和视频文件元数据。每条学生记录可关联多条媒体记录。

**字段定义：**

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| `id` | `BIGSERIAL` | - | `PK` | 自动递增 | 主键 |
| `student_id` | `BIGINT` | - | `NOT NULL, FK → core_student(id)` | - | **所属同学外键** |
| `file` | `VARCHAR` | 255 | `NOT NULL` | - | 文件存储路径 |
| `file_type` | `VARCHAR` | 10 | `NOT NULL, CHECK` | - | `'photo'` 或 `'video'` |
| `uploaded_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 上传时间 |
| `file_size` | `BIGINT` | - | `NULLABLE` | `NULL` | 文件大小（字节） |

**CHECK 约束：**
```sql
CHECK (file_type IN ('photo', 'video'))
```

**索引：**
```sql
PRIMARY KEY (id)
CREATE INDEX ix_core_mediafile_student ON core_mediafile(student_id);
CREATE INDEX ix_core_mediafile_type    ON core_mediafile(student_id, file_type);
```

**DDL（完整）：**
```sql
CREATE TABLE core_mediafile (
    id              BIGSERIAL       PRIMARY KEY,
    student_id      BIGINT          NOT NULL REFERENCES core_student(id) ON DELETE CASCADE,
    file            VARCHAR(255)    NOT NULL,
    file_type       VARCHAR(10)     NOT NULL CHECK (file_type IN ('photo', 'video')),
    uploaded_at     TIMESTAMPTZ     NOT NULL DEFAULT now(),
    file_size       BIGINT
);

CREATE INDEX ix_core_mediafile_student ON core_mediafile(student_id);
CREATE INDEX ix_core_mediafile_type    ON core_mediafile(student_id, file_type);
```

**文件存储路径规则：**
```
MEDIA_ROOT/student_<student_id>/<uuid>.<ext>
```

**Django 模型：**
```python
def student_upload_path(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else ''
    name = uuid.uuid4().hex
    return f'student_{instance.student_id}/{name}.{ext}'

class MediaFile(models.Model):
    PHOTO = 'photo'
    VIDEO = 'video'
    FILE_TYPE_CHOICES = [(PHOTO, '照片'), (VIDEO, '视频')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='media_files')
    file = models.FileField(upload_to=student_upload_path)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(null=True, blank=True)
```

---

### 2.5 `core_verificationcode` — 验证码表

**用途：** 存储邮箱注册验证码。可作为 Django Cache 的替代方案（表方案更可靠，不依赖额外组件）。

**字段定义：**

| 字段名 | 数据类型 | 长度 | 约束 | 默认值 | 说明 |
|--------|----------|------|------|--------|------|
| `id` | `BIGSERIAL` | - | `PK` | 自动递增 | 主键 |
| `email` | `VARCHAR` | 254 | `NOT NULL` | - | 目标邮箱 |
| `code` | `VARCHAR` | 6 | `NOT NULL` | - | 6 位数字验证码 |
| `created_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now()` | 创建时间 |
| `expires_at` | `TIMESTAMPTZ` | - | `NOT NULL` | `now() + 5min` | 过期时间 |
| `is_used` | `BOOLEAN` | - | `NOT NULL` | `FALSE` | 是否已被使用 |

**DDL（完整）：**
```sql
CREATE TABLE core_verificationcode (
    id              BIGSERIAL       PRIMARY KEY,
    email           VARCHAR(254)    NOT NULL,
    code            VARCHAR(6)      NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ     NOT NULL DEFAULT now() + INTERVAL '5 minutes',
    is_used         BOOLEAN         NOT NULL DEFAULT FALSE
);

CREATE INDEX ix_core_verification_query   ON core_verificationcode(email, code, expires_at DESC);
CREATE INDEX ix_core_verification_expires ON core_verificationcode(expires_at) WHERE is_used = FALSE;
```

**Django 模型：**
```python
class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'code', 'expires_at']),
        ]

    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() <= self.expires_at
```

---

## 三、完整建表 SQL（按顺序执行）

```sql
-- ===================================================
-- 数据库初始化脚本
-- 数据库：PostgreSQL 16
-- 字符集：UTF-8
-- 执行方式：psql -U classmates -d classmates -f init.sql
-- ===================================================

-- 第 1 部分：core_user 表（由 Django migrate 自动生成）
-- 执行命令：python manage.py migrate

-- ===================================================
-- 第 2 部分：core_notebook — 同学录表
-- ===================================================
CREATE TABLE core_notebook (
    id          BIGSERIAL       PRIMARY KEY,
    owner_id    BIGINT          NOT NULL REFERENCES core_user(id) ON DELETE CASCADE,
    title       VARCHAR(100)    NOT NULL,
    share_code  UUID            NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT now()
);
CREATE INDEX ix_core_notebook_owner   ON core_notebook(owner_id);
CREATE INDEX ix_core_notebook_created ON core_notebook(created_at DESC);

-- ===================================================
-- 第 3 部分：core_student — 同学信息表（核心表）
-- ===================================================
CREATE TABLE core_student (
    id                  BIGSERIAL       PRIMARY KEY,
    notebook_id         BIGINT          NOT NULL REFERENCES core_notebook(id) ON DELETE CASCADE,
    edit_code           VARCHAR(64)     UNIQUE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    edit_deadline       TIMESTAMPTZ,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ,
    restore_deadline    TIMESTAMPTZ,
    name                VARCHAR(50)     NOT NULL,
    nickname            VARCHAR(50)     NOT NULL,
    phone               VARCHAR(20)     NOT NULL,
    wechat              VARCHAR(50)     NOT NULL,
    first_impression    TEXT            NOT NULL,
    words_to_me         TEXT            NOT NULL,
    message             TEXT            NOT NULL,
    birthday            DATE,
    zodiac_sign         VARCHAR(10),
    constellation       VARCHAR(10),
    qq                  VARCHAR(20),
    xiaohongshu         VARCHAR(100),
    douyin              VARCHAR(100),
    email               VARCHAR(254),
    address             TEXT,
    hobbies             TEXT,
    motto               TEXT,
    crush               TEXT,
    dislike             TEXT,
    wish                TEXT,
    dream               TEXT,
    favorite_food       TEXT,
    most_want_to_see    TEXT,
    favorite_movie      TEXT,
    favorite_music      TEXT,
    most_want_to_go     TEXT,
    most_unforgettable  TEXT,
    hope_10_years       TEXT
);
CREATE INDEX ix_core_student_notebook           ON core_student(notebook_id);
CREATE INDEX ix_core_student_name               ON core_student(name);
CREATE INDEX ix_core_student_notebook_name      ON core_student(notebook_id, name);
CREATE INDEX ix_core_student_notebook_active    ON core_student(notebook_id) WHERE is_deleted = FALSE;
CREATE INDEX ix_core_student_notebook_trash     ON core_student(notebook_id) WHERE is_deleted = TRUE;
CREATE INDEX ix_core_student_restore_deadline   ON core_student(restore_deadline) WHERE is_deleted = TRUE;

-- ===================================================
-- 第 4 部分：core_mediafile — 媒体文件表
-- ===================================================
CREATE TABLE core_mediafile (
    id              BIGSERIAL       PRIMARY KEY,
    student_id      BIGINT          NOT NULL REFERENCES core_student(id) ON DELETE CASCADE,
    file            VARCHAR(255)    NOT NULL,
    file_type       VARCHAR(10)     NOT NULL CHECK (file_type IN ('photo', 'video')),
    uploaded_at     TIMESTAMPTZ     NOT NULL DEFAULT now(),
    file_size       BIGINT
);
CREATE INDEX ix_core_mediafile_student ON core_mediafile(student_id);
CREATE INDEX ix_core_mediafile_type    ON core_mediafile(student_id, file_type);

-- ===================================================
-- 第 5 部分：core_verificationcode — 验证码表
-- ===================================================
CREATE TABLE core_verificationcode (
    id              BIGSERIAL       PRIMARY KEY,
    email           VARCHAR(254)    NOT NULL,
    code            VARCHAR(6)      NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ     NOT NULL DEFAULT now() + INTERVAL '5 minutes',
    is_used         BOOLEAN         NOT NULL DEFAULT FALSE
);
CREATE INDEX ix_core_verification_query   ON core_verificationcode(email, code, expires_at DESC);
CREATE INDEX ix_core_verification_expires ON core_verificationcode(expires_at) WHERE is_used = FALSE;
```

---

## 四、关键 SQL 查询语句

### 4.1 同学录列表（仪表盘用）

```sql
-- 查询某用户的所有同学录及人数统计
SELECT
    n.id,
    n.title,
    n.share_code,
    n.created_at,
    COUNT(s.id) FILTER (WHERE s.is_deleted = FALSE) AS active_count
FROM core_notebook n
LEFT JOIN core_student s ON s.notebook_id = n.id
WHERE n.owner_id = 1
GROUP BY n.id, n.title, n.share_code, n.created_at
ORDER BY n.created_at DESC;

-- Django ORM 等价写法
-- Notebook.objects.filter(owner=request.user)
--     .annotate(active_count=Count('students', filter=Q(students__is_deleted=False)))
--     .order_by('-created_at')
```

### 4.2 同学录详情页（正常列表）

```sql
-- 查询某本同学录所有有效同学，按名字排序
SELECT id, name, nickname, phone, wechat, created_at
FROM core_student
WHERE notebook_id = 1
  AND is_deleted = FALSE
ORDER BY name ASC;
```

### 4.3 搜索功能

```sql
-- 在同学录中按名字模糊搜索
SELECT id, name, nickname, phone, wechat, first_impression
FROM core_student
WHERE notebook_id = 1
  AND is_deleted = FALSE
  AND name ILIKE '%张%'
ORDER BY name ASC;

-- ILIKE 是 PostgreSQL 的模糊匹配（不区分大小写）
-- 中文搜索时和 LIKE 效果一致
```

### 4.4 回收站列表

```sql
-- 查询回收站内容，按删除时间倒序
SELECT id, name, deleted_at, restore_deadline,
       EXTRACT(EPOCH FROM (restore_deadline - NOW())) / 86400 AS remaining_days
FROM core_student
WHERE notebook_id = 1
  AND is_deleted = TRUE
ORDER BY deleted_at DESC;

-- remaining_days 为剩余天数（小数），可在模板中用 timeuntil 格式化
```

### 4.5 定时清理过期回收站

```sql
-- 查找过期记录
SELECT id, name
FROM core_student
WHERE is_deleted = TRUE
  AND restore_deadline < NOW();

-- 删除过期记录（级联删除关联的 MediaFile）
DELETE FROM core_student
WHERE is_deleted = TRUE
  AND restore_deadline < NOW();
```

### 4.6 查询媒体文件

```sql
-- 查询某同学的全部媒体文件，按类型分组
SELECT id, file, file_type, uploaded_at
FROM core_mediafile
WHERE student_id = 1
ORDER BY file_type, uploaded_at;
```

### 4.7 验证码校验

```sql
-- 查询指定邮箱和验证码的有效记录
SELECT id FROM core_verificationcode
WHERE email = 'xxx@example.com'
  AND code = '123456'
  AND is_used = FALSE
  AND expires_at > NOW()
ORDER BY expires_at DESC
LIMIT 1;
```

### 4.8 编辑码有效期检查

```sql
-- 检查编辑码是否有效
SELECT id, edit_deadline
FROM core_student
WHERE edit_code = 'abc123...'
  AND edit_deadline > NOW()
  AND is_deleted = FALSE
LIMIT 1;
```

---

## 五、数据完整性规则

### 5.1 业务约束

| 规则编号 | 规则 | 违反后果 | 处理方式 |
|----------|------|----------|----------|
| R1 | 同一邮箱只能注册一个账户 | UNIQUE(email) 约束 | 提示"该邮箱已被注册" |
| R2 | 每本同学录的 share_code 全局唯一 | UNIQUE(share_code) | Django 自动处理 |
| R3 | 编辑码全局唯一 | UNIQUE(edit_code) | secrets.token_urlsafe 冲突概率极低 |
| R4 | 必填字段不能为 NULL | NOT NULL 约束 | Django Form 校验 |
| R5 | file_type 必须是 photo 或 video | CHECK 约束 | Django choices 校验 |
| R6 | 验证码 5 分钟后过期 | expires_at 校验 | View 层判断 |
| R7 | 编辑码 3 天后过期 | edit_deadline 校验 | View 层判断 |
| R8 | 回收站 10 天后永久删除 | restore_deadline 校验 | 定时任务执行 |
| R9 | 删除同学录时级联删除关联数据 | ON DELETE CASCADE | 数据库自动执行 |
| R10 | 同一个邮箱 60 秒内不能重复发验证码 | 应用层防刷 | View 层判断 |

### 5.2 级联删除路径

```
DELETE core_notebook (id=1)
  → DELETE core_student (notebook_id=1)           [CASCADE]
    → DELETE core_mediafile (student_id IN ...)   [CASCADE]

DELETE core_student (id=1)
  → DELETE core_mediafile (student_id=1)          [CASCADE]
```

---

## 六、迁移策略

### 6.1 Django Migrations 工作流

```bash
# 开发阶段
cd backend
python manage.py makemigrations    # 检测模型变更，生成迁移文件
python manage.py migrate           # 执行迁移
python manage.py showmigrations    # 查看迁移状态
python manage.py sqlmigrate core 0001  # 查看迁移生成的 SQL

# 生产部署
python manage.py migrate --run-syncdb  # 兼容模式
```

### 6.2 模型变更规范

| 变更类型 | 安全 | 说明 |
|----------|------|------|
| 新增字段（允许 NULL） | ✅ 安全 | Django 自动添加 |
| 新增字段（NOT NULL） | ⚠️ 需提供默认值 | 生产环境需分两步：先加 NULL 字段，再填充数据，最后改 NOT NULL |
| 删除字段 | ⚠️ 谨慎 | 确认无代码引用后删除 |
| 重命名字段 | ❌ 不安全 | 手动编写迁移，先新增字段迁移数据再删旧字段 |
| 修改字段类型 | ⚠️ 需手动迁移 | 编写 `RunSQL` 或 `SeparateDatabaseAndState` |
| 新增表 | ✅ 安全 | 直接 makemigrations |

---

## 七、性能优化策略

| 场景 | 策略 | 说明 |
|------|------|------|
| 同学录列表（仪表盘） | `annotate` + 子查询 | 避免 N+1 查询 |
| 搜索 | `name__icontains` + B-tree 索引 | ILIKE 走索引 |
| 同学录详情 | 部分索引 `WHERE is_deleted=FALSE` | 索引体积减少 ~50% |
| 回收站查询 | 部分索引 `WHERE is_deleted=TRUE` | 回收站记录少时效果显著 |
| 媒体文件查询 | `select_related('student')` | 减轻外键查询开销 |
| 文件大小统计 | `MediaFile.objects.aggregate(Sum('file_size'))` | 聚合查询 |
| 连接池 | `CONN_MAX_AGE=60` | 避免每次请求建立连接 |
| 大字段 | TEXT 字段不建索引 | PostgreSQL TEXT 不默认索引 |

---

## 八、字段长度与空间估算

### 8.1 单条记录空间估算

| 表 | 字段数 | 固定字段大小 | 变长字段 | 预估单行大小 |
|------|--------|-------------|----------|-------------|
| `core_notebook` | 6 | ~120 bytes | - | ~120 bytes |
| `core_student` | 24 | ~400 bytes | ~1000 bytes（平均） | ~1.5 KB |
| `core_mediafile` | 6 | ~150 bytes | ~260 bytes（路径） | ~400 bytes |
| `core_verificationcode` | 6 | ~150 bytes | - | ~150 bytes |

### 8.2 容量预估

| 数据量 | Student 行数 | 总大小（不含文件） | 媒体文件存储 |
|--------|-------------|-------------------|-------------|
| 小型（1个班级） | 50 行 | ~75 KB | 取决于上传 |
| 中型（5个班级） | 500 行 | ~750 KB | 取决于上传 |
| 大型（100个班级） | 10,000 行 | ~15 MB | 取决于上传 |

---

*文档版本：v2.0（完整优化版）*
*编写日期：2026-07-29*

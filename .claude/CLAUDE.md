# CLAUDE.md

本文件为在此仓库工作的 Claude Code 提供指引。

## 项目是什么

个人记账 Web 应用。单页，四个功能区用页签切换：添加账目、明细列表、删除、分类统计。
面向编程新手，所以代码优先追求"读得懂、错误信息好懂"，而非"写得巧"。

## 技术栈

Python 3.13 + Streamlit（界面）+ sqlite3（存储，标准库，无需安装）。
第三方依赖只有两个：`streamlit`、`pandas`。

实测装到的版本（2026-09-19）：**streamlit 1.64.0、pandas 3.0.5**。
网上大量教程是针对 streamlit 1.2x 写的，抄参数前先用
`inspect.signature(st.某函数)` 确认一下，别照抄。

## 目录结构与职责

```
app.py              入口：set_page_config、init_db、sidebar 月份筛选、tabs 调度
core/db.py          数据层：建表 DDL、所有 SQL、CATEGORIES 常量
views/add.py        页签 1：添加（st.form）
views/entries.py    页签 2：明细（分类筛选 + 表格）
views/delete.py     页签 3：删除（下拉框 + 两步确认）
views/stats.py      页签 4：统计（柱状图 + 统计表）
utils/money.py      元/分换算与金额格式化
data/finance.db     数据库文件，运行时自动生成，不进 git
```

## 架构铁律

**依赖必须单向，绝不能有循环导入：**

```
app.py ──▶ views/* ──▶ core/db ──▶ sqlite3 / pathlib
             └──────▶ utils/money
```

- `core/db.py` 和 `utils/money.py` **不导入任何本项目其他模块**，也不导入 streamlit。
  这让数据层可以脱离浏览器单独运行和测试。
- `views/*.py` 只导入 `core`、`utils` 和 streamlit，**绝不导入 `app`**。
- `app.py` 导入 views，不被 views 导入。

反过来写会得到 `ImportError: cannot import name ... (most likely due to a circular import)`。

**每个 `views/*.py` 暴露一个 `render()`**，参数是它需要的共享状态
（`app.py` 通过 `render(month)` 把侧边栏选中的月份传下去）。

## 编码约定

- **金额一律用整数「分」存储**，列名必须带 `_cents`。元↔分的换算**只在 `utils/money.py`
  一处**发生，别在别的文件里再写 `* 100` 或 `/ 100`。
- **日期一律存 `'YYYY-MM-DD'` 字符串**，不存 `datetime.date` 对象
  （Python 3.12+ 已弃用 sqlite3 的日期适配器）。写入前用 `.isoformat()`。
- **数据库连接每次操作现开现关**（`core/db.py` 的 `query()` / `execute()`），
  不用全局连接、不用 `@st.cache_resource`、不用 `check_same_thread=False`。
  这是为了避免 Streamlit 多线程重跑时那个极难诊断的报错。
- **不缓存任何查询结果**（不用 `@st.cache_data`）。数据每次增删都在变，
  缓存只会制造"删了但还在屏幕上"的问题，而本地查询本来就是微秒级。
- **SQL 只用具名占位符 `:name`**，让 SQLite 转义。永远不要用 f-string 拼 SQL。
- **金额进入数据库前必须过 `to_cents()`**；显示给人看用 `yuan()`（返回 `'¥12.34'`），
  喂给图表和表格用 `to_yuan()`（返回数字 `12.34`）。
  直接把 `amount_cents` 显示出来会差 100 倍。
- **pandas 列做换算要用 `df["amount_cents"].map(to_yuan)`**，不要写 `df[...] / 100`。

## 常用命令

```bash
# 启动（必须先激活虚拟环境）
source .venv/Scripts/activate
streamlit run app.py                  # 浏览器打开 http://localhost:8501，Ctrl+C 停止

# 单独测数据层——不需要开浏览器，调试时优先用这个
.venv/Scripts/python.exe -c "from core import db; db.init_db(); print(db.list_entries())"
```

## 已知的坑

- **`streamlit run` 不会切换工作目录。** 所有路径都要用
  `Path(__file__).resolve()` 推导，绝不能写相对路径，否则换个目录启动会静默新建一个空数据库。
- **`core/db.py` 在子目录里**，定位项目根要 `.parent.parent`。少写一层不会报错，
  只会把 `finance.db` 建到 `core/` 里面。
- **`st.rerun()` 不能在 `with st.form` 块内部调用**，会抛 `StreamlitAPIException`。
  `if submitted:` 必须写在 `with` 块外面。
- **`st.success()` 后面紧跟 `st.rerun()` 会被冲掉**，用户看不到任何提示。
  要用 `st.session_state["flash"]` 暂存，下一轮在页面顶部渲染（`app.py` 里有示例）。
- **不要用 `use_container_width` 参数**，已废弃。1.64 里它还在、传了不报错，
  但是废弃路径，别用。改用 `width="stretch"`——而 `width` 的默认值本来就是
  `'stretch'`，所以多数情况**什么都不用传**。
- **`st.text_input` 限制长度是 `max_chars`，不是 `maxlength`**（后者会直接
  `TypeError`）。这个坑是实测踩出来的，网上教程两种写法都有。
- **从终端跑脚本打印中文，前面加 `PYTHONIOENCODING=utf-8`**，否则 GBK 控制台会抛
  `UnicodeEncodeError`。加了之后不仅不报错，中文还能正常显示。
- **不要给控件设 `key=`**。当前设计只用 `flash` 和 `pending_delete` 两个普通
  session_state 键，就是为了绕开"控件实例化后不能再改同名 session_state"的限制。
- **`st.set_page_config` 必须是第一个 Streamlit 调用**，且每次运行只能调一次。
- **调试用 `st.write()`，不要用 `print()`**——从 GBK 代码页的终端启动时，
  打印中文可能抛 `UnicodeEncodeError`。

## Git

**仓库根目录是父目录 `D:\AICoding`，不是本目录。**

- 在本目录执行 `git status` 会看到 `claude_deepseek/`、`hello_world/`、`test1-3/` 等兄弟目录。
- **提交时必须显式 `git add finance_cli`，不要用 `git add -A`**，否则会把无关目录一起加进来。
- 仓库根目录没有 `.gitignore`；本目录的 `.gitignore` 只管本目录。

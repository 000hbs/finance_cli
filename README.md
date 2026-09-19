# 我的记账本

一个本地运行的个人记账 Web 应用。数据存在你自己电脑上的一个文件里，不上传任何服务器。

四个功能，在页面顶部用页签切换：

- **添加** —— 填金额、分类、日期、备注，保存
- **明细** —— 表格展示所有记录，可按月份和分类筛选
- **删除** —— 下拉框选中某条记录，两步确认后删除
- **统计** —— 各分类的柱状图 + 统计表（含占比）

## 安装

只需要做一次。

```bash
cd /d/AICoding/finance_cli
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## 启动

```bash
cd /d/AICoding/finance_cli
.venv/Scripts/python.exe -m streamlit run app.py
```

浏览器会自动打开 <http://localhost:8501>。**停止服务按 Ctrl+C**（不要直接叉掉终端窗口）。

也可以直接双击 `run.bat`。

## 数据存在哪

`data/finance.db` —— 一个 SQLite 数据库文件，里面就一张 `entries` 表。

**备份 = 复制这一个文件。** 想看看里面有什么，可以用免费的
[DB Browser for SQLite](https://sqlitebrowser.org/) 打开它。
（注意：用别的程序打开着看的时候，别在事务中途关掉，否则 app 这边可能报 `database is locked`。）

这个文件**不会**被提交到 git（`.gitignore` 里排除了 `*.db`）——它是你的私人数据。

## 目录结构

```
app.py              入口：页面配置、初始化、全局筛选、页签调度
core/db.py          数据层：建表语句、所有 SQL、分类列表 CATEGORIES
views/add.py        页签 1：添加
views/entries.py    页签 2：明细
views/delete.py     页签 3：删除
views/stats.py      页签 4：统计
utils/money.py      元 / 分换算
data/finance.db     数据库文件（自动生成，不进 git）
```

想改界面就改 `views/` 里的文件，想改数据逻辑就改 `core/db.py`。
依赖方向是单向的（`app.py → views/ → core/`），改的时候别反过来引用。

## 怎么加分类

改 `core/db.py` 里的这一行，加进去就生效：

```python
CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "居住", "其他"]
```

已经记过的分类如果被删掉，那些记录还在库里，只是统计表不显示它们了。

## 常见问题

**端口被占用** —— 上次的没停干净。换一个端口启动：

```bash
.venv/Scripts/python.exe -m streamlit run app.py --server.port 8502
```

**`database is locked`** —— 有别的程序正开着 `finance.db` 并且持有写锁。关掉那个程序再试。

**命令找不到 / `ModuleNotFoundError`** —— 忘了激活虚拟环境，或者不是从 `finance_cli`
目录里启动的。注意每行命令开头都是 `.venv/Scripts/python.exe -m ...`，
用这个写法就不需要手动 `activate`。

**改了代码但页面没变** —— Streamlit 通常会自己检测到并提示 "Rerun"，点一下就行。
没反应就在浏览器里按 F5。

**只想测数据层，不想开浏览器**：

```bash
.venv/Scripts/python.exe -c "from core import db; db.init_db(); print(db.list_entries())"
```

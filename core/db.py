"""core/db.py —— 数据层。

不导入 streamlit，也不导入本项目其他模块。
这让数据层可以脱离浏览器单独运行和测试：

    .venv/Scripts/python.exe -c "from core import db; db.init_db(); print(db.list_entries())"
"""

import sqlite3
from pathlib import Path

# __file__ = <项目根>/core/db.py
#   .parent        -> <项目根>/core
#   .parent.parent -> <项目根>            ← 项目根目录
# 少写一层不会报错，只会把 finance.db 建到 core/ 里面去。
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "finance.db"

CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "居住", "其他"]

CREATE_ENTRIES = """
    CREATE TABLE IF NOT EXISTS entries (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date   TEXT    NOT NULL,
        category     TEXT    NOT NULL,
        amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
        note         TEXT    NOT NULL DEFAULT '',
        created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
    )
"""


def get_conn():
    """每次操作开一个新连接，用完立刻关。这是避免跨线程报错的关键。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让结果能按列名取值：row["amount_cents"]
    return conn


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # git 不跟踪空目录，这里自己建
    conn = get_conn()
    try:
        with conn:  # with conn = 事务（成功提交 / 异常回滚）
            conn.execute(CREATE_ENTRIES)
    finally:
        conn.close()  # 坑：with conn 不会关闭连接，必须手动关


def query(sql, params=None):
    """查询 -> list[dict]"""
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(sql, params or {}).fetchall()]
    finally:
        conn.close()


def execute(sql, params=None):
    """增 / 删 / 改，自动提交，出错自动回滚"""
    conn = get_conn()
    try:
        with conn:
            conn.execute(sql, params or {})
    finally:
        conn.close()


def add_entry(entry_date, category, amount_cents, note=""):
    execute(
        """INSERT INTO entries (entry_date, category, amount_cents, note)
           VALUES (:entry_date, :category, :amount_cents, :note)""",
        {
            "entry_date": entry_date,
            "category": category,
            "amount_cents": amount_cents,
            "note": note,
        },
    )


def delete_entry(entry_id):
    execute("DELETE FROM entries WHERE id = :id", {"id": entry_id})


def list_entries(month=None, category=None):
    """month: 'YYYY-MM' 或 None（全部）；category: 分类名 或 None（全部）"""
    return query(
        """SELECT id, entry_date, category, amount_cents, note
             FROM entries
            WHERE (:month IS NULL OR substr(entry_date, 1, 7) = :month)
              AND (:category IS NULL OR category = :category)
            ORDER BY entry_date DESC, id DESC""",
        {"month": month, "category": category},
    )


def available_months():
    return [
        r["ym"]
        for r in query(
            "SELECT DISTINCT substr(entry_date, 1, 7) AS ym FROM entries ORDER BY ym DESC"
        )
    ]


def stats_by_category(month=None):
    """只返回「分」。转成元是 utils/money.py 的事，不在这里重复一遍除以 100。"""
    return query(
        """SELECT category,
                  COUNT(*)          AS cnt,
                  SUM(amount_cents) AS total_cents
             FROM entries
            WHERE (:month IS NULL OR substr(entry_date, 1, 7) = :month)
            GROUP BY category
            ORDER BY total_cents DESC""",
        {"month": month},
    )

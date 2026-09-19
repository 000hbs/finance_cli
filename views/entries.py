"""views/entries.py —— 页签 2：明细列表。"""

import pandas as pd
import streamlit as st

from core import db
from utils.money import to_yuan, yuan


def render(month):
    st.subheader("明细")

    # 标签叫"按分类筛选"，和 add.py 里的"分类"故意不同：
    # 两个都没设 key 的控件用同样的标签，是 Streamlit 里一个没必要的混淆来源。
    category = st.selectbox("按分类筛选", ["全部"] + db.CATEGORIES)
    category = None if category == "全部" else category

    rows = db.list_entries(month=month, category=category)

    if not rows:
        st.info("没有符合条件的记录。")
        return

    df = pd.DataFrame(rows)
    table = df.rename(
        columns={
            "id": "ID",
            "entry_date": "日期",
            "category": "分类",
            "note": "备注",
        }
    )
    table["金额（元）"] = df["amount_cents"].map(to_yuan)

    # ID 列保留显示，这样"明细"表和"删除"下拉框里的 ID 能对上。
    st.dataframe(
        table[["ID", "日期", "分类", "金额（元）", "备注"]],
        hide_index=True,
    )
    st.caption(f"共 {len(table)} 条，合计 {yuan(int(df['amount_cents'].sum()))}")

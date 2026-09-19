"""views/stats.py —— 页签 4：分类统计（柱状图 + 统计表）。"""

import pandas as pd
import streamlit as st

from core import db
from utils.money import to_yuan, yuan


def render(month):
    st.subheader("分类统计")
    st.caption("统计范围只受侧边栏的「月份」筛选影响。")

    stats = db.stats_by_category(month=month)
    if not stats:
        st.info("所选月份没有数据。")
        return

    by_cat = {r["category"]: r for r in stats}

    # 按 CATEGORIES 固定顺序重排，没记账的分类补 0。
    # 否则柱子会随月份增删而左右跳动，没法跨月比较同一个分类。
    data = [
        {
            "分类": c,
            "笔数": by_cat[c]["cnt"] if c in by_cat else 0,
            "金额（元）": to_yuan(by_cat[c]["total_cents"]) if c in by_cat else 0.0,
        }
        for c in db.CATEGORIES
    ]
    table = pd.DataFrame(data)

    total_cents = sum(
        by_cat[c]["total_cents"] if c in by_cat else 0 for c in db.CATEGORIES
    )
    table["占比"] = (table["金额（元）"] / to_yuan(total_cents) * 100).round(1)

    # 限宽：默认会撑满容器，窗口一宽柱子就粗得笨重。
    left, _ = st.columns([2, 1])
    with left:
        # 6 根柱子用同一个颜色——这是单序列的数值比较，颜色不承载信息。
        # 给每个分类配一种颜色是反模式：颜色重复编码了柱子长度已经表达的东西。
        # 传「元」列，绝不能传 total_cents，否则每根柱子高 100 倍。
        st.bar_chart(table.set_index("分类")[["金额（元）"]])

    # 统计表是图表的"文字版孪生"，带占比列。
    st.dataframe(table, hide_index=True)
    st.caption(f"合计 {yuan(total_cents)}")

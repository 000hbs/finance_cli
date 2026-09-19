"""views/delete.py —— 页签 3：删除（下拉框选择 + 两步确认）。"""

import streamlit as st

from core import db
from utils.money import yuan


def render(month):
    st.subheader("删除记录")
    st.caption("下面的列表受侧边栏的月份筛选影响——看得见什么，就能删什么。")

    # ── 第二步：确认面板 ───────────────────────────────────────────
    if "pending_delete" in st.session_state:
        t = st.session_state["pending_delete"]
        st.warning(
            f"确认删除？ID {t['id']} ｜ {t['entry_date']} ｜ {t['category']} ｜ "
            f"{yuan(t['amount_cents'])} ｜ {t['note']}"
        )
        c1, c2 = st.columns(2)
        if c1.button("确认删除", type="primary"):
            db.delete_entry(t["id"])
            st.session_state.pop("pending_delete", None)
            st.session_state["flash"] = f"已删除 ID {t['id']}。"
            st.rerun()
        if c2.button("取消"):
            st.session_state.pop("pending_delete", None)
            st.rerun()
        return

    # ── 第一步：选择 ───────────────────────────────────────────────
    rows = db.list_entries(month=month)  # 注意：不受"明细"的分类筛选影响
    if not rows:
        st.info("没有可以删除的记录。")
        return

    by_id = {r["id"]: r for r in rows}
    picked = st.selectbox(
        "选择要删除的记录",
        options=list(by_id),
        format_func=lambda i: (
            f"ID {i} ｜ {by_id[i]['entry_date']} ｜ {by_id[i]['category']} ｜ "
            f"{yuan(by_id[i]['amount_cents'])}"
        ),
    )

    if st.button("删除这条"):
        # 只是把意图记下来，还不删。用户还有一次"取消"的机会。
        # 存成普通 session_state 键（不是控件状态），所以删完一行后
        # 下拉框选项变化会自然重新默认，不会出现"选中值指向已删除 ID"。
        st.session_state["pending_delete"] = by_id[picked]
        st.rerun()

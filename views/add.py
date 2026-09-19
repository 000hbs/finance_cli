"""views/add.py —— 页签 1：添加账目。"""

import datetime as dt

import streamlit as st

from core import db
from utils.money import to_cents, yuan


def render():
    st.subheader("添加账目")

    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        amount = c1.number_input(
            "金额（元）", min_value=0.01, value=10.0, step=1.0, format="%.2f"
        )
        category = c2.selectbox("分类", db.CATEGORIES)
        entry_date = st.date_input("日期", value=dt.date.today())
        note = st.text_input("备注（可选）", max_chars=50)
        submitted = st.form_submit_button("保存")

    # ↓ 必须在 with 块【外面】：在 form 内部调用 st.rerun() 会抛 StreamlitAPIException
    if submitted:
        cents = to_cents(amount)
        db.add_entry(entry_date.isoformat(), category, cents, note.strip())
        # 不能直接 st.success()——紧跟着 st.rerun() 会把它冲掉，用户什么都看不到。
        # 存进 session_state，由 app.py 在下一轮页面顶部渲染。
        st.session_state["flash"] = f"已保存：{entry_date} {category} {yuan(cents)}"
        st.rerun()

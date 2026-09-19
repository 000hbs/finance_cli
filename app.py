"""app.py —— 入口：页面配置、初始化、全局筛选、页签调度。

启动方式（必须先激活虚拟环境）：
    streamlit run app.py
"""

import streamlit as st

from core import db
from views import add, delete, entries, stats

st.set_page_config(page_title="我的记账本", page_icon="💰")  # 必须是第一个 st 调用

db.init_db()  # 幂等（IF NOT EXISTS），每次刷新跑一遍也无害

# 一次性提示：上一轮存下的保存/删除结果。
# 必须在任何 widget 之前 pop，否则会跟控件状态打架。
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

st.title("💰 我的记账本")

# 全局月份筛选——明细 / 删除 / 统计 三个页签共用。
# 放在侧边栏而不是各个页签里，否则用户切一次页签就要重选一次。
with st.sidebar:
    st.header("筛选")
    month_label = st.selectbox("月份", ["全部月份"] + db.available_months())
    month = None if month_label == "全部月份" else month_label

tab_add, tab_list, tab_delete, tab_stats = st.tabs(
    ["➕ 添加", "📋 明细", "🗑️ 删除", "📊 统计"]
)

with tab_add:
    add.render()
with tab_list:
    entries.render(month)
with tab_delete:
    delete.render(month)
with tab_stats:
    stats.render(month)

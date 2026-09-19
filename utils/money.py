"""utils/money.py —— 金额换算。

全项目**唯一**做元/分换算的地方。谁都不依赖，所以放最底层。
"""


def to_cents(yuan_amount: float) -> int:
    """元 -> 分。所有金额在进入数据库之前都必须过这一道。"""
    return int(round(yuan_amount * 100))


def to_yuan(cents: int) -> float:
    """分 -> 元（数值）。给画图和表格用，因为图表要的是数字不是字符串。

    显示给人看的字符串请用 yuan()。
    """
    return cents / 100


def yuan(cents: int) -> str:
    """分 -> '¥12.34'。所有金额在显示之前都必须过这一道。"""
    return f"¥{cents / 100:.2f}"

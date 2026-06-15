"""
同一个需求，两种写法对比：普通 if/else 函数 vs LangGraph。

场景：简单的订单处理流程
  1. 检查库存
  2. 计算价格（库存不足直接拒绝）
  3. 判断是否满足折扣条件
  4. 生成订单结果
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from typing import TypedDict, Literal
from langgraph.graph import END, StateGraph


# ══════════════════════════════════════════════════════════════════
# 版本 A：普通函数（if/else 嵌套）
# ══════════════════════════════════════════════════════════════════

def process_order_plain(item: str, quantity: int, stock: int, unit_price: float) -> dict:
    # 检查库存
    if quantity > stock:
        return {"status": "rejected", "reason": "库存不足", "total": 0}

    # 计算价格
    total = quantity * unit_price

    # 判断折扣
    if total >= 500:
        total *= 0.9
        discount = "9折"
    else:
        discount = "无折扣"

    return {"status": "accepted", "discount": discount, "total": round(total, 2)}


# ══════════════════════════════════════════════════════════════════
# 版本 B：LangGraph
# ══════════════════════════════════════════════════════════════════

class OrderState(TypedDict):
    item: str
    quantity: int
    stock: int
    unit_price: float
    total: float
    discount: str
    status: str     # "accepted" | "rejected"
    reason: str


# ── 节点 ─────────────────────────────────────────────────────────

def check_stock(state: OrderState) -> OrderState:
    if state["quantity"] > state["stock"]:
        return {**state, "status": "rejected", "reason": "库存不足"}
    return {**state, "status": "ok"}


def calc_price(state: OrderState) -> OrderState:
    total = state["quantity"] * state["unit_price"]
    return {**state, "total": total}


def apply_discount(state: OrderState) -> OrderState:
    if state["total"] >= 500:
        return {**state, "total": round(state["total"] * 0.9, 2), "discount": "9折"}
    return {**state, "discount": "无折扣"}


def accept_order(state: OrderState) -> OrderState:
    return {**state, "status": "accepted"}


def reject_order(state: OrderState) -> OrderState:
    return state  # reason 已在 check_stock 写入


# ── 路由 ─────────────────────────────────────────────────────────

def route_stock(state: OrderState) -> Literal["calc_price", "reject_order"]:
    return "calc_price" if state["status"] == "ok" else "reject_order"


# ── 构图 ─────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(OrderState)

    graph.add_node("check_stock", check_stock)
    graph.add_node("calc_price", calc_price)
    graph.add_node("apply_discount", apply_discount)
    graph.add_node("accept_order", accept_order)
    graph.add_node("reject_order", reject_order)

    graph.set_entry_point("check_stock")
    graph.add_conditional_edges("check_stock", route_stock)
    graph.add_edge("calc_price", "apply_discount")
    graph.add_edge("apply_discount", "accept_order")
    graph.add_edge("accept_order", END)
    graph.add_edge("reject_order", END)

    return graph.compile()


# ══════════════════════════════════════════════════════════════════
# 对比运行
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    cases = [
        {"item": "键盘", "quantity": 2,  "stock": 10, "unit_price": 299.0},
        {"item": "显示器", "quantity": 5, "stock": 3,  "unit_price": 1500.0},
        {"item": "鼠标",  "quantity": 3,  "stock": 10, "unit_price": 199.0},
    ]

    app = build_graph()

    print("=" * 50)
    for c in cases:
        print(f"\n订单：{c['item']} x{c['quantity']}（库存 {c['stock']}，单价 {c['unit_price']}）")

        # 版本 A
        r_plain = process_order_plain(**c)
        print(f"  [普通函数] {r_plain}")

        # 版本 B
        init: OrderState = {**c, "total": 0, "discount": "", "status": "", "reason": ""}
        r_graph = app.invoke(init)
        print(f"  [Graph]    status={r_graph['status']} discount={r_graph['discount']} total={r_graph['total']} reason={r_graph['reason']}")

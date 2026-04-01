import uuid
from datetime import datetime

from app.models.models import Item


def build_out_trade_no(order):
    return f'ORDER_{order.id}'


def parse_order_id_from_out_trade_no(out_trade_no):
    prefix = 'ORDER_'
    if not out_trade_no or not out_trade_no.startswith(prefix):
        raise ValueError('无效的订单号')
    return uuid.UUID(out_trade_no[len(prefix):])


def restore_inventory_for_order(order):
    item = order.item or Item.query.get(order.item_id)
    if not item:
        return None

    current_quantity = max(int(item.quantity or 0), 0)
    restore_quantity = max(int(order.quantity or 1), 1)
    item.quantity = current_quantity + restore_quantity

    if item.status != 'deleted':
        item.status = 'on_sale'

    return item


def cancel_order(order):
    if order.status == 'cancelled':
        return order

    restore_inventory_for_order(order)
    order.status = 'cancelled'
    return order


def mark_order_paid(order, trade_no=None, payment_channel='alipay'):
    order.status = 'paid'
    order.payment_channel = payment_channel
    order.payment_trade_no = (trade_no or order.payment_trade_no or '')[:64] or None
    if not order.paid_at:
        order.paid_at = datetime.now()
    return order

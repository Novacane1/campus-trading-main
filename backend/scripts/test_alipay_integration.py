"""
支付宝沙箱接入验证脚本
"""
import os
import sys
import time
from decimal import Decimal

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)

from flask_jwt_extended import create_access_token
from alipay.aop.api.util.SignatureUtils import get_sign_content, sign_with_rsa2

from app import create_app, db
from app.models.models import Category, Item, Order, User
from app.services.alipay_service import AlipayService
from app.services.order_service import build_out_trade_no
from config.config import Config


PASS = 0
FAIL = 0


def report(ok, name, detail=''):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f'  [PASS] {name}')
    else:
        FAIL += 1
        print(f'  [FAIL] {name}: {detail}')


def auth_header(user_id):
    token = create_access_token(identity=str(user_id))
    return {'Authorization': f'Bearer {token}'}


def build_notify_payload(order, trade_status='TRADE_SUCCESS', trade_no='202604010001'):
    payload = {
        'app_id': Config.ALIPAY_APP_ID,
        'charset': 'utf-8',
        'notify_id': f'test-{int(time.time())}',
        'notify_time': '2026-04-01 12:00:00',
        'notify_type': 'trade_status_sync',
        'out_trade_no': build_out_trade_no(order),
        'seller_id': '2088102177846880',
        'total_amount': f'{Decimal(str(order.amount)):.2f}',
        'trade_no': trade_no,
        'trade_status': trade_status,
    }
    sign_content = get_sign_content(payload)
    payload['sign_type'] = 'RSA2'
    payload['sign'] = sign_with_rsa2(
        Config.ALIPAY_APP_PRIVATE_KEY,
        sign_content,
        'utf-8'
    )
    return payload


def main():
    app = create_app()

    with app.app_context():
        category = Category.query.first()
        if not category:
            print('未找到分类数据，无法执行测试')
            raise SystemExit(1)

        suffix = str(int(time.time()))
        seller = User(
            username=f'alipay_seller_{suffix}',
            student_id=f'ALIPAYSELLER{suffix}',
            school_name='测试大学',
            email=f'alipay_seller_{suffix}@example.com',
        )
        seller.set_password('Password123')

        buyer = User(
            username=f'alipay_buyer_{suffix}',
            student_id=f'ALIPAYBUYER{suffix}',
            school_name='测试大学',
            email=f'alipay_buyer_{suffix}@example.com',
        )
        buyer.set_password('Password123')

        item = Item(
            seller=seller,
            category_id=category.id,
            name='支付宝测试商品',
            description='用于验证支付宝接入',
            price=Decimal('99.00'),
            quantity=3,
            status='on_sale',
            images=[],
            location='图书馆'
        )

        second_item = Item(
            seller=seller,
            category_id=category.id,
            name='支付宝取消库存测试商品',
            description='用于验证取消订单后库存恢复',
            price=Decimal('59.00'),
            quantity=3,
            status='on_sale',
            images=[],
            location='食堂'
        )

        sync_item = Item(
            seller=seller,
            category_id=category.id,
            name='支付宝同步查询测试商品',
            description='用于验证返回页同步状态',
            price=Decimal('39.00'),
            quantity=1,
            status='on_sale',
            images=[],
            location='宿舍区'
        )

        db.session.add_all([seller, buyer, item, second_item, sync_item])
        db.session.commit()

        created_order_ids = []

        try:
            client = app.test_client()
            buyer_headers = auth_header(buyer.id)
            seller_headers = auth_header(seller.id)

            resp = client.post('/api/orders/', json={'item_id': item.id, 'quantity': 1}, headers=buyer_headers)
            report(resp.status_code == 201, '创建待支付订单', resp.get_json())
            order_id = resp.get_json()['id']
            order = db.session.get(Order, order_id)
            created_order_ids.append(order.id)

            pay_resp = client.post('/api/payments/alipay/page', json={'order_id': order_id}, headers=buyer_headers)
            pay_json = pay_resp.get_json() or {}
            report(pay_resp.status_code == 200, '发起支付宝支付单', pay_json)
            report('alipay.trade.page.pay' in (pay_json.get('payment_form') or ''), '返回支付宝页面支付表单')
            report(build_out_trade_no(order) == pay_json.get('out_trade_no'), '外部交易单号映射正确', pay_json)

            manual_paid_resp = client.put(
                f'/api/orders/{order_id}/status',
                json={'status': 'paid'},
                headers=buyer_headers
            )
            report(manual_paid_resp.status_code == 400, '禁止前端手动改成已付款', manual_paid_resp.get_json())

            pre_ship_resp = client.put(
                f'/api/orders/{order_id}/status',
                json={'status': 'shipped'},
                headers=seller_headers
            )
            report(pre_ship_resp.status_code == 400, '未付款前禁止发货', pre_ship_resp.get_json())

            original_alipay_public_key = Config.ALIPAY_PUBLIC_KEY
            Config.ALIPAY_PUBLIC_KEY = Config.ALIPAY_APP_PUBLIC_KEY
            try:
                notify_payload = build_notify_payload(order)
                notify_resp = client.post('/api/payments/alipay/notify', data=notify_payload)
                db.session.refresh(order)
                report(notify_resp.status_code == 200 and notify_resp.data.decode() == 'success', '回调验签并更新订单', notify_resp.data.decode())
                report(order.status == 'paid', '回调后订单为已付款', order.to_dict())
                report(bool(order.paid_at), '记录付款时间', order.to_dict())
                report(order.payment_trade_no == '202604010001', '记录支付宝交易号', order.to_dict())
            finally:
                Config.ALIPAY_PUBLIC_KEY = original_alipay_public_key

            ship_resp = client.put(
                f'/api/orders/{order_id}/status',
                json={'status': 'shipped'},
                headers=seller_headers
            )
            db.session.refresh(order)
            report(ship_resp.status_code == 200 and order.status == 'shipped', '已付款后允许卖家发货', ship_resp.get_json())

            confirm_resp = client.put(f'/api/orders/{order_id}/confirm', headers=buyer_headers)
            db.session.refresh(order)
            report(confirm_resp.status_code == 200 and order.status == 'completed', '买家确认收货', confirm_resp.get_json())

            cancel_create_resp = client.post(
                '/api/orders/',
                json={'item_id': second_item.id, 'quantity': 2},
                headers=buyer_headers
            )
            report(cancel_create_resp.status_code == 201, '创建可取消订单', cancel_create_resp.get_json())
            cancel_order_id = cancel_create_resp.get_json()['id']
            cancel_order = db.session.get(Order, cancel_order_id)
            created_order_ids.append(cancel_order.id)

            cancel_resp = client.put(
                f'/api/orders/{cancel_order_id}/status',
                json={'status': 'cancelled'},
                headers=buyer_headers
            )
            db.session.refresh(second_item)
            report(cancel_resp.status_code == 200, '买家取消待付款订单', cancel_resp.get_json())
            report(second_item.quantity == 3, '取消后库存恢复正确', second_item.to_dict())
            report(second_item.status == 'on_sale', '取消后商品重新上架', second_item.to_dict())

            sync_create_resp = client.post('/api/orders/', json={'item_id': sync_item.id, 'quantity': 1}, headers=buyer_headers)
            report(sync_create_resp.status_code == 201, '创建待同步订单', sync_create_resp.get_json())
            sync_order_id = sync_create_resp.get_json()['id']
            sync_order = db.session.get(Order, sync_order_id)
            created_order_ids.append(sync_order.id)

            original_query_trade = AlipayService.query_trade
            AlipayService.query_trade = staticmethod(lambda _order: {
                'trade_status': 'TRADE_SUCCESS',
                'trade_no': 'SYNC20260401001',
            })
            try:
                sync_resp = client.get(f'/api/payments/alipay/orders/{sync_order_id}/status', headers=buyer_headers)
                db.session.refresh(sync_order)
                report(sync_resp.status_code == 200, '返回页同步支付状态接口可用', sync_resp.get_json())
                report(sync_order.status == 'paid', '同步接口可更新待支付订单状态', sync_order.to_dict())
            finally:
                AlipayService.query_trade = original_query_trade

        finally:
            Order.query.filter(Order.id.in_(created_order_ids)).delete(synchronize_session=False)
            Item.query.filter(Item.id.in_([item.id, second_item.id, sync_item.id])).delete(synchronize_session=False)
            User.query.filter(User.id.in_([seller.id, buyer.id])).delete(synchronize_session=False)
            db.session.commit()

    print('=' * 56)
    print(f'  测试汇总: PASS={PASS} FAIL={FAIL}')
    print('=' * 56)
    raise SystemExit(1 if FAIL else 0)


if __name__ == '__main__':
    main()

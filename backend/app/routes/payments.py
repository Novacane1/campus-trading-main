from datetime import datetime
from html import escape
from urllib.parse import urlparse, urlunparse

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import decode_token, get_jwt_identity, jwt_required

from app import db
from app.models.models import Order
from app.models.models import serialize_datetime
from app.services.alipay_service import AlipayService
from app.services.order_service import cancel_order, mark_order_paid, parse_order_id_from_out_trade_no
from config.config import Config

payments_bp = Blueprint('payments', __name__)


def _configuration_error_response():
    missing = AlipayService.get_missing_config()
    return jsonify({
        'msg': '支付宝配置不完整',
        'missing': missing,
    }), 503


def _orders_page_url():
    return_url = (Config.ALIPAY_RETURN_URL or '').strip()
    if not return_url:
        return '/orders'

    parts = urlparse(return_url)
    cleaned = parts._replace(params='', query='', fragment='')
    return urlunparse(cleaned) or '/orders'


def _html_message_response(title, message, status_code=400):
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f7f8; color: #1f2937; margin: 0; }}
    .wrap {{ max-width: 560px; margin: 10vh auto; background: #fff; border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,.08); }}
    h1 {{ font-size: 24px; margin: 0 0 12px; }}
    p {{ line-height: 1.7; margin: 0 0 18px; }}
    a {{ color: #1677ff; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{escape(title)}</h1>
    <p>{escape(message)}</p>
    <a href="{escape(_orders_page_url())}">返回订单页</a>
  </div>
</body>
</html>"""
    return Response(html, status=status_code, mimetype='text/html')


def _html_launch_response(order, payment_form):
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>正在前往支付宝</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f7f7f8; color: #1f2937; margin: 0; }}
    .wrap {{ max-width: 560px; margin: 10vh auto; background: #fff; border-radius: 16px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,.08); text-align: center; }}
    h1 {{ font-size: 24px; margin: 0 0 12px; }}
    p {{ line-height: 1.7; margin: 0 0 12px; }}
    .hint {{ color: #6b7280; font-size: 14px; }}
    form[name="punchout_form"] input[type="submit"] {{
      display: none;
      width: 100%;
      margin-top: 18px;
      border: 0;
      border-radius: 10px;
      padding: 12px 16px;
      background: #1677ff;
      color: #fff;
      font-size: 16px;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>正在前往支付宝沙箱</h1>
    <p>订单号：{escape(str(order.id))}</p>
    <p class="hint">如果没有自动跳转，请点击下方按钮继续。</p>
    {payment_form}
  </div>
  <script>
    const payForm = document.forms[0];
    const submitBtn = payForm?.querySelector('input[type="submit"]');
    if (submitBtn) {{
      submitBtn.value = '继续前往支付宝';
    }}
    window.setTimeout(() => {{
      if (submitBtn) {{
        submitBtn.style.display = 'block';
      }}
    }}, 1200);
  </script>
</body>
</html>"""
    return Response(html, mimetype='text/html')


def _get_user_id_from_submitted_token():
    token = (request.form.get('token') or '').strip()
    if not token:
        raise ValueError('登录状态缺失，请重新登录')

    decoded = decode_token(token)
    subject = decoded.get('sub')
    if subject in (None, ''):
        raise ValueError('登录信息无效，请重新登录')
    return int(subject)


@payments_bp.route('/alipay/page', methods=['POST'])
@jwt_required()
def create_alipay_page_payment():
    if not AlipayService.is_configured():
        return _configuration_error_response()

    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    order_id = data.get('order_id')

    if not order_id:
        return jsonify({'msg': '订单号不能为空'}), 400

    order = Order.query.get_or_404(order_id)
    if order.buyer_id != user_id:
        return jsonify({'msg': 'Forbidden'}), 403
    if order.status != 'pending':
        return jsonify({'msg': '当前订单状态无法发起支付'}), 400
    if order.expire_time and order.expire_time <= datetime.now():
        cancel_order(order)
        db.session.commit()
        return jsonify({'msg': '订单已超时，已自动取消'}), 400

    payment_data = AlipayService.create_page_payment_form(order)
    return jsonify({
        'order_id': str(order.id),
        'expires_at': serialize_datetime(order.expire_time),
        **payment_data,
    }), 200


@payments_bp.route('/alipay/launch', methods=['POST'])
def launch_alipay_page_payment():
    if not AlipayService.is_configured():
        return _html_message_response('支付宝不可用', '当前支付宝配置不完整，请稍后再试', 503)

    try:
        user_id = _get_user_id_from_submitted_token()
    except Exception as exc:
        return _html_message_response('登录已失效', str(exc), 401)

    order_id = request.form.get('order_id')
    if not order_id:
        return _html_message_response('无法发起支付', '订单号不能为空')

    order = Order.query.get(order_id)
    if not order:
        return _html_message_response('订单不存在', '请刷新订单列表后重试', 404)
    if order.buyer_id != user_id:
        return _html_message_response('无权操作', '这不是你的订单', 403)
    if order.status != 'pending':
        return _html_message_response('无法发起支付', '当前订单状态不能发起支付')
    if order.expire_time and order.expire_time <= datetime.now():
        cancel_order(order)
        db.session.commit()
        return _html_message_response('订单已超时', '该订单已自动取消，请重新下单')

    payment_data = AlipayService.create_page_payment_form(order)
    return _html_launch_response(order, payment_data['payment_form'])


@payments_bp.route('/alipay/notify', methods=['POST'])
def handle_alipay_notify():
    if not AlipayService.is_configured():
        return Response('failure', mimetype='text/plain'), 503

    form_data = request.values.to_dict(flat=True)
    if not form_data:
        return Response('failure', mimetype='text/plain'), 400
    if not AlipayService.verify_notification_signature(form_data):
        return Response('failure', mimetype='text/plain'), 400

    if form_data.get('app_id') != Config.ALIPAY_APP_ID:
        return Response('failure', mimetype='text/plain'), 400

    try:
        order_id = parse_order_id_from_out_trade_no(form_data.get('out_trade_no', ''))
    except ValueError:
        return Response('failure', mimetype='text/plain'), 400

    order = Order.query.get(order_id)
    if not order:
        return Response('failure', mimetype='text/plain'), 404
    if not AlipayService.amount_matches(order, form_data.get('total_amount')):
        return Response('failure', mimetype='text/plain'), 400

    trade_status = form_data.get('trade_status')
    if AlipayService.is_success_status(trade_status):
        if order.status == 'cancelled':
            return Response('failure', mimetype='text/plain'), 409
        mark_order_paid(order, trade_no=form_data.get('trade_no'))
    elif trade_status == 'TRADE_CLOSED' and order.status == 'pending':
        cancel_order(order)

    db.session.commit()
    return Response('success', mimetype='text/plain')


@payments_bp.route('/alipay/orders/<string:order_id>/status', methods=['GET'])
@jwt_required()
def sync_alipay_order_status(order_id):
    if not AlipayService.is_configured():
        return _configuration_error_response()

    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != user_id:
        return jsonify({'msg': 'Forbidden'}), 403

    synced = False
    sync_error = None
    trade_status = None

    if order.status == 'pending':
        try:
            trade_data = AlipayService.query_trade(order)
            trade_status = trade_data.get('trade_status')

            if AlipayService.is_success_status(trade_status):
                mark_order_paid(order, trade_no=trade_data.get('trade_no'))
                db.session.commit()
                synced = True
            elif trade_status == 'TRADE_CLOSED':
                cancel_order(order)
                db.session.commit()
                synced = True
        except Exception as exc:
            sync_error = str(exc)

    return jsonify({
        'order': order.to_dict(),
        'synced': synced,
        'trade_status': trade_status,
        'sync_error': sync_error,
    }), 200

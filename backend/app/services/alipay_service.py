import json
import math
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
from alipay.aop.api.util.SignatureUtils import get_sign_content, verify_with_rsa

from config.config import Config
from app.services.order_service import build_out_trade_no


class AlipayService:
    REQUIRED_CONFIG = (
        'ALIPAY_APP_ID',
        'ALIPAY_APP_PRIVATE_KEY',
        'ALIPAY_PUBLIC_KEY',
        'ALIPAY_NOTIFY_URL',
        'ALIPAY_RETURN_URL',
    )

    @staticmethod
    def get_missing_config():
        return [
            field_name
            for field_name in AlipayService.REQUIRED_CONFIG
            if not getattr(Config, field_name, '')
        ]

    @staticmethod
    def is_configured():
        return not AlipayService.get_missing_config()

    @staticmethod
    def _create_client():
        if not AlipayService.is_configured():
            missing = ', '.join(AlipayService.get_missing_config())
            raise ValueError(f'支付宝配置缺失: {missing}')

        client_config = AlipayClientConfig()
        client_config.server_url = Config.ALIPAY_GATEWAY
        client_config.app_id = Config.ALIPAY_APP_ID
        client_config.app_private_key = Config.ALIPAY_APP_PRIVATE_KEY
        client_config.alipay_public_key = Config.ALIPAY_PUBLIC_KEY
        client_config.charset = 'utf-8'
        client_config.format = 'json'
        client_config.sign_type = 'RSA2'
        client_config.sandbox_debug = Config.ALIPAY_DEBUG

        return DefaultAlipayClient(alipay_client_config=client_config, logger=None)

    @staticmethod
    def _format_amount(amount):
        return str(Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    @staticmethod
    def _build_return_url(order):
        parts = urlparse(Config.ALIPAY_RETURN_URL)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query.update({
            'alipay_return': '1',
            'order_id': str(order.id),
        })
        return urlunparse(parts._replace(query=urlencode(query)))

    @staticmethod
    def _get_timeout_express(order):
        if not order.expire_time:
            return '15m'

        remaining_seconds = (order.expire_time - datetime.now()).total_seconds()
        minutes = max(1, math.ceil(max(remaining_seconds, 1) / 60))
        return f'{minutes}m'

    @staticmethod
    def create_page_payment_form(order):
        client = AlipayService._create_client()
        request = AlipayTradePagePayRequest()
        request.notify_url = Config.ALIPAY_NOTIFY_URL
        request.return_url = AlipayService._build_return_url(order)

        model = AlipayTradePagePayModel()
        model.out_trade_no = build_out_trade_no(order)
        model.total_amount = AlipayService._format_amount(order.amount)
        model.subject = f'校园交易 - {order.item.name if order.item else "商品订单"}'[:120]
        model.product_code = 'FAST_INSTANT_TRADE_PAY'
        model.timeout_express = AlipayService._get_timeout_express(order)
        model.body = f'订单 {order.id}'
        request.biz_model = model

        payment_form = client.page_execute(request, http_method='POST')
        payment_url = client.page_execute(request, http_method='GET')
        return {
            'payment_form': payment_form,
            'payment_url': payment_url,
            'out_trade_no': model.out_trade_no,
        }

    @staticmethod
    def query_trade(order):
        client = AlipayService._create_client()
        request = AlipayTradeQueryRequest()

        model = AlipayTradeQueryModel()
        model.out_trade_no = build_out_trade_no(order)
        request.biz_model = model

        response = client.execute(request)
        payload = json.loads(response) if response else {}
        return payload.get('alipay_trade_query_response', payload)

    @staticmethod
    def verify_notification_signature(form_data):
        sign = form_data.get('sign')
        if not sign:
            return False

        filtered = {
            key: value
            for key, value in form_data.items()
            if key not in ('sign', 'sign_type') and value not in (None, '')
        }
        message = get_sign_content(filtered).encode('utf-8')
        try:
            return verify_with_rsa(Config.ALIPAY_PUBLIC_KEY, message, sign)
        except Exception:
            return False

    @staticmethod
    def is_success_status(trade_status):
        return trade_status in ('TRADE_SUCCESS', 'TRADE_FINISHED')

    @staticmethod
    def amount_matches(order, amount_text):
        if amount_text in (None, ''):
            return False
        local_amount = Decimal(str(order.amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        remote_amount = Decimal(str(amount_text)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return local_amount == remote_amount

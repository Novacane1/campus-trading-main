from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone='Asia/Shanghai')


def init_scheduler(app):
    def cancel_expired_orders():
        """扫描超时未支付订单，自动取消并恢复商品状态"""
        with app.app_context():
            from app import db
            from app.models.models import Order
            from app.services.order_service import cancel_order

            now = datetime.now()
            expired = Order.query.filter(
                Order.status == 'pending',
                Order.expire_time != None,
                Order.expire_time <= now
            ).all()

            if not expired:
                return

            for order in expired:
                cancel_order(order)

            try:
                db.session.commit()
                logger.info(f'自动取消 {len(expired)} 笔超时订单')
            except Exception as e:
                db.session.rollback()
                logger.error(f'取消超时订单失败: {e}')

    scheduler.add_job(
        func=cancel_expired_orders,
        trigger='interval',
        minutes=1,
        id='cancel_expired_orders',
        replace_existing=True
    )
    scheduler.start()
    logger.info('订单超时定时任务已启动（每分钟扫描一次）')

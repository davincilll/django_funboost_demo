# 定时取消订单
from funboost import boost, BoosterParams, BrokerEnum

import demo.models


# 这里启用了自动消费功能


@boost(BoosterParams(queue_name="cancel_order", broker_kind=BrokerEnum.REDIS_STREAM, is_auto_start_consuming_message=True))
def wait_pay_auto_cancel_order(order):
    if order.status == demo.models.OrderStatus.WAIT_PAY:
        order.close_trigger()

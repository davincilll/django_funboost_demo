# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from funboost import PriorityConsumingControlConfig

from demo.funboost_service import wait_pay_auto_cancel_order


class OrderStatus(models.IntegerChoices):
    PRE_PAY = 0, _("预订单")
    WAIT_PAY = 1, _("待付款")
    WAIT_DELIVER = 2, _("待发货")
    DELIVERED = 3, _("已收货")
    FINISHED = 4, _("已完成")
    CLOSED = -1, _("订单已关闭")
    CANCELED = -2, _("订单已取消")


# 将公共的信息抽离出来作为一个订单的公共信息
class WXCommodityOrderExtension(models.Model):
    address = models.CharField(max_length=256, verbose_name='收货地址', null=True, blank=True)
    # 订单物流单号
    logistics_no = models.CharField(max_length=128, verbose_name='物流单号', null=True, blank=True)
    # 订单备注
    remark = models.CharField(max_length=128, verbose_name='订单备注', null=True, blank=True)
    # 订单状态
    status = models.IntegerField(verbose_name='订单状态', choices=OrderStatus.choices,
                                 default=OrderStatus.PRE_PAY)

    def on_enter_WAIT_PAY(self):
        self.status = OrderStatus.WAIT_PAY
        # 发布自动触发closed的任务
        wait_pay_auto_cancel_order.publish({"order": self}, priority_control_config=PriorityConsumingControlConfig(
            countdown=60 * 15, misfire_grace_time=None))
        self.save()

    def close_trigger(self):
        pass

    class Meta:
        db_table = 'order'
        verbose_name = "订单"
        verbose_name_plural = verbose_name

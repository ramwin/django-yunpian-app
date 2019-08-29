from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.db.models.signals import post_save
import json
import logging
from yunpian_python_sdk.ypclient import YunpianClient
from . import exceptions


log = logging.getLogger(__name__)


@python_2_unicode_compatible
class Account(models.Model):
    """云片网注册的帐号"""
    name = models.CharField("帐号名称", unique=True, max_length=63)
    apikey = models.CharField("APIKEY", unique=True, max_length=63)

    def __str__(self):
        return "Account: {}".format(self.id)

    @property
    def ypclient(self):
        return YunpianClient(self.apikey)


@python_2_unicode_compatible
class Sign(models.Model):
    """签名"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField("签名内容", max_length=31)

    def __str__(self):
        return "Sign: {}".format(self.id)


@python_2_unicode_compatible
class Template(models.Model):
    """短信模板"""
    TYPE_CHOICE = (
        ("验证码类", "验证码类"),
        ("通知类", "通知类"),
        ("会员营销类", "会员营销类"),
    )
    id = models.IntegerField(unique=True, primary_key=True)
    sign = models.ForeignKey(Sign, on_delete=models.CASCADE)
    _type = models.CharField("短信类型", choices=TYPE_CHOICE, max_length=15)
    content = models.TextField(
        "模板内容", help_text="要是python的format形式.里面的变量用{}包裹")

    def __str__(self):
        return "Template: {}".format(self.id)


@python_2_unicode_compatible
class Message(models.Model):
    """发送的短信记录"""
    STATUS_CHOICE = (
        ("发送成功", "发送成功"),
        ("发送中", "发送中"),
        ("发送失败", "发送失败"),
    )
    mobile = models.CharField("手机号", max_length=14)
    template = models.ForeignKey(
        Template, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        "状态", choices=STATUS_CHOICE, max_length=31, default="发送中")
    params = models.TextField(
        "短信参数", help_text="用json.dumps后的参数", default="{}")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Message: {}".format(self.id)

    def send(self):
        """发送短信"""
        ypclient = self.template.sign.account.ypclient
        params = json.loads(self.params)
        text = "【{}】{}".format(
            self.template.sign.name,
            self.template.content.format(**params)
        )
        r = ypclient.sms().single_send({
            "mobile": self.mobile,
            "text": text,
        })
        if r.code() == 0:
            self.status = "发送成功"
            self.save()
        else:
            self.status = "发送失败"
            self.save()
        if r.code() == 10:
            log.error(r.detail())
            log.error(self)
            raise exceptions.NoHarassException(r.detail())
        if r.code() != 0:
            log.error("短信发送失败")
            log.error(self)
            log.error(r)
            log.error(r.exception())
            raise exceptions.YunpianException(r.detail())

    @classmethod
    def post_save(cls, sender, *args, **kwargs):
        instance = kwargs["instance"]
        created = kwargs["created"]
        if created:
            instance.send()


post_save.connect(Message.post_save, sender=Message)

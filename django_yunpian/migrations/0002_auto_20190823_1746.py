# Generated by Django 2.1.5 on 2019-08-23 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_yunpian', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(choices=[('发送成功', '发送成功'), ('发送中', '发送中')], default='发送中', max_length=7, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='template',
            name='content',
            field=models.TextField(help_text='要是python的format形式.里面的变量用{}包裹', verbose_name='模板内容'),
        ),
    ]
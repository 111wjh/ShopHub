
import os

from celery import Celery

# 设置 Django 默认配置文件
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 Celery 应用
app = Celery('shophub')

# 从 Django settings 中读取 CELERY_ 开头的配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现各个 Django 应用中的 tasks.py
app.autodiscover_tasks()

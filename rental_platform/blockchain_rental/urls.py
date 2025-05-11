from django.urls import path
from . import views

urlpatterns = [
    # 区块链浏览器页面
    path('explorer/', views.explorer_view, name='explorer'),
    
    # 首页 - 重定向到浏览器页面
    path('', views.explorer_view, name='home'),
    
    # API - 准备交易数据
    path('api/prepare/user-registration/', views.prepare_user_registration_tx, name='prepare_user_registration'),
    path('api/prepare/property-registration/', views.prepare_property_registration_tx, name='prepare_property_registration'),
    
    # API - 读取链上数据
    path('api/user/<str:user_address>/', views.get_user_blockchain_info, name='get_user_info'),
    path('api/property/<int:property_id>/', views.get_property_blockchain_info, name='get_property_info'),
    path('api/property/count/', views.get_total_property_count, name='get_property_count'),
] 
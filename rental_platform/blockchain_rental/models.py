from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    用户模型 - 扩展Django的标准用户模型
    
    区块链关联:
    - blockchain_address: 用户在区块链上的地址，用于身份验证和声誉跟踪
    - identity_verification_hash: 存储在链上的身份验证信息哈希值
    - is_identity_verified: 表示用户是否已通过链上身份验证
    """
    blockchain_address = models.CharField(max_length=42, blank=True, null=True, help_text=_("用户的区块链钱包地址"))
    identity_verification_hash = models.CharField(max_length=64, blank=True, null=True, help_text=_("链上存储的身份验证信息哈希"))
    is_identity_verified = models.BooleanField(default=False, help_text=_("用户是否已通过链上身份验证"))
    
    class Meta:
        verbose_name = _("用户")
        verbose_name_plural = _("用户")
    
    def __str__(self):
        return self.username

class Property(models.Model):
    """
    房源模型 - 存储房源基本信息
    
    区块链关联:
    - blockchain_property_id: 房源在区块链上的唯一标识
    - verification_hash: 房源验证信息（如照片、地址等）的哈希，存储在链上
    - is_verified: 表示房源是否已通过验证并在链上记录
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties", help_text=_("房源所有者"))
    title = models.CharField(max_length=100, help_text=_("房源标题"))
    description = models.TextField(help_text=_("房源描述"))
    location = models.CharField(max_length=255, help_text=_("房源位置"))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("每晚价格"))
    
    # 区块链相关字段
    blockchain_property_id = models.CharField(max_length=64, blank=True, null=True, help_text=_("房源在区块链上的唯一标识"))
    verification_hash = models.CharField(max_length=64, blank=True, null=True, help_text=_("房源验证信息的哈希值"))
    is_verified = models.BooleanField(default=False, help_text=_("房源是否已验证"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("房源")
        verbose_name_plural = _("房源")
    
    def __str__(self):
        return self.title
        
class Booking(models.Model):
    """
    预订模型 - 处理租客对房源的预订
    
    区块链关联:
    - blockchain_contract_id: 预订在区块链上的智能合约ID
    - contract_hash: 预订合约条款的哈希，存储在链上确保不可篡改
    - contract_status: 链上合约的当前状态
    """
    STATUS_CHOICES = [
        ('pending', _('等待确认')),
        ('confirmed', _('已确认')),
        ('completed', _('已完成')),
        ('cancelled', _('已取消')),
        ('disputed', _('存在争议')),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="bookings", help_text=_("预订的房源"))
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings", help_text=_("租客"))
    check_in_date = models.DateField(help_text=_("入住日期"))
    check_out_date = models.DateField(help_text=_("退房日期"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("总价格"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text=_("预订状态"))
    
    # 区块链相关字段
    blockchain_contract_id = models.CharField(max_length=64, blank=True, null=True, help_text=_("区块链上的智能合约ID"))
    contract_hash = models.CharField(max_length=64, blank=True, null=True, help_text=_("预订合约条款的哈希值"))
    contract_status = models.CharField(max_length=20, blank=True, null=True, help_text=_("链上合约状态"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("预订")
        verbose_name_plural = _("预订")
    
    def __str__(self):
        return f"{self.renter.username} - {self.property.title} ({self.check_in_date} to {self.check_out_date})"

class Review(models.Model):
    """
    评价模型 - 处理预订完成后的评价
    
    区块链关联:
    - review_hash: 评价内容的哈希，存储在链上确保真实性和不可篡改性
    - blockchain_verification: 表示评价是否已在链上验证
    """
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="reviews", help_text=_("关联的预订"))
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", help_text=_("评价者"))
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews", help_text=_("评价接收者"))
    rating = models.IntegerField(choices=RATING_CHOICES, help_text=_("评分 (1-5)"))
    comment = models.TextField(help_text=_("评价内容"))
    
    # 区块链相关字段
    review_hash = models.CharField(max_length=64, blank=True, null=True, help_text=_("评价内容的哈希值"))
    blockchain_verification = models.BooleanField(default=False, help_text=_("评价是否已在链上验证"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("评价")
        verbose_name_plural = _("评价")
    
    def __str__(self):
        return f"{self.reviewer.username}'s review for {self.receiver.username}"

class BlockchainTransaction(models.Model):
    """
    区块链交易模型 - 记录所有与区块链交互的交易
    
    此模型帮助追踪所有区块链交易，提供透明的链上操作记录
    """
    TRANSACTION_TYPES = [
        ('identity', _('身份验证')),
        ('property', _('房源验证')),
        ('booking', _('预订合约')),
        ('review', _('评价验证')),
        ('payment', _('支付交易')),
        ('other', _('其他')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions", help_text=_("发起交易的用户"))
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, help_text=_("交易类型"))
    transaction_hash = models.CharField(max_length=66, help_text=_("区块链交易哈希"))
    related_object_id = models.IntegerField(null=True, blank=True, help_text=_("关联对象ID"))
    related_object_type = models.CharField(max_length=20, null=True, blank=True, help_text=_("关联对象类型"))
    status = models.CharField(max_length=20, default='pending', help_text=_("交易状态"))
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True, help_text=_("交易确认时间"))
    
    class Meta:
        verbose_name = _("区块链交易")
        verbose_name_plural = _("区块链交易")
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash[:10]}..."

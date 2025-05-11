from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Property, Booking, Review, BlockchainTransaction

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_identity_verified', 'blockchain_address')
    list_filter = ('is_identity_verified', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('区块链信息', {'fields': ('blockchain_address', 'identity_verification_hash', 'is_identity_verified')}),
    )

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'location', 'price_per_night', 'is_verified')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('title', 'description', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'renter', 'check_in_date', 'check_out_date', 'total_price', 'status')
    list_filter = ('status', 'check_in_date')
    search_fields = ('property__title', 'renter__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'receiver', 'rating', 'blockchain_verification', 'created_at')
    list_filter = ('rating', 'blockchain_verification')
    search_fields = ('reviewer__username', 'receiver__username', 'comment')

@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'transaction_hash', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__username', 'transaction_hash')

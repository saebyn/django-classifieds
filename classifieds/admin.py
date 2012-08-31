"""
"""

from django.contrib import admin

import models


class AdFieldInline(admin.StackedInline):
    model = models.FieldValue


class AdAdmin(admin.ModelAdmin):
    list_filter = ('active', 'category',)
    list_display = ('title', 'category', 'expires_on',)
    search_fields = ('title',)
    inlines = [AdFieldInline]


class CategoryFieldInline(admin.StackedInline):
    model = models.Field


class CategoryAdmin(admin.ModelAdmin):
    inlines = [CategoryFieldInline]
    prepopulated_fields = {'slug': ('name',)}


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ad', 'amount', 'paid', 'paid_on',)

    def paid(self):
        return self.instance.paid

    def paid_on(self):
        return self.instance.paid_on


admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.Ad, AdAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register([models.Field, models.FieldValue, models.Pricing,
                     models.PricingOptions, models.ImageFormat])

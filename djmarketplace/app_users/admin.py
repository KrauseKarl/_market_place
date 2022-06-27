from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'get_avatar', 'status', 'balance', 'verified_id',)
    list_editable = ['balance', 'verified_id', 'status']
    list_filter = ['verified_id', 'status']
    actions = ['mark_as_deleted_by_admin', 'user_verified']
    search_fields = ['user__profile']
    radio_fields = {"status": admin.VERTICAL, }
    raw_id_fields = ("user",)
    save_on_top = True

    def user_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    def get_avatar(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}", width=60')

    def user_verified(self, request, queryset):
        return queryset.update(verified_id=True)

    user_verified.short_description = _('Verify selected profile')


admin.site.register(Profile, ProfileAdmin)

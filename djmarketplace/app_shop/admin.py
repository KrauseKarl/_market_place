from django.contrib import admin
from django.utils.safestring import mark_safe

from app_shop.models import *


class ItemInline(admin.StackedInline):
    model = Item
    extra = 2
    fields = (('name', 'category', 'description',), 'image', ('price', 'discount', 'stock'), 'available',)

    def get_avatar(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}", width=60')

    get_avatar.__name__ = 'Изображение'


class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_avatar_sh', 'category', 'description', ]
    list_display_links = ['description',]
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'category']
    search_fields = ['category__name']
    radio_fields = {"category": admin.VERTICAL}
    inlines = [
        ItemInline,
    ]
    save_on_top = True

    def get_avatar_sh(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}", width=60')

    get_avatar_sh.allow_tags = True


class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_avatar_sh_ct', 'description']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def get_avatar_sh_ct(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}", width=60')
        return None

    get_avatar_sh_ct.short_description = 'img'



class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'img', 'price', 'discount', 'sale', 'stock',
                    'available', 'created_at', 'update_at']
    list_display_links = ['name',]
    list_filter = ['available', 'created_at', 'name', 'category']
    list_editable = ['price', 'discount', 'stock', 'available']
    search_fields = ['name', 'id', 'category__name', 'shop__name', ]
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    list_per_page = 5
    list_select_related = ('shop', 'category')
    show_full_result_count = True
    date_hierarchy = 'created_at'

    def img(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}", width=60')

    img.short_description = 'Картинка'
    img.allow_tags = True


class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class RepostListAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity']
    list_filter = ['quantity']
    search_fields = ['item__name']


admin.site.register(Shop, ShopAdmin)
admin.site.register(ShopCategory, ShopCategoryAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(RepostList, RepostListAdmin)
admin.site.empty_value_display = '(пусто)'

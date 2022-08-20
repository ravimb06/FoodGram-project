from django.contrib import admin

from .models import Follow, User


class BaseAdminSetting(admin.ModelAdmin):
    """Базовая настройка администраторской панели."""
    empty_value_display = '-пусто-'
    list_filter = ('email', 'username')


class UsersAdmin(BaseAdminSetting):
    """Настройка панели управления пользователями."""
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'first_name',
        'last_name'
    )
    list_display_links = ('id', 'username')
    search_fields = ('role', 'username')


class FollowAdmin(admin.ModelAdmin):
    """Настройка панели управления подписками."""
    list_display = (
        'id',
        'user',
        'author'
    )
    list_display_links = ('id', 'user')
    search_fields = ('user',)


admin.site.register(User, UsersAdmin)
admin.site.register(Follow, FollowAdmin)

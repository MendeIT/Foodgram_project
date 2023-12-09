from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'first_name', 'last_name', 'email',
        'password', 'followers_counter', 'following_counter',
        'date_joined', 'last_login'
    ]
    list_display_links = ['username']
    list_editable = ['password']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    date_hierarchy = 'date_joined'
    list_per_page = 10

    @admin.display(
        description='Кол-во подписчиков'
    )
    def followers_counter(self, obj):
        return obj.follower.count()

    @admin.display(
        description='Кол-во подписок'
    )
    def following_counter(self, obj):
        return obj.following.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['author', 'user']
    search_fields = ['author__username', 'user__username']
    ordering = ['author']
    list_select_related = ['author', 'user']

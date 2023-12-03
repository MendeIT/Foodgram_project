from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name',
                    'email', 'password', 'date_joined', 'last_login')
    list_display_links = ['username']
    list_editable = ('password', 'first_name', 'last_name')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ['id']
    date_hierarchy = 'date_joined'
    list_per_page = 10


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    search_fields = ('author', 'user')

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs.select_related(
                'author')

        return qs.filter(user=request.user)

from django.contrib import admin

from users.models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username')
    search_fields = ('username', 'email')
    empty_value_display = '-empty-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user',)
    search_fields = (
        'author__username',
        'author__email',
        'user__username',
        'user__email',
    )
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Chat, Message


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Chat)
admin.site.register(Message)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from server.models import Council, Student, MessMenu, Event, Complaint, HostelFile, OtherImages, InventoryCategory, InventoryItem, Meal


admin.site.register([Council, Event, MessMenu, Complaint, HostelFile, OtherImages, InventoryItem, InventoryCategory, Meal])


class StudentAdmin(UserAdmin):
    list_display = ["name", "rollNumber", 'last_login', 'is_admin']
    search_fields = ["rollNumber", 'name']
    readonly_fields = ['last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'rollNumber', 'mobileNumber', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ['rollNumber']



admin.site.register(Student, StudentAdmin)
# admin.py
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse #builds urls by name
from .models import (
    MenuFood, Drinks, MenuCategory, DrinksCategory,
    ContactMessage, Reservation, Table, Review
)

admin.site.register(MenuFood)
admin.site.register(MenuCategory)
admin.site.register(DrinksCategory)
admin.site.register(ContactMessage)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'party_size', 'table')

admin.site.register(Reservation, ReservationAdmin)

class DrinksAdmin(admin.ModelAdmin):
    filter_horizontal = ('categories',)

admin.site.register(Drinks, DrinksAdmin)

#custom bulk action 
def safe_delete_selected(modeladmin, request, queryset):
    blocked, allowed = [], []

    for table in queryset:
        if table.has_future_reservations():
            blocked.append(table)
        else:
            allowed.append(table)

    # delete the allowed ones
    for t in allowed:
        t.delete()

    if allowed:
        messages.success(request, f"Deleted {len(allowed)} table(s).")
    if blocked:
        names = ", ".join(str(t) for t in blocked)
        messages.warning(
            request,
            f"Skipped {len(blocked)} table(s) with future reservations: {names}."
        )

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'capacity', 'allows_shared')

    #bulk deleting tables
    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        actions['safe_delete_selected'] = (
            safe_delete_selected,
            'safe_delete_selected',
            "Delete selected tables (skips those with future reservations)"
        )
        return actions

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.has_future_reservations():
            self.message_user(
                request,
                "Cannot delete this table: it has future reservations.",
                level=messages.ERROR
            )
            # redirect back to the change form for this object
            opts = self.model._meta
            change_url = reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[obj.pk])
            return HttpResponseRedirect(change_url)

        # no future reservations , so delete
        else:
            return super().delete_view(request, object_id, extra_context=extra_context)
        
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("name", "comment")
    actions = ["approve_selected"]

    @admin.action(description="Approve selected reviews")
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
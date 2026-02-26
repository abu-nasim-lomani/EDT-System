# events/admin.py
from django.contrib import admin
from .models import Event, Invitation


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'start_datetime', 'location', 'created_by')
    search_fields = ('title', 'description', 'location')
    list_filter = ('type', 'status', 'start_datetime')
    inlines = [InvitationInline]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'invitee', 'status')
    list_filter = ('status',)
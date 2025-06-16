from django.contrib import admin
from .models import SavedText, UserTyping, TypingEvent, Exercise

@admin.register(SavedText)
class SavedTextAdmin(admin.ModelAdmin):
    list_display    = ('pk', 'text', 'score', 'created_at', 'updated_at')
    list_filter     = ('created_at', 'updated_at')
    list_editable   = ('score',)
    search_fields   = ('text',)

@admin.register(UserTyping)
class UserTypingAdmin(admin.ModelAdmin):
    list_display    = ('pk', 'session_id', 'cursor_position', 'created_at')
    list_filter     = ('created_at',)
    search_fields   = ('session_id',)
    ordering        = ('-created_at',)

@admin.register(TypingEvent)
class TypingEventAdmin(admin.ModelAdmin):
    list_display    = (
        'pk',
        'student',
        'exercise',
        'timestamp',
        'cursor_position',
        'action',
    )
    list_filter     = ('action', 'exercise', 'student')
    search_fields   = ('student__username', 'exercise__title')
    ordering        = ('-timestamp',)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display    = ('pk', 'title', 'author', 'created_at')
    list_filter     = ('author', 'created_at')
    search_fields   = ('title', 'content', 'author__username')
    date_hierarchy  = 'created_at'

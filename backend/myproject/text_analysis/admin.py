from django.contrib import admin
from .models import SavedText, UserTyping

# Enregistrement de SavedText dans l'admin avec une personnalisation
class SavedTextAdmin(admin.ModelAdmin):
    list_display = ('text', 'score', 'created_at', 'updated_at')  # Si tu as `updated_at` dans le modèle
    list_filter = ('created_at',)  # Si tu ne veux pas filtrer par `updated_at`, retire-le
    list_editable = ('score',)

admin.site.register(SavedText, SavedTextAdmin)


# Enregistrement de UserTyping dans l'admin avec une personnalisation

class UserTypingAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'cursor_position', 'text_progression', 'created_at')  # Liste des champs à afficher
    list_filter = ('session_id',)  # Filtrer par session_id
    search_fields = ('session_id',)  # Permet de chercher par session_id

admin.site.register(UserTyping, UserTypingAdmin)
from django.contrib import admin
from .models import TypingEvent

@admin.register(TypingEvent)
class TypingEventAdmin(admin.ModelAdmin):
    list_display = ("session_id", "cursor_position", "text_progression", "timestamp")
    ordering = ("-timestamp",)  # Trie par date décroissante

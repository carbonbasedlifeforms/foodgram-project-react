from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)


class FavoriteAdmin(admin.ModelAdmin):
    """Админка модели Favorite"""
    list_display = ('recipe', 'user',)
    search_fields = ('recipe__name', 'user__username', 'user__email')
    empty_value_display = '-empty-'


class IngredientAdmin(admin.ModelAdmin):
    """Админка модели Ingredient"""
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-empty-'


class RecipeAdmin(admin.ModelAdmin):
    """Админка модели Recipe"""
    list_display = ('pk', 'author', 'name',)
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    empty_value_display = '-empty-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админка модели RecipeIngredient"""
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('ingredient',)
    empty_value_display = '-empty-'


class ShoppingListAdmin(admin.ModelAdmin):
    """Админка модели ShoppingList"""
    list_display = ('pk', 'user', 'recipe',)
    list_filter = ('user',)


class TagAdmin(admin.ModelAdmin):
    """Админка модели Tag"""
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-empty-'


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Tag, TagAdmin)

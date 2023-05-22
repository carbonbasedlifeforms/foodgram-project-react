from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from users.models import Follow
from .validators import validate_cooking_time, validate_count

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор кастомной модели User"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        """Метод проверки наличия подписки на пользователя"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class BreifRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта с кратким набором полей"""
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class FollowingSerializer(serializers.ModelSerializer):
    """Сериализатор подписок на авторов"""
    author = CustomUserSerializer()
    recipes = BreifRecipeSerializer(
        many=True,
        read_only=True,
        source='author.recipe_author'
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('author', 'recipes', 'recipes_count', 'user')

    def get_recipes_count(self, obj):
        """Метод возвращает кол-во рецептов автора"""
        return obj.author.recipe_author.count()

    def to_representation(self, instance):
        """Метод представления результатов сериализатора"""
        representation = super().to_representation(instance)
        return {
            'email': representation['author']['email'],
            'id': representation['author']['id'],
            'username': representation['author']['username'],
            'first_name': representation['author']['first_name'],
            'last_name': representation['author']['last_name'],
            'is_subscribed': representation['author']['is_subscribed'],
            'recipes': representation['recipes'],
            'recipes_count': representation['recipes_count'],
        }


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и удаления ингредиентов в рецепте"""
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(validators=[validate_count])

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class MainRecipeSerializer(serializers.ModelSerializer):
    """Cериализатор рецептов"""
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
        write_only=True,
    )
    cooking_time = serializers.IntegerField(
        validators=[validate_cooking_time]
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """Метод для добавления ингредиентов"""
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        current_user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=current_user)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredient.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод представления результатов сериализатора"""
        return ReadRecipeSerializer(instance, context=self.context).data

    def validate_author(self, value):
        """Метод валидации подписки на самого себя"""
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'На себя подписаться нельзя!'
            )

    def validate_ingredients(self, value):
        """Метод валидации кол-ва игредиентов в рецепте"""
        if not value or len(value) < settings.MIN_INGREDIENTS_QTY:
            raise serializers.ValidationError(
                f'Рецепт должен содержать хотя бы '
                f'{settings.MIN_INGREDIENTS_QTY} ингредиент!'
            )
        return value

    def validate_tags(self, value):
        """Метод валидации кол-ва игредиентов в рецепте"""
        if not value or len(value) < settings.MIN_INGREDIENTS_QTY:
            raise serializers.ValidationError(
                f'Рецепт должен содержать хотя бы '
                f'{settings.MIN_INGREDIENTS_QTY} тег!'
            )
        return value


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов"""

    ingredients = IngredientsInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        """Имеется ли рецепт в избранном"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Имеется ли рецепт в списке покупок"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            user=request.user,
            recipe=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = fields

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientFilter
from .paginations import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    BreifRecipeSerializer,
    CustomUserSerializer,
    FollowingSerializer,
    IngredientSerializer,
    MainRecipeSerializer,
    ReadRecipeSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет работы с пользователями"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        methods=('GET', ),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def read_subscribe(self, request):
        """Метод вывода существующих подписок"""
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowingSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Метод добавления/удаления подписки на пользователя"""
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'Error': 'Уже есть такая подписка'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user.id == author.id:
                return Response(
                    {'Error': 'На себя подписаться нельзя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Follow.objects.create(
                user=user,
                author=author
            )
            serializer = FollowingSerializer(
                subscription,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follow.objects.get(
            user=user,
            author=self.get_object()
        ).delete()
        return Response(
            {'message': 'Подписка удалена'},
            status=status.HTTP_204_NO_CONTENT
        )


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет игредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = MainRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от типа запроса POST/PATCH"""
        if self.request.method in ('POST', 'PATCH'):
            return MainRecipeSerializer
        return ReadRecipeSerializer

    def add_obj(self, model, user, pk):
        """Метод добавления рецепта"""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        serializer = BreifRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        """Метод удаления рецепта"""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление/удаление в избранное"""
        if request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, pk)
        return self.add_obj(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление в список покупок"""
        if request.method == 'DELETE':
            return self.delete_obj(ShoppingList, request.user, pk)
        return self.add_obj(ShoppingList, request.user, pk)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Выгрузка списка покупок в формате txt"""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppinglist_recipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

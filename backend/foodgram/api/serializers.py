from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)

from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from users.models import Follow, User


class RecipeShortInfo(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class UsersSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj).exists()


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class FollowListSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortInfo(
                Recipe.objects.filter(author=author),
                many=True,
                context={'request': queryset}
            ).data
        return RecipeShortInfo(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True, context={'request': queryset}
        ).data

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=author
        ).exists()


class FollowSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'errors': 'На себя подписываться нельзя.'
            })
        if Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
        ):
            raise ValidationError({
                'errors': 'Вы уже подписаны.'
            })
        return data

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class IngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        read_only=True,
        slug_field='measurement_unit',
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    Ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredients_recipe',
    )
    author = UsersSerializer(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author', 'ingredients',
            'image', 'text', 'tags', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

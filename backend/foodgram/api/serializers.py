from django.db.transaction import atomic
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


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


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
    ingredients = IngredientRecipeSerializer(
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


class CreateIngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, data):
        if int(data) < 1:
            raise ValidationError({
                'ingredients': ('Не может быть меньше 1'),
                'msg': data
            })
        return data

    def create(self, validated_data):
        return IngredientRecipe.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class CreateRecipeSerializer(ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = UsersSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'image', 'author',
            'tags', 'cooking_time', 'ingredients',
        )

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            ingredient_amount = ingredient['amount']
            if ingredient_amount <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0 !'
                )
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Ингредиенты повторяются!'
                )
            ingredients_list.append(ingredient_id)
        if self.data.get('cooking_time') <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0 !'
            )
        return data

    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        recipe.ingredients_recipe.delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class RecipeShortInfo(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CartSerializer(ModelSerializer):
    class Meta:
        fields = ['recipe', 'user']
        model = Cart

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if Cart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Этот рецепт уже в корзине.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfo(instance.recipe, context=context).data


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError({
                'errors': 'Уже есть в избранном.'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortInfo(
            instance.recipe, context=context).data


class FollowListSerializer(ModelSerializer):
    recipes = SerializerMethodField(method_name='get_recipes')
    recipes_count = SerializerMethodField(method_name='get_recipes_count')
    is_subscribed = SerializerMethodField(method_name='get_is_subscribed',
                                          read_only=True)

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

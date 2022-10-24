"""
Test Recipe API
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse("recipe:recipe-list")


def detail_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def image_upload_url(recipe_id):
    """return image upload url"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def create_recipe(user, **params):
    """Create and return recipe"""
    defaults = {
        "title": "Sample Recipe title",
        "time_minutes": 7,
        "price": Decimal("5.99"),
        "description": "Sample description",
        "link": "http://example.com/recipe.png",
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test Unauth API req"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test Auth recipe API req"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@mail.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrive a list of recipe"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by("-id")

        recipe_list_serialized = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_list_serialized.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipe is limited to auth user"""
        other_user = create_user(
            email="other@mail.com",
            password="password",
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        recipe_list_serialized = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_list_serialized.data)

    def test_get_recipe_detail(self):
        """test get recipe Details"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        recipe_detail_serialized = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, recipe_detail_serialized.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            "title": "Sample Recipe title 2",
            "time_minutes": 2,
            "price": Decimal("5.99"),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_patch_recipe(self):
        """Test patch  recipe"""
        original_link = "http://example.com/recipe.png"
        recipe = create_recipe(
            user=self.user,
            title="sample recipe title",
            link=original_link
        )

        payload = {
            "title": "Udpated title"
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_put_recipe(self):
        """Test put  recipe"""
        original_link = "http://example.com/recipe.png"
        recipe = create_recipe(
            user=self.user,
            title="sample recipe title",
            link=original_link,
            description="Sample description",
        )

        payload = {
            "title": "Udpated title",
            "link": "http://samplenew.com/recipe.png",
            "description": "New recipe description",
            "time_minutes": 10,
            "price": Decimal("2.56")
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_return_error(self):
        """Test update with other user"""
        other_user = create_user(
            email="other@mail.com",
            password="password",
        )
        recipe = create_recipe(user=self.user)

        payload = {"user": other_user.id}
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test Delete Recipe"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id))

    def test_del_recipe_by_other_user(self):
        """Test delete recipe by ither user"""
        other_user = create_user(
            email="other@mail.com",
            password="password",
        )
        recipe = create_recipe(user=other_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_tag_with_recipe(self):
        """Test create recipe with Tag"""
        payload = {
            "title": "Thai Prawn curry",
            "time_minutes": 30,
            "price": Decimal("10.5"),
            "tags": [
                {"name": "Thai"},
                {"name": "Dinner"}
            ]
        }

        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """Test recipe creation with existing tag"""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "Pongal",
            "time_minutes": 60,
            "price": Decimal("6.2"),
            "tags": [
                {"name": "Indian"},
                {"name": "Sweet"}
            ],
        }
        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

        tag_check = Tag.objects.filter(name="Indian")

        self.assertEqual(tag_check.count(), 1)

    def test_create_tag_on_update(self):
        """Test createing tag if updaeting recipe tag"""
        recipe = create_recipe(self.user)

        payload = {
            "tags": [
                {"name": "Lunch"}
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_tag(self):
        """Test assign an exist tag when updating recipe"""
        tag_brakfast = Tag.objects.create(user=self.user, name="breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_brakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {
            "tags": [
                {"name": "Lunch"}
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_brakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing all recipe tags"""
        tag_brakfast = Tag.objects.create(user=self.user, name="breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_brakfast)

        payload = {
            "tags": []
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_ingredient(self):
        """Test create recipe with Ingredient"""
        payload = {
            "title": "Ice Cream",
            "time_minutes": 30,
            "price": Decimal("10.5"),
            "ingredients": [
                {"name": "vanilla"},
                {"name": "chocobar"}
            ]
        }

        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existin_ingredient(self):
        """Test create recipe with existing ingredient"""
        ingredient_name = "pongal"
        ingredient_indian = Ingredient.objects.create(
            user=self.user,
            name=ingredient_name
            )
        payload = {
            "title": "Pongal",
            "time_minutes": 60,
            "price": Decimal("6.2"),
            "ingredients": [
                {"name": ingredient_name},
                {"name": "sundal"}
            ],
        }
        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient_indian, recipe.ingredients.all())
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                name=ingredient["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

        ingredient_check = Ingredient.objects.filter(name=ingredient_name)

        self.assertEqual(ingredient_check.count(), 1)

    def test_create_ingredient_on_update(self):
        """Test createing ingredient if updaeting recipe ingredient"""
        recipe = create_recipe(self.user)

        payload = {
            "ingredients": [
                {"name": "Lime"}
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_ingredient = Ingredient.objects.get(user=self.user, name="Lime")
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_ingredient(self):
        """Test assign an exist ingredient when updating recipe"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="breakfast"
            )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name="Lunch")
        payload = {
            "ingredients": [
                {"name": "Lunch"}
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing all recipe ingredients"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="breakfast"
            )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        payload = {
            "ingredients": []
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tag(self):
        """TEst filter recipe by tag"""
        r1 = create_recipe(user=self.user, title="recipe1")
        r2 = create_recipe(user=self.user, title="recipe2")
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        tag2 = Tag.objects.create(user=self.user, name="tag2")
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title="recipe3")

        params = {
            "tags": f"{tag1.id},{tag2.id}"
        }
        res = self.client.get(RECIPES_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredient(self):
        """TEst filter recipe by ingredient"""
        r1 = create_recipe(user=self.user, title="recipe1")
        r2 = create_recipe(user=self.user, title="recipe2")
        ingredient1 = Ingredient.objects.create(user=self.user, name="ing1")
        ingredient2 = Ingredient.objects.create(user=self.user, name="ing2")
        r1.ingredients.add(ingredient1)
        r2.ingredients.add(ingredient2)
        r3 = create_recipe(user=self.user, title="recipe3")

        params = {
            "ingredients": f"{ingredient1.id},{ingredient2.id}"
        }
        res = self.client.get(RECIPES_URL, params)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUplaodTests(TestCase):
    """TEst for Image upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="test@mail.com", password="password")
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_uplaod_image(self):
        """Test image updlaod to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"image": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_req(self):
        """Test uplaod invlaid image"""
        url = image_upload_url(self.recipe.id)
        payload = {"image": "image_text_invlid"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

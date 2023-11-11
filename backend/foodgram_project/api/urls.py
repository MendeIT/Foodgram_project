from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet,
                       RecipeViewSet,
                       TagViewSet,
                       UserViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet, basename='ingredient')
router_v1.register(r'tags', TagViewSet, basename='tag')
router_v1.register(r'recipes', RecipeViewSet, basename='recipe')
router_v1.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router_v1.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]

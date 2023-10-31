from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet,
                       RecipeViewSet,
                       TagViewSet,
                       UserListViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('ingredients', IngredientViewSet, basename='ingredient')
router_v1.register('tags', TagViewSet, basename='tag')
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('users', UserListViewSet, basename='user')

# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',c
#     ReviewViewSet,
#     basename='reviews'


urlpatterns = [
    path('', include(router_v1.urls)),
]

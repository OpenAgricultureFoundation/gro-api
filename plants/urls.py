from rest_framework.routers import DefaultRouter
from plants import views

router = DefaultRouter()
router.register(r'plantSite', views.PlantSiteViewset)
router.register(r'plantType', views.PlantTypeViewset)
router.register(r'plant', views.PlantViewset)

urlpatterns = router.urls

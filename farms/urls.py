from rest_framework.routers import DefaultRouter
from farms import views

router = DefaultRouter()
router.register(r'farms', views.FarmViewset)

urlpatterns = router.urls

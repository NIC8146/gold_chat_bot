from django.urls import path
from .views import ChatAPIView, GoldPurchaseAPIView

urlpatterns = [
    path('chat/', ChatAPIView.as_view(), name='chat-api'),
    path('gold/buy/', GoldPurchaseAPIView.as_view(), name='gold-buy-api'),
]
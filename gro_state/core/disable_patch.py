from rest_framework.mixins import UpdateModelMixin
from rest_framework.generics import (
    UpdateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
)

def disable_patch():
    del UpdateModelMixin.partial_update
    del UpdateAPIView.patch
    del RetrieveUpdateAPIView.patch
    del RetrieveUpdateDestroyAPIView.patch

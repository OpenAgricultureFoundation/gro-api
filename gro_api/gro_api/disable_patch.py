from rest_framework.mixins import UpdateModelMixin
from rest_framework.generics import (
    UpdateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
)

def disable_patch():
    if disable_patch.has_run:
        return
    del UpdateModelMixin.partial_update
    del UpdateAPIView.patch
    del RetrieveUpdateAPIView.patch
    del RetrieveUpdateDestroyAPIView.patch
    disable_patch.has_run = True
disable_patch.has_run = False

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from .views import TeamEditView, TeamListView

urlpatterns = [
    path("", TeamListView.as_view(), name="team-list"),
    path("<int:pk>/edit/", TeamEditView.as_view(), name="team-edit"),
]

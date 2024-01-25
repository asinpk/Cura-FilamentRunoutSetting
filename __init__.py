# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The FilamentRunoutSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import FilamentRunoutSensorSettingsPlugin


def getMetaData():
    return {}

def register(app):
    return {"extension": FilamentRunoutSensorSettingsPlugin.FilamentRunoutSensorSettingsPlugin()}

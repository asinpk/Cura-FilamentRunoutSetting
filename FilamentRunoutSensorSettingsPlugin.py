# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The FilamentRunoutSettingsPlugin is released under the terms of the AGPLv3 or higher.

from UM.Extension import Extension
from cura.CuraApplication import CuraApplication
from UM.Logger import Logger
from UM.Version import Version
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("LinearAdvanceSettingPlugin")

import collections
import json
import os.path

from typing import List, Optional, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.OutputDevice.OutputDevice import OutputDevice

class FilamentRunoutSensorSettingsPlugin(Extension):
    def __init__(self) -> None:
        super().__init__()

        self._application = CuraApplication.getInstance()

        self._i18n_catalog = None  # type: Optional[i18nCatalog]

        self._settings_dict = {}  # type: Dict[str, Any]
        self._expanded_categories = []  # type: List[str]  # temporary list used while creating nested settings

        settings_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FilamentRunoutSensorSettings.def.json")
        try:
            with open(settings_definition_path, "r", encoding = "utf-8") as f:
                self._settings_dict = json.load(f, object_pairs_hook = collections.OrderedDict)
        except:
            Logger.logException("e", "Could not load filamentrunout sensor settings definition")
            return

        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)

    def _onContainerLoadComplete(self, container_id: str) -> None:
        if not ContainerRegistry.getInstance().isLoaded(container_id):
            # skip containers that could not be loaded, or subsequent findContainers() will cause an infinite loop
            return

        try:
            container = ContainerRegistry.getInstance().findContainers(id = container_id)[0]
        except IndexError:
            # the container no longer exists
            return

        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        try:
            material_category = container.findDefinitions(key="material")[0]
        except IndexError:
            Logger.log("e", "Could not find parent category setting to add settings to")
            return

        for setting_key in self._settings_dict.keys():
            setting_definition = SettingDefinition(setting_key, container, material_category, self._i18n_catalog)
            setting_definition.deserialize(self._settings_dict[setting_key])

            # add the setting to the already existing printer settingdefinition
            # private member access is naughty, but the alternative is to serialise, nix and deserialise the whole thing,
            # which breaks stuff
            material_category._children.append(setting_definition)
            container._definition_cache[setting_key] = setting_definition

            self._expanded_categories = self._application.expandedCategories.copy()
            self._updateAddedChildren(container, setting_definition)
            self._application.setExpandedCategories(self._expanded_categories)
            self._expanded_categories = []  # type: List[str]
            container._updateRelations(setting_definition)

    def _updateAddedChildren(self, container: DefinitionContainer, setting_definition: SettingDefinition) -> None:
        children = setting_definition.children
        if not children or not setting_definition.parent:
            return

        # make sure this setting is expanded so its children show up  in setting views
        if setting_definition.parent.key in self._expanded_categories:
            self._expanded_categories.append(setting_definition.key)

        for child in children:
            container._definition_cache[child.key] = child
            self._updateAddedChildren(container, child)

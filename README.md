# Filament runout sensor settings

This simple plugin adds ability to enable/disable filament runout sensor. Marlin only.

## Installation

1. Copy plugin to Cura plugin folder.
2. Add `M412 S{material_frs_enable}` to your start gcode.
3. Make visible "Enable Filament Runout Sensor" setting in Cura settings.
4. Use this setting to manage FRS.

## Limitations

Use only 0 or 1 in input field. 0 - disabled, 1 - enabled.

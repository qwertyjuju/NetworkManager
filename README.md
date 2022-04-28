# NetworkManager

The Network Manager is a module for network commissioning. It is composed of 3 submodules:
- Network creator
- ConfigurationCreationTool
- DeviceLoader

## Network creator
TODO

## ConfigurationCreationTool
Tool for creating a switch or router configuration. The tool will create several files:
- json: contains all the information on the device configuration
- cmdl: binary file used for the deviceloader tool. It contains a list of CLI commands.
current_version: 0.0.1

### V0.0.1
- added port configuration: mode trunk / access/ ip address
- added vlan configuration: name / ip address
- added RIP configuration: version / no auto summary / networks
- added 2 save formats: json / cmdl

## DeviceLoader
TODO
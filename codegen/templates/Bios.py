# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Chassis Template File

import copy
import strgen
from api_emulator.utils import replace_recurse

_TEMPLATE = {
    "@odata.type": "#Bios.v1_2_3.Bios",
    "@odata.id": "{rb}Systems/{system_id}/Bios",
    "Id": "Bios",
    "Name": "BIOS Configuration Current Settings",
    "AttributeRegistry": "BiosAttributeRegistryP89.v1_0_0",
    "Attributes": {
        "AdminPhone": "",
        "BootMode": "Uefi",
        "EmbeddedSata": "Raid",
        "NicBoot1": "NetworkBoot",
        "NicBoot2": "Disabled",
        "PowerProfile": "MaxPerf",
        "ProcCoreDisable": 0,
        "ProcHyperthreading": "Enabled",
        "ProcTurboMode": "Enabled",
        "UsbControl": "UsbEnabled"
    },
    "ResetBiosToDefaultsPending": "true",
    "@Redfish.Settings": {
        "@odata.type": "#Settings.v1_4_0.Settings",
        "ETag": "9234ac83b9700123cc32",
        "Messages": [
            {
                "MessageId": "Base.1.0.SettingsFailed",
                "RelatedProperties": [
                    "/Attributes/ProcTurboMode"
                ]
            }
        ],
        "SettingsObject": {
            "@odata.id": "{rb}Systems/{system_id}/Bios/Settings"
        },
        "Time": "2016-03-07T14:44:30-05:00"
    },
    "Actions": {
        "#Bios.ResetBios": {
            "target": "{rb}Systems/{system_id}/Bios/Actions/Bios.ResetBios"
        },
        "#Bios.ChangePassword": {
            "target": "{rb}Systems/{system_id}/Bios/Actions/Bios.ChangePassword"
        }
    }
}


def get_Bios_instance(wildcards):
    """
    Creates an instance of _TEMPLATE and replaces wildcards as specified.
    """
    c = copy.deepcopy(_TEMPLATE)
    c['@odata.id'] = c['@odata.id'].format(rb=wildcards['rb'], system_id=wildcards['system_id'])
    c['@Redfish.Settings']['SettingsObject']['@odata.id'] = c['@Redfish.Settings']['SettingsObject']['@odata.id'].format(
        rb=wildcards['rb'], system_id=wildcards['system_id'])
    c['Actions']['#Bios.ResetBios']['target'] = c['Actions']['#Bios.ResetBios']['target'].format(
        rb=wildcards['rb'], system_id=wildcards['system_id'])
    c['Actions']['#Bios.ChangePassword']['target'] = c['Actions']['#Bios.ChangePassword']['target'].format(
        rb=wildcards['rb'], system_id=wildcards['system_id'])
    
    replace_recurse(c, wildcards)
    return c
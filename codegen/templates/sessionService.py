#!/usr/bin/env python3
# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# sessionService.py

import copy
from api_emulator.utils import replace_recurse

_TEMPLATE = \
{
    "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
    "@odata.id": "/redfish/v1/Systems/{cs_id}/Bios",
    "@odata.type": "#Bios.v1_2_3.Bios",
    "Id": "{id}",
    "Name": "BIOS Settings",
    "Description": "System BIOS Configuration",
    "AttributeRegistry": "/redfish/v1/Registries/BiosAttributeRegistry",
    "Attributes": {
        "BootMode": "UEFI",
        "VirtualizationEnabled": true,
        "SecureBoot": true,
        "TPMEnabled": true,
        "HyperThreading": "Enabled",
        "NumLock": "On",
        "BootOrder": [
            "NIC",
            "HDD",
            "USB",
            "CD/DVD"
        ],
        "PXEBootEnabled": false,
        "UEFIShellEnabled": false,
        "PowerOnSelfTest": "Minimal",
        "CState": "Enabled",
        "TurboBoost": "Enabled",
        "SR-IOV": "Enabled",
        "WakeOnLAN": "Disabled",
        "ProcessorCoreCount": 8,
        "ProcessorPowerManagement": "BalancedPerformance"
    },
    "Actions": {
        "#Bios.ResetBios": {
            "target": "/redfish/v1/Systems/1/Bios/Actions/Bios.ResetBios",
            "title": "Reset BIOS Settings to Default"
        },
        "#Bios.ChangePassword": {
            "target": "/redfish/v1/Systems/1/Bios/Actions/Bios.ChangePassword",
            "title": "Change BIOS Password",
            "PasswordName": "AdminPassword",
            "OldPassword": "current_password",
            "NewPassword": "new_secure_password"
        }
    },
    "ResetBiosToDefaultsPending": false,
    "Links": {
        "ActiveSoftwareImage": {
            "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BiosFirmware"
        },
        "SoftwareImages": [
            {
                "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BiosFirmware"
            }
        ],
        "SoftwareImages@odata.count": 1
    },
    "Oem": {
        "VendorSpecificSettings": {
            "OverclockingEnabled": false,
            "FanSpeedControl": "Auto"
        }
    }
}

def get_sessionService_instance(wildcards):
    c = copy.deepcopy(_TEMPLATE)
    replace_recurse(c, wildcards)
    return c

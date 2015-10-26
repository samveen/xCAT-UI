#/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configuration module for the app
"""

config={
    'socket': '../fcgi/fcgi.sock',

    'getGroups': {
        'DisplayGroups': [
            "ID-LZD-ALICE-LIVE", "ID-LZD-ALICE-STAG", "ID-LZD-APPS-LIVE",
            "ID-LZD-APPS-SHRM", "ID-LZD-APPS-STAG", "ID-SC-APPS",
            "INFRA-SVC", "uatprovision"
        ]
    },
    'decommNode': {
        'osimage': 'centos7.1-x86_64-install-decommission'
    }
}



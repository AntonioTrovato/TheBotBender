#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType","")
    APP_TENANT_ID = os.environ.get("MicrosoftAppTenantId","")
    COSMOS_DB_URI = ""
    COSMOS_DB_PRIMARY_KEY = ""
    COSMOS_DB_DATABASE_ID = ""
    COSMOS_DB_CONTAINER_ID = ""
    LUIS_APP_ID = ""
    LUIS_API_KEY = ""
    LUIS_API_HOST_NAME = ""

from flask_appbuilder.security.manager import AUTH_OAUTH

# Set the authentication type to OAuth
AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {   'name':'openedxsso',
        'token_key':'access_token', # Name of the token in the response of access_token_url
        'icon':'fa-address-card',   # Icon for the provider
        'remote_app': {
            'client_id':'superset-client',  # Client Id (Identify Superset application)
            'client_secret':'superset-secret', # Secret for this Client Id (Identify Superset application)
            'client_kwargs':{
                'scope': 'read'               # Scope for the Authorization
            },
            'access_token_method':'POST',    # HTTP Method to call access_token_url
            'access_token_params':{        # Additional parameters for calls to access_token_url
                'client_id':'superset-client'
            },
            'access_token_headers':{    # Additional headers for calls to access_token_url
                'Authorization': 'Basic Base64EncodedClientIdAndSecret'
            },
            'api_base_url':'http://local.overhang.io:8000',
            'access_token_url':'http://local.overhang.io:8000/oauth2/access_token/',
            'authorize_url':'http://local.overhang.io:8000/oauth2/authorize/'
        }
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

# Should we replace ALL the user's roles each login, or only on registration?
AUTH_ROLES_SYNC_AT_LOGIN = True

# map from the values of `userinfo["role_keys"]` to a list of Superset roles
AUTH_ROLES_MAPPING = {
    "user": ["User"],
    "admin": ["Admin"],
}

from openedx_sso_security_manager import OpenEdxSsoSecurityManager, can_view_courses
CUSTOM_SECURITY_MANAGER = OpenEdxSsoSecurityManager


# Enable use of variables in datasets/queries
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Add this custom template processor which returns the list of courses the current user can access
JINJA_CONTEXT_ADDONS = {
    'can_view_courses': can_view_courses
}

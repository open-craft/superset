# Superset + Open edX

## Stand up Superset in a development environment

Superset needs to be able to access the Open edX MySQL database. To do this in the Tutor dev environment, Superset needs to share the same docker network.

1. [Install and run Tutor dev][install-tutor]
1. [Install Superset locally using Docker Compose][install-superset], using this fork/branch.

1. Start Superset, using [docker-compose-tutor-dev.yml](docker-compose-tutor-dev.yml) (a modified version of
   [docker-compose-non-dev.yml][upstream-docker-compose-non-dev]) so that it shares Tutor's network:

    ```
	# Pull and start the docker containers
    docker-compose -f docker-compose-tutor-dev.yml pull
    docker-compose -f docker-compose-tutor-dev.yml up
    ```

[install-tutor]: https://docs.tutor.overhang.io/install.html#installing-from-source
[install-superset]: https://superset.apache.org/docs/installation/installing-superset-using-docker-compose/
[upstream-docker-compose-non-dev]: https://github.com/apache/superset/blob/master/docker-compose-non-dev.yml
[login-superset]: https://superset.apache.org/docs/installation/installing-superset-using-docker-compose#4-log-in-to-superset

## Single Sign-On (SSO)

Configure SSO authentication on Superset to use the OAuth2 application created on Open edX.

**WARNING:** The files and credentials presented here are insecure, and should only be used in a development environment.

### Open edX

1. [Launch an LMS shell][tutor-shell]:

    ```
    tutor dev run lms bash
    ```
1. Add a user for superset's authentication:

    ```
    ./manage.py lms manage_user superset superset@apache
    ```
1. Create a Django OAuth Toolkit › Application with provider name openedxsso:

    ```
    ./manage.py lms create_dot_application \
        --grant-type authorization-code \
        --redirect-uris "http://localhost:8088/oauth-authorized/openedxsso" \
        --client-id superset-client \
        --client-secret superset-secret \
        --scopes user_id \
        superset-sso superset
    ```

### Superset

The following files create a custom [Custom OAuth2 Configuration][sso-superset], with a default set of credentials for connecting to Tutor dev.

* [requirements-openedx.txt](docker/requirements-openedx.txt) : installs `authlib `as a python dependency
* [openedx_sso_security_manager.py](docker/pythonpath_dev/openedx_sso_security_manager.py) : adds a custom authentication manager which fetches the SSO user's details from the Open edX API.

   **TODO:** This manager assumes that all authenticated users are Admin users; this will be changed as this document progresses.
* [superset_config_tutor_dev.py](docker/pythonpath_dev/superset_config_tutor_dev.py) : adds configuration for SSO OAuth using the OpenEdxSsoSecurityManager, using an insecure set of credentials for connecting to Tutor dev.


[tutor-shell]: https://github.com/overhangio/tutor/blob/master/docs/dev.rst#running-arbitrary-commands
[sso-superset]: https://superset.apache.org/docs/installation/configuring-superset/#custom-oauth2-configuration

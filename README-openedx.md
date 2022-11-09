# Superset + Open edX

## Stand up Superset in a development environment

Superset needs to be able to access the Open edX MySQL database. To do this in the Tutor dev environment, Superset needs to share the same docker network.

1. [Install and run Tutor dev][install-tutor]
1. [Install Superset locally using Docker Compose][install-superset], using this fork/branch.
1. Create `docker/pythonpath_dev/superset_config_docker.py`, and add:

    ```
    # Copy the `OPENEDX_MYSQL_PASSWORD` generated to your `$(tutor config printroot)/config.yml"`
    OPENEDX_DATABASE_PASSWORD = "<redacted>"
    ```
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
* [superset_config_tutor_dev.py](docker/pythonpath_dev/superset_config_tutor_dev.py) : adds configuration for SSO OAuth using the OpenEdxSsoSecurityManager, using an insecure set of credentials for connecting to Tutor dev.


[tutor-shell]: https://github.com/overhangio/tutor/blob/master/docs/dev.rst#running-arbitrary-commands
[sso-superset]: https://superset.apache.org/docs/installation/configuring-superset/#custom-oauth2-configuration

## Connect Superset to the Open edX MySQL database

[Connecting to a MySQL database][mysql-superset] requires adding a python dependency, which has been added for this fork to
[requirements-openedx.txt](docker/requirements-openedx.txt).

1. Login to Superset UI via SSO as a LMS superuser.
1. Add a [new Data connection][db-superset] using the MySQL connector and the Tutor dev MySQL database credentials.

    For Tutor dev, these are:
    * Host: `tutor_dev_mysql_1`
    * Port: `3306`
    * Database name: `openedx`
    * Username: `openedx`
    * Password: use the `OPENEDX_MYSQL_PASSWORD` generated to your `$(tutor config printroot)/config.yml"`
1. Create a [Dataset][dashboard-superset] using the above data connection on the `openedx` database.
1. Create a [Chart][chart-superset] using the above data set, and Save:
    * Title: `Open edX Enrollments`
    * Chart Source: `openedx.student_courseenrollment`
    * Metrics: `COUNT(*)`
    * Data > Time Column: `created`
    * Data > Time Grain: `Day`


[mysql-superset]: https://superset.apache.org/docs/databases/mysql
[db-superset]: https://superset.apache.org/docs/databases/db-connection-ui/
[dashboard-superset]: https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard/
[chart-superset]: https://superset.apache.org/docs/miscellaneous/chart-params/#chart-parameters

## Restrict access to Open edX Enrollments to course staff

We can use the following Superset features to enforce a restriction to protect access by course to enrollments data:

* [Built-in roles][roles-superset]
* [Dataset security][dataset-security-superset] applied to a custom role we will add manually.
* [SQL Templating][sql-templating-superset], and the `can_view_courses()` custom Jinja template function added by this fork/branch.
* Superset's [Row Level Security][row-level-security-superset] filters.

Steps to follow:

1. Login to Superset UI via SSO as a LMS superuser.
1. [Create a new role][gamma-dataset-role-superset] with access to the `openedx` MySQL data set created above.
    * Name: `Open edX`
    * Permissions: `schema access on [Open edX MySQL].[openedx]`
    * User: (leave blank)
      Users will be automatically assigned to this role when they login via our custom SSO Security Manager.
1. Create a [Row Level Security][row-level-security-superset] filter:
    * Name: `Enrollments`
    * Description: `Restrict access to the Course Enrollments table`
    * Filter Type: `Regular`
    * Tables: `openedx.student_courseenrollment`
    * Roles: `Open edX`
    * Group Key: `courses`
    * Clause: `{{can_view_courses()}}`

To try this out:

1. Login to Tutor Studio as a staff or superuser.
1. Create one or more courses.
1. Add various users as staff members to your courses.
1. Login to Superset as one of those staff members, and view the `Open edX Enrollment` chart created above.
   Note that it shows different course enrollment data depending on who is logged in.

### Know issues

[Superset caches][cache-superset] charts and result sets by default, and these caches don't take into account dynamic row-based permissions. So you have to refresh the cache in order to see different
data for different users.

This can be fixed with configuration, but might prove a detriment to performance.


[roles-superset]: https://superset.apache.org/docs/security/#provided-roles
[sql-templating-superset]: https://superset.apache.org/docs/installation/sql-templating/#sql-templating
[gamma-dataset-role-superset]: https://superset.apache.org/docs/security/#managing-data-source-access-for-gamma-roles
[dataset-security-superset]: https://superset.apache.org/docs/security/#restricting-access-to-a-subset-of-data-sources
[row-level-security-superset]: https://superset.apache.org/docs/security/#row-level-security
[cache-superset]: https://superset.apache.org/docs/installation/cache/

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

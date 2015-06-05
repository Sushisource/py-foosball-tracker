# Fabric is shitty so don't foget to run this with python 2

from __future__ import with_statement
from fabric.api import run, env, cd, put, lcd, local, settings
import time

env.user = "local-admin"
env.hosts = ["10.32.136.5"]


def package():
    with lcd(".."):
        local("mvn package")


def install_docker():
    run("wget -qO- https://get.docker.com/ | sh")
    run("sudo usermod -aG docker {}".format(env.user))


def deploy():
    # Fabric is extremely stupid and expands ~ locally, so it cannot be used on
    # the remote end.
    with cd("/home/{}/fb-tracker".format(env.user)):
        run("git pull")
        with cd("ops"):
            run("docker build -t fb-tracker/app .")
            run("docker build -t fb-tracker/pgsql postgres")
        # Run everything TODO: Probably don't just brutally end running
        # containers.
        with settings(warn_only=True):
            run("docker rm -f pgsql")
        run("docker run -d -P --name pgsql fb-tracker/pgsql")

        # Gotta wait a sec to give postgres a minute to finish starting.
        time.sleep(3)
        with settings(warn_only=True):
            run("docker rm -f fb-tracker-app")
        run("docker run -d -p 80:8080 -p 8081:8081 --link pgsql:pgsql --name "
            "fb-tracker-app tableau/cat")


def deploy_prod():
    deploy("cat-config.yml")

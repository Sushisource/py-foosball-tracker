Deploying
==============
Deployment is accomplished via docker. The only dependency is a postgres
server, which should be started as a docker container like so:

    docker run -p 5432:5432 --name postgres -e USER=foosball -e PASSWORD=foosball -e SCHEMA=fbdb -e ENCODING=UTF8 -d jamesbrink/postgres

Then build and deploy the Dockerfile for the app.

    docker build -t fbserver .
    docker run -p 5000:500 --name fbserver --link postgres:postgres fbserver

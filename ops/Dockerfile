FROM java:8

# TODO: Consider running as non-root user.
WORKDIR /srv/fb-tracker

EXPOSE 5000

COPY cat.jar /srv/cat/cat.jar
COPY cat-config.yml /srv/cat/cat-config.yml
CMD ["/usr/lib/jvm/java-8-openjdk-amd64/bin/java", "-jar", "cat.jar", "server", "cat-config.yml"]

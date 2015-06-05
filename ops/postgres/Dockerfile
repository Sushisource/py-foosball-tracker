FROM postgres:9.4

ENV DB_NAME fbdb
ENV DB_USER foosball
ENV DB_PASS foosball
ADD setup-remote-connections.sh /docker-entrypoint-initdb.d/
RUN chmod 755 /docker-entrypoint-initdb.d/setup-remote-connections.sh
ADD setup-database.sh /docker-entrypoint-initdb.d/
RUN chmod 755 /docker-entrypoint-initdb.d/setup-database.sh

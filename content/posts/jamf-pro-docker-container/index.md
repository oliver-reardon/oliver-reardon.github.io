---
title: Jamf Pro Docker Container
date: 2023-01-22T10:09:06-04:00
author: Oliver Reardon
tags: 
  - jamf
  - docker
  - dev-environment
keywords: 
  - jamf pro
  - docker
  - mysql
  - testing
description: Use Docker to quickly stand up a Jamf Pro testing environment with MySQL and custom configuration.
showFullContent: false
readingTime: true
hideComments: false
---

Setting up an additional Jamf Pro environment for development or testing can be time-consuming. Docker reduces this overhead and allows for fast and repeatable creation of a ready-to-use Jamf instance.

Full build guide – https://github.com/1sth1sth1ng0n/jamfpro_cont

---

The following Docker base image is used along with the latest Jamf Pro Java collection (`ROOT.war`):

- **Docker image**: [jamf/jamfpro on Docker Hub](https://hub.docker.com/r/jamf/jamfpro)
- **Java collection**: Available from a licensed Jamf Account – [Jamf Account](https://account.jamf.com/)

---

Once the new image is built, it can be run directly via `docker run`, or more ideally, managed with **Docker Compose**. Docker compose allows for a more structured approach where defining the database parameters and networks are more clear.

Additionally Jamf Pro does not support the latest MySQL version 8.x default authentication method. We need to change the default to `mysql_native_password` using a custom _my.cnf_ conf file which is mapped to the new MySQL container in `/etc/mysql/conf.d/my.cnf`.

```text
[mysqld] 
default-authentication-plugin=mysql_native_password
```

The following docker compose yaml file defines all the required components. This includes the Jamf Pro docker image previously created and a base MySQL image with the _my.cnf_ definition. This also creates a bridged network named _jamfnet_ which can be modified to accommodate various requirements. Also defined is our mapped host to container HTTPS and MySQL ports and a `depends_on` feature which ensures the MySQL container is up before the Jamf Pro container.

```yaml
version: "3"
services:
  mysql:
    image: "mysql:8.0.31"
    networks:
      - jamfnet
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: "jamfsw03"
      MYSQL_DATABASE: "jamfsoftware"
    volumes:
      - ./my.cnf:/etc/mysql/conf.d/my.cnf
  jamfpro:
    image: "jamfpro:10.42.1"
    networks:
      - jamfnet
    ports:
      - "8443:8080"
    environment:
      DATABASE_USERNAME: "root"
      DATABASE_PASSWORD: "jamfsw03"
      DATABASE_HOST: "mysql"
    depends_on:
      - mysql
networks:
  jamfnet:
```
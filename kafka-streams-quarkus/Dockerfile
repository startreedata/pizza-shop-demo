FROM maven:3.5-jdk-11 AS build
COPY src /usr/src/app/src
COPY pom.xml /usr/src/app
RUN mvn -f /usr/src/app/pom.xml clean package

CMD ["java", "-Dquarkus.http.host=0.0.0.0", "-cp", ".", "-jar", "/usr/src/app/target/quarkus-app/quarkus-run.jar"]

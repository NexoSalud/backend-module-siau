FROM maven:3.9.6-eclipse-temurin-17-alpine AS build
WORKDIR /app

# Cache de dependencias Maven
COPY pom.xml .
RUN mvn dependency:go-offline

# Compilación
ARG DEPLOY_VERSION=1
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
RUN apk add --no-cache wget curl
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8088
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8088/actuator/health || exit 1
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]

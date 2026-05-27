# --- Etapa 1: Construcción (Maven Build) ---
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build

# Copiar configuración del proyecto y dependencias
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copiar código fuente y empaquetar
COPY src ./src
RUN mvn package -DskipTests -B

# --- Etapa 2: Imagen de Ejecución (JRE) ---
FROM eclipse-temurin:17-jre
WORKDIR /app

# Crear usuario de sistema no-root para seguridad
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

# Copiar el empaquetado JAR desde la etapa anterior
COPY --from=builder /build/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]

package com.reactive.nexo.siau.initialize;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.r2dbc.core.DatabaseClient;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;

@Component
@Profile("!test")
public class SiauPermissionInitializer implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(SiauPermissionInitializer.class);

    private final DatabaseClient databaseClient;

    public SiauPermissionInitializer(DatabaseClient databaseClient) {
        this.databaseClient = databaseClient;
    }

    @Override
    public void run(String... args) {
        log.info("SiauPermissionInitializer - checking if SIAU permissions need to be seeded...");

        // Check if SIAU permissions already exist
        databaseClient.sql("SELECT COUNT(*) FROM permission WHERE endpoint LIKE '/api/v1/siau/%'")
                .fetch()
                .one()
                .flatMap(row -> {
                    long count = ((Number) row.getOrDefault("count", 0)).longValue();
                    if (count > 0) {
                        log.info("SiauPermissionInitializer - SIAU permissions already exist ({} found), skipping seed.", count);
                        return Mono.empty();
                    }
                    return seedPermissions();
                })
                .blockOptional();
    }

    private Mono<Void> seedPermissions() {
        log.info("SiauPermissionInitializer - seeding SIAU permissions...");

        // First ensure SIAU role exists
        return ensureSiauRole()
                .flatMap(rolId -> {
                    // Insert permissions for SIAU role
                    return insertPermission(rolId, "GET", "/api/v1/siau/dashboard")
                            .then(insertPermission(rolId, "GET", "/api/v1/siau/pqrsdf"))
                            .then(insertPermission(rolId, "GET", "/api/v1/siau/pqrsdf/*"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/pqrsdf"))
                            .then(insertPermission(rolId, "PATCH", "/api/v1/siau/pqrsdf/*"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/pqrsdf/*/responder"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/pqrsdf/*/cerrar"))
                            .then(insertPermission(rolId, "GET", "/api/v1/siau/pqrsdf/*/trazabilidad"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/asignaciones"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/asignaciones/*/responder"))
                            .then(insertPermission(rolId, "GET", "/api/v1/siau/departamentos"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/departamentos"))
                            .then(insertPermission(rolId, "PUT", "/api/v1/siau/departamentos/*"))
                            .then(insertPermission(rolId, "PATCH", "/api/v1/siau/departamentos/*/toggle"))
                            .then(insertPermission(rolId, "POST", "/api/v1/siau/actas-buzon"))
                            .then(insertPermission(rolId, "GET", "/api/v1/siau/actas-buzon"))

                            // Also insert permissions for ADMIN role (rol_id=1)
                            .then(insertPermission(1, "GET", "/api/v1/siau/dashboard"))
                            .then(insertPermission(1, "GET", "/api/v1/siau/pqrsdf"))
                            .then(insertPermission(1, "GET", "/api/v1/siau/pqrsdf/*"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/pqrsdf"))
                            .then(insertPermission(1, "PATCH", "/api/v1/siau/pqrsdf/*"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/pqrsdf/*/responder"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/pqrsdf/*/cerrar"))
                            .then(insertPermission(1, "GET", "/api/v1/siau/pqrsdf/*/trazabilidad"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/asignaciones"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/asignaciones/*/responder"))
                            .then(insertPermission(1, "GET", "/api/v1/siau/departamentos"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/departamentos"))
                            .then(insertPermission(1, "PUT", "/api/v1/siau/departamentos/*"))
                            .then(insertPermission(1, "PATCH", "/api/v1/siau/departamentos/*/toggle"))
                            .then(insertPermission(1, "POST", "/api/v1/siau/actas-buzon"))
                            .then(insertPermission(1, "GET", "/api/v1/siau/actas-buzon"))

                            .then(Mono.fromRunnable(() ->
                                    log.info("SiauPermissionInitializer - {} SIAU permissions seeded successfully (roles: SIAU, ADMIN)", 32)));
                });
    }

    private Mono<Integer> ensureSiauRole() {
        return databaseClient.sql("SELECT id FROM rol WHERE name = 'SIAU'")
                .fetch()
                .one()
                .flatMap(row -> {
                    if (row.containsKey("id") && row.get("id") != null) {
                        return Mono.just(((Number) row.get("id")).intValue());
                    }
                    // Create SIAU role (not asistencial)
                    return databaseClient.sql("INSERT INTO rol (name, asistencial) VALUES ('SIAU', false)")
                            .fetch()
                            .first()
                            .map(r -> ((Number) r.get("id")).intValue());
                })
                .switchIfEmpty(
                        databaseClient.sql("INSERT INTO rol (name, asistencial) VALUES ('SIAU', false)")
                                .fetch()
                                .first()
                                .map(r -> ((Number) r.get("id")).intValue())
                );
    }

    private Mono<Void> insertPermission(int rolId, String method, String endpoint) {
        return databaseClient.sql("INSERT INTO permission (rol_id, method, endpoint) VALUES ($1, $2, $3)")
                .bind("$1", rolId)
                .bind("$2", method)
                .bind("$3", endpoint)
                .fetch()
                .rowsUpdated()
                .then();
    }
}

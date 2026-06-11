package com.reactive.nexo.siau.repository;

import com.reactive.nexo.siau.entity.PqrsdfEntity;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDate;

@Repository
public interface PqrsdfRepository extends ReactiveCrudRepository<PqrsdfEntity, Long> {

    Mono<PqrsdfEntity> findByConsecutivo(String consecutivo);

    Flux<PqrsdfEntity> findByEstado(String estado);

    Flux<PqrsdfEntity> findByTipo(String tipo);

    Flux<PqrsdfEntity> findByNumeroDocumento(String numeroDocumento);

    Flux<PqrsdfEntity> findByFechaRadicadoBetween(LocalDate desde, LocalDate hasta);

    @Query("SELECT COUNT(*) FROM siau_pqrsdf")
    Mono<Long> countTotal();

    @Query("SELECT COUNT(*) FROM siau_pqrsdf WHERE estado = :estado")
    Mono<Long> countByEstado(String estado);

    @Query("SELECT COUNT(*) FROM siau_pqrsdf WHERE tipo = :tipo")
    Mono<Long> countByTipo(String tipo);

    @Query("SELECT COALESCE(MAX(id), 0) FROM siau_pqrsdf")
    Mono<Long> findMaxId();

    @Query("SELECT * FROM siau_pqrsdf ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    Flux<PqrsdfEntity> findAllPaged(int limit, long offset);
}

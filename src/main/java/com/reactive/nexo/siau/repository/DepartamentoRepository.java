package com.reactive.nexo.siau.repository;

import com.reactive.nexo.siau.entity.DepartamentoEntity;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Repository
public interface DepartamentoRepository extends ReactiveCrudRepository<DepartamentoEntity, Long> {

    Flux<DepartamentoEntity> findByActivoTrue();

    Mono<DepartamentoEntity> findByNombre(String nombre);

    @Query("SELECT COUNT(*) FROM siau_departamentos WHERE activo = true")
    Mono<Long> countActivos();
}

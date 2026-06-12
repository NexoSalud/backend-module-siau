package com.reactive.nexo.siau.repository;

import com.reactive.nexo.siau.entity.AsignacionEntity;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Repository
public interface AsignacionRepository extends ReactiveCrudRepository<AsignacionEntity, Long> {

    Flux<AsignacionEntity> findByPqrsdfId(Long pqrsdfId);

    Flux<AsignacionEntity> findByDepartamentoId(Long departamentoId);

    Flux<AsignacionEntity> findByEstado(String estado);

    Flux<AsignacionEntity> findByFuncionarioId(Long funcionarioId);

    @Query("SELECT COUNT(*) FROM siau_asignaciones WHERE estado = :estado")
    Mono<Long> countByEstado(String estado);

    @Query("SELECT COUNT(*) FROM siau_asignaciones WHERE departamento_id = :deptoId AND estado = :estado")
    Mono<Long> countByDepartamentoAndEstado(Long deptoId, String estado);

    @Query("SELECT COUNT(*) FROM siau_asignaciones WHERE departamento_id = :deptoId")
    Mono<Long> countByDepartamento(Long deptoId);

    @Query("SELECT * FROM siau_asignaciones WHERE pqrsdf_id = :pqrsdfId ORDER BY created_at DESC LIMIT 1")
    Mono<AsignacionEntity> findUltimaByPqrsdfId(Long pqrsdfId);
}

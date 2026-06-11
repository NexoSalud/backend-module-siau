package com.reactive.nexo.siau.repository;

import com.reactive.nexo.siau.entity.TrazabilidadEntity;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;

@Repository
public interface TrazabilidadRepository extends ReactiveCrudRepository<TrazabilidadEntity, Long> {

    Flux<TrazabilidadEntity> findByPqrsdfIdOrderByCreatedAtDesc(Long pqrsdfId);

    @Query("SELECT * FROM siau_trazabilidad WHERE pqrsdf_id = :pqrsdfId ORDER BY created_at DESC")
    Flux<TrazabilidadEntity> findHistorialByPqrsdfId(Long pqrsdfId);
}

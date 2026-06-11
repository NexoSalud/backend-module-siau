package com.reactive.nexo.siau.repository;

import com.reactive.nexo.siau.entity.ActaBuzonEntity;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import org.springframework.stereotype.Repository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDate;

@Repository
public interface ActaBuzonRepository extends ReactiveCrudRepository<ActaBuzonEntity, Long> {

    Flux<ActaBuzonEntity> findByFechaAperturaBetween(LocalDate desde, LocalDate hasta);

    @Query("SELECT COALESCE(SUM(total_pqrsdf), 0) FROM siau_actas_buzon WHERE fecha_apertura BETWEEN :desde AND :hasta")
    Mono<Long> sumTotalByFechaBetween(LocalDate desde, LocalDate hasta);
}

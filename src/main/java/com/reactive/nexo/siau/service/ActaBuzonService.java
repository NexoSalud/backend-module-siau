package com.reactive.nexo.siau.service;

import com.reactive.nexo.siau.dto.ActaBuzonRequest;
import com.reactive.nexo.siau.dto.ActaBuzonResponse;
import com.reactive.nexo.siau.entity.ActaBuzonEntity;
import com.reactive.nexo.siau.repository.ActaBuzonRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.scheduler.Schedulers;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class ActaBuzonService {

    private static final Logger log = LoggerFactory.getLogger(ActaBuzonService.class);

    private final ActaBuzonRepository repo;

    public ActaBuzonService(ActaBuzonRepository repo) {
        this.repo = repo;
    }

    public ActaBuzonResponse create(ActaBuzonRequest req, Long employeeId) {
        ActaBuzonEntity entity = ActaBuzonEntity.builder()
                .fechaApertura(req.getFechaApertura())
                .ubicacion(req.getUbicacion())
                .servicio(req.getServicio())
                .totalPqrsdf(req.getTotalPqrsdf())
                .detallePorTipo(req.getDetallePorTipo())
                .observaciones(req.getObservaciones())
                .createdAt(LocalDateTime.now())
                .createdBy(req.getCreatedBy() != null ? req.getCreatedBy() : employeeId)
                .build();

        ActaBuzonEntity saved = repo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        log.info("Acta de apertura de buzón creada: {} en {} ({} PQRSDF)",
                saved.getFechaApertura(), saved.getUbicacion(), saved.getTotalPqrsdf());

        return mapToResponse(saved);
    }

    public List<ActaBuzonResponse> findAll() {
        List<ActaBuzonEntity> list = repo.findAll()
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());

        list.sort((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()));

        List<ActaBuzonResponse> result = new ArrayList<>();
        for (ActaBuzonEntity e : list) result.add(mapToResponse(e));
        return result;
    }

    public Optional<ActaBuzonResponse> findById(Long id) {
        ActaBuzonEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        return Optional.ofNullable(entity).map(this::mapToResponse);
    }

    private ActaBuzonResponse mapToResponse(ActaBuzonEntity e) {
        return ActaBuzonResponse.builder()
                .id(e.getId())
                .fechaApertura(e.getFechaApertura())
                .ubicacion(e.getUbicacion())
                .servicio(e.getServicio())
                .totalPqrsdf(e.getTotalPqrsdf())
                .detallePorTipo(e.getDetallePorTipo())
                .observaciones(e.getObservaciones())
                .createdAt(e.getCreatedAt())
                .createdBy(e.getCreatedBy())
                .build();
    }
}

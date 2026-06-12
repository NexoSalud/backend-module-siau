package com.reactive.nexo.siau.service;

import com.reactive.nexo.siau.dto.CreateDepartamentoRequest;
import com.reactive.nexo.siau.dto.DepartamentoResponse;
import com.reactive.nexo.siau.entity.DepartamentoEntity;
import com.reactive.nexo.siau.repository.AsignacionRepository;
import com.reactive.nexo.siau.repository.DepartamentoRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.scheduler.Schedulers;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class DepartamentoService {

    private static final Logger log = LoggerFactory.getLogger(DepartamentoService.class);

    private final DepartamentoRepository repo;
    private final AsignacionRepository asignacionRepo;

    public DepartamentoService(DepartamentoRepository repo, AsignacionRepository asignacionRepo) {
        this.repo = repo;
        this.asignacionRepo = asignacionRepo;
    }

    public DepartamentoResponse create(CreateDepartamentoRequest req) {
        DepartamentoEntity entity = DepartamentoEntity.builder()
                .nombre(req.getNombre())
                .descripcion(req.getDescripcion())
                .responsable(req.getResponsable())
                .responsableId(req.getResponsableId())
                .activo(true)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        DepartamentoEntity saved = repo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        log.info("Departamento creado: {} (ID: {})", saved.getNombre(), saved.getId());
        return mapToResponse(saved, 0L);
    }

    public Optional<DepartamentoResponse> findById(Long id) {
        DepartamentoEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return Optional.empty();

        Long pendientes = asignacionRepo.countByDepartamentoAndEstado(id, "PENDIENTE")
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(0L);

        return Optional.of(mapToResponse(entity, pendientes));
    }

    public List<DepartamentoResponse> findAll() {
        List<DepartamentoEntity> list = repo.findAll()
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());

        List<DepartamentoResponse> result = new ArrayList<>();
        for (DepartamentoEntity e : list) {
            Long pendientes = asignacionRepo.countByDepartamentoAndEstado(e.getId(), "PENDIENTE")
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(0L);
            result.add(mapToResponse(e, pendientes));
        }
        return result;
    }

    public List<DepartamentoResponse> findActivos() {
        List<DepartamentoEntity> list = repo.findByActivoTrue()
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());

        List<DepartamentoResponse> result = new ArrayList<>();
        for (DepartamentoEntity e : list) {
            Long pendientes = asignacionRepo.countByDepartamentoAndEstado(e.getId(), "PENDIENTE")
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(0L);
            result.add(mapToResponse(e, pendientes));
        }
        return result;
    }

    public DepartamentoResponse update(Long id, CreateDepartamentoRequest req) {
        DepartamentoEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return null;

        if (req.getNombre() != null) entity.setNombre(req.getNombre());
        if (req.getDescripcion() != null) entity.setDescripcion(req.getDescripcion());
        if (req.getResponsable() != null) entity.setResponsable(req.getResponsable());
        if (req.getResponsableId() != null) entity.setResponsableId(req.getResponsableId());
        entity.setUpdatedAt(LocalDateTime.now());

        DepartamentoEntity saved = repo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        Long pendientes = asignacionRepo.countByDepartamentoAndEstado(id, "PENDIENTE")
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(0L);

        return mapToResponse(saved, pendientes);
    }

    public boolean toggleActivo(Long id) {
        DepartamentoEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return false;

        entity.setActivo(!Boolean.TRUE.equals(entity.getActivo()));
        entity.setUpdatedAt(LocalDateTime.now());
        repo.save(entity).subscribeOn(Schedulers.boundedElastic()).block();
        return true;
    }

    public boolean delete(Long id) {
        DepartamentoEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return false;

        // Primero verificar si tiene asignaciones
        Long asignaciones = asignacionRepo.countByDepartamento(id)
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(0L);

        if (asignaciones > 0) {
            log.warn("No se puede eliminar departamento {} porque tiene {} asignaciones activas", id, asignaciones);
            return false;
        }

        repo.deleteById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        log.info("Departamento eliminado: ID {}", id);
        return true;
    }

    private DepartamentoResponse mapToResponse(DepartamentoEntity e, Long pendientes) {
        return DepartamentoResponse.builder()
                .id(e.getId())
                .nombre(e.getNombre())
                .descripcion(e.getDescripcion())
                .responsable(e.getResponsable())
                .responsableId(e.getResponsableId())
                .activo(e.getActivo())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .pqrsdfPendientes(pendientes)
                .build();
    }
}

package com.reactive.nexo.siau.service;

import com.reactive.nexo.siau.dto.*;
import com.reactive.nexo.siau.entity.*;
import com.reactive.nexo.siau.model.*;
import com.reactive.nexo.siau.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.scheduler.Schedulers;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class PqrsdfService {

    private static final Logger log = LoggerFactory.getLogger(PqrsdfService.class);

    private final PqrsdfRepository pqrsdfRepo;
    private final AsignacionRepository asignacionRepo;
    private final TrazabilidadRepository trazabilidadRepo;
    private final DepartamentoRepository departamentoRepo;

    public PqrsdfService(PqrsdfRepository pqrsdfRepo,
                         AsignacionRepository asignacionRepo,
                         TrazabilidadRepository trazabilidadRepo,
                         DepartamentoRepository departamentoRepo) {
        this.pqrsdfRepo = pqrsdfRepo;
        this.asignacionRepo = asignacionRepo;
        this.trazabilidadRepo = trazabilidadRepo;
        this.departamentoRepo = departamentoRepo;
    }

    public PqrsdfResponse create(CreatePqrsdfRequest req, Long employeeId) {
        // Generar consecutivo automático
        Long maxId = pqrsdfRepo.findMaxId()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(0L);
        String consecutivo = generarConsecutivo(maxId + 1, req.getTipo());

        LocalDate hoy = LocalDate.now();
        String hora = req.getHoraRadicado() != null ? req.getHoraRadicado()
                : LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm"));

        PqrsdfEntity entity = PqrsdfEntity.builder()
                .consecutivo(consecutivo)
                .tipo(req.getTipo())
                .fechaRadicado(req.getFechaRadicado() != null ? req.getFechaRadicado() : hoy)
                .horaRadicado(hora)
                .nombresUsuario(req.getNombresUsuario())
                .tipoDocumento(req.getTipoDocumento())
                .numeroDocumento(req.getNumeroDocumento())
                .telefono(req.getTelefono())
                .email(req.getEmail())
                .direccion(req.getDireccion())
                .eps(req.getEps())
                .regimen(req.getRegimen())
                .medioRecepcion(req.getMedioRecepcion())
                .servicioInvolucrado(req.getServicioInvolucrado())
                .funcionarioInvolucrado(req.getFuncionarioInvolucrado())
                .descripcion(req.getDescripcion())
                .clasificacion(req.getClasificacion())
                .estado(EstadoPqrsdf.RECIBIDO.getValue())
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .createdBy(req.getCreatedBy() != null ? req.getCreatedBy() : employeeId)
                .actaBuzonId(req.getActaBuzonId())
                .build();

        PqrsdfEntity saved = pqrsdfRepo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        // Registrar trazabilidad
        registrarTrazabilidad(saved.getId(), "CREACION",
                "PQRSDF " + consecutivo + " creada - Tipo: " + req.getTipo(),
                employeeId, null);

        log.info("PQRSDF {} creada: {}", consecutivo, saved.getId());
        return mapToResponse(saved, null, null, 0);
    }

    public Optional<PqrsdfResponse> findById(Long id) {
        PqrsdfEntity entity = pqrsdfRepo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return Optional.empty();

        // Obtener última asignación si existe
        AsignacionEntity ultimaAsignacion = asignacionRepo.findUltimaByPqrsdfId(id)
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(null);

        String deptoNombre = null;
        String estadoAsig = null;
        if (ultimaAsignacion != null) {
            estadoAsig = ultimaAsignacion.getEstado();
            DepartamentoEntity depto = departamentoRepo.findById(ultimaAsignacion.getDepartamentoId())
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(null);
            if (depto != null) deptoNombre = depto.getNombre();
        }

        int diasTranscurridos = (int) ChronoUnit.DAYS.between(entity.getFechaRadicado(), LocalDate.now());
        return Optional.of(mapToResponse(entity, deptoNombre, estadoAsig, diasTranscurridos));
    }

    public List<PqrsdfResponse> search(Map<String, String> filters, int page, int size) {
        List<PqrsdfEntity> all = pqrsdfRepo.findAll()
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());

        // Aplicar filtros en memoria (por simplicidad, igual que el patrón de appointments)
        if (filters.containsKey("estado")) {
            String est = filters.get("estado");
            all = all.stream().filter(e -> e.getEstado().equalsIgnoreCase(est)).collect(Collectors.toList());
        }
        if (filters.containsKey("tipo")) {
            String tip = filters.get("tipo");
            all = all.stream().filter(e -> e.getTipo().equalsIgnoreCase(tip)).collect(Collectors.toList());
        }
        if (filters.containsKey("numeroDocumento")) {
            String doc = filters.get("numeroDocumento");
            all = all.stream().filter(e -> doc.equals(e.getNumeroDocumento())).collect(Collectors.toList());
        }
        if (filters.containsKey("fechaDesde")) {
            LocalDate desde = LocalDate.parse(filters.get("fechaDesde"));
            all = all.stream().filter(e -> !e.getFechaRadicado().isBefore(desde)).collect(Collectors.toList());
        }
        if (filters.containsKey("fechaHasta")) {
            LocalDate hasta = LocalDate.parse(filters.get("fechaHasta"));
            all = all.stream().filter(e -> !e.getFechaRadicado().isAfter(hasta)).collect(Collectors.toList());
        }

        // Ordenar por fecha descendente
        all.sort((a, b) -> b.getCreatedAt().compareTo(a.getCreatedAt()));

        int from = Math.min(page * size, all.size());
        int to = Math.min(from + size, all.size());
        List<PqrsdfEntity> pageList = all.subList(from, to);

        List<PqrsdfResponse> result = new ArrayList<>();
        for (PqrsdfEntity e : pageList) {
            int dias = (int) ChronoUnit.DAYS.between(e.getFechaRadicado(), LocalDate.now());
            result.add(mapToResponse(e, null, null, dias));
        }
        return result;
    }

    public long count(Map<String, String> filters) {
        if (filters.isEmpty()) {
            return pqrsdfRepo.countTotal()
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(0L);
        }
        // Si hay filtros, contar desde la lista completa
        List<PqrsdfEntity> all = pqrsdfRepo.findAll()
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());
        return all.size();
    }

    public PqrsdfResponse update(Long id, UpdatePqrsdfRequest req, Long employeeId) {
        PqrsdfEntity entity = pqrsdfRepo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return null;

        if (req.getClasificacion() != null) entity.setClasificacion(req.getClasificacion());
        if (req.getObservaciones() != null) entity.setObservaciones(req.getObservaciones());
        entity.setUpdatedAt(LocalDateTime.now());
        entity.setUpdatedBy(req.getUpdatedBy() != null ? req.getUpdatedBy() : employeeId);

        PqrsdfEntity saved = pqrsdfRepo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        registrarTrazabilidad(id, "ACTUALIZACION",
                "PQRSDF " + entity.getConsecutivo() + " actualizada",
                employeeId, null);

        return mapToResponse(saved, null, null, 0);
    }

    public PqrsdfResponse responder(Long id, ResponderPqrsdfRequest req, Long employeeId) {
        PqrsdfEntity entity = pqrsdfRepo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return null;

        entity.setRespuestaFinal(req.getRespuestaFinal());
        entity.setMedioRespuesta(req.getMedioRespuesta());
        entity.setFechaRespuesta(LocalDate.now());
        entity.setEstado(EstadoPqrsdf.RESPONDIDO.getValue());
        if (req.getClasificacion() != null) entity.setClasificacion(req.getClasificacion());
        entity.setUpdatedAt(LocalDateTime.now());
        entity.setUpdatedBy(req.getUpdatedBy() != null ? req.getUpdatedBy() : employeeId);

        PqrsdfEntity saved = pqrsdfRepo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        // Actualizar asignaciones relacionadas
        List<AsignacionEntity> asignaciones = asignacionRepo.findByPqrsdfId(id)
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());
        for (AsignacionEntity asig : asignaciones) {
            if (!"RESPONDIDA".equals(asig.getEstado())) {
                asig.setEstado("RESPONDIDA");
                asig.setFechaRespuestaArea(LocalDateTime.now());
                asig.setUpdatedAt(LocalDateTime.now());
                asignacionRepo.save(asig)
                        .subscribeOn(Schedulers.boundedElastic())
                        .block();
            }
        }

        registrarTrazabilidad(id, "RESPUESTA",
                "PQRSDF " + entity.getConsecutivo() + " respondida - Medio: " + req.getMedioRespuesta(),
                employeeId, null);

        return mapToResponse(saved, null, null, 0);
    }

    public PqrsdfResponse cerrar(Long id, Long employeeId) {
        PqrsdfEntity entity = pqrsdfRepo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return null;

        entity.setEstado(EstadoPqrsdf.CERRADO.getValue());
        entity.setUpdatedAt(LocalDateTime.now());
        entity.setUpdatedBy(employeeId);

        PqrsdfEntity saved = pqrsdfRepo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        registrarTrazabilidad(id, "CIERRE",
                "PQRSDF " + entity.getConsecutivo() + " cerrada",
                employeeId, null);

        return mapToResponse(saved, null, null, 0);
    }

    public List<TrazabilidadResponse> getTrazabilidad(Long pqrsdfId) {
        List<TrazabilidadEntity> list = trazabilidadRepo.findHistorialByPqrsdfId(pqrsdfId)
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());
        List<TrazabilidadResponse> result = new ArrayList<>();
        for (TrazabilidadEntity te : list) {
            result.add(mapTrazabilidad(te));
        }
        return result;
    }

    // --- Métodos auxiliares ---

    private String generarConsecutivo(Long id, String tipo) {
        String anio = String.valueOf(LocalDate.now().getYear());
        return String.format("PQRS-%s-%s-%04d", tipo.toUpperCase(), anio, id);
    }

    private void registrarTrazabilidad(Long pqrsdfId, String accion, String descripcion,
                                       Long usuarioId, String metadataJson) {
        TrazabilidadEntity entity = TrazabilidadEntity.builder()
                .pqrsdfId(pqrsdfId)
                .accion(accion)
                .descripcion(descripcion)
                .usuarioId(usuarioId)
                .createdAt(LocalDateTime.now())
                .metadataJson(metadataJson)
                .build();
        trazabilidadRepo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .subscribe();
    }

    private PqrsdfResponse mapToResponse(PqrsdfEntity e, String ultimoDepto,
                                          String ultimoEstadoAsig, int diasTranscurridos) {
        TipoPqrsdf tipo = TipoPqrsdf.fromCodigo(e.getTipo());
        return PqrsdfResponse.builder()
                .id(e.getId())
                .consecutivo(e.getConsecutivo())
                .tipo(e.getTipo())
                .tipoNombre(tipo.getNombre())
                .fechaRadicado(e.getFechaRadicado())
                .horaRadicado(e.getHoraRadicado())
                .nombresUsuario(e.getNombresUsuario())
                .tipoDocumento(e.getTipoDocumento())
                .numeroDocumento(e.getNumeroDocumento())
                .telefono(e.getTelefono())
                .email(e.getEmail())
                .direccion(e.getDireccion())
                .eps(e.getEps())
                .regimen(e.getRegimen())
                .medioRecepcion(e.getMedioRecepcion())
                .servicioInvolucrado(e.getServicioInvolucrado())
                .funcionarioInvolucrado(e.getFuncionarioInvolucrado())
                .descripcion(e.getDescripcion())
                .clasificacion(e.getClasificacion())
                .estado(e.getEstado())
                .fechaRespuesta(e.getFechaRespuesta())
                .medioRespuesta(e.getMedioRespuesta())
                .respuestaFinal(e.getRespuestaFinal())
                .observaciones(e.getObservaciones())
                .createdAt(e.getCreatedAt())
                .updatedAt(e.getUpdatedAt())
                .createdBy(e.getCreatedBy())
                .updatedBy(e.getUpdatedBy())
                .ultimoDepartamentoAsignado(ultimoDepto)
                .ultimoEstadoAsignacion(ultimoEstadoAsig)
                .diasTranscurridos(diasTranscurridos)
                .build();
    }

    private TrazabilidadResponse mapTrazabilidad(TrazabilidadEntity te) {
        return TrazabilidadResponse.builder()
                .id(te.getId())
                .pqrsdfId(te.getPqrsdfId())
                .accion(te.getAccion())
                .descripcion(te.getDescripcion())
                .usuarioId(te.getUsuarioId())
                .usuarioNombre(te.getUsuarioNombre())
                .metadataJson(te.getMetadataJson())
                .createdAt(te.getCreatedAt())
                .build();
    }
}

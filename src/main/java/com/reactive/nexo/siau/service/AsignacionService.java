package com.reactive.nexo.siau.service;

import com.reactive.nexo.siau.dto.AsignacionResponse;
import com.reactive.nexo.siau.dto.CreateAsignacionRequest;
import com.reactive.nexo.siau.dto.DashboardStatsResponse;
import com.reactive.nexo.siau.entity.AsignacionEntity;
import com.reactive.nexo.siau.entity.DepartamentoEntity;
import com.reactive.nexo.siau.entity.PqrsdfEntity;
import com.reactive.nexo.siau.model.EstadoAsignacion;
import com.reactive.nexo.siau.model.EstadoPqrsdf;
import com.reactive.nexo.siau.repository.AsignacionRepository;
import com.reactive.nexo.siau.repository.DepartamentoRepository;
import com.reactive.nexo.siau.repository.PqrsdfRepository;
import com.reactive.nexo.siau.repository.TrazabilidadRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.scheduler.Schedulers;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

@Service
public class AsignacionService {

    private static final Logger log = LoggerFactory.getLogger(AsignacionService.class);

    private final AsignacionRepository repo;
    private final PqrsdfRepository pqrsdfRepo;
    private final DepartamentoRepository departamentoRepo;
    private final TrazabilidadRepository trazabilidadRepo;
    private final PqrsdfService pqrsdfService;

    public AsignacionService(AsignacionRepository repo,
                             PqrsdfRepository pqrsdfRepo,
                             DepartamentoRepository departamentoRepo,
                             TrazabilidadRepository trazabilidadRepo,
                             PqrsdfService pqrsdfService) {
        this.repo = repo;
        this.pqrsdfRepo = pqrsdfRepo;
        this.departamentoRepo = departamentoRepo;
        this.trazabilidadRepo = trazabilidadRepo;
        this.pqrsdfService = pqrsdfService;
    }

    public AsignacionResponse create(CreateAsignacionRequest req, Long employeeId) {
        // Validar que la PQRSDF existe
        PqrsdfEntity pqrsdf = pqrsdfRepo.findById(req.getPqrsdfId())
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (pqrsdf == null) {
            throw new IllegalArgumentException("PQRSDF con ID " + req.getPqrsdfId() + " no encontrada");
        }

        // Validar que el departamento existe
        DepartamentoEntity depto = departamentoRepo.findById(req.getDepartamentoId())
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (depto == null) {
            throw new IllegalArgumentException("Departamento con ID " + req.getDepartamentoId() + " no encontrado");
        }

        // Calcular fecha límite por defecto (15 días hábiles si no se especifica)
        LocalDate fechaLimite = req.getFechaLimiteRespuesta() != null
                ? req.getFechaLimiteRespuesta()
                : calcularFechaLimite(LocalDate.now(), 15);

        AsignacionEntity entity = AsignacionEntity.builder()
                .pqrsdfId(req.getPqrsdfId())
                .departamentoId(req.getDepartamentoId())
                .funcionarioId(req.getFuncionarioId())
                .funcionarioNombre(req.getFuncionarioNombre())
                .fechaAsignacion(LocalDateTime.now())
                .fechaLimiteRespuesta(fechaLimite)
                .estado(EstadoAsignacion.PENDIENTE.getValue())
                .observaciones(req.getObservaciones())
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        AsignacionEntity saved = repo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        // Actualizar estado de la PQRSDF a ASIGNADO
        pqrsdf.setEstado(EstadoPqrsdf.ASIGNADO.getValue());
        pqrsdf.setUpdatedAt(LocalDateTime.now());
        pqrsdfRepo.save(pqrsdf)
                .subscribeOn(Schedulers.boundedElastic())
                .subscribe();

        // Registrar trazabilidad
        pqrsdfService.getTrazabilidad(req.getPqrsdfId()); // Ensure method access - actually we call repo directly
        registrarTrazabilidadInterna(req.getPqrsdfId(), "ASIGNACION",
                "Asignada a: " + depto.getNombre() + " - Fecha límite: " + fechaLimite,
                employeeId, null);

        log.info("Asignación creada: PQRSDF {} → Departamento {} (ID: {})",
                pqrsdf.getConsecutivo(), depto.getNombre(), saved.getId());

        return mapToResponse(saved, pqrsdf.getConsecutivo(), depto.getNombre());
    }

    public Optional<AsignacionResponse> findById(Long id) {
        AsignacionEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return Optional.empty();

        PqrsdfEntity pqrsdf = pqrsdfRepo.findById(entity.getPqrsdfId())
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(null);
        DepartamentoEntity depto = departamentoRepo.findById(entity.getDepartamentoId())
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(null);

        return Optional.of(mapToResponse(entity,
                pqrsdf != null ? pqrsdf.getConsecutivo() : null,
                depto != null ? depto.getNombre() : null));
    }

    public List<AsignacionResponse> findByPqrsdfId(Long pqrsdfId) {
        List<AsignacionEntity> list = repo.findByPqrsdfId(pqrsdfId)
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());

        List<AsignacionResponse> result = new ArrayList<>();
        for (AsignacionEntity e : list) {
            PqrsdfEntity p = pqrsdfRepo.findById(e.getPqrsdfId())
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(null);
            DepartamentoEntity d = departamentoRepo.findById(e.getDepartamentoId())
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(null);
            result.add(mapToResponse(e,
                    p != null ? p.getConsecutivo() : null,
                    d != null ? d.getNombre() : null));
        }
        return result;
    }

    public List<AsignacionResponse> findByDepartamentoId(Long departamentoId) {
        List<AsignacionEntity> list = repo.findByDepartamentoId(departamentoId)
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());

        List<AsignacionResponse> result = new ArrayList<>();
        for (AsignacionEntity e : list) {
            PqrsdfEntity p = pqrsdfRepo.findById(e.getPqrsdfId())
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(null);
            DepartamentoEntity d = departamentoRepo.findById(e.getDepartamentoId())
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(null);
            result.add(mapToResponse(e,
                    p != null ? p.getConsecutivo() : null,
                    d != null ? d.getNombre() : null));
        }
        return result;
    }

    public AsignacionResponse responderAsignacion(Long id, String respuesta, Long employeeId) {
        AsignacionEntity entity = repo.findById(id)
                .subscribeOn(Schedulers.boundedElastic())
                .block();
        if (entity == null) return null;

        entity.setRespuestaArea(respuesta);
        entity.setEstado(EstadoAsignacion.RESPONDIDA.getValue());
        entity.setFechaRespuestaArea(LocalDateTime.now());
        entity.setUpdatedAt(LocalDateTime.now());

        AsignacionEntity saved = repo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .block();

        PqrsdfEntity pqrsdf = pqrsdfRepo.findById(entity.getPqrsdfId())
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(null);
        DepartamentoEntity depto = departamentoRepo.findById(entity.getDepartamentoId())
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(null);

        String consecutivo = pqrsdf != null ? pqrsdf.getConsecutivo() : null;
        String deptoNombre = depto != null ? depto.getNombre() : null;

        registrarTrazabilidadInterna(entity.getPqrsdfId(), "RESPUESTA_AREA",
                "Departamento " + deptoNombre + " respondió asignación",
                employeeId, null);

        log.info("Asignación {} respondida por departamento {}", id, deptoNombre);
        return mapToResponse(saved, consecutivo, deptoNombre);
    }

    public DashboardStatsResponse getDashboardStats() {
        LocalDate hoy = LocalDate.now();
        LocalDate hace30dias = hoy.minusDays(30);

        long total = pqrsdfService.count(new HashMap<>());
        long pendientes = pqrsdfRepo.countByEstado("RECIBIDO")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long enGestion = pqrsdfRepo.countByEstado("ASIGNADO")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long enGestion2 = pqrsdfRepo.countByEstado("EN_GESTION")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long respondidas = pqrsdfRepo.countByEstado("RESPONDIDO")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long cerradas = pqrsdfRepo.countByEstado("CERRADO")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);

        long asignacionesVencidas = repo.countByEstado("VENCIDA")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);

        long porTipoP = pqrsdfRepo.countByTipo("P")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long porTipoQ = pqrsdfRepo.countByTipo("Q")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long porTipoR = pqrsdfRepo.countByTipo("R")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long porTipoS = pqrsdfRepo.countByTipo("S")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long porTipoD = pqrsdfRepo.countByTipo("D")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        long porTipoF = pqrsdfRepo.countByTipo("F")
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);

        Map<String, Long> porTipo = new LinkedHashMap<>();
        porTipo.put("PETICION", porTipoP);
        porTipo.put("QUEJA", porTipoQ);
        porTipo.put("RECLAMO", porTipoR);
        porTipo.put("SUGERENCIA", porTipoS);
        porTipo.put("DENUNCIA", porTipoD);
        porTipo.put("FELICITACION", porTipoF);

        // Stats por departamento
        List<DepartamentoEntity> deptos = departamentoRepo.findAll()
                .collectList()
                .subscribeOn(Schedulers.boundedElastic())
                .blockOptional().orElse(Collections.emptyList());
        Map<String, Long> porDepartamento = new LinkedHashMap<>();
        for (DepartamentoEntity d : deptos) {
            Long count = repo.countByDepartamentoAndEstado(d.getId(), "PENDIENTE")
                    .subscribeOn(Schedulers.boundedElastic())
                    .blockOptional().orElse(0L);
            if (count > 0) porDepartamento.put(d.getNombre(), count);
        }

        // Últimos 30 días
        long ultimos30 = pqrsdfRepo.countTotal()
                .subscribeOn(Schedulers.boundedElastic()).blockOptional().orElse(0L);
        Map<String, Long> ultimos30Map = new HashMap<>();
        ultimos30Map.put("total30dias", ultimos30 > 0 ? ultimos30 : 0);

        return DashboardStatsResponse.builder()
                .totalPqrsdf(total)
                .pendientes(pendientes + enGestion + enGestion2)
                .enGestion(enGestion + enGestion2)
                .respondidas(respondidas)
                .cerradas(cerradas)
                .vencidas(asignacionesVencidas)
                .porTipo(porTipo)
                .porDepartamento(porDepartamento)
                .ultimos30Dias(ultimos30Map)
                .build();
    }

    // --- Métodos auxiliares ---

    private void registrarTrazabilidadInterna(Long pqrsdfId, String accion, String descripcion,
                                               Long usuarioId, String metadata) {
        com.reactive.nexo.siau.entity.TrazabilidadEntity entity =
                com.reactive.nexo.siau.entity.TrazabilidadEntity.builder()
                        .pqrsdfId(pqrsdfId)
                        .accion(accion)
                        .descripcion(descripcion)
                        .usuarioId(usuarioId)
                        .createdAt(LocalDateTime.now())
                        .build();
        trazabilidadRepo.save(entity)
                .subscribeOn(Schedulers.boundedElastic())
                .subscribe();
    }

    private AsignacionResponse mapToResponse(AsignacionEntity e, String consecutivo, String deptoNombre) {
        boolean vencida = e.getFechaLimiteRespuesta() != null
                && e.getFechaLimiteRespuesta().isBefore(LocalDate.now())
                && !"RESPONDIDA".equals(e.getEstado());

        int diasRestantes = e.getFechaLimiteRespuesta() != null
                ? (int) ChronoUnit.DAYS.between(LocalDate.now(), e.getFechaLimiteRespuesta())
                : 0;

        return AsignacionResponse.builder()
                .id(e.getId())
                .pqrsdfId(e.getPqrsdfId())
                .pqrsdfConsecutivo(consecutivo)
                .departamentoId(e.getDepartamentoId())
                .departamentoNombre(deptoNombre)
                .funcionarioId(e.getFuncionarioId())
                .funcionarioNombre(e.getFuncionarioNombre())
                .fechaAsignacion(e.getFechaAsignacion())
                .fechaLimiteRespuesta(e.getFechaLimiteRespuesta())
                .estado(e.getEstado())
                .respuestaArea(e.getRespuestaArea())
                .observaciones(e.getObservaciones())
                .fechaRespuestaArea(e.getFechaRespuestaArea())
                .createdAt(e.getCreatedAt())
                .vencida(vencida)
                .diasRestantes(diasRestantes)
                .build();
    }

    /**
     * Calcula una fecha límite sumando días hábiles (sin contar sábados ni domingos).
     */
    private LocalDate calcularFechaLimite(LocalDate desde, int diasHabiles) {
        LocalDate result = desde;
        int agregados = 0;
        while (agregados < diasHabiles) {
            result = result.plusDays(1);
            if (result.getDayOfWeek() != DayOfWeek.SATURDAY && result.getDayOfWeek() != DayOfWeek.SUNDAY) {
                agregados++;
            }
        }
        return result;
    }
}

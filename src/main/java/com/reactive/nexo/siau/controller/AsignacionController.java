package com.reactive.nexo.siau.controller;

import com.reactive.nexo.siau.dto.AsignacionResponse;
import com.reactive.nexo.siau.dto.CreateAsignacionRequest;
import com.reactive.nexo.siau.dto.DashboardStatsResponse;
import com.reactive.nexo.siau.service.AsignacionService;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping(path = "/api/v1/siau", produces = MediaType.APPLICATION_JSON_VALUE)
public class AsignacionController {

    private final AsignacionService service;

    public AsignacionController(AsignacionService service) {
        this.service = service;
    }

    @PostMapping("/asignaciones")
    public Mono<ResponseEntity<AsignacionResponse>> create(
            @Valid @RequestBody CreateAsignacionRequest req,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        return Mono.fromCallable(() -> service.create(req, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(ResponseEntity::ok);
    }

    @GetMapping("/asignaciones/{id}")
    public Mono<ResponseEntity<AsignacionResponse>> get(@PathVariable("id") Long id) {
        return Mono.fromCallable(() -> service.findById(id))
                .subscribeOn(Schedulers.boundedElastic())
                .map(resp -> resp.map(ResponseEntity::ok)
                        .orElseGet(() -> ResponseEntity.notFound().build()));
    }

    @GetMapping("/pqrsdf/{pqrsdfId}/asignaciones")
    public Mono<ResponseEntity<List<AsignacionResponse>>> listByPqrsdf(@PathVariable("pqrsdfId") Long pqrsdfId) {
        return Mono.fromCallable(() -> ResponseEntity.ok(service.findByPqrsdfId(pqrsdfId)))
                .subscribeOn(Schedulers.boundedElastic());
    }

    @GetMapping("/departamentos/{deptoId}/asignaciones")
    public Mono<ResponseEntity<List<AsignacionResponse>>> listByDepartamento(@PathVariable("deptoId") Long deptoId) {
        return Mono.fromCallable(() -> ResponseEntity.ok(service.findByDepartamentoId(deptoId)))
                .subscribeOn(Schedulers.boundedElastic());
    }

    @PostMapping("/asignaciones/{id}/responder")
    public Mono<ResponseEntity<AsignacionResponse>> responder(
            @PathVariable("id") Long id,
            @RequestBody Map<String, String> body,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        String respuesta = body.getOrDefault("respuesta", "");
        return Mono.fromCallable(() -> service.responderAsignacion(id, respuesta, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(r -> r == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(r));
    }

    @GetMapping("/dashboard")
    public Mono<ResponseEntity<DashboardStatsResponse>> dashboard() {
        return Mono.fromCallable(() -> ResponseEntity.ok(service.getDashboardStats()))
                .subscribeOn(Schedulers.boundedElastic());
    }
}

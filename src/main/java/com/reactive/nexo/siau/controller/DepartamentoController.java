package com.reactive.nexo.siau.controller;

import com.reactive.nexo.siau.dto.CreateDepartamentoRequest;
import com.reactive.nexo.siau.dto.DepartamentoResponse;
import com.reactive.nexo.siau.service.DepartamentoService;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.List;

@RestController
@RequestMapping(path = "/api/v1/siau/departamentos", produces = MediaType.APPLICATION_JSON_VALUE)
public class DepartamentoController {

    private final DepartamentoService service;

    public DepartamentoController(DepartamentoService service) {
        this.service = service;
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    public Mono<ResponseEntity<DepartamentoResponse>> create(@Valid @RequestBody CreateDepartamentoRequest req) {
        return Mono.fromCallable(() -> service.create(req))
                .subscribeOn(Schedulers.boundedElastic())
                .map(ResponseEntity::ok);
    }

    @GetMapping
    public Mono<ResponseEntity<List<DepartamentoResponse>>> list() {
        return Mono.fromCallable(() -> ResponseEntity.ok(service.findAll()))
                .subscribeOn(Schedulers.boundedElastic());
    }

    @GetMapping("/activos")
    public Mono<ResponseEntity<List<DepartamentoResponse>>> listActivos() {
        return Mono.fromCallable(() -> ResponseEntity.ok(service.findActivos()))
                .subscribeOn(Schedulers.boundedElastic());
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<DepartamentoResponse>> get(@PathVariable("id") Long id) {
        return Mono.fromCallable(() -> service.findById(id))
                .subscribeOn(Schedulers.boundedElastic())
                .map(resp -> resp.map(ResponseEntity::ok)
                        .orElseGet(() -> ResponseEntity.notFound().build()));
    }

    @PutMapping("/{id}")
    public Mono<ResponseEntity<DepartamentoResponse>> update(
            @PathVariable("id") Long id,
            @Valid @RequestBody CreateDepartamentoRequest req) {
        return Mono.fromCallable(() -> service.update(id, req))
                .subscribeOn(Schedulers.boundedElastic())
                .map(updated -> updated == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(updated));
    }

    @PatchMapping("/{id}/toggle")
    public Mono<ResponseEntity<Void>> toggleActivo(@PathVariable("id") Long id) {
        return Mono.fromCallable(() -> {
            boolean ok = service.toggleActivo(id);
            return ok ? ResponseEntity.noContent().build() : ResponseEntity.notFound().<Void>build();
        }).subscribeOn(Schedulers.boundedElastic());
    }
}

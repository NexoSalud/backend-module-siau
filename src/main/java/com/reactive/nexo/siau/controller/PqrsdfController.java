package com.reactive.nexo.siau.controller;

import com.reactive.nexo.siau.dto.*;
import com.reactive.nexo.siau.service.PqrsdfService;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping(path = "/api/v1/siau/pqrsdf", produces = MediaType.APPLICATION_JSON_VALUE)
public class PqrsdfController {

    private final PqrsdfService service;

    public PqrsdfController(PqrsdfService service) {
        this.service = service;
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    public Mono<ResponseEntity<PqrsdfResponse>> create(
            @Valid @RequestBody CreatePqrsdfRequest req,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        return Mono.fromCallable(() -> service.create(req, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(ResponseEntity::ok);
    }

    @GetMapping
    public Mono<ResponseEntity<PagedResponse<PqrsdfResponse>>> list(
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "10") int size,
            @RequestParam Map<String, String> allParams) {
        return Mono.fromCallable(() -> {
            Map<String, String> filters = new HashMap<>(allParams);
            filters.remove("page");
            filters.remove("size");
            List<PqrsdfResponse> content = service.search(filters, page, size);
            long total = service.count(filters);
            int totalPages = (int) Math.ceil(total / (double) size);
            PagedResponse<PqrsdfResponse> resp = new PagedResponse<>();
            resp.setContent(content);
            resp.setPage(page);
            resp.setSize(size);
            resp.setTotalElements(total);
            resp.setTotalPages(totalPages);
            resp.setLast(page + 1 >= totalPages);
            return ResponseEntity.ok(resp);
        }).subscribeOn(Schedulers.boundedElastic());
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<PqrsdfResponse>> get(@PathVariable("id") Long id) {
        return Mono.fromCallable(() -> service.findById(id))
                .subscribeOn(Schedulers.boundedElastic())
                .map(resp -> resp.map(ResponseEntity::ok)
                        .orElseGet(() -> ResponseEntity.notFound().build()));
    }

    @PatchMapping("/{id}")
    public Mono<ResponseEntity<PqrsdfResponse>> update(
            @PathVariable("id") Long id,
            @Valid @RequestBody UpdatePqrsdfRequest req,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        return Mono.fromCallable(() -> service.update(id, req, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(updated -> updated == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(updated));
    }

    @PostMapping("/{id}/responder")
    public Mono<ResponseEntity<PqrsdfResponse>> responder(
            @PathVariable("id") Long id,
            @Valid @RequestBody ResponderPqrsdfRequest req,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        return Mono.fromCallable(() -> service.responder(id, req, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(r -> r == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(r));
    }

    @PostMapping("/{id}/cerrar")
    public Mono<ResponseEntity<PqrsdfResponse>> cerrar(
            @PathVariable("id") Long id,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        return Mono.fromCallable(() -> service.cerrar(id, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(r -> r == null ? ResponseEntity.notFound().build() : ResponseEntity.ok(r));
    }

    @GetMapping("/{id}/trazabilidad")
    public Mono<ResponseEntity<List<TrazabilidadResponse>>> trazabilidad(@PathVariable("id") Long id) {
        return Mono.fromCallable(() -> service.getTrazabilidad(id))
                .subscribeOn(Schedulers.boundedElastic())
                .map(ResponseEntity::ok);
    }
}

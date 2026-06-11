package com.reactive.nexo.siau.controller;

import com.reactive.nexo.siau.dto.ActaBuzonRequest;
import com.reactive.nexo.siau.dto.ActaBuzonResponse;
import com.reactive.nexo.siau.service.ActaBuzonService;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.List;

@RestController
@RequestMapping(path = "/api/v1/siau/actas-buzon", produces = MediaType.APPLICATION_JSON_VALUE)
public class ActaBuzonController {

    private final ActaBuzonService service;

    public ActaBuzonController(ActaBuzonService service) {
        this.service = service;
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
    public Mono<ResponseEntity<ActaBuzonResponse>> create(
            @Valid @RequestBody ActaBuzonRequest req,
            @RequestHeader(value = "x-employee-id", required = false) Long employeeId) {
        return Mono.fromCallable(() -> service.create(req, employeeId != null ? employeeId : 0L))
                .subscribeOn(Schedulers.boundedElastic())
                .map(ResponseEntity::ok);
    }

    @GetMapping
    public Mono<ResponseEntity<List<ActaBuzonResponse>>> list() {
        return Mono.fromCallable(() -> ResponseEntity.ok(service.findAll()))
                .subscribeOn(Schedulers.boundedElastic());
    }

    @GetMapping("/{id}")
    public Mono<ResponseEntity<ActaBuzonResponse>> get(@PathVariable("id") Long id) {
        return Mono.fromCallable(() -> service.findById(id))
                .subscribeOn(Schedulers.boundedElastic())
                .map(resp -> resp.map(ResponseEntity::ok)
                        .orElseGet(() -> ResponseEntity.notFound().build()));
    }
}

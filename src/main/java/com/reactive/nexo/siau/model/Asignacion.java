package com.reactive.nexo.siau.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Asignacion {
    private Long id;
    private Long pqrsdfId;
    private Long departamentoId;
    private Long funcionarioId;
    private String funcionarioNombre;
    private LocalDateTime fechaAsignacion;
    private LocalDate fechaLimiteRespuesta;
    private String estado;
    private String respuestaArea;
    private String observaciones;
    private LocalDateTime fechaRespuestaArea;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}

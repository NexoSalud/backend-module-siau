package com.reactive.nexo.siau.dto;

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
public class AsignacionResponse {
    private Long id;
    private Long pqrsdfId;
    private String pqrsdfConsecutivo;
    private Long departamentoId;
    private String departamentoNombre;
    private Long funcionarioId;
    private String funcionarioNombre;
    private LocalDateTime fechaAsignacion;
    private LocalDate fechaLimiteRespuesta;
    private String estado;
    private String respuestaArea;
    private String observaciones;
    private LocalDateTime fechaRespuestaArea;
    private LocalDateTime createdAt;
    private Boolean vencida;
    private Integer diasRestantes;
}

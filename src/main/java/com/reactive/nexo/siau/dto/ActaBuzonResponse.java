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
public class ActaBuzonResponse {
    private Long id;
    private LocalDate fechaApertura;
    private String ubicacion;
    private String servicio;
    private Integer totalPqrsdf;
    private String detallePorTipo;
    private String observaciones;
    private LocalDateTime createdAt;
    private Long createdBy;
}

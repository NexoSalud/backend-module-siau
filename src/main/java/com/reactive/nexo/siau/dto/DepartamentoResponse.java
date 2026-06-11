package com.reactive.nexo.siau.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DepartamentoResponse {
    private Long id;
    private String nombre;
    private String descripcion;
    private String responsable;
    private Boolean activo;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Long pqrsdfPendientes;
}

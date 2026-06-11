package com.reactive.nexo.siau.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Trazabilidad {
    private Long id;
    private Long pqrsdfId;
    private String accion;
    private String descripcion;
    private Long usuarioId;
    private String usuarioNombre;
    private String metadataJson;
    private LocalDateTime createdAt;
}

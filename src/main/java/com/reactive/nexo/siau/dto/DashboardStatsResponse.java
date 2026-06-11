package com.reactive.nexo.siau.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DashboardStatsResponse {
    private long totalPqrsdf;
    private long pendientes;
    private long enGestion;
    private long respondidas;
    private long cerradas;
    private long vencidas;

    private Map<String, Long> porTipo;
    private Map<String, Long> porDepartamento;
    private Map<String, Long> ultimos30Dias;
}

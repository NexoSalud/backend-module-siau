package com.reactive.nexo.siau.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ActaBuzonRequest {

    @NotNull(message = "La fecha de apertura es obligatoria")
    private LocalDate fechaApertura;

    @NotBlank(message = "La ubicación es obligatoria")
    private String ubicacion;

    private String servicio;

    @NotNull(message = "El total de PQRSDF es obligatorio")
    private Integer totalPqrsdf;

    private String detallePorTipo;
    private String observaciones;
    private Long createdBy;
}

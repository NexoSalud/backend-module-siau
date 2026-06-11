package com.reactive.nexo.siau.dto;

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
public class CreateAsignacionRequest {

    @NotNull(message = "El ID de la PQRSDF es obligatorio")
    private Long pqrsdfId;

    @NotNull(message = "El ID del departamento es obligatorio")
    private Long departamentoId;

    private Long funcionarioId;
    private String funcionarioNombre;

    private LocalDate fechaLimiteRespuesta;

    private String observaciones;
}

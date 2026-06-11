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
public class ResponderPqrsdfRequest {

    @NotBlank(message = "La respuesta final es obligatoria")
    private String respuestaFinal;

    @NotBlank(message = "El medio de respuesta es obligatorio")
    private String medioRespuesta;

    private String clasificacion;
    private Long updatedBy;
}

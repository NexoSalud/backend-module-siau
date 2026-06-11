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
public class UpdatePqrsdfRequest {

    private String clasificacion;
    private String observaciones;
    private String medioRespuesta;
    private String respuestaFinal;
    private Long updatedBy;
}

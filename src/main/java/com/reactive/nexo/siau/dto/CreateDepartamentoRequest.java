package com.reactive.nexo.siau.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateDepartamentoRequest {

    @NotBlank(message = "El nombre del departamento es obligatorio")
    private String nombre;

    private String descripcion;

    private String responsable;

    private Long responsableId;
}

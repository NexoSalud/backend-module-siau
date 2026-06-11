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
public class CreatePqrsdfRequest {

    @NotBlank(message = "El tipo es obligatorio (P, Q, R, S, D, F)")
    private String tipo;

    private LocalDate fechaRadicado;
    private String horaRadicado;

    @NotBlank(message = "El nombre del usuario es obligatorio")
    private String nombresUsuario;

    private String tipoDocumento;
    private String numeroDocumento;
    private String telefono;
    private String email;
    private String direccion;
    private String eps;
    private String regimen;

    @NotBlank(message = "El medio de recepción es obligatorio")
    private String medioRecepcion;

    private String servicioInvolucrado;
    private String funcionarioInvolucrado;

    @NotBlank(message = "La descripción es obligatoria")
    private String descripcion;

    private String clasificacion;
    private String observaciones;
    private Long createdBy;
    private Long actaBuzonId;
}

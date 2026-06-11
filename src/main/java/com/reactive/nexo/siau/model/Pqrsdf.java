package com.reactive.nexo.siau.model;

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
public class Pqrsdf {
    private Long id;
    private String consecutivo;
    private String tipo;
    private LocalDate fechaRadicado;
    private String horaRadicado;

    private String nombresUsuario;
    private String tipoDocumento;
    private String numeroDocumento;
    private String telefono;
    private String email;
    private String direccion;
    private String eps;
    private String regimen;

    private String medioRecepcion;
    private String servicioInvolucrado;
    private String funcionarioInvolucrado;
    private String descripcion;
    private String clasificacion;

    private String estado;
    private LocalDate fechaRespuesta;
    private String medioRespuesta;
    private String respuestaFinal;
    private String observaciones;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Long createdBy;
    private Long updatedBy;
    private Long actaBuzonId;
}

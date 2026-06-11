package com.reactive.nexo.siau.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table("siau_pqrsdf")
public class PqrsdfEntity {
    @Id
    private Long id;

    private String consecutivo;
    private String tipo;

    @Column("fecha_radicado")
    private LocalDate fechaRadicado;

    @Column("hora_radicado")
    private String horaRadicado;

    @Column("nombres_usuario")
    private String nombresUsuario;

    @Column("tipo_documento")
    private String tipoDocumento;

    @Column("numero_documento")
    private String numeroDocumento;

    private String telefono;
    private String email;
    private String direccion;
    private String eps;
    private String regimen;

    @Column("medio_recepcion")
    private String medioRecepcion;

    @Column("servicio_involucrado")
    private String servicioInvolucrado;

    @Column("funcionario_involucrado")
    private String funcionarioInvolucrado;

    private String descripcion;
    private String clasificacion;
    private String estado;

    @Column("fecha_respuesta")
    private LocalDate fechaRespuesta;

    @Column("medio_respuesta")
    private String medioRespuesta;

    @Column("respuesta_final")
    private String respuestaFinal;

    private String observaciones;

    @Column("created_at")
    private LocalDateTime createdAt;

    @Column("updated_at")
    private LocalDateTime updatedAt;

    @Column("created_by")
    private Long createdBy;

    @Column("updated_by")
    private Long updatedBy;

    @Column("acta_buzon_id")
    private Long actaBuzonId;
}

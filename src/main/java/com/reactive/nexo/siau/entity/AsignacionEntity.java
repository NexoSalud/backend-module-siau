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
@Table("siau_asignaciones")
public class AsignacionEntity {
    @Id
    private Long id;

    @Column("pqrsdf_id")
    private Long pqrsdfId;

    @Column("departamento_id")
    private Long departamentoId;

    @Column("funcionario_id")
    private Long funcionarioId;

    @Column("funcionario_nombre")
    private String funcionarioNombre;

    @Column("fecha_asignacion")
    private LocalDateTime fechaAsignacion;

    @Column("fecha_limite_respuesta")
    private LocalDate fechaLimiteRespuesta;

    private String estado;

    @Column("respuesta_area")
    private String respuestaArea;

    private String observaciones;

    @Column("fecha_respuesta_area")
    private LocalDateTime fechaRespuestaArea;

    @Column("created_at")
    private LocalDateTime createdAt;

    @Column("updated_at")
    private LocalDateTime updatedAt;
}

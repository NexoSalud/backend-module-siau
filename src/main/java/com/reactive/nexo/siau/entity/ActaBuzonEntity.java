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
@Table("siau_actas_buzon")
public class ActaBuzonEntity {
    @Id
    private Long id;

    @Column("fecha_apertura")
    private LocalDate fechaApertura;

    private String ubicacion;
    private String servicio;

    @Column("total_pqrsdf")
    private Integer totalPqrsdf;

    @Column("detalle_por_tipo")
    private String detallePorTipo;

    private String observaciones;

    @Column("created_at")
    private LocalDateTime createdAt;

    @Column("created_by")
    private Long createdBy;
}

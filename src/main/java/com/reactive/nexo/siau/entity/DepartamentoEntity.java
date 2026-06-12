package com.reactive.nexo.siau.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table("siau_departamentos")
public class DepartamentoEntity {
    @Id
    private Long id;

    private String nombre;
    private String descripcion;
    private String responsable;

    @Column("responsable_id")
    private Long responsableId;

    private Boolean activo;

    @Column("created_at")
    private LocalDateTime createdAt;

    @Column("updated_at")
    private LocalDateTime updatedAt;
}

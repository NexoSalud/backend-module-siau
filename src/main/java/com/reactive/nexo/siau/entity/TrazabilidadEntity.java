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
@Table("siau_trazabilidad")
public class TrazabilidadEntity {
    @Id
    private Long id;

    @Column("pqrsdf_id")
    private Long pqrsdfId;

    private String accion;
    private String descripcion;

    @Column("usuario_id")
    private Long usuarioId;

    @Column("usuario_nombre")
    private String usuarioNombre;

    @Column("metadata_json")
    private String metadataJson;

    @Column("created_at")
    private LocalDateTime createdAt;
}

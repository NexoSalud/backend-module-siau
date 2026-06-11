package com.reactive.nexo.siau.model;

import lombok.Getter;

@Getter
public enum PlazoRespuesta {
    RIESGO_VITAL("RIESGO_VITAL", "Reclamo de riesgo vital", 24, "horas"),
    RIESGO_PRIORIZADO("RIESGO_PRIORIZADO", "Reclamo de riesgo priorizado", 48, "horas"),
    RIESGO_SIMPLE("RIESGO_SIMPLE", "Reclamo de riesgo simple", 72, "horas"),
    PETICIONES_GENERALES("PETICIONES_GENERALES", "Peticiones generales", 15, "días hábiles"),
    SOLICITUDES_INFORMACION("SOLICITUDES_INFORMACION", "Solicitudes de información", 10, "días hábiles"),
    COPIAS("COPIAS", "Copias de documentos", 3, "días hábiles"),
    QUEJAS_RECLAMOS("QUEJAS_RECLAMOS", "Quejas y reclamos", 15, "días hábiles"),
    FELICITACION_SUGERENCIA("FELICITACION_SUGERENCIA", "Felicitaciones y sugerencias", 15, "días hábiles");

    private final String codigo;
    private final String nombre;
    private final int plazo;
    private final String unidad;

    PlazoRespuesta(String codigo, String nombre, int plazo, String unidad) {
        this.codigo = codigo;
        this.nombre = nombre;
        this.plazo = plazo;
        this.unidad = unidad;
    }
}

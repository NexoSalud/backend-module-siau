package com.reactive.nexo.siau.model;

import lombok.Getter;

@Getter
public enum ClasificacionQueja {
    FALTA_OPORTUNIDAD_PRESTACION(1, "Falta de oportunidad en la prestación de tecnologías en salud"),
    NEGACION_TECNOLOGIAS(2, "Negación de tecnologías en salud y otros elementos"),
    FALTA_OPORTUNIDAD_AUTORIZACION(3, "Falta de oportunidad en la autorización de tecnologías en salud"),
    INSATISFACCION_ATENCION_SALUD(4, "Insatisfacción relacionada con la atención en salud"),
    INSATISFACCION_ATENCION_PERSONAL(5, "Insatisfacción relacionada con la atención del personal"),
    INSATISFACCION_CONDICIONES_INADECUADAS(6, "Insatisfacción relacionada con condiciones insuficientes o inadecuadas de infraestructura"),
    INSATISFACCION_PROCESOS_LOGISTICOS(7, "Insatisfacción relacionada con procesos logísticos"),
    INSATISFACCION_COMUNICACION(8, "Insatisfacción con la comunicación o información entregada"),
    DIFICULTAD_CANALES_COMUNICACION(9, "Dificultad en la comunicación con las líneas y/o canales de atención"),
    INSATISFACCION_ATENCION_PERSONAL_ADMIN(10, "Insatisfacción relacionada con la atención del personal administrativo"),
    INSATISFACCION_TRAMITES_ADMINISTRATIVOS(11, "Insatisfacción relacionada con trámites administrativos"),
    PROBLEMAS_PAGO_PRESTACIONES(12, "Problemas en el reconocimiento y/o pago de prestaciones económicas");

    private final int codigo;
    private final String descripcion;

    ClasificacionQueja(int codigo, String descripcion) {
        this.codigo = codigo;
        this.descripcion = descripcion;
    }
}

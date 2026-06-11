package com.reactive.nexo.siau.model;

public enum EstadoAsignacion {
    PENDIENTE("PENDIENTE"),
    EN_GESTION("EN_GESTION"),
    RESPONDIDA("RESPONDIDA"),
    VENCIDA("VENCIDA");

    private final String value;

    EstadoAsignacion(String value) { this.value = value; }
    public String getValue() { return value; }

    public static EstadoAsignacion fromValue(String value) {
        for (EstadoAsignacion e : values()) {
            if (e.value.equalsIgnoreCase(value)) return e;
        }
        return PENDIENTE;
    }
}

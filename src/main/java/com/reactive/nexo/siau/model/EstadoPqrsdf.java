package com.reactive.nexo.siau.model;

public enum EstadoPqrsdf {
    RECIBIDO("RECIBIDO"),
    ASIGNADO("ASIGNADO"),
    EN_GESTION("EN_GESTION"),
    RESPONDIDO("RESPONDIDO"),
    CERRADO("CERRADO");

    private final String value;

    EstadoPqrsdf(String value) { this.value = value; }
    public String getValue() { return value; }

    public static EstadoPqrsdf fromValue(String value) {
        for (EstadoPqrsdf e : values()) {
            if (e.value.equalsIgnoreCase(value)) return e;
        }
        return RECIBIDO;
    }
}

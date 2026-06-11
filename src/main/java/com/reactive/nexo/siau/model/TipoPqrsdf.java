package com.reactive.nexo.siau.model;

public enum TipoPqrsdf {
    PETICION("P", "Petición"),
    QUEJA("Q", "Queja"),
    RECLAMO("R", "Reclamo"),
    SUGERENCIA("S", "Sugerencia"),
    DENUNCIA("D", "Denuncia"),
    FELICITACION("F", "Felicitación");

    private final String codigo;
    private final String nombre;

    TipoPqrsdf(String codigo, String nombre) {
        this.codigo = codigo;
        this.nombre = nombre;
    }

    public String getCodigo() { return codigo; }
    public String getNombre() { return nombre; }

    public static TipoPqrsdf fromCodigo(String codigo) {
        for (TipoPqrsdf t : values()) {
            if (t.codigo.equalsIgnoreCase(codigo)) return t;
        }
        throw new IllegalArgumentException("Código de tipo PQRSDF inválido: " + codigo);
    }
}

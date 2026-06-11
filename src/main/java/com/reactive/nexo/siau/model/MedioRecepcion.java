package com.reactive.nexo.siau.model;

public enum MedioRecepcion {
    BUZON("Buzón de sugerencias"),
    OFICIO("Oficio"),
    EMAIL("Correo electrónico"),
    PAGINA_WEB("Página web"),
    TELEFONICA("Vía telefónica"),
    PRESENCIAL("Presencial"),
    WHATSAPP("WhatsApp");

    private final String descripcion;

    MedioRecepcion(String descripcion) { this.descripcion = descripcion; }
    public String getDescripcion() { return descripcion; }
}

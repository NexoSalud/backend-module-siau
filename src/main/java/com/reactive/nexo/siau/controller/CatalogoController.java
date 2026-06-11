package com.reactive.nexo.siau.controller;

import com.reactive.nexo.siau.model.ClasificacionQueja;
import com.reactive.nexo.siau.model.MedioRecepcion;
import com.reactive.nexo.siau.model.PlazoRespuesta;
import com.reactive.nexo.siau.model.TipoPqrsdf;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.util.*;

@RestController
@RequestMapping("/api/v1/siau/catalogos")
public class CatalogoController {

    @GetMapping("/tipos-pqrsdf")
    public Mono<ResponseEntity<List<Map<String, String>>>> getTipos() {
        List<Map<String, String>> list = new ArrayList<>();
        for (TipoPqrsdf t : TipoPqrsdf.values()) {
            Map<String, String> m = new LinkedHashMap<>();
            m.put("codigo", t.getCodigo());
            m.put("nombre", t.getNombre());
            list.add(m);
        }
        return Mono.just(ResponseEntity.ok(list));
    }

    @GetMapping("/medios-recepcion")
    public Mono<ResponseEntity<List<Map<String, String>>>> getMedios() {
        List<Map<String, String>> list = new ArrayList<>();
        for (MedioRecepcion m : MedioRecepcion.values()) {
            Map<String, String> entry = new LinkedHashMap<>();
            entry.put("nombre", m.name());
            entry.put("descripcion", m.getDescripcion());
            list.add(entry);
        }
        return Mono.just(ResponseEntity.ok(list));
    }

    @GetMapping("/clasificaciones")
    public Mono<ResponseEntity<List<Map<String, Object>>>> getClasificaciones() {
        List<Map<String, Object>> list = new ArrayList<>();
        for (ClasificacionQueja c : ClasificacionQueja.values()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("codigo", c.getCodigo());
            m.put("nombre", c.name());
            m.put("descripcion", c.getDescripcion());
            list.add(m);
        }
        return Mono.just(ResponseEntity.ok(list));
    }

    @GetMapping("/plazos-respuesta")
    public Mono<ResponseEntity<List<Map<String, Object>>>> getPlazos() {
        List<Map<String, Object>> list = new ArrayList<>();
        for (PlazoRespuesta p : PlazoRespuesta.values()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("codigo", p.getCodigo());
            m.put("nombre", p.getNombre());
            m.put("plazo", p.getPlazo());
            m.put("unidad", p.getUnidad());
            list.add(m);
        }
        return Mono.just(ResponseEntity.ok(list));
    }
}

"""Tests for PQRSDF CRUD endpoints."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crear_pqrsdf(client: AsyncClient) -> None:
    """POST /api/siau/pqrsdf — crea una PQRSDF y verifica la respuesta."""
    payload = {
        "tipo": "PQ",
        "nombresUsuario": "Juan Pérez",
        "tipoDocumento": "CC",
        "numeroDocumento": "123456789",
        "telefono": "3001234567",
        "email": "juan@example.com",
        "medioRecepcion": "WEB",
        "descripcion": "Solicitud de prueba para verificar el servicio PQRSDF",
        "clasificacion": "QUEJA",
    }
    response = await client.post("/api/siau/pqrsdf", json=payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["success"] is True
    pqrsdf = data["data"]
    assert pqrsdf["consecutivo"] is not None
    assert pqrsdf["tipo"] == "PQ"
    assert pqrsdf["nombresUsuario"] == "Juan Pérez"
    assert pqrsdf["descripcion"] == payload["descripcion"]
    assert pqrsdf["estado"] == "RECIBIDO"


@pytest.mark.asyncio
async def test_listar_vacio(client: AsyncClient) -> None:
    """GET /api/siau/pqrsdf — sin datos devuelve lista vacía con paginación."""
    response = await client.get("/api/siau/pqrsdf")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    page = data["data"]
    assert page["content"] == []
    assert page["page"] == 0
    assert page["totalElements"] == 0
    assert page["totalPages"] == 0
    assert page["last"] is True


@pytest.mark.asyncio
async def test_get_no_existe(client: AsyncClient) -> None:
    """GET /api/siau/pqrsdf/{id} — contrato no existente devuelve 404."""
    response = await client.get("/api/siau/pqrsdf/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "no encontrado" in data["message"].lower() or "not found" in data["message"].lower()

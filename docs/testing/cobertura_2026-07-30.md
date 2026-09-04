# Cobertura real — 2026-07-30

Comando ejecutado:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=simulador_ev3 --cov-report=term --cov-report=json:build\qa-coverage.json -q
```

Resultado: **801 aprobadas, 4 omitidas, 1 advertencia, en 149.84 s**.

- Cobertura total: **71.35%**.
- Umbral configurado: **70.0%**; aprobado.
- Informe estructurado: `build/qa-coverage.json`.
- Advertencia: `coverage` empleó el trazador Python al no estar disponible el
  trazador C. No afecta al resultado funcional ni al cálculo de cobertura.

Las cuatro omisiones pertenecen a las pruebas E2E Tkinter que requieren un
escritorio Windows visible.

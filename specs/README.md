# Specs — Spec‑Driven Development (SDD)

En este repo **la spec es la fuente del diseño**. El código implementa specs; los tests verifican sus criterios de aceptación; la documentación técnica se deriva de ellas.

## Índice

| # | Spec | Rúbrica | Responsable propuesto |
|---|---|---|---|
| 000 | [Constitución](000-constitucion.md) — principios no negociables | transversal | Ambos |
| 001 | [Escenario JSON, modelo y validación](001-escenario-json/spec.md) | Validación 5 % | Juan |
| 002 | [Modelo de estado, acciones y reglas](002-modelo-estado-reglas/spec.md) | Modelado 15 % | Daniel |
| 003 | [BFS, DFS y Costo Uniforme + métricas](003-busqueda-no-informada-y-costo/spec.md) | 15 % | Juan |
| 004 | [A\*, heurísticas y Beam Search](004-busqueda-informada/spec.md) | 20 % | Juan |
| 005 | [Minimax, alfa‑beta y función de utilidad](005-adversarial/spec.md) | 20 % | Daniel |
| 006 | [Verificación de soluciones](006-verificacion/spec.md) | Validación 5 % | Daniel |
| 007 | [Interfaz y visualización](007-interfaz/spec.md) | 5 % | Daniel |
| 008 | [Casos mínimos y experimentación](008-experimentos/spec.md) | 10 % | Juan |
| 009 | [Documentación y entregables](009-documentacion-entregables/spec.md) | Calidad/doc 10 % | Ambos |

## Orden de implementación (dependencias)

```
001 escenario ──► 002 estado/reglas ──► 003 BFS/DFS/UCS ──► 004 A*/Beam ──┐
                          │                                               ├─► 008 experimentos ─► 009 entregables
                          └──────────► 005 Minimax/αβ ────────────────────┤
                    006 verificación (crece junto a 003–005) ─────────────┤
                    007 interfaz (empieza con 001, crece con cada spec) ──┘
```

Hitos sugeridos:
- **H1 – Contrato:** 001 + 002 + tests de carga con el JSON del enunciado.
- **H2 – Rutas:** 003 + 004 + verificador de caminos + casos 1–6.
- **H3 – Adversario:** 005 + verificador de decisiones + casos 7–10.
- **H4 – Producto:** 007 completa, 008 experimentos con evidencia, 009 documentos finales y simulacros de sustentación.

## Ciclo de vida de una spec

`borrador` → `aprobada` (ambos la leyeron y entienden) → `en progreso` → `implementada` (tests verdes) → `sustentable` (ambos pasaron el simulacro de `/sustentacion`).

## Cómo escribir una spec nueva

Copiar [`_plantilla/spec.md`](_plantilla/spec.md). Cada criterio de aceptación debe poder convertirse en **un test**. Si un criterio no se puede probar, reescríbelo.

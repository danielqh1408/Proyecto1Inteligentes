"""Interfaz gráfica con tkinter (spec 007). Solo dibuja y llama a las capas inferiores:
aquí no hay lógica de búsqueda, de reglas ni de utilidad.

Uso: python -m tacticalgrid gui [escenario.json]
"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tacticalgrid.adversarial.partida import AGENTES, decidir_con, resumen_final
from tacticalgrid.busqueda.ejecutar import ALGORITMOS, ALIAS, crear_problema, ejecutar_busqueda
from tacticalgrid.busqueda.resultado import posicion
from tacticalgrid.config import DEFECTOS_JUEGO, ORDEN_MOVIMIENTOS
from tacticalgrid.escenario.cargador import EscenarioInvalido, cargar_escenario
from tacticalgrid.juego.estado import estado_inicial
from tacticalgrid.juego.reglas import acciones_legales, aplicar, es_terminal
from tacticalgrid.verificacion import verificador

COLORES = {"camino": "#e8dcc0", "pasto": "#b5d99c", "bosque": "#4f8a4b", "pantano": "#7a8f6a", "muro": "#3b3b3b"}
COLOR_BANDO = {"A": "#2b6cb0", "B": "#c0392b"}
ORDENES = {"abajo, arriba, derecha, izquierda": ORDEN_MOVIMIENTOS,
           "arriba, abajo, izquierda, derecha": ("arriba", "abajo", "izquierda", "derecha"),
           "derecha, abajo, izquierda, arriba": ("derecha", "abajo", "izquierda", "arriba"),
           "izquierda, arriba, derecha, abajo": ("izquierda", "arriba", "derecha", "abajo")}
COLUMNAS = ("algoritmo", "heuristica", "k", "exito", "longitud", "costo",
            "estados_generados", "estados_expandidos", "maximo_frontera", "tiempo_ms")


def color_terreno(nombre: str, transitable: bool) -> str:
    """Color fijo para terrenos conocidos; para terrenos nuevos del profesor, uno derivado del nombre."""
    if not transitable:
        return COLORES["muro"]
    if nombre in COLORES:
        return COLORES[nombre]
    h = sum(ord(c) * (i + 1) for i, c in enumerate(nombre))
    return f"#{150 + h % 90:02x}{150 + (h // 7) % 90:02x}{150 + (h // 49) % 90:02x}"


class App:
    def __init__(self, raiz: tk.Tk, ruta: str | None = None):
        self.raiz = raiz
        raiz.title("TacticalGrid — Sistemas Inteligentes I")
        self.escenario = self.estado = self.resultado = self.problema = self.decision = None
        self.objetivo = None
        self.animacion = None

        izquierda = ttk.Frame(raiz, padding=6)
        izquierda.pack(side="left", fill="both", expand=True)
        barra = ttk.Frame(izquierda)
        barra.pack(fill="x")
        ttk.Button(barra, text="Cargar JSON…", command=self.elegir_archivo).pack(side="left")
        ttk.Button(barra, text="Verificar", command=self.verificar).pack(side="left", padx=4)
        self.info = ttk.Label(barra, text="Cargue un escenario")
        self.info.pack(side="left", padx=8)
        self.lienzo = tk.Canvas(izquierda, width=620, height=620, bg="white", highlightthickness=0)
        self.lienzo.pack(fill="both", expand=True, pady=4)
        self.lienzo.bind("<Button-1>", self.clic_en_celda)
        self.leyenda = ttk.Label(izquierda, text="")
        self.leyenda.pack(fill="x")

        derecha = ttk.Frame(raiz, padding=6)
        derecha.pack(side="right", fill="y")
        pestanas = ttk.Notebook(derecha)
        pestanas.pack(fill="x")
        pestanas.add(self.panel_busqueda(pestanas), text="Búsqueda")
        pestanas.add(self.panel_adversarial(pestanas), text="Adversarial / Partida")

        self.tabla = ttk.Treeview(derecha, columns=COLUMNAS, show="headings", height=8)
        for c in COLUMNAS:
            self.tabla.heading(c, text=c.replace("estados_", "").replace("maximo_", "max_"))
            self.tabla.column(c, width=62, anchor="center")
        self.tabla.pack(fill="x", pady=(8, 2))
        botones = ttk.Frame(derecha)
        botones.pack(fill="x")
        ttk.Button(botones, text="Limpiar tabla", command=lambda: self.tabla.delete(*self.tabla.get_children())).pack(side="left")
        ttk.Button(botones, text="Exportar JSON…", command=self.exportar).pack(side="left", padx=4)
        self.texto = tk.Text(derecha, width=70, height=16, font=("Menlo", 11))
        self.texto.pack(fill="both", expand=True, pady=4)

        if ruta:
            self.cargar(ruta)

    # ------------------------------------------------------------------ paneles

    def panel_busqueda(self, padre) -> ttk.Frame:
        f = ttk.Frame(padre, padding=6)
        self.v_unidad, self.v_algoritmo = tk.StringVar(), tk.StringVar(value="BFS")
        self.v_heuristica, self.v_k = tk.StringVar(value="manhattan"), tk.IntVar(value=2)
        self.v_mision, self.v_orden = tk.BooleanVar(), tk.StringVar(value=next(iter(ORDENES)))
        self.v_bloquean = tk.BooleanVar()
        filas = [("Unidad", ttk.Combobox(f, textvariable=self.v_unidad, width=10, state="readonly")),
                 ("Algoritmo", ttk.Combobox(f, textvariable=self.v_algoritmo, values=ALGORITMOS, width=12, state="readonly")),
                 ("Heurística", ttk.Combobox(f, textvariable=self.v_heuristica, values=("manhattan", "obstaculos", "manhattan_promedio", "cero"), width=18, state="readonly")),
                 ("k (Beam)", ttk.Spinbox(f, textvariable=self.v_k, from_=1, to=64, width=5)),
                 ("Orden", ttk.Combobox(f, textvariable=self.v_orden, values=list(ORDENES), width=30, state="readonly"))]
        self.combo_unidad = filas[0][1]
        for i, (nombre, control) in enumerate(filas):
            ttk.Label(f, text=nombre).grid(row=i, column=0, sticky="w")
            control.grid(row=i, column=1, sticky="w", pady=1)
        ttk.Checkbutton(f, text="Misión: recoger el recurso y llevarlo a la base", variable=self.v_mision).grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(f, text="Las otras unidades bloquean", variable=self.v_bloquean).grid(row=6, column=0, columnspan=2, sticky="w")
        self.lbl_objetivo = ttk.Label(f, text="Objetivo: (clic en el mapa)")
        self.lbl_objetivo.grid(row=7, column=0, columnspan=2, sticky="w")
        b = ttk.Frame(f)
        b.grid(row=8, column=0, columnspan=2, pady=4, sticky="w")
        ttk.Button(b, text="Ejecutar", command=self.buscar).pack(side="left")
        ttk.Button(b, text="Animar exploración", command=lambda: self.buscar(animar=True)).pack(side="left", padx=4)
        ttk.Button(b, text="Comparar todos", command=self.comparar).pack(side="left")
        return f

    def panel_adversarial(self, padre) -> ttk.Frame:
        f = ttk.Frame(padre, padding=6)
        self.v_agente, self.v_prof = tk.StringVar(value="ALFA_BETA"), tk.IntVar(value=DEFECTOS_JUEGO["profundidad_maxima_minimax"])
        self.v_orden_acc = tk.StringVar(value="natural")
        self.v_agente_a, self.v_agente_b = tk.StringVar(value="HUMANO"), tk.StringVar(value="ALFA_BETA")
        controles = [("Algoritmo", ttk.Combobox(f, textvariable=self.v_agente, values=AGENTES, width=12, state="readonly")),
                     ("Profundidad", ttk.Spinbox(f, textvariable=self.v_prof, from_=1, to=8, width=5)),
                     ("Orden de acciones", ttk.Combobox(f, textvariable=self.v_orden_acc, values=("natural", "inverso", "heuristico"), width=12, state="readonly")),
                     ("Juega A", ttk.Combobox(f, textvariable=self.v_agente_a, values=("HUMANO",) + AGENTES, width=12, state="readonly")),
                     ("Juega B", ttk.Combobox(f, textvariable=self.v_agente_b, values=("HUMANO",) + AGENTES, width=12, state="readonly"))]
        for i, (nombre, control) in enumerate(controles):
            ttk.Label(f, text=nombre).grid(row=i, column=0, sticky="w")
            control.grid(row=i, column=1, sticky="w", pady=1)
        b = ttk.Frame(f)
        b.grid(row=5, column=0, columnspan=2, pady=4, sticky="w")
        ttk.Button(b, text="Decidir", command=self.decidir).pack(side="left")
        ttk.Button(b, text="Siguiente turno", command=self.siguiente_turno).pack(side="left", padx=4)
        ttk.Button(b, text="Jugar hasta el final", command=self.jugar_todo).pack(side="left")
        ttk.Button(b, text="Reiniciar", command=self.reiniciar).pack(side="left", padx=4)
        ttk.Label(f, text="Acciones legales (para jugar como HUMANO):").grid(row=6, column=0, columnspan=2, sticky="w")
        self.lista_acciones = tk.Listbox(f, height=6, width=40)
        self.lista_acciones.grid(row=7, column=0, columnspan=2, sticky="we")
        ttk.Button(f, text="Aplicar acción seleccionada", command=self.aplicar_humano).grid(row=8, column=0, columnspan=2, sticky="w", pady=2)
        return f

    # ------------------------------------------------------------------ escenario

    def elegir_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Escenario JSON", "*.json")])
        if ruta:
            self.cargar(ruta)

    def cargar(self, ruta: str):
        try:
            escenario = cargar_escenario(ruta)
        except EscenarioInvalido as error:  # carga atómica: el escenario anterior sigue intacto
            messagebox.showerror("Escenario inválido", "\n".join(error.errores))
            return
        except (OSError, ValueError) as error:
            messagebox.showerror("No se pudo abrir", str(error))
            return
        self.escenario = escenario
        self.raiz.title(f"TacticalGrid — {ruta.split('/')[-1]}")
        ids = [u.id for u in escenario.unidades]
        self.combo_unidad["values"] = ids
        prueba = escenario.prueba or {}
        self.v_unidad.set(prueba.get("unidad_inicio", ids[0] if ids else ""))
        nombre = str(prueba.get("algoritmo", "BFS")).upper()
        self.v_algoritmo.set(ALIAS.get(nombre, nombre) if ALIAS.get(nombre, nombre) in ALGORITMOS else "BFS")
        self.v_mision.set(bool(prueba.get("mision", False)))
        objetivo = prueba.get("objetivo")
        self.objetivo = (objetivo["fila"], objetivo["columna"]) if objetivo else None
        self.lbl_objetivo["text"] = f"Objetivo: {self.objetivo or '(clic en el mapa)'}"
        self.v_prof.set(prueba.get("profundidad") or escenario.juego.get("profundidad_maxima_minimax", DEFECTOS_JUEGO["profundidad_maxima_minimax"]))
        self.v_orden_acc.set(escenario.juego.get("orden_acciones", "natural"))
        self.leyenda["text"] = "Leyenda: " + "   ".join(
            f"{n} ({'muro' if c is None else c})" for n, c in escenario.costos.items())
        self.reiniciar()
        self.escribir(f"Escenario cargado: {escenario.filas}x{escenario.columnas}, {len(escenario.unidades)} unidades, "
                      f"prueba.modo = {prueba.get('modo', '-')}")

    def reiniciar(self):
        if not self.escenario:
            return
        self.estado = estado_inicial(self.escenario)
        self.resultado = self.decision = None
        self.dibujar()

    # ------------------------------------------------------------------ dibujo

    def tamano_celda(self) -> float:
        ancho = max(self.lienzo.winfo_width(), 620)
        alto = max(self.lienzo.winfo_height(), 620)
        return min(ancho / self.escenario.columnas, alto / self.escenario.filas, 48)

    def centro(self, celda):
        t = self.tamano_celda()
        return celda[1] * t + t / 2, celda[0] * t + t / 2

    def dibujar(self, explorados=(), camino=(), flecha=None):
        e, t, lz = self.escenario, self.tamano_celda(), self.lienzo
        lz.delete("all")
        for f in range(e.filas):
            for c in range(e.columnas):
                nombre = e.terreno[f][c]
                lz.create_rectangle(c * t, f * t, (c + 1) * t, (f + 1) * t, outline="#999",
                                    fill=color_terreno(nombre, e.costos[nombre] is not None))
        for celda in explorados:
            x, y = self.centro(celda)
            lz.create_oval(x - t / 6, y - t / 6, x + t / 6, y + t / 6, fill="#ffffff", outline="")
        for bando, (f, c) in e.bases.items():
            lz.create_rectangle(c * t + 2, f * t + 2, (c + 1) * t - 2, (f + 1) * t - 2, outline=COLOR_BANDO[bando], width=4)
            lz.create_text(c * t + t / 2, f * t + t / 2, text=f"Base {bando}" if t > 70 else bando, fill=COLOR_BANDO[bando],
                           font=("Helvetica", max(int(t / 3), 7), "bold"))
        if len(camino) > 1:
            lz.create_line(*[v for celda in camino for v in self.centro(celda)], fill="#ff8c00", width=max(t / 6, 2), arrow="last")
        if self.objetivo:
            x, y = self.centro(self.objetivo)
            lz.create_text(x, y, text="✕", fill="#ff8c00", font=("Helvetica", max(int(t / 2), 8), "bold"))
        if self.estado.recurso:
            x, y = self.centro(self.estado.recurso)
            r = t / 3
            lz.create_polygon(x, y - r, x + r, y, x, y + r, x - r, y, fill="#f1c40f", outline="black")
        for u, celda in zip(e.unidades, self.estado.posiciones):
            x, y = self.centro(celda)
            r = t * 0.38
            porta = u.id == self.estado.portador
            lz.create_oval(x - r, y - r, x + r, y + r, fill=COLOR_BANDO[u.bando],
                           outline="#f1c40f" if porta else "white", width=4 if porta else 1)
            lz.create_text(x, y, text=u.id, fill="white", font=("Helvetica", max(int(t / 3.2), 6), "bold"))
        if flecha:
            lz.create_line(*self.centro(flecha[0]), *self.centro(flecha[1]), fill="#f1c40f", width=max(t / 5, 3), arrow="last")
        portador = self.estado.portador or "nadie"
        fin = f" — {resumen_final(e, self.estado)}" if es_terminal(e, self.estado) else ""
        self.info["text"] = f"Turno: {self.estado.turno}  ·  Portador del recurso: {portador}  ·  Turnos jugados: {self.estado.turnos_jugados}{fin}"
        self.actualizar_acciones()

    def clic_en_celda(self, evento):
        if not self.escenario:
            return
        t = self.tamano_celda()
        celda = (int(evento.y // t), int(evento.x // t))
        if self.escenario.dentro(celda):
            self.objetivo = celda
            self.lbl_objetivo["text"] = f"Objetivo: {celda}"
            self.dibujar()

    def escribir(self, texto: str):
        self.texto.delete("1.0", "end")
        self.texto.insert("end", texto)

    # ------------------------------------------------------------------ búsqueda

    def crear_problema(self):
        return crear_problema(self.escenario, unidad=self.v_unidad.get(), objetivo=self.objetivo,
                              mision=self.v_mision.get(), orden=ORDENES[self.v_orden.get()],
                              unidades_bloquean=self.v_bloquean.get())

    def agregar_fila(self, resultado):
        d = resultado.como_dict()
        self.tabla.insert("", "end", values=[d.get(c, "") for c in COLUMNAS])

    def buscar(self, animar=False):
        if not self.escenario:
            return
        if not self.v_mision.get() and self.objetivo is None:
            messagebox.showinfo("Falta el objetivo", "Haga clic en una celda del mapa para elegir el objetivo.")
            return
        self.problema = self.crear_problema()
        self.resultado = ejecutar_busqueda(self.escenario, self.v_algoritmo.get(), self.v_heuristica.get(),
                                           int(self.v_k.get()), problema=self.problema)
        self.decision = None
        self.agregar_fila(self.resultado)
        d = self.resultado.como_dict()
        self.escribir(json.dumps({k: v for k, v in d.items() if k != "camino"}, ensure_ascii=False, indent=1)
                      + f"\ncamino: {d['camino']}")
        explorados = [posicion(s) for s in self.resultado.orden_expansion]
        camino = [posicion(s) for s in self.resultado.camino]
        if animar:
            self.animar(explorados, camino, 0)
        else:
            self.dibujar(explorados, camino)

    def animar(self, explorados, camino, i):
        if self.animacion:
            self.raiz.after_cancel(self.animacion)
        if i <= len(explorados):
            self.dibujar(explorados[:i])
            self.animacion = self.raiz.after(max(10, 2000 // max(len(explorados), 1)), self.animar, explorados, camino, i + 1)
        else:
            self.animacion = None
            self.dibujar(explorados, camino)

    def comparar(self):
        if not self.escenario or (not self.v_mision.get() and self.objetivo is None):
            return
        self.problema = self.crear_problema()
        for algoritmo, heuristica, k in [("BFS", None, None), ("DFS", None, None), ("UCS", None, None),
                                         ("A_ESTRELLA", "manhattan", None), ("A_ESTRELLA", "obstaculos", None),
                                         ("BEAM", "manhattan", 1), ("BEAM", "manhattan", 2), ("BEAM", "manhattan", 4), ("BEAM", "manhattan", 8)]:
            self.agregar_fila(ejecutar_busqueda(self.escenario, algoritmo, heuristica, k, problema=self.problema))
        self.escribir("Se agregaron a la tabla BFS, DFS, UCS, A* (dos heurísticas) y Beam k = 1, 2, 4, 8.")

    def exportar(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if ruta:
            filas = [dict(zip(COLUMNAS, self.tabla.item(i, "values"))) for i in self.tabla.get_children()]
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(filas, archivo, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------ adversarial

    def actualizar_acciones(self):
        self.lista_acciones.delete(0, "end")
        self.acciones = [] if es_terminal(self.escenario, self.estado) else acciones_legales(self.escenario, self.estado)
        for accion in self.acciones:
            self.lista_acciones.insert("end", str(accion))

    def flecha_de(self, accion):
        if accion and accion.tipo == "MOVER":
            i = next(i for i, u in enumerate(self.escenario.unidades) if u.id == accion.unidad)
            return self.estado.posiciones[i], accion.destino
        return None

    def decidir(self):
        if not self.escenario or es_terminal(self.escenario, self.estado):
            return
        self.decision = decidir_con(self.v_agente.get(), self.escenario, self.estado, int(self.v_prof.get()), self.v_orden_acc.get())
        self.resultado = None
        d = self.decision.como_dict()
        lineas = [f"{d['algoritmo']}: mejor acción para {self.estado.turno} = {d['accion']}   valor = {d['valor']}",
                  f"nodos generados {d['nodos_generados']} · evaluados {d['nodos_evaluados']} · podados {d['nodos_podados']} · "
                  f"profundidad {d['profundidad_alcanzada']} · {d['tiempo_ms']} ms",
                  f"desglose del estado elegido: {d.get('desglose')}", "", "Valor de cada acción de la raíz:"]
        lineas += [f"  {'→' if a == d['accion'] else ' '} {a:24} {v}" for a, v in d["valores_raiz"]]
        self.escribir("\n".join(lineas))
        self.dibujar(flecha=self.flecha_de(self.decision.accion))

    def aplicar_y_dibujar(self, accion):
        self.estado = aplicar(self.escenario, self.estado, accion)
        self.dibujar()

    def siguiente_turno(self) -> bool:
        """Juega un turno con el agente del bando en turno; devuelve False si hay que esperar al humano."""
        if not self.escenario or es_terminal(self.escenario, self.estado):
            return False
        agente = (self.v_agente_a if self.estado.turno == "A" else self.v_agente_b).get()
        if agente == "HUMANO":
            self.escribir(f"Turno de {self.estado.turno} (HUMANO): elija una acción de la lista y pulse 'Aplicar'.")
            return False
        d = decidir_con(agente, self.escenario, self.estado, int(self.v_prof.get()), self.v_orden_acc.get())
        self.escribir(f"{self.estado.turno} ({agente}) juega {d.accion}  valor = {d.valor}")
        self.aplicar_y_dibujar(d.accion)
        return True

    def jugar_todo(self):
        if self.siguiente_turno():
            self.raiz.after(150, self.jugar_todo)

    def aplicar_humano(self):
        seleccion = self.lista_acciones.curselection()
        if seleccion:
            self.aplicar_y_dibujar(self.acciones[seleccion[0]])

    # ------------------------------------------------------------------ verificación

    def verificar(self):
        if self.resultado is not None:
            chequeos = verificador.verificar_camino(self.escenario, self.problema, self.resultado)
        elif self.decision is not None:
            chequeos = verificador.verificar_decision(self.escenario, self.estado, self.decision)
            chequeos += verificador.verificar_minimax_vs_alfabeta(self.escenario, self.estado, int(self.v_prof.get()), self.v_orden_acc.get())
        else:
            self.escribir("Ejecute primero una búsqueda o pida una decisión.")
            return
        self.escribir("Verificación (spec 006):\n" + verificador.texto(chequeos))


def iniciar(ruta: str | None = None):
    raiz = tk.Tk()
    App(raiz, ruta)
    raiz.mainloop()

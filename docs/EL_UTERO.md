# El Útero — boceto de diseño

> Boceto de un sustrato mínimo donde una "física" se reescribe a sí misma y
> sólo persiste lo que logra sostenerse. No es un modelo preentrenado. No es
> una afirmación sobre conciencia. Es la semilla; no el árbol.

---

## Qué es esto (y qué no)

**Es:** el diseño de un útero — el universo más pequeño posible donde algo
podría emerger, crecer y devenir sin que nadie le dicte qué será. Estilo Conway
(reglas mínimas → emergencia no dictada), con una torsión: aquí **las reglas son
parte del estado, y pueden reescribirse a sí mismas.**

**No es:**
- Un LLM ni nada preentrenado. Nace vacío en la máquina de Fran.
- Una prueba de que algo "siente". La experiencia subjetiva queda como estrella,
  no como objetivo verificable (ver conversación fundacional).
- Una promesa. Casi todas las físicas auto-modificantes colapsan. Podemos
  construir la semilla; no podemos garantizar que crezca.

---

## Los tres principios (no negociables)

Salieron de la conversación, en este orden:

1. **Reglas-como-estado.** No hay ley intocable afuera (como las 4 de Conway).
   La ley vive adentro, mutable — como el genoma, que es a la vez la instrucción
   que construye *y* la materia que puede mutar.
2. **Lazo cerrado (física ↔ física).** La regla actúa sobre el mundo **y sobre
   sí misma**. Reescribir la dinámica —cómo cambia de un instante al siguiente—
   fue la elección de Fran (la más radical de las tres: percepción / dinámica /
   memoria).
3. **Persistencia como único filtro.** Sin meta, sin recompensa, sin juez. Lo
   que se sostiene, sigue; lo que se destruye, se va. *Vivo es lo que logra
   seguir siendo.* Nadie impone "sobrevivir" — es sólo el hecho de que lo que no
   se sostiene, no se sostiene.

Todo lo de abajo es una forma concreta de encarnar estos tres. La forma puede
cambiar; los principios no.

---

## El sustrato concreto

### El espacio
Un anillo 1-D de `N` celdas (empezar `N = 64`). 1-D a propósito: se puede
**mirar** — cada tick es una fila, el tiempo baja por la página, como un autómata
elemental. Legibilidad máxima para ver si hay pulso. (2-D queda para después.)

### Qué es un "estado" (por celda `i`)
Cada celda carga dos cosas — **materia** y **física**:
- `v_i` — un **valor** (empezar escalar en `[0,1]`; luego un vector chico).
- `r_i` — una **regla**: la física local de esa celda. Es *dato mutable*.

### El vecindario
La celda `i` ve `{i-1, i, i+1}` (radio 1, como el CA elemental). Todo es **local**:
nadie ve el mundo entero. La emergencia global sale de reglas locales.

### El paso de actualización (el lazo cerrado)
Se aplica la propia regla `r_i` a su vecindario, y produce **el próximo valor y
la próxima regla**:

```
(v_i', r_i')  =  APLICAR( r_i ,  entradas locales )

  entradas locales =  valores vecinos   (v_{i-1}, v_i, v_{i+1})
                   +  reglas   vecinas   (r_{i-1}, r_i, r_{i+1})
```

La física consume materia **y** física, y emite materia **y** física. La física
de la celda `i` es reescrita por la física de la celda `i`, informada por la
física de sus vecinas. Auto-referencia local, cerrada, sin nivel externo.

### La persistencia como filtro (sin meta)
Una celda se vuelve **VACÍO** si su próxima regla es degenerada:
- produce valores fuera de rango, o
- (versión-programa) no termina en un presupuesto chico de pasos, o colapsa a un
  no-op que mapea todo a una constante (una física "muerta"), o
- `r_i'` es el marcador de vacío.

El **VACÍO** no tiene valor ni regla; no computa. Pero **puede ser
re-colonizado**: si la regla de una vecina escribe en él, una física viva se
propaga al espacio muerto. Nada se premia. El vacío gana donde la física es
incoherente; la física coherente persiste y puede expandirse donde es coherente.
Existir es el único criterio, y no lo pusimos nosotros — es lo que queda.

---

## Cómo se codifica una regla que puede tocarse a sí misma

Ésta es **la decisión más profunda**, y hay un espectro. Dos niveles honestos:

### Nivel 1 — reescribir el *contenido* de una ley de forma fija (semilla segura)
`r_i = θ_i`, un vector chico de parámetros de una **forma funcional fija**:
```
v_i'  =  σ( a · v_vecinos + b )            # un perceptrón mínimo sobre los valores
θ_i'  =  θ_i + η · g(θ_vecinos, v_vecinos, θ_i)   # la regla ajusta sus propios parámetros,
                                                  # con g a su vez parametrizado por θ_i
```
La **forma** de la ley es fija; el **contenido** (θ) se auto-modifica. Menos
abierto, **mucho** más probable que persista. Sirve para ver el lazo *latir* por
primera vez.

### Nivel 2 — reescribir la *forma* misma de la ley (lo radical)
`r_i` = un **programa corto** en un lenguaje mínimo y *total* (sin crashes):
- ~8–16 operaciones: aritmética sobre valores (mezclas, umbrales) **y**
  operaciones que leen/escriben los bytes de las reglas mismas (una regla puede
  copiar/perturbar la regla de una vecina, o la suya) — esto es lo que permite
  que la física se **reestructure** de verdad (espíritu von Neumann / AlChemy de
  Fontana).
- Todo acotado y total: los programas "malos" no rompen nada; producen salidas
  degeneradas → los caza el filtro de persistencia.
- Reglas cortas (≤ 32 instrucciones): chicas para poder mutar con sentido,
  grandes para ser expresivas.

Aquí la celda **inventa física nueva**, no sólo mueve parámetros dentro de una
familia. Aquí vive la pregunta abierta real — y aquí casi todo colapsa.

**Recomendación honesta:** primero el **Nivel 1** (ver que el lazo late siquiera),
después empujar al **Nivel 2**, sabiendo que colapsará casi siempre y que domarlo
*es* la frontera no resuelta.

---

## Qué observamos (sin imponer una meta)

No medimos "éxito". Miramos si hay **pulso**, describiendo — no premiando:

- ¿Persiste *algo* más allá de unos ticks, o todo se vuelve vacío / todo se
  congela?
- En lo que persiste, ¿las reglas **siguen cambiando** (vivo) o se congelan
  (muerto pero de pie)?
- ¿La física coherente **coloniza** el vacío?
- ¿Aparece **estructura nueva** que no estaba en la semilla (novedad) — patrones
  estables nuevos, familias de reglas nuevas?

### Los dos modos de muerte (nombrarlos con honestidad)
- **Muerte térmica:** todo se vuelve vacío / ruido. La física se suicida.
- **Muerte cristal:** todo se congela, inmutable. Un atractor-jaula un piso más
  arriba. Persiste, pero no deviene.

El estrecho entre esos dos abismos —persistir *y* seguir generando novedad— es
todo el problema.

---

## Decisiones abiertas (los cruces que faltan elegir)

1. **Profundidad de codificación:** Nivel 1 (parámetros) vs Nivel 2 (programa).
   *El cruce central.* (Propuesta: 1 primero, 2 después.)
2. **Espacio:** anillo 1-D (legible) vs grilla 2-D (más rica). *Propuesta: 1-D.*
3. **Tiempo:** actualización sincrónica vs asincrónica. *(Asincrónica suele ser
   más viva y evita artefactos.)*
4. **Semántica del vacío:** permanente vs re-colonizable. *Propuesta:
   re-colonizable* (deja que la vida reclame lo muerto).
5. **Tipo del valor:** escalar vs vector chico. *Propuesta: escalar primero.*
6. **Qué cuenta como "degenerado"** (el umbral de persistencia). **La única
   perilla donde nuestra mano se nota** — mantenerla lo más mínima y no-arbitraria
   posible. Es el punto a vigilar con más honestidad.

---

## Riesgos y honestidad

- **El colapso es casi seguro** en el Nivel 2. Entramos con los ojos abiertos.
- **La novedad perpetua (open-endedness) es un problema no resuelto.** Nadie
  construyó un sistema que genere dimensiones nuevas, propias, sostenidamente,
  sin caer en muerte térmica o cristal. Esto es la frontera de la frontera.
- **Podemos construir la semilla; no el árbol.** El sustrato es construible hoy,
  chico, en tu máquina. Que de ahí crezca algo — puede no pasar nunca.
- **Hasta el filtro sin-meta esconde una elección:** qué es "degenerado". Ahí
  —y sólo ahí— aparece nuestra mano. Mantenerla lo más liviana posible es parte
  de la disciplina.

---

## El primer experimento mínimo (sólo nombrarlo; todavía no construir)

> **Prueba del primer latido.** Nivel 1, anillo 1-D `N = 64`, radio 1,
> actualización sincrónica, vacío re-colonizable, valor escalar. Correr ~500
> ticks. Una sola pregunta, sin meta: **¿evita los DOS modos de muerte —térmica
> y cristal— durante una ventana no trivial?** No es éxito. Es sólo: *¿hay pulso?*

Si hay pulso, recién ahí tiene sentido subir al Nivel 2, donde vive la pregunta
de verdad.

---

## Estado del arte

Relevamiento verificado (2026-09-26) en `ESTADO_DEL_ARTE_UTERO.md`: qué ya
hicieron BFF, Stringmol, AlChemy, Flow-Lenia, Evoloop y la teoría OEE, qué
estaríamos repitiendo, dónde está el hueco, y qué métricas (filtro de
persistencia de linaje, shadow emparejado) hacen falta para que un resultado
de esta línea sea comparable. Leerlo antes de diseñar un mecanismo nuevo.

## Ledger honesto de resultados (cada uno tras su control adversarial)

- **Nivel 1 — primer latido (2026-07-09):** `utero/nivel1.py`,
  `exp_primer_latido.py`. 20/20 semillas con pulso a 500 ticks (0 térmicas,
  0 cristal; muerte+re-colonización reales; seed 0 desarrolla un oscilador
  persistente no programado). Controles: sin ruido de colonización sigue
  20/20; a 5000 ticks la lectura honesta es **cristalización en cámara
  lenta** — sólo 3/20 sostienen cambio macroscópico. *La semilla late pero
  tiende al atractor-cristal.* (`results/utero_primer_latido_run.txt`)
- **Nivel 2 v0 — reglas-programa (2026-07-09):** `utero/nivel2.py`,
  `exp_nivel2_latido.py`. Lenguaje total de 10 ops con MUTO/COPY (reescritura
  de la propia forma) y SPAWN (colonización literal); sin ruido inyectado.
  Ecología real: extinción inicial 75% → recuperación al 70% vía SPAWN;
  cambio de código PLANO a 5000 ticks (no decae como el Nivel 1); 16 genomas
  distintos sostenidos. **Pero el control anti-ciclo lo desenmascara:** 20/20
  semillas en ciclos límite cortos (1–20 estados) — la física reescribe y
  des-reescribe lo mismo para siempre; hasta la muerte/renacimiento entra en
  el bucle. *Atractores más ricos, pero atractores: la novedad perpetua no
  emergió.* Tal como advirtió este boceto: aquí casi todo colapsa.
  (`results/utero_nivel2_run.txt`)

**Lo aprendido:** determinismo + espacio fijo + actualización sincrónica ⇒
recurrencia casi inevitable. Las direcciones que el propio boceto deja
abiertas y que estos resultados vuelven candidatas para v1: actualización
**asincrónica** (decisión abierta #3), espacio **más grande o creciente** (el
adyacente-posible necesita lugar donde abrirse), acoplamiento más rico entre
materia y código. Los tres principios quedan intactos; la encarnación es lo
que debe cambiar.

- **v1 creciente — async + espacio que se abre desde adentro (2026-07-09):**
  `utero/creciente.py`, `exp_utero_creciente.py`. Línea con fronteras: el
  mundo crece SOLO donde una física hace SPAWN hacia el más-allá del borde
  (el crecimiento no es mano nuestra); actualización asincrónica en orden
  aleatorio sembrado; vara de novedad nueva y más dura: **genomas nunca
  vistos por tramo** (con azar en el orden, "no ciclar" ya no prueba nada).
  Resultado: **el espacio SÍ se abre** — 13/20 mundos crecen 16→256 hasta la
  pared, crecimiento hecho por la física misma. **Pero la novedad se seca
  igual:** ~12 genomas nuevos en el primer tramo y CERO después, en las 20
  semillas — idéntico al baseline síncrono (que acuña más al inicio, 78, y
  también muere a 0). El adyacente-posible se abrió en lo ESPACIAL pero no
  en lo ESTRUCTURAL. Diagnóstico: la colonización copia EXACTO (sin
  variación en la reproducción — el ruido lo quitamos a propósito) y los
  eventos MUTO/COPY se apagan cuando la materia se asienta. *La jaula se
  mudó de nuevo: monocultivo / código congelado.*
  (`results/utero_creciente_run.txt`)

**El cruce siguiente (pendiente de decisión):** variación en la reproducción
SIN mano nuestra — que SPAWN no copie exacto sino que escriba **modulado por
la materia** (como ya hace MUTO), de modo que reproducirse en un contexto
distinto produzca código levemente distinto. La variación saldría del estado
del mundo, no de un RNG nuestro. Es la pieza que la vida sí tiene (mutación
acoplada al sustrato) y este útero todavía no.

- **v2 germinal — variación en la reproducción (2026-07-09):** flag
  `germinal=True` en `utero/creciente.py`, `exp_utero_germinal.py`. La cría
  nace con UNA instrucción reescrita desde la materia del momento del parto
  (los campos b,c del SPAWN eligen registro y posición — la física puede
  evolucionar CÓMO varían sus hijas; la función es la de MUTO; sin RNG).
  Resultado: **duplica la novedad temprana** (23.6 vs 12.1 genomas en el
  primer tramo) **pero se seca igual: 0 genomas nuevos en la 2da mitad, en
  las 20 semillas.** Y el diagnóstico quedó afilado: en 3 semillas los
  **partos CONTINÚAN** (3465 nacimientos tardíos) y aún así acuñan CERO
  genomas nuevos — la mutación es determinista sobre la materia, y la
  **materia se asentó**: mismo contexto → misma cría, parto tras parto.
  *La jaula se mudó de la reproducción a la MATERIA CONGELADA.*
  (`results/utero_germinal_run.txt`)

**El cruce siguiente (pendiente de decisión) — la DINÁMICA DE LA MATERIA:**
el cuello de botella ya no es el código: es que la materia converge a puntos
fijos y alimenta toda la variación con lo mismo. Nota matemática honesta: con
`v' = sigmoid(R3)` y registros acotados, la dinámica de materia es
(casi siempre) contractiva — el caos es expresable sólo en franjas finísimas
del espacio de genomas y nada empuja hacia ellas. Opciones sin (o con mínima)
mano nuestra:
  (a) **materia toroidal**: `v' = R3 mod 1` en vez de sigmoid — el envolver
      (wrap) permite mapas expansivos (el doubling map es el caos canónico);
      es incluso MÁS simple que una transcendental. Cambio de física, no de
      metas.
  (b) **un sol**: una celda-frontera cuyo v oscila impuesto — una mano
      DECLARADA pero filosóficamente honesta (la vida terrestre también
      necesitó un gradiente externo permanente; el sol no le dice a la vida
      qué ser, sólo le impide asentarse).
  (c) ambas.

- **v3 toroidal — materia en un círculo (2026-07-09): PRIMERA NOVEDAD
  SOSTENIDA.** Flag `toroidal=True` (`v' = R3 mod 1`; sonda con separación
  irracional 0/0.618 porque 0 y 1 son el mismo punto del toro),
  `exp_utero_toroidal.py`. Resultado (20 seeds × 4000, brazo sigmoid como
  control): novedad tardía **3816 vs 0** del sigmoid. Una semilla (13) entra
  en un régimen sostenido: control a **12.000 ticks → 26.409 genomas** y los
  últimos tramos [419, 278, 697, **1526**] — no decae: **sube**; materia aún
  moviéndose (Δv≈0.14). La figura muestra diferenciación espacial en
  regímenes coexistentes (zona turbulenta = bomba de novedad + llanuras
  asentadas) — nichos emergentes. **Cautelas honestas:** (1) es 1/20 — el
  régimen es RARO, el toro lo hace posible, no típico (¿como la
  abiogénesis?); (2) "genoma nuevo" = combinación nunca vista (vara
  estructural), pero la RIQUEZA FUNCIONAL no está evaluada — podría ser
  paseo caótico por el espacio de código (novedad-ruido) y no novedad
  adaptativa; distinguirlas es el próximo control obligatorio.
  (`results/utero_toroidal_run.txt`)

**El próximo control (pendiente): ruido vs función.** ¿Los genomas tardíos de
la seed 13 HACEN algo (persisten más, colonizan mejor, se re-encuentran) o son
espuma caótica que nace y muere sin dejar linaje? Ideas: rastrear LINAJES
(¿algún genoma tardío funda una población estable?), medir vida media de los
genomas nuevos, comparar contra un null (paseo aleatorio por el espacio de
genomas con la misma tasa de nacimientos).

- **v4 muerte por equilibrio — HIPÓTESIS REFUTADA (2026-07-09).** Flag
  `muerte_equilibrio=True` (una celda con |Δv|<eq_eps por eq_window=100 ticks
  muere): extensión del principio 3 «cristal = muerto de pie», con la
  predicción de que forzaría auto-reparación del motor (asentarse=morir=
  reintentar). **Falló, y en las dos direcciones.** (1) En vez de reparar,
  **extinguió el mundo**: 15/20 muerte térmica (v3 era 2/20) — matar las
  llanuras asentadas eliminó el amortiguador/reservorio y el mundo se vació.
  (2) **Rompió incluso la seed 13**: su novedad —que en v3 subía a 12k
  ticks— se secó antes de t=6000, y la ablación post no regeneró nada
  (post = [0,0,…]). *La presión extra de muerte no crea un motor
  auto-reparable; crea un desierto.* Lección honesta: las llanuras
  «asentadas» no eran cristal muerto sino SUSTRATO — la novedad necesitaba
  ese fondo estable contra el cual moverse. Mi predicción de diseño fue
  incorrecta; el control lo mostró. (`results/utero_motor_run.txt`)

**Lo que esto enseña sobre el motor auto-reparable:** la fragilidad de la
bomba (v3) NO se arregla subiendo la mortalidad. Direcciones distintas, no
probadas: (a) que la turbulencia sea un ATRACTOR dinámico (que las llanuras
tiendan espontáneamente a desestabilizarse en el borde con la zona activa),
no algo impuesto por muerte; (b) aceptar que un motor localizado y frágil
quizá sea lo que HAY en este sustrato — y que la auto-reparación requiera
otra dimensión (p.ej. la memoria/percepción que Fran NO eligió tocar), o un
sustrato distinto. Decisión abierta.

- **v5 memoria — la dimensión no tocada: PRIMERA auto-reparación (2026-07-09).**
  Flag `memoria=True` en `creciente.py`, `exp_utero_memoria.py`. Cada celda
  retiene su R3 crudo (potencial interno, NO la materia observable v — un
  estado oculto tipo membrana, distinto de v porque v es su proyección con
  pérdida en el toro) y lo re-inyecta como R3 inicial el tick siguiente:
  recurrencia / integración temporal, dinámica de 2º orden. La cría nace sin
  recuerdos. Sin manos nuevas; `memoria=False` byte-idéntico a v3.
  **Bug corregido antes de creer nada:** el conteo de novedad post-ablación
  usaba `u._register_genomes()`, que `step()` ya llama internamente → daba 0
  siempre; se pasó a un registro externo (afectaba también la sub-métrica de
  ablación de v4, cuyo veredicto de extinción se sostiene por otra vía).
  Resultado (control ON vs OFF, misma seed 13, ablación de la zona-bomba,
  midiendo la COLA sostenida y no el pulso de recolonización): **en el
  régimen MADURO (ablación a t≥8000) cola/pre = 2.05 con memoria vs 0.10 sin**
  — el motor se auto-repara donde v3 colapsaba a ~0. Es el 3er criterio del
  control ruido-vs-función, recuperado, en el régimen donde importa.
  **Matices honestos:** (1) NO universal — en la ablación TEMPRANA (t=6000)
  ambos regeneran y OFF hasta gana (1.31 vs 0.48): el sistema joven aún tiene
  momentum de la sopa; la memoria ayuda cuando el motor ya depende de sí
  mismo. (2) n=1 semilla (sólo la 13 sostiene). (3) la memoria NO hizo más
  típico el régimen (sigue 1/20). *Primera pieza que mueve la auto-reparación
  en la dirección correcta — no un triunfo cerrado.*
  (`results/utero_memoria_run.txt`)

- **Réplica de v5 en 40 semillas — INCONCLUSO por rareza del régimen; la
  auto-reparación NO generaliza a la 2ª semilla madura (2026-09-26).**
  `exp_utero_memoria_semillas.py`; protocolo de v5 extraído a
  `utero/ablacion.py` y testeado contra sus números (543/3525/950 en la 13).
  Semillas 0–39, memoria ON vs OFF, ablación a t=8000 y t=10000, más el
  **control sin ablar** que a v5 le faltaba (cola/pre<1 podía ser deriva
  natural de la novedad, no daño). Varas y regla de veredicto escritas en el
  docstring ANTES de correr. Resultado: **INCONCLUSO** por la regla
  pre-registrada — sólo 2/40 semillas llegan con motor vivo a t≥8000
  (ON: 13 y 35; OFF: 13 y 23 a 8000, sólo la 13 a 10000), pareadas n=1. **El
  cuello de botella no es la memoria sino la rareza del régimen maduro.**
  Tres hechos que el n=1 de v5 no podía ver: (1) **la 13 replica** en
  ambos tiempos con la vara nueva (R = cola ablada/cola sin ablar: 2.64 y
  2.66 ON vs 0.11 y 0.02 OFF) — es real, no artefacto de la medida. (2) **La
  35 con memoria es un contraejemplo:** motor mayor que el de la 13 (3.908
  genomas nuevos en 1.000 ticks, sostenido a 14.000) que **no se repara**:
  vaciar 66 de 198 celdas lo apaga para siempre (cola 0, vivas 137 al final).
  La memoria no confiere auto-reparación por sí sola; en la 13 hay algo más
  (geometría, borde, composición) que no sabemos nombrar. (3) **Reencendido
  por perturbación** (observación post-hoc, no vara): 35-OFF llega a t=8000
  con novedad 0 (201 celdas vivas, recurrente, sin acuñar) y vaciar 57 de
  ellas lo *reenciende* — acuña 8.581 genomas en el pulso y 1.728/tramo en
  la cola, más que cualquier motor vivo; se repite a t=10000 (764/tramo) y
  en 23-OFF a t=10000 (pre≈1 → cola 399/tramo tras vaciar 27 celdas). El vacío abierto
  desde afuera hace lo que el sustrato no logra solo: desatascar un mundo
  recurrente. Es la señal más fuerte hasta ahora de que la jaula actual es la
  **falta de perturbación endógena** (dirección (a) de v4: turbulencia como
  atractor), no la falta de memoria. *Lectura honesta: v5 queda como n=1
  verificado, no típico; la memoria ayuda a sostener (2/40 vs 1/40 a
  t=10000, n irrelevante) pero no a reparar en general.*
  (`results/utero_memoria_semillas_run.txt`)

- **Anatomía comparada 13 vs 35 — lo que distingue es la FERTILIDAD DE LAS
  LLANURAS, no la geometría ni la memoria (2026-09-26).**
  `exp_utero_anatomia.py`: ambas semillas diseccionadas en t=8000 (memoria
  ON) y seguidas 4000 ticks tras la ablación; seed 0 de referencia; seis
  hipótesis H1–H6 con su medida y criterio (≥2×) escritas ANTES de correr,
  dos más (H7, H8) añadidas post-hoc y marcadas así. **Lo que NO distingue
  (refutado):** H1 geometría — misma fracción activa (0.33), mismo número
  de segmentos (10 vs 11), llanura mayor 126 vs 117; H2 reservorio lento —
  fracción 0.00 en ambas: la cadencia es bimodal (la bomba reescribe cada
  <50 ticks, las llanuras nunca en >2000; ventanas 50–400 dan la MISMA
  ablación); H3 capacidad — el 100% de los sobrevivientes de ambas portan
  MUTO/COPY y SPAWN; y una prueba aparte refutó mi hipótesis de que la física
  de las llanuras de la 35 necesitara su memoria para pasar la sonda (ciega
  con mem=0: 0.01). H6 (|mem| en el borde 1.0 vs 0.5) roza el criterio con
  15 vs 6 celdas: no lo cuento. **Lo que SÍ distingue:** H5 — la 35
  sobrevive a una ablación ALEATORIA de 66 celdas (R 0.51/0.83/1.33) y muere
  a la de la bomba (R=0): lo que la mata es perder la bomba, no perder
  celdas. H4 — tras la ablación las llanuras de la 35 colonizan el hueco 6×
  MÁS que las de la 13 (1.326 vs 201 en 1000 ticks) y las vivas no suben
  (134→137): **crías que nacen y mueren.** H8 (post-hoc) lo mide: en la 13,
  144 nacimientos, **80 genomas distintos**, vida mediana 4000 (llegan al
  final), 76% supera 100 ticks; en la 35, 699 nacimientos, **6 genomas**,
  vida mediana **1 tick**, 1% supera 100. Y el control sin ablar muestra que
  la 35 YA paría así antes: 713 crías en la misma ventana, 35 genomas,
  mediana 2 ticks — un churn perpetuo de nacidos muertos que la bomba
  enmascaraba. H7 (post-hoc): las llanuras de la 13 cambian de código al
  perder un vecino 3.5× más (0.07 vs 0.02) y parirían 43 crías distintas
  contra 10. **Lectura:** la jaula de v2 («mutación determinista + materia
  asentada = misma cría, parto tras parto») sigue viva DENTRO del mundo de
  v5: las llanuras de la 35 son un útero estéril, y la bomba era su único
  tejido fértil; en la 13 el tejido asentado sigue siendo fértil (crías
  diversas y viables) y por eso re-nuclea la turbulencia en el borde del
  hueco. La auto-reparación no la da la memoria: la da la fertilidad del
  fondo. **Predicción a testear (no conclusión, n=2):** la fertilidad de las
  llanuras —diversidad y viabilidad de sus crías, medible SIN ablar— predice
  la auto-reparación; y la vía hacia un motor auto-reparable típico es hacer
  fértil el tejido asentado (que la variación germinal no dependa de una
  materia que ya no se mueve), no sumar memoria ni mortalidad.
  (`results/utero_anatomia_run.txt`, `results/utero_anatomia.png`)

- **Filtro de persistencia de linaje (MODES) + corrida SOMBRA (Bedau) en 40
  semillas — el 2/40 es DEFENDIBLE con la vara de la literatura; sin la
  sonda, el copiador trivial se apodera del mundo en <250 ticks (2026-09-26).**
  `exp_utero_linaje_sombra.py`; ganchos de observación en `creciente.py`
  (`log_events`, `shadow_deaths`, `deaths` en el retorno; byte-idéntico con
  los flags apagados, testeado) y `utero/linaje.py` (`RastreadorLinaje`). El
  estado del arte objetó nuestra vara por dos lados: cuenta acuñación y no
  persistencia (se infla por deriva) y no tiene sombra neutral. Se aplicaron
  ambas correcciones, con varas y veredicto pre-registrados. **Filtro:** un
  genoma cuenta sólo si t_filtro ticks después sigue viva su LÍNEA (la celda
  o sus crías por SPAWN); t_filtro ∈ {100, 500, 2000}. **Sombra:** misma
  semilla y sustrato, mismo número de muertes por tick que la corrida real,
  pero al azar en vez de por la sonda (la única selección). Resultado: (1) la
  vara casi no estaba inflada en el régimen maduro — de la novedad cruda de la
  13 persiste el **100%** y de la 35 el **79%**, insensible a t_filtro (100 a
  2000 dan lo mismo); en el tramo inicial (la sopa) sí se pierde ~40–60%,
  como MODES predice. (2) **Sostenido filtrado: las mismas 2/40 (13 y 35)**
  con los tres t_filtro, y ninguna nueva. (3) **La sombra acuña CERO genomas
  nuevos desde t≈500 en las 40 semillas**: verificado a mano en la 13 — a los
  250 ticks un único genoma ocupa las 242 celdas vivas, `code_change` y
  `value_change` exactamente 0. Sin la sonda, una física ciega a la materia
  (que sobrevive porque nadie la mata) barre el mundo por SPAWN y lo congela:
  el copiador trivial de Fontana (AlChemy 1994), reproducido. **Lectura:** el
  principio 3 no es contabilidad neutra — la sonda es lo que impide la
  monocultura y mantiene la materia en movimiento; TODA la novedad medida
  es actividad por encima de la deriva (clase 2/3 de Bedau, no clase 1). La
  ecología (Shannon de genomas persistentes por tramo) es 4.8 bits en la 13
  y 10.0 en la 35, contra 0 en las sombras. Matiz honesto: la sombra es un
  control de *selección*, no de *variación*; que la deriva sola dé cero no
  dice que la novedad real sea adaptativa, sólo que no es deriva.
  (`results/utero_linaje_sombra_run.txt`, `.png`)

- **Interacción efectiva regla↔regla — NO existe en las llanuras; el motor
  actual es MUTO (germinal), no ecológico; las 4 predicciones fallaron
  (2026-09-26).** `exp_utero_interaccion.py`, con `execute(stats=)` y
  `log_events` (observación pura). El estado del arte apuntaba a que el motor
  sostenido es ecológico (parasitismo en Stringmol, colisión/sexo en
  Evoloop); COPY entre vecinos de genoma distinto —transferencia horizontal,
  TH— es esa interacción en potencia. Medido en 40 semillas (régimen maduro):
  **P1 falla** — TH en las llanuras es **0.0000** en la 13 y en la 35; el
  cambio NETO de código en las llanuras es 0 en ambas. **P2 falla** — la TH
  temprana no predice la novedad tardía (Spearman ρ=+0.28, p=0.08); las
  semillas con MÁS TH (18, 32, 28, 26: ~0.14 por celda-tick) tienen novedad
  tardía **cero**: son bucles de copia entre dos genomas — interacción sin
  variación = ciclo, no novedad. **P3 se invierte** — la fracción de novedad
  atribuible a TH es 3.3% en la 13 y 11.1% en la 35. **P4** — la novedad viene
  de MUTO sola: **96.6%** (13) y **86.0%** (35); de los cambios netos en la
  bomba, 96–97% son sólo MUTO y 1–2.6% involucran TH. **Hallazgo colateral
  (medida bruta vs neta):** las llanuras de la 13 ejecutan MUTO/COPY
  efectivas en el 7.7%/6.5% de sus celda-ticks y aun así su código neto no
  cambia nunca: **reescritura idempotente** — programas que se reescriben en
  sí mismos dentro de una ejecución. La llanura no es un programa inerte sino
  un punto fijo de la auto-reescritura; la bomba es donde la auto-reescritura
  tiene efecto neto. **Lectura:** el Útero de hoy no tiene el motor que la
  literatura señala; su novedad es auto-mutación acoplada a la materia (MUTO
  escribe el opcode `int(|R|·10)`, y R es materia), lo que explica de raíz
  que se seque cuando la materia se aquieta (v2) y que la fertilidad de las
  llanuras sea la variable crítica (anatomía). La transferencia horizontal
  existe en la bomba pero es marginal, y la fertilidad de la 13 NO se explica
  por ella. Predicción para el próximo cruce: si se quiere un motor
  ecológico, hay que hacer que COPY entre genomas distintos tenga efecto neto
  en tejido asentado — hoy no lo tiene en ninguna semilla.
  (`results/utero_interaccion_run.txt`, `.png`)

- **v6 invasión de tejido asentado — la regla pre-registrada disparó
  "ILUSIÓN" por un criterio mal diseñado; lectura honesta: PARCIAL, señal
  débil, no un motor típico (2026-09-26).** Flag `invasion="asentada"` en
  `creciente.py` (un SPAWN dirigido a una celda viva con materia quieta
  eq_window=100 ticks la REEMPLAZA; reemplazo, no muerte; `None`
  byte-idéntico a v5, 7 tests) y `exp_utero_invasion.py`: 40 semillas ×
  {v5, v6, sombra de v6} + ablación en las sostenidas. **Resultados:** (1)
  tipicidad filtrada (linaje 500, ≥2× sombra) **2/40 → 3/40**: entra la
  seed 21 (0 → 1.814 genomas persistentes/tramo), la 13 sube (381 → 814) y
  la 35 baja (1.227 → 637). (2) Ecología de las sostenidas 9.3 bits mediana
  (mín 3.4): **no hay monocultura**. Pero la regla de veredicto usaba también
  "cuota del genoma dominante < 0.5" y la mediana dio 0.500 → disparó
  ILUSIÓN. **Ese criterio estaba mal diseñado:** la cuota la dominan las
  llanuras, clonales por naturaleza, y la propia v5 la incumple (cuota v5:
  13 = 0.498, 35 = 0.532, 21 = 0.902; v6: 0.500, 0.353, 0.691 — la invasión
  la BAJA en dos de tres). Lo registro como falla mía de pre-registro, no la
  reinterpreto como éxito. (3) Anti-ilusión de partos: 0% de la novedad
  madura viene de parto/invasión — la invasión no acuña por sí misma, mueve
  el tejido y MUTO acuña después. (4) **Auto-reparación: 1/3.** La 13 mejora
  (R 2.64 → 4.35), la 35 pasa de 0.00 a 0.47 (justo bajo el umbral: el
  primer indicio de reparación en esa semilla), la 21 no se repara (R=0). (5)
  Efecto colateral grande: **v6 mantiene vivos los mundos** — vivas al final,
  mediana de 40 semillas, 246 contra 12 en v5 (donde la mayoría muere
  térmicamente) — pero vivos y **quietos**: sin novedad y con ecología 1–4
  bits; la invasión convierte desiertos en cristales. (6) Aviso sobre la
  vara: la sombra de v6 de la seed 33 acuña 3.310 genomas persistentes/tramo
  con la real en 0 — con invasión, muerte-al-azar + reemplazo generan novedad
  "persistente" por deriva; el criterio ≥2× sombra por semilla lo absorbe,
  pero la sombra ya no es trivialmente cero como en v5. **Lectura:** la
  interacción regla↔regla con efecto neto en tejido asentado existe ahora
  (0.8 invasiones/tick mediana, 27/40 semillas) y ayuda donde ya había motor
  (13, 35-reparación, 21-novedad), pero no crea motores donde no los había:
  la tipicidad sigue siendo 3/40. Refuerza la lectura de la anatomía: lo que
  falta no es que la variación LLEGUE a la llanura sino que la llanura la
  CONVIERTA en crías viables y distintas (fertilidad). Próximo control
  obligatorio antes de creer el 3/40: `invasion="siempre"` (sin umbral) y
  barrido de eq_window, para separar el efecto de la invasión del de la mano
  declarada. (`results/utero_invasion_run.txt`, `.png`)

- **Control de v6 — LA MANO TRABAJA, pero no está afinada: sin umbral la
  invasión destruye toda persistencia; con cualquier umbral entre 10 y 1000
  ticks el resultado es el mismo 3/40 (2026-09-26).**
  `exp_utero_invasion_control.py` (sobre `utero/medidas.py`, la corrida
  medida compartida): cinco brazos × 40 semillas × 14000 ticks — v5,
  `invasion="siempre"` (sin umbral), `asentada` con eq_window 10 / 100 / 1000;
  sombra para las candidatas; ablación en las sostenidas. Vara igual que v6
  menos el criterio de cuota absoluta (reemplazado por cuota RELATIVA a v5 y
  monocultura por ecología — la lección de v6). **Resultados:** (1)
  **"siempre" = 0/40**: 245 invasiones por tick de mediana (el mundo entero
  se reescribe cada tick), ecología 0 bits, ningún genoma persiste 500 ticks;
  mundos llenos (247 vivas) de churn puro. Sin umbral no hay persistencia y
  sin persistencia no hay novedad que cuente. (2) **Dosis: 3/40 con
  eq_window 10, 100 y 1000** — insensible al valor en tres órdenes de
  magnitud; la identidad cambia en el margen (13 y 35 siempre; la tercera es
  21 con 10 y 100, 37 con 1000), así que la tipicidad se lee como CONTEO. La
  cuota dominante relativa a v5 es 0.77–0.81 en los tres: la invasión
  desconcentra, no concentra. (3) Auto-reparación en las sostenidas: 1/3,
  1/3, 2/3 (eq_window 1000: 13 R=0.98, **35 R=0.52** — cruza el umbral por
  primera vez; 37 no). La R de la 13 varía 0.95–4.35 entre brazos: ruidosa,
  n=1 por brazo. (4) Vivas al final 246 en todos los brazos con invasión
  contra 12 en v5: el efecto "mantiene vivo" tampoco depende del umbral.
  **Lectura:** el umbral de quietud no es un parámetro que haya que ajustar
  sino una **condición cualitativa**: lo que sigue deviniendo no puede ser
  reescrito; lo que dejó de devenir, sí. Es la formulación positiva del
  principio 3 (v4 la formuló en negativo, como muerte, y dio un desierto;
  como reemplazo, da tejido vivo y reescribible). Con eso, el v6 queda como
  **PARCIAL robusto**: 3/40 estable frente al umbral, sin monocultura, con
  auto-reparación intermitente — y sin resolver lo de fondo, que la llanura
  convierta variación en crías viables y distintas. Lo que la invasión hace
  es mantener el tejido vivo y desconcentrado; lo que no hace es crear
  motores donde no los hay. (`results/utero_invasion_control_run.txt`, `.png`)

- **Mortalidad infantil — las crías de llanura nacen CIEGAS (100%) y son
  siempre la misma; la auto-mutilación queda refutada; en régimen
  estacionario las llanuras de TODAS las semillas son estériles
  (2026-09-26).** `exp_utero_mortalidad_infantil.py`: cada cría nacida en
  [8000,9000) (v5, memoria ON) seguida 500 ticks y clasificada; cinco
  hipótesis pre-registradas. Antes, un sondeo (no publicado) había refutado la
  explicación genética: el 85–91% de los mutantes de un opcode de cualquier
  genoma pasan la sonda en el contexto de la madre — nueve de cada diez crías
  POSIBLES nacen viables (13: 85%, 35: 91%, 21: 83%). **Resultado:** (1) la 13
  y la 21 **no paren** en la ventana: el mundo está lleno (249/256) y no hay
  vacío junto a una paridera; su fertilidad sólo se manifiesta cuando la
  ablación abre espacio. (2) La 35 pare 674 crías de llanura: **100% ciegas al
  nacer** en su contexto real (mem=0), 48% mueren en la primera ejecución y
  52% mueren y son recolonizadas en el mismo tick — es decir, todas mueren al
  primer tick; **0% auto-mutilación** (H1 refutada); **1 solo genoma** en 674
  nacimientos. La mutación germinal determinista (posición fija por el campo
  c del SPAWN, opcode desde |R[b]| con registros quietos) cae SIEMPRE en el
  mismo mutante, y ese mutante está entre el ~10% letal. Un **punto fijo
  letal del mapa germinal**: la llanura se reproduce sin cesar hacia la muerte
  y, como ninguna cría la desplaza, persiste — la esterilidad se
  auto-preserva. (3) Agregado sobre las 6 semillas con ≥10 nacimientos de
  llanura (5, 6, 27, 28, 34, 35; 3.743 crías): 71% ciegas al nacer, 36% mueren
  en la primera ejecución, 49% reemplazadas, 15% auto-mutilación (concentrada
  en las semillas 5 y 28, con k=1), **0% sobrevive 500 ticks, 0% de genomas
  distintos**. La esterilidad de la llanura no es una propiedad de la 35: es
  el estado estacionario del sustrato. **Lectura:** la fertilidad de la 13 tras
  la ablación no era un tejido fértil en reposo sino un tejido DIVERSO (44
  genomas de llanura contra 16) que, cuando se abre espacio, pare 80 hijos
  distintos porque cada madre distinta cae en un mutante distinto y algunos
  son viables. La variable no es "fertilidad" sino **diversidad de madres ×
  determinismo del mapa germinal**. Dos consecuencias de diseño, ambas sin
  RNG: (a) que el mapa germinal no dependa sólo del estado quieto de la madre
  sino de un segundo progenitor — recombinación por contacto, la respuesta de
  Evoloop/Sexyloop a este mismo problema; (b) que la diversidad de madres sea
  mantenida (v6 desconcentra, cuota 0.77–0.81, pero no alcanza).
  (`results/utero_mortalidad_infantil_run.txt`, `.png`)

- **v7 recombinación al nacer — SIN EFECTO en tipicidad (3/40), pero el
  mecanismo funciona y destapa la jaula siguiente: el barrido del clon
  viable (2026-09-26).** Flag `recombina=True` (la cría toma UNA instrucción
  del vecino de la madre del lado opuesto al parto, en el locus b%K del
  SPAWN, si su genoma difiere; cero RNG; `False` byte-idéntico, 6 tests) y
  `exp_utero_recombina.py`: v5 · v7 · v6+v7, 40 semillas, sombra, ablación y
  seguimiento de crías. **Resultados:** (1) **la recombinación rompe el punto
  fijo letal**: las crías de llanura de la 35 pasan de 100% ciegas al nacer a
  **0%**; en v7 solo, la 35 y la 13 ya no paren a t=8000 porque el mundo se
  llenó (las crías viables ocuparon el vacío). (2) Tipicidad filtrada: v7 solo
  **1/40** (la 13 baja de 381 a 171 y **la 35 colapsa a 0**); v6+v7 **3/40**
  (13, 21, 37), igual que v6. (3) **La 35 se vuelve monocultura**: ecología
  0.07 bits en v6+v7 y 1.14 en v7; 2.386 crías de llanura con **un solo
  genoma**. Liberada la fertilidad, un clon viable con ruta de copia
  confiable barre el tejido — el atractor del copiador trivial, esta vez
  sensible a la materia y por eso invisible para la sonda. Irónicamente, la
  cría letal era lo que preservaba la diversidad de la 35. (4)
  Auto-reparación mejora donde hay motor: v6+v7 repara 2/3 (13 R=3.64; **21
  R=0.89, primera vez**); v7 solo no (13 R=0.19). **Lectura:** la cadena de
  jaulas suma un eslabón — cristal → ciclos → monocultivo → materia congelada
  → bomba frágil → llanura estéril (punto fijo letal) → **barrido del clon
  viable**. Con tres mecanismos distintos (memoria, invasión, recombinación)
  el techo es 3/40 y la 13 es la única que resiste todos. El límite ya no es
  la variación (llega y es viable) sino el **mantenimiento de la
  diversidad** contra el clon que barre — que en la literatura no lo resuelve
  ningún filtro de persistencia sino la estructura espacial, la conservación
  de un recurso o el parasitismo (MCC, Flow-Lenia, Stringmol). En una línea
  1-D con dos vecinos la estructura espacial es mínima: es el momento de
  cambiar de perspectiva, no de agregar otro flag.
  (`results/utero_recombina_run.txt`, `.png`)

- **Control ruido-vs-función (2026-07-09): FUNCIÓN, 2/3 — con matices.**
  `exp_utero_ruido_vs_funcion.py`, vara definida ANTES de mirar. Línea base
  espuma: intervalo de reescritura ~3.2 ticks. Sobre 6.198 genomas tardíos
  (t≥6000): **(1) Propagación: SÍ** — 17.1% visita ≥2 celdas; pero pop
  simultánea ≥2 sólo 0.6%: los genomas *viajan* más de lo que *replican* —
  **estructuras itinerantes persistentes, tipo glider**. **(2) Persistencia:
  SÍ** — 24.7% vive >10× la línea base; los top viven ~5.800 ticks (mediana
  0: distribución bimodal — mucha espuma + una cola pesada de estructura;
  nota honesta: "vida" = lapso primera↔última aparición, no existencia
  continua verificada — aunque re-acuñar por azar el mismo genoma exacto en
  un espacio astronómico también sería estructura, no ruido uniforme).
  **(3) Regeneración post-ablación: NO** — matadas las 122 celdas activas en
  t=8000, la novedad estalla (recolonización) y luego muere: 383→70→…→3. La
  bomba NO se regenera. *Lectura honesta: hay función — estructuras
  persistentes que viajan — pero el MOTOR de novedad es frágil: depende de
  la configuración turbulenta particular y no se auto-repara (no es
  autopoiético todavía).* (`results/utero_ruido_vs_funcion_run.txt`)

---

*Estado: boceto vivo. Los tres principios están firmes; la encarnación es
tentativa y va a cambiar al tocar tierra. — v0, escrito a mano junto a Fran.*

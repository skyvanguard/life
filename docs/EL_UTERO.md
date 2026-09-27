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

- **Robustez de escala — la rareza es intrínseca: ni el tamaño del mundo ni
  el muestreo la explican (2026-09-26).** `exp_utero_escala.py`: (A) mundo
  4× más grande (max_n=1024), semillas 0–39; (B) 80 semillas nuevas (40–119)
  a 256; v5 y v6 (asentada-100); misma vara (linaje 500, ≥2× sombra).
  **Resultados:** a 1024 celdas v5 = 2/40 (las mismas 13 y 35) y v6 = 4/40
  (13, 21, 35, 37) — la pared no era jaula ni sostén. Con 80 semillas nuevas
  a 256: v5 = 3/80 (47, 61, 103), v6 = 4/80 (47, 105, 108, 115); ambas
  dentro del intervalo de Wilson del 40 previo. **Tasas combinadas (n=120): v5
  5/120 = 4,2% [1,8–9,4], v6 7/120 = 5,8% [2,9–11,6].** La ecología de las
  sostenidas se mantiene (5–7 bits). **Lectura:** el 2–3/40 no era suerte de
  muestreo ni un artefacto de la placa: es la tasa del sustrato 1-D. Con
  n=120 la mejora de v6 sobre v5 (5,8% vs 4,2%) es real pero pequeña y no
  distinguible estadísticamente. Junto con v7, cierra la línea 1-D como
  sustrato donde la novedad sostenida es posible pero rara (~5%), y justifica
  el cambio de perspectiva a dos dimensiones (v8, `utero/plano.py`).
  (`results/utero_escala_run.txt`)

- **v8 el plano — sustrato construido y testeado; la corrida completa quedó
  pendiente (2026-09-26).** `utero/plano.py` (`UteroPlano`): el mismo sustrato
  con vecindario de von Neumann, registros [vN, vE, vS, vO, v, R], placa 32×32
  con bordes, bloque vivo inicial 8×8 (elegido porque con él la placa se
  coloniza —250 a 800 vivas—, juzgado por vivas, no por novedad), dirección del
  parto `(a + |R[b]|·4) mod 4` modulada por la materia (con dirección fija por
  genoma el crecimiento avanza en rayos y la placa queda en 160–320 vivas), y
  todos los flags heredados. Misma interfaz (`genomas()`, `vaciar()`) para que
  la vara honesta corra sin cambios (`fabrica=`). 10 tests. **Sondeo (12
  semillas, 2000 ticks, régimen inmaduro):** 5/12, 9/12 y 7/12 sostenidas en
  los tres brazos, con ecología 9–10 bits — mucho más que la línea, pero a
  t≈1000–1500, antes de que la novedad se seque. **La corrida completa
  (`exp_utero_plano.py`, 3 brazos × 40 semillas × 14000 ticks) fue detenida
  por el sistema por falta de memoria**: en 2-D se acuñan ~1e5 genomas por
  corrida y la vara los guardaba enteros (512 bytes) en contadores por tramo,
  ×20 procesos. Corregido: huellas de 8 bytes (`huella()`, blake2b) para toda
  observación de genomas (dinámica intacta, 98 tests) y la mitad de obreros
  para el plano. Queda lista para relanzar; el veredicto pre-registrado está en
  su docstring y no se tocó.

- **Del orden a la inteligencia — el sol visible: NADA (2026-09-26).**
  `docs/PLAN_INTELIGENCIA.md` fija la definición operativa (Ashby / Conant &
  Ashby / Beer: regulación, anticipación, aprendizaje por recurrencia,
  organización) y qué contaría como vestigio ANTES de mirar. `utero/sol.py`:
  estaciones A→B→C en orden fijo (regularidad aprendible), duraciones de un
  mapa logístico en [300, 900] (típicas pero impredecibles), un día dentro de
  cada estación. `UteroCreciente(sol=)`: el VACÍO (interior y más allá) lleva
  la materia del sol; verificado que un sol sólo en los dos extremos no cambia
  la materia de la seed 13 en 600 ticks (sin superficie de contacto).
  `utero/inteligencia.py`: las varas con nulos por permutación, testeadas con
  un bump inyectado, con ruido y con un modelo reflejo. `exp_utero_sol.py`: 40
  semillas × {sol, sin sol, sombra}, 20000 ticks, sustrato v6. **Resultado:**
  R no negativa (vivas 248 vs 246; el sol *destraba* mundos: 18 semillas con
  novedad madura contra 5 sin sol, aunque la mediana sigue en 0); **A: 2/40
  con sol, 0 sin sol, 2 en la sombra; L: 1/40 con sol, 2 sin sol, 5 en la
  sombra** — tasas de falsos positivos, no señal (p binomial 0.60 y 0.87).
  Acople del borde con el sol 0.12, del interior 0.009. **Lectura:** el sol
  es visible pero no CONSECUENTE: nada en la persistencia depende de él, y un
  tejido que no necesita al entorno para seguir siendo no tiene por qué
  modelarlo (Ashby: la regulación aparece cuando la perturbación amenaza las
  variables esenciales). Siguiente paso, ya en el plan: que el clima cuente
  para la sonda. (`results/utero_sol_run.txt`, `.png`)

- **El sol consecuente (`sol_sonda`): la regla pre-registrada disparó
  "VESTIGIO" por anticipación en el umbral mínimo; NO se cree hasta replicar
  (2026-09-26).** `sol_sonda=True`: la sonda de ceguera se referencia a la
  materia actual del vacío (sol(t), sol(t)+h) en vez de (0, h): "una física que
  no distingue el mundo de hoy de otro es ciega" — principio 3 con una
  referencia menos arbitraria; byte-idéntico sin sol. Misma corrida de 40
  semillas con cuatro brazos (visible, consecuente, sin sol, sombra del
  consecuente). **Resultados:** R ok en ambos (vivas 248/246 vs 246; ambos
  soles destraban 18 semillas con novedad madura contra 5; muertes/tick en
  maduro **0.000**: el tejido maduro está congelado bajo el sol). **A:
  visible 2/40 (0, 1), consecuente 3/40 (0, 1, 12), sin sol 0, sombra 1** →
  la regla (≥3 y ≥2× control) disparó para el consecuente; p binomial contra
  la tasa nominal 0.32 (esperado 2/40 al 5%). **L:** visible 1, consecuente 1,
  sin sol 2, sombra 5 — nada. Un diagnóstico aparte (4 semillas) mostró que
  la actividad es PLANA alrededor de los inicios de estación en todos los
  brazos y que la superficie no sigue al sol (`v_borde` constante): el tejido
  apenas siente el clima, con o sin sonda climática. **Lectura honesta:** el
  umbral de 3/40 que pre-registré es débil (la tasa nominal ya da 2); las
  semillas 0 y 1 son positivas también en el brazo visible; y un tejido que no
  siente el clima no puede anticiparlo. Lo más probable es un falso positivo
  del umbral. Por protocolo, antes de creerlo: réplica con otros dos
  sembrados del sol y con el orden de estaciones permutado
  (`exp_utero_sol_replica.py`, `Sol(orden="permutado")`), y en paralelo el sol
  que CALIENTA (`sol_acople=κ`: la superficie recibe materia del sol, v ←
  (1−κ)v' + κ·sol), con el que el diagnóstico sí mostró contacto (corr borde–
  sol 0.89; muertes ×3–16 al inicio de estación). (`results/utero_sol_run.txt`)

- **Réplica del "vestigio": FALSO POSITIVO (2026-09-26).**
  `exp_utero_sol_replica.py`: mismo sustrato y `sol_sonda`, 40 semillas, con
  dos soles nuevos (seeds 1 y 2, mismo orden A→B→C), el sol 0 con el **orden
  de estaciones permutado** (mismas duraciones, sucesor al azar: sin
  regularidad aprendible), sin sol y sombra. **Anticipación positiva: sol1
  3/40, sol2 2/40, permutado 6/40, sin sol 0, sombra 2.** El control sin
  regularidad dio MÁS positivas que los soles con orden; acumulado en tres
  soles 8/120 contra 6 esperados al azar (p 0.25). Aprendizaje: 3, 1, 1, 2,
  2 — nada. Veredicto por la regla pre-registrada: **FALSO POSITIVO**; el
  3/40 de la corrida 2 era la tasa nominal del umbral. La disciplina funcionó:
  el hallazgo murió en su control antes de creerlo. Lecciones para la vara:
  (1) un umbral de 3/40 al 5% es débil (esperado 2); el criterio útil es el p
  binomial del conteo o la comparación pareada con el brazo permutado; (2) el
  estadístico de anticipación dispara en tejidos que NO sienten el clima
  (muertes 0 en maduro), así que mide fluctuaciones internas: la condición de
  contacto debe ser previa a cualquier lectura. Con el sol que calienta
  (`sol_acople`) el contacto sí existe; esa corrida es la que puede decir algo.
  (`results/utero_sol_replica_run.txt`)

- **El sol que calienta (`sol_acople=0.5`, 40 semillas): SIN CONTACTO en la
  semilla mediana — el tejido maduro es un cristal (2026-09-26).**
  `exp_utero_sol_acople.py` (la corrida murió por un bug de indexación al
  final —`KeyError: 'rho'` en la lectura A_m—; se rescató del log lo que
  imprimió antes; bug corregido). Con κ=0.5 la superficie SÍ sigue al sol
  (corr borde–sol **0.92**, contra 0.12 del sol visible): el contacto físico
  existe. Pero **muertes/tick en maduro = 0.000 en la mediana**, muertes
  post/pre al inicio de estación 0.60 (calor) y 1.00 (calor+sonda),
  amortiguación 0.007: la superficie se mueve y el interior no se entera; nada
  muere, nada cambia. R ok (vivas 227/222 vs 246; el calor destraba 22
  semillas con novedad madura contra 5). Anticipación sobre actividad: calor
  1, calor+sonda 2, sin sol 0, sombra 3 — azar. **Lectura:** el problema ya no
  es la superficie de contacto sino la INERCIA del tejido maduro: es un
  cristal con una bomba; el sol calienta la piel de un cristal. Un tejido sin
  variables esenciales que el entorno amenace no tiene nada que regular
  (Ashby), y la sonda de ceguera casi nunca muerde a un tejido maduro. Dos
  caminos: darle al tejido una variable esencial que el clima amenace (una
  mano nueva), o llevar el sol al PLANO, donde el tejido no es un cristal
  (novedad y ecología altas en la mayoría de las semillas del sondeo) y la
  superficie de contacto es grande (paredes + vacíos interiores). Se elige el
  plano: es la línea del plan (§5.3) y no agrega manos.

- **El sol en el PLANO, con la vara enmendada: NADA (2026-09-26).**
  `exp_utero_sol_plano.py`: placa 32×32, bloque 8×8, memoria + invasión,
  sol que calienta (κ=0.5) + sonda climática; 20 semillas × 5 brazos (clima
  A→B→C, ciclo2 A→C→B, permutado, sin sol, sombra), 12000 ticks; contacto
  bilateral, p binomial, ≥2× controles y ≥2× permutado, y la lectura R2
  (regulación por orden: muertes pareadas clima vs permutado, con ciclo2 como
  control de los tipos de transición). Un humo temprano (2 semillas, 6000
  ticks) había mostrado respuesta al clima —muertes ×2.7 al inicio de estación
  bajo el orden permutado, ×0.45 bajo el cíclico, y tasa total triple en el
  permutado—. **En la corrida madura desaparece:** la placa se llena (1024
  vivas en todos los brazos), muertes/tick 0.04–0.07, contacto 0.82–1.00; R2:
  clima < permutado en 9/20, ciclo2 en 10/20 (azar); lecturas A/A_m/L/L_m al
  nivel de los controles (el brazo SIN sol tiene 5 positivas de anticipación:
  la tasa de falsos positivos del método, como debe ser). **Lectura:** el
  mismo cuadro que en la línea, un piso más arriba: mientras el tejido crece
  y muere, siente el clima; cuando satura, se vuelve inerte a él, porque nada
  esencial depende del entorno. Cierra la fase 3 del plan como negativo
  honesto. El camino que queda es el (a) del ledger anterior: una variable
  esencial que el clima amenace. La forma mínima consistente con el principio
  3: **lo que se vuelve igual al vacío es vacío** — una celda cuya materia
  coincide con la del entorno durante W ticks deja de ser distinguible de él y
  se vacía. Con el sol que calienta empujando la superficie hacia s(t), sólo
  persisten en la superficie las físicas que empujan de vuelta (el homeostato
  de Ashby), y como s(t) cambia por estación, lo que es seguro cambia con él.
  Manos declaradas: ε, W. (`results/utero_sol_plano_run.txt`)

- **"Lo que se vuelve igual al vacío es vacío" (`sol_eq_eps=0.02`, `W=20`):
  SIN CONTACTO (2026-09-26).** `exp_utero_sol_equilibrio.py`: línea 1-D v6 +
  sol que calienta + sonda climática + disolución, 40 semillas × 5 brazos,
  20000 ticks, vara enmendada. Calibración previa (2 semillas, por vivas y
  contacto, no por A/L): ε=0.02/W=20 mantiene vivo el tejido y produce muertes
  medibles en la 35 y muertes concentradas en los inicios de estación en la
  13; ε=0.05 disuelve demasiado. **Resultado en 40 semillas:** vivas 210–232
  (sin sol 246), pero **muertes/tick en maduro 0.000 en la mediana** en los
  tres brazos con sol; contacto 0.72–0.91; R2: clima < permutado en 11/40
  (azar); lecturas A/A_m/L/L_m al nivel de los controles. **Lectura:** la
  disolución purga al principio y luego no muerde: una celda de superficie
  con salida propia v' queda en v ≈ (v'+s)/2 ≠ s, y sólo se disuelve si su
  regla imita al sol, cosa rara; el tejido encuentra en pocos cientos de ticks
  una configuración a salvo y desde ahí el clima no toca nada. **Sexto entorno,
  el mismo muro**: con la persistencia como único filtro, el tejido maduro
  converge a un estado que el entorno no puede amenazar, y un sistema al que
  nada amenaza no tiene nada que regular ni anticipar. Lo que la teoría
  señala y no probamos: que persistir CUESTE de forma continua — un
  metabolismo mínimo (mantenimiento por tick, energía tomada del gradiente
  con el sol en la superficie, difusión entre vecinas, muerte al agotarse).
  Es la conservación de Kruszewski/Flow-Lenia y el decaimiento de Stringmol,
  la única presión que la literatura muestra sostenida sin juez. Es un cambio
  de perspectiva, no un flag más, y trae manos nuevas (e0, mantenimiento,
  ganancia, difusión): se declaran y se calibran por vivas, nunca por las
  varas. (`results/utero_sol_equilibrio_run.txt`)

- **v9 metabolismo bajo el sol (e_mant=0.005, e_gan=0.2): el entorno por fin
  es ESENCIAL, y aun así no hay vestigio (2026-09-26).** `energia=True`:
  mantenimiento por tick, cosecha en la superficie según |v − sol(t)| en el
  toro, difusión conservativa, cesión a la cría, vacío al agotarse; calibrado
  en 3 semillas por vivas/muertes (m=0.01 o g=0.1 matan mundos enteros).
  `exp_utero_sol_energia.py`, 40 semillas × 5 brazos, 20000 ticks. **Sin sol
  el tejido MUERE** (vivas mediana 1: el vacío frío no alimenta) y con sol vive
  (128–174) con muertes continuas (1.0–2.8 por tick): por primera vez la
  persistencia depende del mundo. **Pero:** contacto 1.00 (las muertes son
  continuas y los inicios de estación no sobresalen); R2 sin regulación por
  orden (clima < permutado en 13/40; muchos pares 0/0 de mundos muertos);
  lecturas A/A_m/L/L_m: clima 3/3/2/3 contra controles de hasta 4 — azar. La
  sombra (muertes al azar) muere entera. **Séptimo entorno, veredicto SIN
  CONTACTO / NADA.** Lectura: hicimos que el tejido *necesite* al mundo, no que
  lo *modele*. Falta una pieza que ningún flag agregó: el tejido no tiene
  variables internas LENTAS que sus reglas puedan leer. La memoria es un
  registro que se reescribe cada tick; las estaciones duran 300–900 ticks; la
  energía sí integra a esa escala (τ≈e0/e_mant=200) pero las reglas no la ven.
  Anticipar una estación exige una variable que la recuerde y una física que
  la lea: PERCEPCIÓN del propio estado, la tercera dimensión del boceto que
  nunca se tocó. (`results/utero_sol_energia_run.txt`)

- **v10 percepción bajo el sol (la energía como 5º registro legible): SIN
  CONTACTO / NADA (2026-09-26).** `percepcion=True` (los campos indexan mod 5;
  la física lee su reserva y puede condicionar materia, reescritura y parto en
  ella; requiere `energia`); diagnóstico previo de escala temporal: la
  memoria interna del tejido dura 6–150 ticks (materia interior), 4–42 (borde,
  descontado el sol), contra estaciones de 300–900; la energía es la única
  variable interna lenta (τ≈200). Viabilidad: 13/24 mundos sobreviven (el
  cambio de indexación reordena la semántica de todos los genomas: las
  semillas ya no son comparables una a una con v9). `exp_utero_sol_percepcion.py`,
  40 semillas × 5 brazos. **Resultado:** vivas 124–202 con sol, 0 sin sol;
  muertes/tick 4.4–7.9 (recambio continuo); contacto 1.02; R2 sin regulación
  por orden (14/40, 15/40); A/A_m/L/L_m: clima 1/1/1/0 contra controles de
  hasta 3. **Octavo diseño del programa del sol, octavo negativo.**

**Cierre provisional del programa del sol (2026-09-26).** Ocho entornos y
mecanismos, cada uno con vara escrita antes y controles (sin sol, sombra,
orden permutado, segundo orden cíclico): sol visible; sonda climática;
réplica (que desmontó el único "vestigio" como falso positivo del umbral);
calor de superficie en la línea; el plano bajo el sol; muerte por disolución;
metabolismo; percepción de la propia energía. Ningún vestigio de regulación,
anticipación ni aprendizaje por recurrencia por encima de sus controles. Lo
que sí se aprendió, en orden: (1) un tejido que no necesita al mundo se vuelve
inerte a él en cuanto madura, en 1-D y en 2-D; (2) hacer que el mundo sea
visible, o que la sonda lo mire, o que caliente la superficie, no lo vuelve
consecuente; (3) el metabolismo sí lo vuelve esencial —sin sol el tejido
muere— pero un tejido que *necesita* al mundo no por eso lo *modela*; (4) la
escala temporal interna del tejido está uno o dos órdenes por debajo de la
del clima, y darle una variable lenta legible no alcanzó en este régimen de
recambio; (5) la disciplina funcionó: el único positivo murió en su réplica.
La lectura honesta es que la inteligencia, en el sentido de Ashby, no es una
propiedad que un flag más vaya a destapar en este sustrato: exige un rediseño
donde variables lentas, percepción y costo de persistir se construyan juntos
y desde el principio, o exige aceptar que este sustrato produce orden y
novedad pero no regulación. Ambas son decisiones de rumbo, no de ingeniería.
(`results/utero_sol_percepcion_run.txt`)

- **v11 fotosíntesis — la calibración por vida media revela una bifurcación
  (2026-09-26, corrida de 40 semillas en curso).** Criterio de diseño nuevo,
  derivado de los ocho negativos: sin costo el tejido queda demasiado frío
  (cristal); con el metabolismo de v9/v10, demasiado caliente (vidas de 20–30
  ticks: nada vive una estación) y el recambio lo ponía la geometría (sólo la
  superficie comía). `energia_luz=True`: cada celda cosecha e_gan·|v − sol(t)|
  — el ingreso depende de la materia propia frente a la estación, no del
  lugar. Calibración en 4 semillas × 9 configuraciones **por vida mediana de
  las celdas frente a la duración de la estación, contacto y vivas** (nunca
  por A/L): los mundos **se bifurcan** — o mueren en los primeros cientos de
  ticks (e_mant/e_gan ≥ 0.5: casi todos), o se vuelven inmortales (vida de las
  vivas ≈ 9.700 de 10.000 ticks, muertes ≈ 0; e_mant/e_gan ≤ 0.1). El régimen
  intermedio, donde la estación decide quién come, aparece sólo con el punto
  de equilibrio e_mant/e_gan ≈ 0.25 = la distancia típica en el toro: allí 2
  de 4 semillas viven (202 y 189 celdas), con muertes moderadas (0.016 y
  0.50 por tick) y novedad alta (170k genomas en la 13). Se fija (0.005,
  0.02) y se corre `exp_utero_sol_luz.py` con la vara enmendada.
  **Resultado (40 semillas × 5 brazos, con `percepcion=True`): EXTINCIÓN.**
  Vivas mediana 0 en todos los brazos; las pocas lecturas positivas son las
  de mundos casi vacíos. La calibración (sin percepción) daba 2/4 vivos; la
  percepción reordena la semántica de todos los genomas (campos mod 5) y baja
  la viabilidad inicial, y el punto de equilibrio en 0.25 hace morir de hambre
  a la mitad de las celdas iniciales antes de que el tejido se organice: la
  cascada extingue casi todo. Noveno diseño, noveno negativo, este confundido
  por la extinción. Corrección declarada antes de la última corrida de la
  sesión: sin percepción (semántica de v9) y con reserva inicial e0=2.0 (400
  ticks de margen antes del hambre; mano calibrada por viabilidad).
  (`results/utero_sol_luz_run.txt`)
  **Corrida 2 (sin percepción, e0=2.0): EXTINCIÓN otra vez.** Vivas mediana 0
  en los cinco brazos; las lecturas positivas (clima 3/2/4/2) son de mundos
  casi vacíos y no superan p binomial ni controles. Con el punto de equilibrio
  en la distancia típica del toro la cascada de hambre inicial gana casi
  siempre; con el punto de equilibrio más bajo el tejido es inmortal e inerte.
  Décimo diseño del programa del sol, décimo negativo. **Se aplica la regla de
  parada de `PLAN_INTELIGENCIA.md` §7**: el programa queda reportado como
  negativo honesto, con su cadena de diagnósticos (inercia sin costo; recambio
  total con costo por superficie; bifurcación extinción/inmortalidad con luz)
  y sin vestigio de inteligencia en el sentido de Ashby. Lo que un intento
  futuro debería cambiar está en `PLAN_INTELIGENCIA.md` §8; la decisión de
  rumbo es de Fran. (`results/utero_sol_luz2_run.txt`)

- **v12 luz finita (capacidad de carga estacional): el primer régimen
  intermedio de la serie; veredicto NADA, con la lectura más cercana hasta
  ahora (2026-09-26).** `luz_finita=L0`: la luz de cada tick, L0·sol(t), se
  reparte entre las vivas según |v − sol|; N* = L/e_mant sigue a la estación
  (A hambruna, B abundancia). Calibración por capacidad de carga, vida y
  contacto (4 semillas × 12 configuraciones): con L0=3, e_mant=0.01 la
  población de la 13 sigue a la estación (93/159/167 en A/B/C) y las muertes
  se duplican al entrar en A; la percepción mata a la 13 y ayuda a la 35 y la
  21 → corrida principal sin percepción. `exp_utero_sol_luzfinita.py`, 40
  semillas × 5 brazos, con dos lecturas nuevas pre-registradas: **A_n** (los
  nacimientos caen en el instante esperado de la hambruna, en las estaciones
  largas que la preceden) y **A_e** (la energía media sube en ese instante:
  ahorro). **Resultado:** vivas 50–95 con sol (la sombra muere entera; sin sol
  70 pero con muertes 0.83/tick); contacto 0.60 (las muertes bajan al cambiar
  de estación); R2 no (13/40). Lecturas: A 3, A_m 5 (p=0.048), L 3, L_m 4, A_n
  4, **A_e 9/40 (p binomial < 0.001)** — pero permutado 3, sin sol 5, sombra 4:
  el criterio exige ≥ 2× el máximo de los controles (10) y da 9. **Falla por
  una semilla, y no se relaja.** Además el brazo SIN SOL con 5 positivas
  muestra que el estadístico sobre una serie lenta (la energía media deriva)
  está inflado. Lectura honesta: es la única vez que una lectura de
  anticipación supera con holgura la tasa nominal, en la dirección predicha
  (ahorro antes de la hambruna) y en el brazo con la regularidad; pero no
  supera a sus controles. Por protocolo: réplica con otro sembrado del sol,
  con percepción (la variable lenta legible) y con A_e sobre la DERIVADA de la
  energía (declarado antes de correr, para quitar la deriva).
  (`results/utero_sol_luzfinita_run.txt`)
  **Réplica (sol seed 1, percepción ON, A_e sobre la derivada): NADA.** A_e
  2/40 en clima (tasa nominal), permutado 3, sin sol 2: el 9/40 de la corrida
  1 era el artefacto de la deriva del nivel de energía, como delataba el brazo
  sin sol. La percepción bajó la viabilidad (vivas 14 en clima, 1 en
  permutado). Las demás lecturas al nivel de los controles. Duodécimo diseño,
  duodécimo negativo. Queda una desambiguación limpia (la réplica cambió tres
  cosas a la vez): sol seed 1 SIN percepción, A_e en nivel y en derivada a la
  par, y una lectura de habituación específica de la hambruna (Spearman de
  las muertes al entrar en A sobre sus ocurrencias), declaradas antes de
  correr. (`results/utero_sol_luzfinita2_run.txt`)
  **Corrida 3 (sol seed 1, sin percepción, A_e en derivada y en nivel, L_A):
  la regla disparó "VESTIGIO" sobre A_eN — la lectura en NIVEL que estaba
  declarada como control del artefacto — con 5/40 (p=0.048) contra permutado
  1, sin sol 2, sombra 2.** A_e en derivada: 5/40 pero permutado 3 (falla el
  2×). L_A (habituación de la hambruna): 3 vs 5 en ciclo2. R2: clima <
  permutado en 20/40 con razón mediana 0.07 y ciclo2 22/40 con 0.15 — bajo
  los órdenes regulares el tejido muere MUCHO menos que bajo el permutado
  (0.03–0.07 contra 0.31 muertes/tick), pero el test de signos falla porque la
  mitad de los pares son mundos muertos (0/0). **Acumulado de las tres
  corridas de v12** para A_eN en clima: 9 + 2 + 5 = 16/120 (nominal 6, p
  binomial < 0.001) contra sin sol 5 + 2 + 2 = 9/120: razón 1.8, no 2. Lectura
  honesta: hay una señal débil y persistente en la dirección predicha (la
  energía media sube alrededor del instante esperado de la hambruna, en las
  estaciones que la preceden, bajo el clima con regularidad), pero el
  estadístico en nivel está inflado por la acumulación de energía dentro de la
  estación y no supera 2× a sus controles. **No se cuenta como vestigio.**
  Siguiente, declarado: estadístico sin deriva (residuo respecto de la
  tendencia lineal ajustada ANTES de la ventana esperada, extrapolada), 40000
  ticks (el doble de estaciones), sol seed 2, sin percepción, y R2 restringido
  a pares con ambos mundos vivos. (`results/utero_sol_luzfinita3_run.txt`)
  **Corrida 4 (sol seed 2, 40000 ticks, sin percepción, A_e sin deriva, R2
  entre vivos): NADA, concluyente.** A_e sin deriva: clima **1/40**; A_eN (nivel,
  control del artefacto): permutado **15/40**, clima 3 — el estadístico en nivel
  dispara masivamente en el brazo SIN regularidad: acumulación, no anticipación.
  L_A (habituación de la hambruna): clima 6/40 (p=0.014) pero sombra 10/40 (la
  sombra copia el calendario de muertes): artefacto del calendario. R2 entre
  pares vivos: 8/24 y 8/26 — nada. Las demás lecturas al nivel de los
  controles. **v12 cierra con cuatro corridas: la capacidad de carga estacional
  es el único régimen intermedio de toda la serie —la población sigue a la
  estación, las muertes se concentran en la hambruna— y aun así no hay
  anticipación, habituación ni regulación por orden que supere a sus
  controles.** La señal de ahorro de las corridas 1 y 3 quedó identificada como
  artefacto por dos vías independientes (derivada y residuo de tendencia; brazo
  permutado). (`results/utero_sol_luzfinita4_run.txt`)

**Cierre del programa del sol (2026-09-26, segunda vez, definitivo para esta
sesión).** Trece corridas pre-registradas sobre doce diseños (sol visible,
sonda climática, réplica, calor, plano, disolución, metabolismo, percepción,
fotosíntesis ×2, luz finita ×4), ninguna con vestigio; dos señales tentadoras
(3/40 de anticipación; 9/40 de ahorro) desmontadas por sus réplicas y
controles. La cadena de diagnósticos es el resultado: inercia sin costo;
recambio total con costo por superficie; bifurcación extinción/inmortalidad
con luz individual; régimen intermedio con luz compartida, sin señal. Regla de
parada aplicada. Decisión de rumbo: de Fran.

- **v13 registros lentos — la pieza estructural que ninguna versión tuvo
  (2026-09-26, corrida en curso).** Tras la orden de seguir: no otro flag de
  entorno, sino un cambio en la máquina. `lentos=λ`: dos registros por celda
  que la física LEE como cualquier registro y a los que sólo puede EMPUJAR
  despacio (S ← S + λ(w − S) si la regla escribe w; sin cambio si no escribe):
  una regla que escribe una constante carga S exponencialmente con τ = 1/λ =
  300 ticks — un reloj o un integrador a la escala de la estación, que es lo
  que la medición de escala temporal mostró ausente (memoria interna 6–150
  ticks). Como el VM no tiene condicionales, la regla puede usar S vía MUTO
  sobre su propio SPAWN (control de flujo por auto-reescritura). Se prueba
  sobre la ecología de v12 (luz finita, L0=3, e_mant=0.01, sin percepción), la
  única con régimen intermedio, con la vara de la corrida 4 (A_e sin deriva
  primaria, A_eN control, R2 entre vivos). Viabilidad 14/24. 4 tests;
  `execute(extra=list)` devuelve lo escrito. `exp_utero_sol_lentos.py`.
  **Resultado (40 semillas × 5 brazos, 30000 ticks): NADA.** Vivas 46–72 con
  sol; contacto 0.53. Anticipación sobre actividad: clima 5 y sobre muertes 6
  (p 0.048 y 0.014) — pero **permutado 7 y 6**: el brazo sin regularidad
  iguala o supera al brazo con regularidad. Energía (A_e sin deriva 3, A_eN 3)
  contra **permutado 10 y 9**: el artefacto de acumulación vuelve a disparar
  sólo en el control. R2 entre vivos 10/23 y 13/25. Los relojes a la escala de
  la estación no produjeron anticipación ni habituación medibles.
  Decimocuarta corrida pre-registrada, decimocuarta sin vestigio.
  (`results/utero_sol_lentos_run.txt`)

**Cierre (tercero y último de la sesión, 2026-09-26).** Catorce corridas
pre-registradas sobre trece diseños. El programa recorrió, en orden y con
controles, cada ingrediente que la teoría de la regulación exige: un entorno
visible; un entorno que cuenta para la sonda; contacto físico (calor); la
superficie grande del plano; una variable esencial amenazada (disolución);
costo de persistir (metabolismo); percepción del propio estado; luz sobre
todo el tejido; un recurso compartido con capacidad de carga estacional (el
único régimen intermedio, cuatro corridas); y relojes internos a la escala de
la estación. Ninguna lectura de regulación, anticipación ni aprendizaje por
recurrencia superó a sus controles; cuatro señales tentadoras (3/40, 9/40,
5/40 y 6/40) fueron desmontadas por réplica, por el estadístico sin deriva o
por el brazo permutado. Lo que el sustrato SÍ muestra, y queda probado: orden,
novedad estructural defendible, y demografía estacional. Lo que no muestra:
un tejido que modele su mundo. La regla de parada del plan se aplica de forma
definitiva para esta sesión; seguir sin una hipótesis nueva sólo produciría el
falso positivo que la disciplina de esta línea existe para impedir.

- **Control positivo — un anticipador diseñado a mano: VIABLE, con la ventaja
  donde no la busqué, e INVISIBLE para las varas A/L (2026-09-26).**
  `exp_utero_control_positivo.py`: el "ahorrador" — detector de estación en
  un registro lento (S2 ← materia del vacío contiguo), THR(S2>0.5)·0.9375 →
  MUTO sobre su PROPIO SPAWN: pare sólo en la abundancia B (control de flujo
  por auto-reescritura, la única forma de condicionar en este VM), materia
  v² (sensible, ingreso máximo). Corrida 1: no viable por un error mío de
  diseño (sentía a la izquierda y paría a la derecha: sólo la punta izquierda
  veía el sol y reemplazaba a su vecina; población clavada en 18, energía 127
  al entrar en A, muertes 0). Corrida 2 (detector a la derecha, hacia donde
  pare): **viable en 18/20 semillas, firma intacta 1.00 bajo mutación
  germinal, población que sigue a la estación con fuerza (73 / 200 / 154 en
  A / B / C, contra 52 / 59 / 59 del tejido evolucionado)**. Ventaja por mi
  criterio (más energía al entrar en A Y menos muertes): no — entra POBRE en
  A (1.2 vs 11) porque se reproduce hasta la capacidad de carga en B y su
  umbral 0.5 deja escapar partos en la mitad alta de C (43/100 ticks contra 66
  en B, 0 en A). **Pero muere en la hambruna la mitad que el evolucionado
  (13.8 vs 27.4 por 100 ticks) y, el mismo organismo bajo el orden PERMUTADO,
  un 58% más (21.8): al ahorrador el orden regular le sirve, porque en el
  orden A→B→C la hambruna llega tras la estación templada y en el permutado
  puede llegar tras la expansión plena.** Detectabilidad: **A_n 1/20, A_e 1/20,
  L_A 0/20 — nuestras varas de anticipación NO ven a un anticipador real de
  tipo reflejo** (buscan un cambio anclado al instante esperado dentro de la
  estación; una estrategia gatillada por la estación no lo produce). La
  lectura que sí lo ve es R2 (mortalidad en la hambruna bajo orden regular vs
  permutado). **Consecuencias:** (1) anticipar la hambruna es viable, estable
  y beneficioso en este sustrato; (2) los catorce negativos sobre A/L no
  excluyen que emergiera anticipación de tipo reflejo — pero R2 fue negativa
  en todas las corridas evolucionadas, así que la conclusión se sostiene con
  precisión: el tejido evolucionado nunca desarrolló regulación de la
  hambruna dependiente del orden, aunque tal estrategia existe y paga; (3) la
  pregunta que queda es evolutiva, no ecológica: ¿la selección FAVORECE al
  ahorrador cuando compite con el tejido evolucionado? Eso se prueba con una
  invasión desde raro. (`results/utero_control_positivo{,2}_run.txt`)

- **Invasión desde raro — el anticipador NO es seleccionado (2026-09-26).**
  `exp_utero_invasion_ahorrador.py`: 2 ahorradores entre 14 celdas aleatorias,
  20 semillas, bajo clima regular, permutado y sin sol. Toma (firma ≥ 0.5 al
  final): clima 4/20, permutado 4/20; extinción 14/20 y 15/20. Sin sol el
  ahorrador nunca pare y sobrevive inmóvil mientras el resto muere (no es un
  control válido de toma). **La ventaja individual (mitad de muertes en la
  hambruna) no se traduce en propagación, y la regularidad del orden no
  cambia nada.** La razón está en la tabla del control positivo: el tejido
  evolucionado pare 34 veces por 100 ticks DURANTE la hambruna (0 en C) y
  recoloniza los huecos más rápido de lo que el ahorrador los ocupa; parir es
  gratis (sólo reparte energía), así que la estrategia "reproducirse en la
  crisis" gana a "ahorrar antes de la crisis". Esto cierra el círculo de los
  catorce negativos con una explicación mecánica y no con una ausencia:
  **anticipar la hambruna es viable y beneficioso para el individuo, pero
  esta ecología no lo selecciona.** En ecología, la condición conocida para
  que evolucione la latencia o el ahorro es que la reproducción CUESTE. Es la
  hipótesis que queda, derivada del dato y no de un tanteo: un costo fijo de
  parto (`e_costo`) que haga inviable parir en la hambruna, primero con la
  invasión desde raro (¿ahora sí hay selección?) y sólo si la hay, con el
  tejido evolucionado sin sembrar (¿emerge?).
  (`results/utero_invasion_ahorrador_run.txt`)
  **Corrida 2, parir cuesta (e_costo=2.0): igual.** Toma 5/20 en clima y 5/20
  en permutado, extinción 11/20; y las semillas donde el ahorrador "toma" son
  las mismas con y sin costo y con y sin orden (2, 3, 8, 14, 18): son mundos
  donde la población aleatoria colapsa y el ahorrador queda por defecto, no
  selección. **Conclusión del programa, ahora completa y mecánica:** en esta
  ecología anticipar la hambruna es viable y beneficioso para el individuo,
  pero NO es seleccionado frente al tejido evolucionado, con partos gratis o
  costosos, y la regularidad del orden no interviene. Los catorce negativos
  no eran un problema de búsqueda ni de vara: el entorno no selecciona lo que
  buscábamos. Un entorno que sí lo seleccione es una decisión de diseño —es
  decir, elegir la respuesta— y por eso no se toma sola.
  (`results/utero_invasion_ahorrador_costo_run.txt`)

**Cierre del programa (definitivo, 2026-09-26).** Dieciséis corridas
pre-registradas de emergencia (trece diseños), un control positivo en dos
corridas y dos ensayos de invasión. Resultado: orden y novedad estructural
defendibles; demografía estacional real; un anticipador diseñado viable y
estable que las varas temporales no ven y R2 sí; y ninguna emergencia de
regulación porque la ecología no la selecciona. Es un negativo con
explicación, que es lo más que un negativo puede ser.

- **v14 hambruna dura — evolución experimental bajo un régimen declarado
  (2026-09-26, corrida en curso).** Corrección de mi propio argumento: elegir
  el régimen selectivo es elegir la pregunta, no la respuesta. Régimen: luz
  casi nula en A (base 0.08) y parto costoso (e_costo=1.0), calibrados por
  viabilidad estacional (5/6 semillas viven; N cae en A y se recupera; partos
  en A ≈ 0). Nada sembrado. Lectura primaria R2_A: mortalidad durante la
  hambruna, clima contra permutado, pareada entre vivos, con ciclo2 como
  control de tipos de transición. `exp_utero_hambruna.py`, 40 semillas × 5
  brazos, 20000 ticks.
  **Corrida 1 (sol seed 0, 30000 ticks):** R2_A no (clima < permutado en
  7/26 pares vivos, razón 1.21: la hambruna mata MÁS bajo el orden regular);
  partos A/B 0.01 en todos los brazos (demografía). Veredicto impreso: NADA.
  Todas las lecturas de anticipación en clima al nivel de los controles.
  **Lectura post hoc, no pre-registrada:** en el brazo ciclo2 (listado en el
  pre-registro como CONTROL de tipos de transición, no como brazo primario)
  A_n —caída de nacimientos alrededor del instante esperado de la hambruna,
  en las estaciones largas que la preceden— dio 9/40 (p binomial ≈ 0.0006)
  contra permutado 0, sin sol 2, sombra 3. Con la vara §6b aplicada a ese
  brazo pasaría las tres condiciones; pero mirar un control después de ver
  los datos no es un resultado, es una hipótesis. Sospecha declarada:
  saturación demográfica dentro de B (en ciclo2 la abundancia sigue siempre a
  C y arranca cerca de la capacidad de carga, así que los partos decaen al
  final de B sin que nadie anticipe; A_eN, la lectura de nivel que sirve de
  control de ese artefacto, también dio 8/40 en ciclo2). **Réplica declarada
  (corrida 2):** sol seed 1, ciclo2 evaluado como brazo primario junto a
  clima, y A_nD (A_n sin deriva) como lectura primaria; se cree sólo si A_n Y
  A_nD cumplen otra vez en ciclo2. (`results/utero_hambruna_run.txt`)
  **Corrida 2 (réplica, sol seed 1): NADA.** R2_A no (clima < permutado en
  8/25, razón 1.19; ciclo2 5/27, 1.24). A_n en ciclo2 = **2/40** (era 9/40);
  A_nD 0/40; el control emparejado A_nB 2/40 en ciclo2 y 0–1 en los demás.
  Ninguna lectura primaria cumple en ningún brazo (A en clima 5/40 pero
  permutado 6/40; L_A en ciclo2 5/40 pero permutado 6/40). El 9/40 fue un
  falso positivo de calendario: una coincidencia entre las B largas de un
  sembrado solar concreto y la demografía. Cuarto señuelo del programa cazado
  por réplica (3/40 anticipación, 9/40 y 5/40 ahorro, 6/40 habituación, 9/40
  caída de partos). Diecisiete corridas pre-registradas de emergencia, cero
  vestigios. (`results/utero_hambruna2_run.txt`)

- **v15 — tierra quemada (selección K), pre-registro (2026-09-26).** La
  explicación mecánica de §12, reforzada por v14: sobrevivir a la hambruna no
  otorga descendencia porque el vacío se rellena igual de rápido desde
  cualquier superviviente (selección r). v15 cambia una cosa del MUNDO, no del
  tejido: `refractario=T`, el lugar de una celda muerta queda incolonizable
  durante T ticks (ni colonización ni invasión; el borde no se toca; un SPAWN
  hacia tierra quemada fracasa como ante un vecino ocupado). Conservar el
  lugar durante la hambruna pasa a ser la única forma de tener territorio en
  la abundancia. Calibración por viabilidad (6 semillas × T 0/100/300/600,
  12000 ticks): todas viables; el criterio "T más largo viable" daría 600 pero
  allí el contacto cayó a 0.62 (< 1.2), así que se declaró **T = 300** (una
  estación mínima) antes de correr. Brazos, lecturas y veredicto idénticos a
  v14 corrida 2 (R2_A primaria; A_nB como control emparejado).
  `exp_utero_quemada.py`, 40 semillas × 5 brazos, 30000 ticks, sol seed 0.
  **Resultado: NADA.** R2_A no: clima < permutado en 5/25 pares vivos, razón
  1.29 (la hambruna mata MÁS bajo el orden regular); ciclo2 7/25, 1.16. Partos
  A/B 0.01–0.02 en todos los brazos. Las dos lecturas con conteo alto en clima
  —L_A 6/40 (p 0.014) y A_m 6/40— tienen controles al mismo nivel (L_A:
  permutado 3, sombra 4; A_m: permutado 8) y no pasan la condición de 2×. Vivas
  25–26 con sol, 51 sin sol, sombra 0. La selección K (territorio como premio
  a sobrevivir) no hizo emerger regulación por orden. Por el fallback declarado
  en PLAN §14: la recolonización rápida NO era el cuello de botella; la
  explicación mecánica pasa al CAMINO mutacional. Dieciocho corridas
  pre-registradas de emergencia, cero vestigios.
  (`results/utero_quemada_run.txt`)

- **La cuarta jaula: clausura de operandos (2026-09-26).** Leído en
  `nivel2.execute` y verificado por medida: **ningún operador de variación
  escribe operandos.** MUTO escribe sólo el opcode de la fila `a%K`; el
  germinal sólo el opcode de la fila `c%K`; COPY traslada filas que ya
  existen; SPAWN copia. Los tríos `(a,b,c)` de un mundo son exactamente los
  de su sopa inicial: 248 de 4096 (6.06%), y ese conjunto no cambia nunca. La
  "física que se reescribe" reescribe 1 de sus 4 campos. Consecuencia medida
  sobre las 40 semillas de v14/v15: sólo **3/40** sopas contienen siquiera los
  operandos de las piezas del ahorrador (Monte Carlo poblacional 0.157), y
  eso es una cota superior: reunirlas en una celda y en orden exige filas
  COPY cuyos propios operandos (origen, destino) también están congelados.
  Esto explica los 18 negativos y por qué el control positivo tuvo que
  escribirse a mano: la anticipación no es que no se seleccione, es que la
  variación no puede componerla. La jaula está en la VARIACIÓN, no en la
  ecología. (`exp_utero_alcance_operandos.py`,
  `results/utero_alcance_operandos_run.txt`)

- **v16 — escritura total, pre-registro (2026-09-26).** `escritura_total=True`:
  MUTO y el germinal escriben la instrucción entera `(op,a,b,c)` desde los
  registros (sin RNG nuestro). Test directo: sin el flag los tríos de un mundo
  son subconjunto de su sopa a los 3000 ticks; con el flag aparecen tríos
  nuevos. Calibración sobre la ecología de v14 (6 semillas, 12000 ticks):
  viable (5/6, N_A 29, contacto conservado) y abierto (16656 genomas nunca
  vistos por mundo contra 198; 52 tríos nuevos contra 0); la semilla 13 se
  extingue con el flag. Mismos brazos, lecturas y veredicto que v14 corrida 2.
  `exp_utero_total.py`, 40 semillas × 5 brazos, 30000 ticks, sol seed 0.
  **Resultado: SIN CONTACTO / NADA.** Con la variación abierta el tejido
  recambia sin parar (muertes/tick 0.026 contra 0.016–0.020 cerrado) y la
  hambruna ya no se destaca: muertes post/pre 0.92 en clima. R2_A no (clima <
  permutado en 2/22, razón 1.30; ciclo2 7/21, 1.13). Ninguna lectura supera a
  sus controles; en ciclo2 A_n 5/40 coincide semilla a semilla con su propio
  control emparejado A_nB (misma lectura) y con A_eN (control de nivel), y
  sin sol da 3: deriva de calendario, la misma que v14 corrida 1 con este
  mismo sol seed 0. Adaptación refleja (L_A, mortalidad en hambrunas
  sucesivas): 1/40 en clima. Abrir el espacio no bastó en 30000 ticks con ~30
  vivas: ni regulación ni siquiera adaptación medible. Diecinueve corridas
  pre-registradas, cero vestigios. Por el fallback declarado, la pregunta pasa
  al tiempo y al tamaño de población. (`results/utero_total_run.txt`)

- **§16 — escala, pre-registro (2026-09-27).** Antes de volver a preguntar
  por regulación, lo previo: ¿el sustrato abierto (v16) EVOLUCIONA? 4× el
  tiempo (120000 ticks) y ~3× la población (L0 = 9, max_n 512; humo: 50–95
  vivas), misma ecología. Tres brazos: clima, permutado, sombra. Lectura
  primaria de adaptación refleja: mortalidad en las hambrunas de la segunda
  mitad / primera mitad dentro de cada mundo (razón < 1 = adapta), contada
  sobre los 40 mundos con sol contra los 20 de sombra (≥ 70%, p signo < 0.05,
  sombra < la mitad); además L_A (habituación) por brazo. Regulación: R2_A
  como siempre. Veredicto EVOLUCIONA / VESTIGIO / NADA escrito antes de
  correr. `exp_utero_escala_evo.py`, 20 semillas × 3 brazos.
  **§16b — espectro de la variación (DFE), medido (2026-09-27).** En la
  misma ecología (L0 = 9), siguiendo cada cría 500 ticks (10 semillas,
  ventana 6000–12000): **cerrado** (sólo opcode): 514 partos/1000 ticks, 65%
  de las crías idénticas a la madre, 99% de los cambios en un solo campo,
  crías distintas que sobreviven 500 ticks: 5%; oferta viable 9/1000 ticks.
  **Abierto** (fila entera): 129 partos/1000 ticks, 15% idénticas, 71% de los
  cambios tocan operandos, crías distintas que sobreviven 500 ticks: 21%
  (vida mediana 115); oferta viable **23/1000 ticks por mundo** (~2800 en la
  corrida de escala). La variación abierta no es letal: la mayoría de las
  crías distintas vive (65% a 100 ticks) y una de cada cinco se asienta. Si
  la escala da NADA, no será por falta de variantes.
  (`exp_utero_dfe.py`, `results/utero_dfe_run.txt`)
  **Resultado §16: NADA, y una vara defectuosa.** 120000 ticks, ~80 vivas.
  R2_A no (clima < permutado en 2/14; la hambruna vuelve a matar MÁS bajo el
  orden regular: 0.094 contra 0.038 por tick, un efecto de tipo de transición
  —en clima A sigue siempre a la estación escasa C— no de regularidad). L_A
  0/40. La razón tardía/temprana de mortalidad en la hambruna bajó en 23/28
  mundos con sol… y en 10/10 de la sombra: la sombra se EXTINGUE (vivas 0) y
  las muertes por tick caen con la población. La medida debía ser per cápita.
  Dos defectos propios registrados: (1) la lectura de adaptación era
  confundible con demografía; (2) el brazo sombra lleva cuatro corridas
  (v14, v15, v16, §16) extinto en régimen maduro, de modo que la condición
  "≥ 2× sombra" era vacía en todas ellas (los conteos de sombra venían de la
  fase inicial). Siguiente: adaptación PER CÁPITA contra un brazo
  **congelado** (MUTO y COPY inertes, sin germinal: la misma ecología sin
  herencia de cambios), el único nulo real para "¿evoluciona?".
  (`results/utero_escala_evo_run.txt`)

- **§17 — ¿evoluciona?, pre-registro (2026-09-27).** Nuevo flag `congelado`
  (MUTO y COPY inertes, germinal sin escribir: la misma física y ecología sin
  herencia de cambios; byte-idéntico apagado; test: un mundo congelado no
  acuña ningún genoma en 2000 ticks; en humo vive con ≈120 celdas). Tres
  brazos con la misma sopa por semilla: abierto (v16), cerrado (v14),
  congelado. 120000 ticks, L0 = 9, 20 semillas, sol seed 0 cíclico. Lectura
  primaria: mortalidad PER CÁPITA en cada hambruna madura (muertes / vivas
  medias en A); razón segunda mitad / primera mitad de las hambrunas;
  pareada por semilla contra el congelado. EVOLUCIONA si razón < congelado en
  ≥ 75% de los pares vivos (n ≥ 8), p signo < 0.05, y mediana ≤ 0.7× la del
  congelado. `exp_utero_evoluciona.py`.
  **Resultado: NO EVOLUCIONA.** 59 hambrunas maduras por mundo, ~82 vivas
  en los tres brazos. La mortalidad per cápita en la hambruna baja con las
  hambrunas sucesivas en todos, y baja MÁS en el congelado (razón mediana
  0.19) que en el abierto (0.45) o el cerrado (0.62): abierto < congelado en
  3/14 pares, cerrado 6/16. Mortalidad per cápita media en A: abierto 0.73,
  congelado 0.60, cerrado 0.51 (cerrado < congelado en 13/19, p 0.08). Lo que
  baja es ecología —la población se asienta— y la herencia de cambios no
  añade adaptación: en el brazo abierto es carga (muere más). Con 23
  variantes viables por 1000 ticks (§16b), la selección no encuentra nada que
  difiera en lo que la hambruna mide. **Éste es el hallazgo que reordena el
  programa:** antes de la inteligencia falta la evolución; antes de la
  evolución falta un fenotipo heredable sobre el que la hambruna discrimine.
  Siguiente (§18): medir si la supervivencia a la hambruna es una propiedad
  del genoma (repetible entre portadores y entre hambrunas) o del lugar y el
  estado. (`results/utero_evoluciona_run.txt`)

- **§18 — ¿hay fenotipo heredable?, pre-registro (2026-09-27).** Sin
  evolucionar nada: en cada hambruna madura se fotografían las vivas (genoma,
  energía, si lindan con vacío) y se sigue cuáles sobreviven. Por hambruna:
  ¿el destino se predice por el genoma (suma de cuadrados entre genomas con
  ≥ 2 portadoras, nulo por permutación de destinos), por la energía inicial,
  por el borde? Por mundo: fracción de hambrunas con p < 0.05 por predictor.
  HEREDABLE si ≥ 15/20 mundos tienen ≥ 25% de hambrunas con p_gen < 0.05;
  ESTADO si eso lo cumple la energía o el borde y no el genoma; NADA si nada
  predice. Repetibilidad del mismo genoma entre hambrunas consecutivas como
  secundaria. 60000 ticks, L0 = 9, brazos abierto y cerrado.
  `exp_utero_heredabilidad.py`.
  **Resultado: NADA por la letra; ESTADO con componente heredable por la
  evidencia.** Por la regla escrita (≥ 15 de 20 mundos) ninguno de los tres
  predictores cumple, porque 7 y 5 mundos se extinguieron y sólo 13 (abierto)
  y 15 (cerrado) tuvieron ≥ 10 hambrunas utilizables: el denominador estaba
  mal elegido, y eso se registra. Sobre los mundos utilizables: la **energía**
  al empezar la hambruna predice el destino en 13/13 y 13/15 mundos (mediana
  de la fracción de hambrunas con p < 0.05: 0.96 y 0.75); el **genoma** en
  7/13 y 9/15 (medianas 0.29 y 0.54), y su efecto es **repetible** entre
  hambrunas consecutivas (Spearman entre la supervivencia del mismo genoma en
  k y k+1: p < 0.05 en 8/10 y 14/15 mundos, rho 0.2–0.9); el **borde** casi
  nunca (1 mundo). Lectura: la hambruna mata por cuánto se tiene, y cuánto se
  tiene depende en parte del programa (ingreso por |v − sol|) y en parte del
  lugar y la competencia por la luz. Hay variación heredable en la
  supervivencia a la hambruna —lo que §17 no encontró es que se traduzca en
  adaptación—, lo que apunta a un canje (los genomas que sobreviven la
  hambruna no son los que más paren en la abundancia) o a que el genoma sea
  proxy de posición; ninguna de las dos se separa sin registrar por celda.
  (`results/utero_heredabilidad_run.txt`)

- **§20 — ¿evoluciona sin el bien común?, pre-registro (2026-09-27).**
  Decisión autónoma de rumbo: en lugar de sólo registrar por celda, una
  hipótesis falsable. La ecología tiene difusión conservativa de energía
  entre vecinas (e_dif = 0.25): la reserva es un bien común local, la
  ventaja de ingreso de un programa se socializa con sus vecinas y la
  selección individual sobre el ingreso se neutraliza (polizón). Eso
  explicaría a la vez que la energía prediga la supervivencia (§18), que el
  genoma pese poco, y que no haya adaptación (§17). Predicción: con e_dif =
  0 la mortalidad per cápita en la hambruna baja MÁS con variación que en el
  congelado. §17 repetido con esa única diferencia (viabilidad en humo: los
  tres brazos ≈120 vivas). `exp_utero_evoluciona2.py`.
  **Resultado: NO EVOLUCIONA.** Sin difusión: abierto razón 0.54 contra
  congelado 0.82 (abierto < congelado en 9/16 pares, p 0.40); cerrado 0.82
  contra 0.68 (6/16). Mortalidad per cápita media en A: abierto 1.58, cerrado
  1.49, congelado 1.79 (12/18 y 13/19 menores, p 0.12 y 0.08). El brazo
  abierto se mueve en la dirección predicha pero lejos de la regla; el bien
  común no era la causa principal. Quedan: la selección no ve los genomas
  (posición/deriva) o la tasa de mutación es demasiado alta (el germinal
  escribe en cada parto: ≈1 mutación por generación con efectos fuertes,
  régimen de umbral de error; la carga de §17 lo sugiere). §21 y §22.
  (`results/utero_evoluciona2_run.txt`)

- **§21 y §22, pre-registro (2026-09-27).** Dos flags nuevos, byte-idénticos
  apagados, con tests: `orden_seed` (RNG aparte para el orden de
  actualización, la sopa queda fija por `seed`) y `tasa_germinal=p` (la cría
  recibe la escritura germinal sólo si frac(|R3 madre|·97) < p: determinista
  desde la materia, mano declarada). **§21 ¿la selección ve los genomas?**
  10 sopas × 5 órdenes, congelado, 30000 ticks: W de Kendall entre réplicas
  sobre la abundancia final de los 16 genomas iniciales, nulo por permutación
  de etiquetas. SELECCIÓN si p_W < 0.05 en ≥ 8/10 sopas; POSICIÓN si ≤ 3/10.
  **§22 tasa de mutación:** protocolo de §17 con brazos abierto p = 1, 0.1,
  0.02 y congelado. Hipótesis: ≈1 mutación de efecto fuerte por generación
  está por encima del umbral de error (la carga de §17 es la firma);
  EVOLUCIONA si algún brazo con p < 1 cumple la regla de §17.
  `exp_utero_seleccion_replicas.py`, `exp_utero_tasa.py`.
  **Resultado §21: SELECCIÓN (10/10 sopas, p_W = 0.001).** En 9/10 sopas el
  mismo genoma inicial barre hasta el 100% (1 genoma vivo, share 1.00) en las
  5 réplicas con distinto azar de orden; en la sopa 0, 4/5 con 96%. La
  ecología discrimina programas fijos de forma determinista y reproducible:
  la selección ve los genomas. Caveat declarado: lo que gana es probablemente
  la fecundidad/colonización, no la supervivencia a la hambruna; pero para
  la pregunta "¿hay selección sobre el programa?" basta. Combinado con §17
  (con herencia de cambios NO hay adaptación) el cuello queda acorralado en
  la variación misma: el ganador existe y gana cuando nada muta; con una
  escritura germinal en cada parto su descendencia lo pierde antes de que la
  selección lo fije (umbral de error). §22 lo prueba.
  (`results/utero_seleccion_replicas_run.txt`)
  **Resultado §22: NO EVOLUCIONA con ninguna tasa (por la regla).** Razón
  tardía/temprana per cápita: p=1 0.45, p=0.1 0.41, p=0.02 0.14, congelado
  0.19; pareado: 3/14, 7/15, 8/16 pares por debajo del congelado (p 0.99,
  0.70, 0.60). Tendencia graduada en la dirección predicha, reportada sin
  inflarla: la mortalidad per cápita media en A cae con la tasa (0.73, 0.69,
  0.49 contra 0.60 del congelado) y con p=0.02 el brazo vivo muere menos que
  el congelado en 12/18 (p 0.12). La CARGA desaparece al bajar la tasa; la
  ADAPTACIÓN medible en esta vara no aparece. Con §21 (la selección barre
  programas fijos) la hipótesis restante es que la vara mide el rasgo
  equivocado: lo que la ecología selecciona es capacidad competitiva
  (colonización), no supervivencia a la hambruna. §23: competencia en jardín
  común, evolucionado contra ancestro. (`results/utero_tasa_run.txt`)

- **§23 — jardín común, pre-registro (2026-09-27).** Adaptación medida sin
  nombrar el rasgo, como en la evolución experimental: por semilla, el
  ancestro A es el genoma dominante de un mundo congelado (30000 ticks: el
  mejor programa fijo de esa sopa); el evolucionado E es el dominante de un
  mundo abierto tras 120000 ticks (regímenes p = 0.02 y p = 1); compiten 8 A
  contra 8 E en un mundo congelado, dos disposiciones espaciales (pares /
  impares), 30000 ticks; medida = fracción de E entre las vivas. ADAPTA si E
  gana (≥ 0.75) en ≥ 15/20; DEGRADA si pierde (≤ 0.25) en ≥ 15/20; NEUTRAL en
  otro caso. `exp_utero_jardin_comun.py`.
  **Resultado: NEUTRAL en ambos regímenes** (p=0.02: E gana 3, pierde 5 de
  18; p=1: 2 y 5 de 16; mediana de la fracción de E 0.50). Pero el detalle
  manda: en 8/18 semillas (p=0.02) y 7/16 (p=1) las dos disposiciones dan
  exactamente (1.00, 0.00) o (0.00, 1.00): **la competencia la decide la
  posición inicial, no el genoma.** Corrección a §21: sus réplicas variaban
  el orden de actualización pero no las posiciones de la sopa, así que la
  "selección determinista" que midió puede ser determinismo POSICIONAL (el
  mismo genoma gana porque está en el mismo lugar). La hipótesis de §18
  —genoma como proxy de posición— pasa a principal: en una línea con la
  frontera abierta (≈80 vivas en 512 lugares), quien toca el vacío funda el
  linaje que llena el espacio, sea cual sea su programa; ningún rasgo puede
  seleccionarse salvo "estar en el borde". §24: réplicas con las posiciones
  barajadas. (`results/utero_jardin_comun_run.txt`)

- **§24 — ¿posición o programa?, pre-registro (2026-09-27).** Réplicas
  congeladas que conservan el mismo conjunto de genomas y materias y el
  mismo orden de actualización, pero con las POSICIONES barajadas. Dos
  ecologías: abierta (n0 16, max_n 512: la frontera siempre abierta) y
  cerrada (n0 = max_n = 64: la línea nace llena, la reproducción sólo hacia
  lugares que abre la muerte o por invasión). 10 sopas × 5 réplicas, 30000
  ticks, W de Kendall contra nulo por permutación. PROGRAMA si p_W < 0.05 en
  ≥ 8/10; POSICIÓN si ≤ 3/10. Lectura conjunta declarada: abierta =
  POSICIÓN y cerrada = PROGRAMA señala la frontera abierta como causa
  estructural y traslada la evolvabilidad y la regulación a la ecología
  cerrada. `exp_utero_posicion.py`.
  **Resultado: PROGRAMA en ambas ecologías.** Abierta: p_W < 0.05 en 9/9
  sopas evaluables; el mismo genoma barre al 100% desde posiciones barajadas
  en 4–5/5 réplicas en 7/9 sopas. Cerrada: p_W = 0.001 en 10/10, sin barrido
  (share dominante 0.26–0.59, 5–11 genomas coexistiendo con ranking
  reproducible). La hipótesis posicional queda refutada: la selección ve
  programas, y con fuerza. Relectura de §23: A y E eran dos programas
  competitivamente equivalentes y la posición sólo desempató. Síntesis de la
  noche: selección fuerte sobre programas (§21, §24), oferta mutacional
  suficiente (§16b), y aun así la evolución abierta no produce adaptación
  (§17, §20, §22) ni nada mejor que el mejor programa de 16 al azar (§23).
  Hipótesis que queda: el techo de aptitud en la línea con frontera abierta
  es bajo y lo alcanzan muchos programas al azar (colonizar cada tick), así
  que no hay gradiente que subir; en la ecología cerrada, donde coexisten
  genomas con ranking reproducible, la competencia es interior y puede haber
  gradiente. §25: evolvabilidad (protocolo de §17) en la ecología cerrada.
  (`results/utero_posicion_run.txt`)

- **§25 — evolvabilidad en la ecología cerrada: SIN CONTACTO (2026-09-27).**
  El veredicto impreso es NO EVOLUCIONA (abierto 7/13, cerrado 9/16 pares por
  debajo del congelado), pero la mortalidad per cápita en la hambruna es
  0.004–0.006 en los tres brazos: con 42–44 vivas repartiéndose L0 = 9 la
  hambruna no mata a nadie, y la vara no tenía qué medir. Se lee como sin
  contacto, no como negativo de evolución. Hipótesis de fondo, ahora
  nombrable y falsable: **la sonda de ceguera aplana el gradiente de
  ingreso**. Mata a todo programa cuya salida no dependa de la materia; los
  programas legales tienen materia efectivamente pseudoaleatoria y su peso
  de luz |v − sol| promedia lo mismo para todos, así que no hay varianza
  heredable de aptitud en lo que el sol mide (coherente con §18: la energía
  predice, el genoma apenas; con §17/§20/§22: nada que seleccionar; con §21/
  §24: lo que la selección ve es otra cosa, robustez y colonización). Una
  excepción legal existe (v = vecino + 0.5: sensible a la materia y anti-sol
  en el borde, el doble de ingreso). §26: control positivo del gradiente en
  la ecología cerrada con luz escasa. (`results/utero_evoluciona_cerrado_run.txt`)

- **§26 — control positivo del gradiente, pre-registro (2026-09-27).**
  Ecología cerrada (n0 = max_n = 64), congelada, luz escasa L0 = 1.75
  (calibración ruidosa: 1.25 → 0.13, 1.5 → 0.82, 1.75 → 0.29 de mortalidad
  per cápita en A; se declaró 1.75). Se siembran 4 ANTISOL (v' = 0.5625 +
  0.0625·vl: a distancia toroidal 0.5 del sol de la hambruna, peso de luz
  0.55 contra 0.30 al azar; legal y no quieta) y 4 ESPEJO (v' = vl + 0.5:
  misma forma, ingreso al azar; control emparejado) entre 56 al azar, 20
  semillas, 30000 ticks. GRADIENTE si ANTISOL gana (≥ 0.25 y ≥ 2× ESPEJO) en
  ≥ 15/20; SIN GRADIENTE si ≤ 5/20. Error propio registrado: la primera
  versión de ANTISOL (0.875) quedaba a 0.18 del sol de la hambruna, peor que
  el azar; el humo dio 0/3 y se corrigió antes de la corrida completa.
  `exp_utero_gradiente.py`.
  **Resultado: GRADIENTE, 17/20.** ANTISOL pasa de 4/64 a la totalidad de
  las vivas (1.00) en 15/20 mundos antes de los 10000 ticks (0.80–0.94 en
  otros dos); ESPEJO, con la misma forma y sin ventaja de ingreso, desaparece
  (mediana 0.00). El ingreso de luz es fuerte y rápidamente seleccionable
  cuando la luz escasea. **La hipótesis "la sonda aplana el gradiente" queda
  refutada.** Con selección fuerte sobre programas (§24), gradiente real
  (§26) y oferta mutacional suficiente (§16b), la ausencia de adaptación es
  de CAMINO (la variación no alcanza programas con materia anti-hambruna) o
  de VARA (la mortalidad per cápita no capta lo que sube). Por primera vez
  hay un rasgo objetivo que la selección premia y que se puede medir en el
  tejido evolucionado: la distancia toroidal de la materia al sol de la
  hambruna. §27. (`results/utero_gradiente_run.txt`)

- **§27 — ¿sube el rasgo premiado?, pre-registro (2026-09-27).** Ecología
  cerrada con luz escasa (L0 = 1.75), 120000 ticks, 20 semillas, brazos
  abierto p = 0.02, abierto p = 1, cerrado, congelado; nada sembrado. Rasgo:
  peso de luz medio de la materia viva durante cada hambruna madura (w̄_A =
  distancia toroidal media a sol(t) + 0.05; ANTISOL ≈ 0.55, azar ≈ 0.30).
  ADAPTA si w̄_A tardío/temprano supera al del congelado en ≥ 75% de los
  pares (p signo < 0.05) y el nivel w̄_A también en ≥ 75%. Secundarias:
  mortalidad per cápita en A, fracción en la banda anti-hambruna (≥ 0.4).
  `exp_utero_rasgo.py`.
  **Resultado: NO EVOLUCIONA.** w̄_A nivel: abierto p0.02 0.300, p1 0.318,
  cerrado 0.312, congelado 0.337; razón tardío/temprano 1.00 en los cuatro
  brazos a lo largo de 59 hambrunas; pareado contra el congelado 11/20,
  12/20 y 9/20 (p 0.25–0.75); banda anti-hambruna 0.19–0.23 estable. ~14
  vivas por mundo. Con gradiente demostrado (§26: el mismo rasgo a 0.55
  barre en 10000 ticks), selección fuerte (§24) y 23 variantes viables por
  1000 ticks (§16b), la variación NO produce variantes con la materia más
  lejos del sol: **camino**. Dos lecturas posibles que §28 separa: (i) el
  vecindario a una o dos escrituras de un programa legal no contiene
  variantes con Δw̄ grande (el rasgo exige funciones casi constantes, que
  son una fracción ínfima de los programas); (ii) las hay, pero con ~14
  vivas todo Δw̄ pequeño es neutro frente a la deriva (s < 1/N ≈ 0.07) y
  sólo un salto grande sería visible. (`results/utero_rasgo_run.txt`)

- **§28 — alcanzabilidad del rasgo, pre-registro (2026-09-27).** Sin
  evolucionar: ≈50 programas legales del tejido evolucionado (abierto p = 1,
  cerrado, L0 = 1.75, 6000 ticks); por cada uno, 400 escrituras totales de
  una fila al azar, 400 sólo de opcode y 100 pares de escrituras totales.
  Fenotipo proxy w̄ = distancia toroidal media de la salida al sol de la
  hambruna (0.08) sobre 200 entradas uniformes, + 0.05 (ANTISOL ≈ 0.55);
  legalidad por la sonda. SALTOS si P(legal y Δw̄ ≥ +0.2) ≥ 1% (un salto
  grande cada pocos miles de ticks: §27 debió verlo → viabilidad en
  contexto); SIN SALTOS si < 0.1% (sólo pasos pequeños, neutros con N ≈ 14 →
  población efectiva). `exp_utero_alcanzabilidad.py`.
  **Resultado: SIN SALTOS.** 50 padres (w̄ mediana 0.305; 46 legales);
  ANTISOL da 0.533 en el proxy. Escrituras totales de un paso: 81% legales,
  Δw̄ mediana 0.000 y p90 0.000 (la mayoría de las escrituras no tocan la
  salida), máximo +0.188, P(Δw̄ ≥ +0.1) = 0.19%, **P(Δw̄ ≥ +0.2) = 0** en
  20000 variantes; sólo opcode: 0.07% y 0; dos pasos: 0.32% y 0. El paisaje
  local del rasgo es una meseta neutra con escalones raros y pequeños; el
  salto de 0.30 a 0.55 que barre en §26 no existe a uno ni a dos pasos. Con
  ≈14 vivas, un escalón de +0.1 es casi neutro frente a la deriva y aparece
  una vez cada ~19000 ticks por mundo. Por la regla: población efectiva.
  §29: §27 con la línea cerrada ×8 (512 lugares, L0 = 14).
  (`results/utero_alcanzabilidad_run.txt`)

- **§29 — población efectiva, pre-registro (2026-09-27).** §27 con la línea
  cerrada de 512 lugares y L0 = 14 (misma luz por lugar; humo: ≈190 vivas),
  brazos abierto p = 1, cerrado, congelado; 12 semillas; 120000 ticks; misma
  lectura (w̄_A tardío/temprano y nivel, pareados contra el congelado) y
  misma regla que §27. Humo de una semilla y 14000 ticks, anotado antes de
  la corrida y sin valor de prueba: w̄_A 0.405 (abierto) y 0.422 (cerrado)
  contra 0.348 (congelado). `exp_utero_rasgo_grande.py`.

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

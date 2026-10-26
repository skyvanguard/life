# El kernel en su propio mundo

*Programa abierto el 2026-10-26, después de cerrar la Fase B con Yvyra
(docs/PHASE_B_DESIGN.md) y por decisión de Fran: el kernel es el agente, sin
Hermes ni ningún LLM. Encarnación de la pregunta de docs/NORTE.md: ¿puede un
sistema nacer vacío, aprender en vida de su propia experiencia y sostener una
identidad, sin entrenamiento previo?*

## Por qué este mundo

Lo que faltó en los programas anteriores, en orden:

- **Yvyra**: la experiencia que recibía el kernel no la causaba el kernel. Era un
  reloj de modos con banderas binarias. Ψ sólo podía ver el reloj.
- **El útero (§45/§49)**: la celda aprendía en vida, pero vivía dos estaciones
  y nunca volvía a ver la misma. Aprender por recurrencia era imposible por
  construcción.
- **Ψ (exp_psi_quiebres.py)**: es un detector de sorpresa relativa. Su vara
  correcta es cuántos eventos detecta y con cuántas falsas alarmas, no qué
  fracción del tiempo pasa en ALTA.

Así que el mundo tiene que cumplir tres cosas: los actos del kernel causan lo
que percibe, los regímenes se repiten muchas veces en una vida, y hay eventos
que el kernel causa y eventos que le pasan.

## El mundo (§K1, `experiments/kernel/exp_mundo_propio.py`)

- **El estado** es un punto del 4-simplex. Se mueve así:
  `s' = normaliza(0.7 s + 0.3 roll(a, k))`. La acción `a` empuja el estado, y el
  régimen `k` (0..3) cambia qué coordenada empuja cada componente de la acción.
  Es una "rotación visuomotora" discreta.
- **La preferencia** es `C = (0.7, 0.1, 0.1, 0.1)`, fija toda la vida y propia
  del kernel. Para sostener `C` en el régimen `k` tiene que actuar `roll(C, -k)`.
- **El calendario** tiene visitas de 300 ticks:
  - Primero un ciclo de balbuceo motor. Son acciones al azar que el kernel
    registra como suyas, con copia eferente.
  - Después actúa durante los ciclos 2 a 6. Sólo tres de los cuatro regímenes
    se repiten, en un ciclo fijo.
  - El cuarto régimen (NUEVO) aparece una sola vez, tarde. Cambia con la
    semilla, así que cada régimen es el nuevo en 3 de las 12 semillas.
  - Después vienen los ciclos 7 y 8.
- **Los ticks de prueba** caen en la segunda mitad de las visitas, ~3 % de cada
  tipo. El mundo ejecuta una acción al azar en vez de la del kernel.
  - EFERENCIA: el kernel registra esa acción como suya.
  - EXO: no la registra; algo más lo movió.
  - La física es la misma; sólo cambia la copia eferente.

Los brazos son el kernel (EFE continuo, aprende toda la vida), el mismo kernel
congelado después del balbuceo (sólo aprende en la infancia) y uno reactivo,
sin meta, como referencia de no-control.

## La regla (pre-registrada en el docstring, antes de correr)

Usa tests de signo sobre 12 semillas; 10/12 da p = 0.019 a una cola.

| Lectura | Pregunta | Criterio |
|---|---|---|
| CONTROLA | ¿sostiene su preferencia? | error tardío del kernel en los ciclos 7–8 < 0.5 × el del reactivo |
| APRENDE | ¿aprende en vida algo que nunca vio? | en la visita NUEVA, error tardío kernel < congelado |
| RECUERDA (primaria) | ¿lo vivido le queda? | a la misma edad, el error temprano de la visita NUEVA > el promedio de las 6 visitas conocidas que la rodean |
| DISTINGUE (secundaria, Ψ) | ¿distingue lo que hizo de lo que le pasó? | Ψ < 0.85 más seguido en el tick que percibe un EXO que en uno de EFERENCIA |

Veredictos: NO CONTROLA, APRENDE Y RECUERDA, APRENDE SIN RECORDAR, RECUERDA
SIN APRENDER, NADA.

**No se mide acá:** la identidad. Necesita un diseño propio (por ejemplo, gemelos
criados en mundos distintos). Queda declarada como el paso siguiente.

## Antecedentes (citados de memoria, sin verificar en esta sesión)

- *Savings* en adaptación motora: la re-adaptación a una rotación ya aprendida
  es más rápida que la primera (Krakauer y colegas; el modelo de dos estados de
  Smith, Ghazizadeh y Shadmehr 2006).
- La inferencia de contexto explica los *savings* y la memoria de repertorios
  motores (COIN: Heald, Lengyel y Wolpert 2021).
- Principio de reaferencia (von Holst y Mittelstaedt 1950). Atenuación de las
  sensaciones autoproducidas: no podemos hacernos cosquillas (Blakemore,
  Wolpert y Frith 1998).

Lo que este programa agrega no son esos paradigmas. Los corre sobre un kernel
que nace vacío, sin preentrenamiento, y en una sola vida.

## §K2 — el sueño repasa el mundo (pre-registrado el 2026-10-26, antes de correr)

Decisión de Fran tras el §K1: "vamos con lo que recomiendas". Un solo cambio en
el kernel, `ConsciousKernel(wm_sleep_replay=...)`: guarda cada transición vivida
y, en cada tick de sueño (cada 50), el modelo del mundo da pasos de gradiente
sobre ventanas sacadas de todo el pasado vivido. Apagado (0, el default) es
idéntico byte a byte (tests en `tests/test_sleep_replay.py`). Experimento:
`experiments/kernel/exp_mundo_propio_sueno.py`; la regla completa está en su
docstring.

**Por qué en secuencia.** Lo encontré leyendo el código, antes de correr. El
régimen está oculto: una transición suelta `(s, a, s')` no dice qué régimen la
produjo. Un repaso paso a paso (el `replay_wm` del modo dreamer) mezcla todos los
regímenes en un modelo que no puede distinguirlos, así que sólo puede
promediarlos. El repaso en secuencia corre la misma recurrencia que la vigilia
(prior → mezcla con la observación) por ventanas de 16 ticks seguidos, con
backprop a través del tiempo, para que el latente aprenda a llevar el régimen
como un contexto inferido de los últimos ticks. Es la inferencia de contexto con
la que COIN explica los *savings*. La vigilia nunca propaga más de un tick, así
que no puede aprender eso.

**Cuánto sueño (declarado, no ajustado).** 50 pasos por sueño, uno por tick
vivido: el sueño duplica el entrenamiento de la transición, mitad del presente y
mitad de todo el pasado. Cada paso repasa 128 transiciones: 8 ventanas de 16 en
`secuencia`, 128 sueltas en `paso`.

**La sonda (lectura del mecanismo, no toca la vida).** Por régimen, 32
secuencias fijas de 24 transiciones de balbuceo. El modelo corre su recurrencia
desde `encode(s0)` y se mide el error después de 8 ticks de contexto, al final de
cada visita. "Otros" son los regímenes conocidos distintos del actual.

**Parte 1, control positivo del mecanismo.** Toda la vida es balbuceo; brazos
`sin_sueno`, `secuencia` y `paso`, 12 semillas.
- RETIENE_CTRL: error de la sonda en los otros, `secuencia` < `sin_sueno` en
  ≥ 10/12.
- CONTEXTO_CTRL: `secuencia` < `paso` en ≥ 10/12.
- **Regla de parada:** si RETIENE_CTRL falla, la parte 2 no se corre con este
  diseño.

**Parte 2, el test del §K1 con sueño.** Brazos `kernel` (el del §K1, que debe
reproducirlo exactamente), `secuencia` (el del veredicto), `paso` (control sin
contexto), `congelado` y `reactivo`. Regla: la del §K1 tal cual, con `secuencia`
en el lugar del kernel; RECUERDA sigue siendo la primaria.
- Atribución: si `secuencia` RECUERDA y `paso` no, es por contexto; si los dos
  recuerdan, es por intercalado y la secuencia no importa.
- Secundarias: RETIENE (sonda en los otros en los ciclos 7–8, `secuencia` <
  `kernel`) y DISTINGUE sobre `secuencia`.
- Advertencia declarada antes de correr, vista en la prueba de humo: el kernel
  que actúa vive cerca de C y sus datos son estrechos. Repasar el balbuceo de la
  infancia baja la sonda en cualquier brazo con sueño. El contraste que aísla el
  contexto es `secuencia` contra `paso`, y se reporta al lado.

**Predicciones, escritas antes de correr.** El brazo `kernel` reproduce el §K1.
`paso` promedia los regímenes y controla peor que `kernel`. `secuencia`: abierto.

**Enmienda (después de la parte 1 y antes de la parte 2, commiteada con el
resultado de la parte 1).** El contraste `secuencia` < `paso` no aislaba el
contexto: medía cuánto promedia cada brazo (ver el ledger). La atribución se
cambia por una vara con base. El promedio exacto de los regímenes conocidos es
el mejor predictor posible sin contexto, porque es el óptimo en error cuadrático
cuando cada régimen ocupa el mismo tiempo. Un modelo que lo supera está usando
contexto.
- MÁS ALLÁ DEL PROMEDIO: al final de las visitas de los ciclos 7–8, el error
  medio de la sonda en los 3 regímenes conocidos es < 0.9 × el del promedio
  exacto en ≥ 10/12. El margen 0.9 cubre la diferencia entre la media de normas
  y el error cuadrático.
- Si `secuencia` RECUERDA, se atribuye "por contexto" sólo si va MÁS ALLÁ DEL
  PROMEDIO. Si no, se atribuye "por promedio": un modelo del mundo generalista.
- La atribución vieja, basada en `paso`, se sigue imprimiendo y queda marcada
  como reemplazada.
- Predicción agregada antes de la parte 2:
  - Si el modelo es un generalista, la re-entrada a un régimen conocido arranca
    desde el promedio, que está más cerca que el especialista de la visita
    anterior. La entrada al NUEVO arranca más lejos (0.145). Por eso RECUERDA
    puede pasar, pero por promedio.
  - CONTROLA está en riesgo: cada sueño tira al especialista actual de vuelta
    hacia el promedio.

## §K3 — un repertorio del mundo (pre-registrado el 2026-10-26, antes de correr)

Decisión de Fran tras el §K2: "vamos con lo que recomiendas". La recomendación
fue un solo cambio, al estilo COIN: que el modelo del mundo vea su propio error
de predicción, para que pueda inferir en qué régimen está y no sólo promediar
lo vivido.

- **El mecanismo**: `ConsciousKernel(wm_error_input=True)`. La entrada de la GRU
  pasa a ser `[acción, observación − predicción del último tick observado]`.
  - En la imaginación y al comienzo de cada ventana de sueño, el error es cero.
  - Apagado es idéntico byte a byte (`tests/test_error_input.py`). La vida
    `secuencia` del §K2, semilla 0, se reproduce con diferencia 0.

**Lo que mostró la calibración (declarado; semillas 100–102 y un piloto offline,
nunca las semillas del test):**
- **Piloto offline.** Es la misma arquitectura, entrenada con BPTT sobre
  secuencias balbuceadas de los 3 regímenes conocidos, 30 000 pasos, 3 semillas.
  - **Hasta sin la entrada de error sale de la meseta del promedio**, después de
    5000–7500 pasos. El error de la sonda en lo conocido baja a 0.018, contra
    0.103 del promedio exacto.
  - La entrada de error acorta la meseta: a los 7500 pasos da 0.019, contra
    0.067 sin ella.
  - El promedio del §K2 era una meseta del entrenamiento, no un límite de
    capacidad.
- **Calibración en vida** (`exp_mundo_propio_contexto.py calibracion`,
  `results/mundo_propio_contexto_calibracion.txt`, vida balbuceada). Es el error
  de la sonda en los regímenes conocidos, en los ciclos 7–8, dividido por el del
  promedio exacto:

| Brazo | Qué tiene | ÷ promedio | Debajo de 0.9 |
|---|---|---|---|
| `secuencia` | el sueño del §K2 | 1.07 | 0/3 |
| `error` | el §K2 + entrada de error | 1.03 | 0/3 |
| `secuencia_x4` | 4 × la dosis de sueño (200 pasos por sueño) | 0.89 | 2/3, tarde (ciclo 8) |
| `error_x4` | las dos cosas | **0.44** | **3/3, desde el ciclo 6** |

Hacen falta las dos cosas. Con la dosis del §K2, la entrada de error no hace
nada, y la dosis sola apenas llega en una vida.

**El cambio que se prueba es `error_x4`**: el sueño del §K2 (ventanas de 16,
lotes de 8) con 4 veces la dosis, más la entrada de error. Los controles de
atribución son `secuencia_x4` (sólo la dosis) y `error` (sólo el error). El
mundo, el calendario, los ticks de prueba, la sonda y la regla del §K1 no
cambian. Los brazos del §K2 (`kernel`, `secuencia`, `congelado`, `reactivo`, y
`sin_sueno` en la parte 1) se leen de sus vidas guardadas: el camino del código
es idéntico byte a byte.

**Parte 1, control positivo en una vida balbuceada** (`control`, semillas 0–11):
- CONTEXTO_CTRL: en `error_x4`, el error medio de la sonda sobre los 3
  regímenes conocidos al final de los ciclos 7–8 < 0.9 × el del promedio exacto,
  en ≥ 10/12. Es la lectura MÁS ALLÁ DEL PROMEDIO del §K2.
- Regla de parada: si falla, la parte 2 no se corre con este diseño.
- Se reporta la atribución (CONTEXTO_CTRL de `secuencia_x4` y de `error`) y la
  ganancia del burn-in.
- `error` corre en la parte 2 sólo si pasa CONTEXTO_CTRL en la parte 1.

**Parte 2, el test del §K1** (por defecto, semillas 0–11):

| Lectura | Criterio |
|---|---|
| CONTEXTO (primaria) | la lectura de CONTEXTO_CTRL sobre `error_x4`, en la vida en que actúa |
| CONDUCTA | la regla del §K1 exacta sobre `error_x4` |
| ESPECIFICIDAD (secundaria) | la diferencia de RECUERDA de `error_x4` > la de `secuencia` (el generalista del §K2), en ≥ 10/12 |

Veredicto:
- CONTEXTO y APRENDE Y RECUERDA → **REPERTORIO**.
- CONTEXTO con otra conducta → **REPERTORIO SIN CONDUCTA**.
- Sin CONTEXTO → **SIN REPERTORIO**, con la conducta entre paréntesis.

Se reportan, sin ser veredictos: la atribución a `secuencia_x4`, DISTINGUE, las
visitas atascadas, la sonda en el régimen actual y en el NUEVO, y los costos de
entrada pareados contra `secuencia`.

**Predicciones escritas antes de correr:**
- Parte 1: `error_x4` pasa, `secuencia_x4` queda en el borde, `error` falla.
- Parte 2: CONTEXTO está en riesgo. El kernel que actúa vive cerca de `C`, así
  que sus datos son estrechos. La salida de la meseta, que en la calibración
  balbuceada llegó en el ciclo 6, puede llegar más tarde o no llegar.
- Si hay CONTEXTO, ESPECIFICIDAD positiva. CONTROLA queda abierto, porque cada
  sueño de 200 pasos mueve mucho al modelo del mundo.

## Ledger

*(se llena sólo con resultados que pasaron su control)*

### §K1 — NO CONTROLA por la letra; aprende en vida, no recuerda (2026-10-26)

`results/mundo_propio_run.txt`: 12 semillas × 3 brazos, 7500 ticks, 8 min.

- **CONTROLA: 9/12, el umbral era 10. Veredicto: NO CONTROLA.** El kernel
  sostiene su preferencia en la mayoría de las visitas: error tardío 0.07–0.12
  contra 0.52 del reactivo. Pero el 10 % de las visitas se atasca (27/264 con
  error tardío > 0.3), y en las 3 semillas que fallan esas visitas caen en los
  ciclos 7–8.
- **APRENDE: 12/12.** En la visita NUEVA, un régimen que nunca vio, el kernel
  llega a 0.084 de error tardío; el congelado tras la infancia queda en 1.052.
  Aprende en vida lo que la infancia no le dio. Es la lectura más fuerte, pero
  no es el veredicto: la regla exigía CONTROLA primero.
- **RECUERDA: 6/12, azar.** Vuelve a un régimen conocido igual de lento que a
  uno nuevo (diferencia mediana −0.017), y el costo de re-entrada no mejora en
  la vida: el error temprano de los ciclos 7–8 es menor que el del ciclo 2 sólo
  en 3/12. **Re-aprende en cada visita.**
- **DISTINGUE (Ψ): 9/12, no.** En el tick que percibe la prueba, Ψ baja de
  ALTA un 93 % de las veces con EXO y un 90 % con EFERENCIA. La energía libre
  tampoco las separa (AUC 0.55). El modelo del mundo no predice la consecuencia
  de una acción fuera de su política aunque la tenga registrada: la copia
  eferente no le sirve.
- **Posterior, no pre-registrado:** el error tardío del ciclo 7 es peor que el
  del ciclo 6 en 11/12. Aprender el régimen NUEVO perturba a los conocidos
  (interferencia). Además Ψ está debajo de ALTA en el 52 % de los ticks
  ordinarios de la segunda mitad de las visitas cuando el kernel actúa (mediana); con Yvyra satura, y acá no.

**Por qué no recuerda (verificado en el código).** El conocimiento de acción →
consecuencia vive sólo en el modelo del mundo, un único aprendiz online por
SGD. La memoria complementaria y el sueño del kernel no lo tocan:
`DreamEngine` recibe la memoria rápida, la lenta y el auto-modelo; el replay
transfiere estados del sí-mismo a la memoria lenta y a la identidad. Ninguno
de los dos archivos menciona `world_model`. La memoria del kernel es memoria
de sí, no del mundo. El replay de transiciones hacia el modelo del mundo
existe, pero sólo en el modo `dreamer` (`ReplayBuffer`, `replay_wm`).

**Convergencia con el útero.** Es el mismo resultado que el §45: un
generalista plástico que re-aprende cada estación. Acá no hay excusa de
vidas cortas: el kernel vio cada régimen conocido ocho veces en su vida,
seis antes de la visita NUEVA. Lo que falta en los dos
sustratos es una memoria del mundo que sobreviva al re-aprendizaje.

### §K2, parte 1 — RETIENE, pero como generalista y no por contexto (2026-10-26)

`results/mundo_propio_sueno_control_run.txt` (7.4 min) y
`results/mundo_propio_sueno_control_relectura.txt`. Vida entera de balbuceo, 12
semillas.

- **Por la letra pasa: RETIENE_CTRL 12/12 y CONTEXTO_CTRL 12/12.** La regla de
  parada deja correr la parte 2. Con sueño en secuencia, el error de la sonda en
  los regímenes que no está visitando baja de 0.191 a 0.124.
- **Pero no hay contexto.** El error después de 8 ticks de contexto es casi el
  de antes: +0.003 sobre 0.12 de ganancia. El signo es consistente (12/12) y el
  tamaño, despreciable.
- **`secuencia` se comporta como el promedio exacto** de los regímenes
  conocidos:

  | | conocidos | NUEVO |
  |---|---|---|
  | `secuencia` | 0.110 | 0.148 |
  | promedio exacto | 0.101–0.103 | 0.145 |

  Además paga en el presente: en el régimen actual el error es 0.081, contra
  0.036 sin sueño.
- Los otros dos brazos:
  - `sin_sueno` es el especialista del régimen actual: 0.191 en los otros, contra
    0.177 del especialista ideal.
  - `paso` queda en el medio, y su recurrencia deriva: el error crece después del
    contexto (−0.020).
- **MÁS ALLÁ DEL PROMEDIO: 0/12 en los tres brazos.**
- **Error de diseño, mío:** pre-registré `secuencia` < `paso` como el contraste
  que aislaba el contexto. Medía cuánto promedia cada brazo. Lo mostró la
  columna del contexto, que estaba en la tabla pre-registrada. Queda corregido
  en la enmienda, antes de la parte 2.
- **Lectura.** El sueño le da al modelo del mundo una memoria, pero es una
  memoria que promedia. BPTT sobre ventanas de 16 ticks, con 7500 pasos de
  gradiente en una vida, no basta para que el latente aprenda a inferir el
  régimen.

### §K2, parte 2 — APRENDE Y RECUERDA por la letra; recuerda por promedio, no por contexto (2026-10-26)

`results/mundo_propio_sueno_run.txt`: 12 semillas × 5 brazos, 18.3 min. Es el
primer veredicto positivo del kernel en su propio mundo.

- **Veredicto de `secuencia`, por la regla del §K1: APRENDE Y RECUERDA.**
  - CONTROLA 12/12. Las visitas atascadas bajan de 27 a 1.
  - APRENDE 12/12: en la visita NUEVA llega a 0.118, contra 1.052 del
    congelado.
  - RECUERDA 11/12: diferencia mediana +0.136, contra −0.017 sin sueño.
- **Atribución, con la vara enmendada antes de correr: por promedio, no por
  contexto.** MÁS ALLÁ DEL PROMEDIO da 0/12 (0.116 contra el límite de 0.093).
  La atribución vieja, la basada en `paso`, habría dicho "por contexto": la
  enmienda atrapó exactamente el señuelo que la parte 1 había mostrado.
- **Reproducción:** el brazo `kernel` reproduce el §K1 visita por visita, con
  diferencia máxima 0.
- **`paso`: APRENDE SIN RECORDAR.** CONTROLA 10/12, RECUERDA 7/12, 15 visitas
  atascadas.
- **Las predicciones, contra lo que pasó:**

  | Predicción | Resultado |
  |---|---|
  | `kernel` reproduce el §K1 | se cumplió |
  | `secuencia` recuerda por promedio | se cumplió |
  | `paso` controla peor que `kernel` | **falló**: controla mejor |
  | CONTROLA de `secuencia` en riesgo | **falló**: 12/12, y el sueño arregló el atasco |

- **DISTINGUE: 10/12 por la letra, y no se le cree.** EXO da 0.94 y EFERENCIA
  0.89, pero sin sueño la separación ya era la misma (mediana 0.035 contra 0.041)
  y el sueño la agranda sólo en 6/12. Es un efecto chico que ya existía y esta
  vez cruzó el umbral; no es atribuible al sueño.
- **Posterior, no pre-registrado:**
  - Ticks hasta llegar a ||s − C|| < 0.15:

    | | conocidos (ciclos 6–7) | NUEVO |
    |---|---|---|
    | `secuencia` | 22 | 46 |
    | `kernel` | 70 | 104 |

  - La re-entrada mejora con la edad (ciclos 7–8 contra ciclo 2) en 7/12; sin
    sueño, en 3/12.
  - La interferencia sigue: el ciclo 7 rinde peor que el 6 en 9/12.
  - El generalista paga en lo nuevo: su error tardío en la visita NUEVA es
    0.118, contra 0.084 sin sueño.

**Lectura.** Con un sueño que repasa lo vivido, el kernel tiene memoria del
mundo:
- vuelve a lo conocido 2–3 veces más rápido que a lo nuevo;
- deja de atascarse;
- su re-entrada mejora con la edad.

Pero esa memoria es un generalista, no un repertorio: no sabe en qué régimen
está, arranca desde el promedio de lo vivido. En términos de adaptación motora,
son *savings* por un mejor punto de partida, no por la inferencia de contexto
de COIN. Todavía no se le cree del todo: un positivo del programa se cree recién
cuando se replica.

**Réplica (pre-registrada el 2026-10-26, después de la parte 2 y antes de
correrla).**
- Semillas 12 a 23; cada régimen sigue siendo el NUEVO en 3 de ellas.
- Brazos `kernel`, `secuencia`, `congelado` y `reactivo`.
- Misma regla y misma atribución enmendada.
- REPLICADO si `secuencia` vuelve a dar APRENDE Y RECUERDA.
- Comando: `exp_mundo_propio_sueno.py replica`.

### §K2, réplica — REPLICADO; el efecto del sueño es sobre todo genérico (2026-10-26)

`results/mundo_propio_sueno_replica_run.txt`: semillas 12–23, 14.2 min.

- **`secuencia`, otra vez APRENDE Y RECUERDA:** CONTROLA 12/12, APRENDE 12/12
  y RECUERDA 10/12, con diferencia mediana +0.312.
- Hay 1 visita atascada, contra 39 sin sueño.
- La atribución es otra vez **por promedio**: MÁS ALLÁ DEL PROMEDIO da 0/12.
- **DISTINGUE: 8/12.** Esto confirma que el 10/12 de la parte 2 no se creía.
- **El brazo `kernel`, sin sueño, da APRENDE SIN RECORDAR** (CONTROLA 11/12,
  RECUERDA 8/12, mediana +0.129). En estas semillas, el contraste entre lo
  conocido y lo NUEVO ya es positivo sin sueño. Sobre las 24 semillas, sin sueño
  da 14/24 (mediana +0.046) y con sueño 21/24 (mediana +0.205).
- **Posterior, no pre-registrado: comparación pareada por semilla entre
  `secuencia` y `kernel`, sobre las 24 semillas.**
  - La re-entrada a lo conocido es más rápida con sueño en **24/24**: error
    temprano 0.26–0.31, contra 0.52–0.55.
  - La entrada a lo NUEVO también es más rápida con sueño, en 17/24.
  - **La especificidad, es decir que el sueño ayude más con lo vivido que con
    lo nuevo, da 16/24 (p = 0.076): sugerente, no establecida.**

**Lectura del §K2 completo.** El veredicto pre-registrado se replicó: con un
sueño que repasa lo vivido, el kernel aprende, controla sin atascarse y vuelve
a lo conocido más rápido que a lo nuevo. Pero la mayor parte de lo que hace el
sueño es genérica. El modelo del mundo pasa a ser el promedio de lo vivido, un
punto de partida mejor para cualquier régimen. La parte específica de lo vivido
existe, porque el promedio está más cerca de lo conocido (0.101) que de lo nuevo
(0.145), pero es modesta. Hay memoria del mundo, sin repertorio: el kernel no
sabe en qué régimen está.

### §K3, parte 1 — el modelo del mundo infiere el régimen en una vida balbuceada (2026-10-26)

`results/mundo_propio_contexto_control_run.txt`: semillas 0–11, 30.1 min.

- **CONTEXTO_CTRL: 11/12. La regla de parada pasa.** `error_x4` llega a 0.056 en
  los regímenes conocidos, contra 0.103 del promedio exacto (0.54×). La ganancia
  del burn-in es +0.020, contra +0.005 del §K2: el latente lleva el contexto de
  los primeros ticks.
- **Atribución: hacen falta las dos cosas.** `secuencia_x4` (sólo la dosis) da
  4/12, con mediana 1.00. `error` (sólo el error) da 0/12, así que no corre en la
  parte 2.
- **La salida de la meseta llega en el ciclo 6**, como en la calibración:
  0.099 → 0.073 → 0.026 en el ciclo 8.
- **El cociente varía mucho entre semillas**, de 0.18 a 0.94. Cuatro semillas
  salen del todo (≤ 0.22), la mayoría queda a medio camino (0.41–0.82) y una
  falla (la 6, con 0.94).
- **El repertorio no le cuesta al presente.** En el régimen actual da 0.039,
  contra 0.081 del generalista del §K2.
- **El NUEVO sigue igual:** 0.136, contra 0.144.
- **Predicciones:** `error_x4` pasa, se cumplió. `error` falla, se cumplió.
  `secuencia_x4` "en el borde" quedó peor que eso: 4/12.

### §K3, parte 2 — REPERTORIO por la letra (2026-10-26)

`results/mundo_propio_contexto_run.txt`: semillas 0–11, 31.4 min.

- **CONTEXTO (primaria): 12/12.** En la vida en que actúa, el modelo del mundo
  de `error_x4` llega a 0.064 en los regímenes conocidos, contra 0.103 del
  promedio exacto (0.64×; por semilla, de 0.41 a 0.81). La ganancia del burn-in
  es +0.028.
- **CONDUCTA: APRENDE Y RECUERDA, con 12/12 en las tres lecturas.** Hay 0
  visitas atascadas, y la diferencia de RECUERDA tiene mediana +0.223 (+0.136 en
  el §K2).
- **La re-entrada a lo conocido casi no cuesta.** El error temprano en las
  visitas conocidas de los ciclos 5–8 es 0.10–0.17, contra 0.20–0.34 del §K2 y
  0.45–0.64 sin sueño.
- **Veredicto pre-registrado: REPERTORIO.** Es el primero del programa: el
  kernel sabe en qué régimen está, y eso le sirve para actuar.
- **ESPECIFICIDAD (secundaria): 8/12, no pasa.** Contra el generalista del §K2,
  la entrada a lo conocido mejora mucho (12/12, mediana 0.134 contra 0.306). La
  entrada a lo NUEVO también mejora, aunque menos (8/12, 0.356 contra 0.402).
  La ganancia es mayor en lo conocido en 8/12.
- **El costo: lo NUEVO tarde.** El error tardío en la visita NUEVA es 0.133,
  contra 0.118 del §K2 y 0.084 sin sueño. APRENDE igual pasa 12/12 contra el
  congelado.
- **Atribución:** `secuencia_x4` (sólo la dosis) da CONTEXTO 3/12. Su conducta
  es APRENDE Y RECUERDA, igual que el §K2: sin el error no hay repertorio.
- **DISTINGUE, reportada y no veredicto en este pre-registro: 12/12.** Ψ cae
  en el 95 % de los EXO y en el 84 % de los EFERENCIA. Las falsas alarmas bajan
  a 0.44.
  - Posterior: la separación EXO − EFERENCIA (+0.119) supera la del kernel sin
    sueño en 12/12, la de `secuencia` en 12/12 y la de `secuencia_x4` en 10/12.
  - A diferencia del §K2, la separación no está ya sin el mecanismo. Pero es
    posterior: va pre-registrada a la réplica.
- **Predicciones:** "CONTEXTO en riesgo" falló, porque se sostuvo 12/12. Que
  hubiera ESPECIFICIDAD positiva si había CONTEXTO también falló: dio 8/12.
  CONTROLA, que estaba abierto, dio 12/12 con 0 atascadas.

**Réplica (pre-registrada el 2026-10-26, después de la parte 2 y antes de
correrla).**
- Semillas 12–23. Corre sólo `error_x4`; los brazos del §K2 se leen de su
  réplica.
- REPLICADO si `error_x4` vuelve a dar REPERTORIO.
- Secundaria pre-registrada: DISTINGUE ≥ 10/12 **y** DISTINGUE PAREADO, es decir
  que la separación de `error_x4` supere la del kernel sin sueño en ≥ 10/12. Hacen
  falta las dos para decir "distingue, y por el mecanismo".
- Comando: `exp_mundo_propio_contexto.py replica`.

### §K3, réplica — NO REPLICADO por la letra; DISTINGUE sí, y por el mecanismo (2026-10-26)

`results/mundo_propio_contexto_replica_run.txt`: semillas 12–23, 16.6 min.

- **CONTEXTO: 8/12, no pasa.** La mediana del cociente es la misma, 0.64×, pero
  cuatro semillas quedan en 0.95–1.01, y una en 0.89, apenas debajo del
  umbral. Veredicto pre-registrado: **SIN REPERTORIO (APRENDE Y RECUERDA)**.
  **El REPERTORIO no se replicó.**
- **La conducta, en cambio, se replicó entera:** 12/12, 12/12 y 12/12, con 0
  visitas atascadas y diferencia de RECUERDA +0.210.
- **DISTINGUE (secundaria pre-registrada): 12/12. DISTINGUE PAREADO: 12/12**,
  con separación +0.135 contra +0.026 del kernel sin sueño. Ψ cae en el 94 % de
  los EXO y en el 81 % de los EFERENCIA. Pasan las dos condiciones: **distingue
  lo que hizo de lo que le pasó, y por el mecanismo.** Es la primera vez en el
  programa.
- **ESPECIFICIDAD: 5/12, otra vez no.** La entrada a lo conocido mejora 12/12
  contra el §K2 (0.137 contra 0.352), pero la entrada a lo NUEVO también mejora,
  8/12 (0.337 contra 0.604).
- **Posterior, no pre-registrado, sobre las 24 semillas:**
  - **La visita NUEVA rompe el repertorio y el sueño lo reconstruye.** El
    cociente de la sonda, en medianas de las partes 2 y réplica, vale 0.47 y 0.36
    al final del ciclo 6. Al final de la visita NUEVA sube a 1.06 y 1.07, peor
    que el promedio. En el ciclo 7 vale 0.79 y 0.76, y en el ciclo 8, 0.48 y
    0.51.
  - Aprender lo nuevo interfiere con lo conocido, como en el §K1, y el sueño lo
    repara en unos dos ciclos. La lectura pre-registrada, la de los ciclos 7–8,
    cae en plena recuperación.
  - Juntando las dos corridas, debajo de 0.9 quedan 20/24 (p = 0.0008).
  - Un mejor contexto va con una re-entrada más barata: Spearman entre el
    cociente y el error temprano de las visitas conocidas de los ciclos 7–8,
    ρ = 0.54 (p = 0.007).
  - La separación de DISTINGUE crece con la calidad del modelo del mundo, según
    la parte 2: `secuencia` +0.041, `secuencia_x4` +0.070, `error_x4` +0.119.
    La copia eferente rinde cuando el modelo predice bien las consecuencias de
    acciones arbitrarias. No es un módulo propio/ajeno.

**Lectura del §K3 completo.**
- **Conducta.** Con la entrada de error y el sueño 4×, el kernel aprende,
  controla sin atascarse y vuelve a lo conocido casi sin costo. Pasa en 24/24
  semillas en las tres lecturas.
- **Distingue.** Distingue lo que hizo de lo que le pasó, y eso es atribuible
  al mecanismo: pre-registrado y replicado.
- **Repertorio.** Su modelo del mundo infiere el régimen en la mayoría de las
  vidas (20/24 debajo de 0.9), pero no con la confiabilidad que pide la regla, y
  la réplica falló.
- **Por qué falla.** El repertorio es frágil ante lo nuevo: una sola visita a
  un régimen desconocido lo deshace, y el sueño tarda unos dos ciclos en
  rehacerlo.
- **La especificidad no se estableció** en ninguna de las dos corridas: la
  mejora sobre el §K2 alcanza también a lo NUEVO.

**Lo que sigue abierto:**
- Un repertorio robusto. El de ahora se deshace con lo nuevo: aprender un régimen
  desconocido pisa a los conocidos. COIN resuelve esto creando un contexto nuevo
  en vez de reescribir los viejos.
- La identidad: gemelos criados en mundos distintos.
- Distinguir lo que hizo de lo que le pasó ya no está abierto (§K3, replicado).

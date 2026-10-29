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

## §K4 — identidad: gemelos criados en mundos distintos (pre-registrado el 2026-10-26, antes de correr)

Decisión de Fran tras el §K3: "continua", sobre la recomendación de ir a la
identidad. Es el pilar de la pregunta del norte que faltaba tocar.

**Qué se entiende acá por identidad.** Continuidad psicológica: una diferencia
individual que escribe el pasado propio, que sobrevive a un presente compartido
y que la señal del propio kernel puede leer. No mide un sentido de sí; eso sigue
siendo la estrella (docs/NORTE.md). Lo que el diseño agrega sobre el §K1–§K3:
- **Gemelos.** La diferencia entre los dos sólo puede venir de la vida, porque
  nacen idénticos.
- **Un adversario largo.** El exilio compartido dura tanto como la niñez; en el
  §K3, lo nuevo era una sola visita de 300 ticks.
- **El módulo de identidad declarado.** Se mide si el `self_embedding` del
  auto-modelo lleva la identidad.

**El diseño** (`experiments/kernel/exp_mundo_propio_gemelos.py`):
- **Gemelos idénticos al nacer**: los mismos pesos y el mismo azar
  (`torch.manual_seed(par)`). Comparten el balbuceo, los ticks de prueba y las
  acciones de prueba. Lo único que cambia es el régimen de su casa.
- **Los mundos** son los 4 regímenes del §K1. En cada par hay cuatro papeles: la
  casa de A, la casa de B, el exilio X (compartido) y N (nadie lo vive). En los
  12 pares, cada régimen juega cada papel 3 veces.
- **La vida** tiene 33 bloques de 300 ticks:
  - 3 de balbuceo en casa;
  - 15 de niñez actuando en casa (los mismos ticks que los ciclos 2–6 del §K1);
  - 15 de exilio en X, los dos gemelos juntos (mismo régimen, mismas pruebas).
  - Son 9900 ticks y entran enteros en el buffer del sueño (capacidad 10 000).
    Mano declarada: una vida más larga empezaría a olvidar la niñez por
    construcción.
  - Asimetría declarada: los gemelos balbucean sólo en casa (la infancia); en
    el exilio sólo actúan.
- **Los ensayos** se hacen antes de los bloques 18 (fin de la niñez, T1), 23
  (1500 ticks de exilio, Tm) y 33 (fin del exilio, T2).
  - Un clon de cada gemelo vive una visita de 300 ticks en la casa de A y otro en
    la de B. Actúa, sin ticks de prueba, desde el estado actual, y después se
    descarta.
  - La vida del original no cambia: verificado, diferencia 0.
  - Los dos gemelos reciben el mismo azar en cada ensayo, así que el ensayo es
    pareado.
  - Prueba de humo (`humo`): los clones de los gemelos recién nacidos dan
    lecturas idénticas (H = 0 exacto), y un clon que sigue con el azar de su
    original lo reproduce (diferencia 0).
- **El cruce.** H = (A en la casa de B + B en la casa de A) − (A en su casa + B
  en su casa), sobre el costo de re-entrada `e_early` (‖s − C‖ medio de los
  ticks 0–99, la lectura de RECUERDA del §K1).
  - Los efectos de mundo y de gemelo se cancelan.
  - H > 0 quiere decir que cada uno anda mejor en su mundo que su hermano.

**Brazos.** `error_x4` (el kernel del §K3) y `kernel` (el del §K1, sin sueño),
que es el control de atribución.

**La regla** (tests de signo sobre 12 pares, ≥ 10/12, p = 0.019 a una cola):

| Lectura | Criterio |
|---|---|
| SE DIFERENCIA (control positivo) | H(T1) > 0 en `error_x4`. Si falla: NO SE DIFERENCIA, y el resto no se lee |
| PERSISTE (primaria) | H(T2) > 0 en `error_x4` |
| RECONOCE (secundaria) | el cruce de la energía libre del propio kernel en los ticks 1–20 de la visita, en T2, > 0 en `error_x4`: su propia sorpresa dice "esta es mi casa" |
| ATRIBUCIÓN | PERSISTE en `kernel`, y el pareado H(T2) de `error_x4` > el de `kernel` |

Veredicto:
- Sin SE DIFERENCIA → **NO SE DIFERENCIA**.
- SE DIFERENCIA y PERSISTE → **IDENTIDAD**, con la atribución:
  - **por el sueño**, si `kernel` no persiste y el pareado pasa;
  - **también sin el sueño**, si `kernel` persiste;
  - **sin atribuir**, en otro caso.
- SE DIFERENCIA sin PERSISTE → **IDENTIDAD FRÁGIL**.

Se reportan, sin ser veredictos: H en Tm (el curso temporal), los cruces de la
sonda y de Ψ, la distancia entre los `self_embedding` de los gemelos en cada
ensayo, el control en casa y en el exilio, los bloques atascados y DESVENTAJA
(abajo).

**Predicciones escritas antes de la calibración:**
- SE DIFERENCIA 12/12 en los dos brazos. Es casi trivial: en T1 el ensayo en
  casa no cambia de régimen y el de afuera sí.
- `kernel`: PERSISTE falla. En el §K1 no había ahorro.
- `error_x4`: PERSISTE pasa, con un H(T2) bastante menor que H(T1). El sueño
  repasa toda la vida vivida, y al final del exilio la mitad de lo que repasa
  es la niñez.
- RECONOCE sigue a PERSISTE.
- `self_embedding`: la distancia entre los gemelos se achica mucho en el exilio.
  Es un EMA de τ ≈ 100 ticks de lo que hace el kernel, así que el módulo de
  identidad declarado no lleva la identidad.

**Calibración** (`calibracion`, pares 100–102, nunca los del test;
`results/mundo_propio_gemelos_calibracion_run.txt`). Los tres pares comparten el
patrón de papeles B − A = 2, X − A = 3. No se ajustó nada.
- SE DIFERENCIA: 3/3 en los dos brazos.
- `error_x4`: H(T1) +1.75 y H(T2) +0.74 (3/3); RECONOCE 3/3.
  - Su modelo del mundo conserva la casa: la sonda da 0.014 en la casa propia,
    contra 0.18 en la del hermano.
  - El régimen del exilio nunca aparece en la sonda (0.18, igual que N, que
    nadie vivió). La sonda usa acciones al azar, y en el exilio no hay balbuceo.
- `kernel`: H(T2) −0.51, sólo 1/3 positivo.
  - Después del exilio, el kernel sin sueño **vuelve más lento a su propia
    casa que a la de su hermano** (A→A 0.88 / 0.43 / 0.36, contra A→B 0.32 /
    0.22 / 0.31). No está explicado.
  - Su sonda olvida la casa: 0.26, igual que la del hermano.
- Ψ se satura después de T1: sus cruces dan 0.
- `self_embedding`: la distancia entre los gemelos no se achica (`error_x4` 2.06
  → 2.40, `kernel` 2.05 → 2.97). La predicción de arriba ya parece equivocada y
  queda como estaba escrita.

**Predicciones agregadas después de la calibración, antes de los pares del
test:**
- PERSISTE y RECONOCE pasan en `error_x4`.
- PERSISTE falla en `kernel`.
- Reportada, con su propio criterio: **DESVENTAJA**, H(T2) < 0 en `kernel` en
  ≥ 10/12. Es la desventaja de la propia casa que se vio en la calibración
  (2/3). Predicción: pasa.

**Réplica (pre-registrada el 2026-10-26, después del test y antes de correrla).**
- Pares 12–23 (cada régimen sigue jugando cada papel 3 veces), los dos brazos y
  la misma regla.
- **REPLICADO** si el veredicto vuelve a ser IDENTIDAD. La atribución se lee con
  la misma regla y se reporta también sobre los 24 pares juntos.
- Secundaria, sacada de una lectura posterior del test (11/12 ahí; el primer
  bloque del exilio, 21/24 gemelos): **RIGIDEZ**. El costo en T1 en la casa del
  hermano (media de los gemelos) de `error_x4` > el de `kernel`, en ≥ 10/12. El
  kernel que conserva su niñez entra peor a un mundo que nunca vivió.
- Se reportan otra vez RECONOCE (8/12 en el test), DESVENTAJA (3/12 en el test:
  falló la predicción de la calibración), el `self_embedding` y los bloques
  atascados.
- Predicciones:
  - PERSISTE se replica: 12/12 en el test, con H mínimo +0.26.
  - PERSISTE en `kernel` es una moneda en el umbral (9/12), así que la
    atribución "por el sueño" está en riesgo.
  - RECONOCE vuelve a fallar.
  - RIGIDEZ pasa.

## §K5 — el precio de la identidad y dónde vive (pre-registrado el 2026-10-26, antes de correr)

Decisión de Fran tras el §K4: "push todo a main, luego vamos con los 3 pasos que
mencionaste". Los pasos eran tres: la rigidez, un nulo de deriva para el
`self_embedding` y un repertorio robusto a lo nuevo. Este experimento cubre los
dos primeros; el repertorio robusto necesita un mecanismo nuevo y va aparte.

**Por qué.** El §K4 dejó dos cosas abiertas.
- **El precio.** Criado en un solo mundo, el kernel que conserva su niñez entra
  peor que el kernel sin sueño a un mundo que nunca vivió. Fue RIGIDEZ 12/12,
  pre-registrada en la réplica. En el §K3, criado entre tres regímenes, ese
  mismo kernel aprendía a inferir el régimen. ¿Una niñez plural quita el precio
  sin perder la identidad?
- **Dónde vive.** La distancia entre los `self_embedding` de los gemelos no se
  achicó en el exilio; en la réplica creció. Sin un nulo, no se puede saber si
  lleva algo de la vida o si es deriva.

**P1 — crianza** (`experiments/kernel/exp_mundo_propio_crianza.py`).
- Mismos gemelos, mismos papeles, mismo exilio y mismos ensayos que el §K4. Sólo
  cambia la niñez.
- **`una`** es el §K4. Sus vidas guardadas se reutilizan y no se vuelven a
  correr. Se verifica que el camino del código es el mismo re-corriendo una vida:
  la diferencia máxima tiene que dar 0. En la prueba de humo dio 0.
- **`dos`.** Los 18 bloques de la niñez alternan la casa y una ESCUELA, que es el
  régimen N: lo comparten los dos gemelos y en el §K4 nadie lo vivía. El último
  bloque de la niñez es en casa: los bloques 1, 3, …, 17 en casa y los 0, 2, …,
  16 en la escuela, 9 y 9. De los de balbuceo, 1 es en casa y 2 en la escuela.
- Manos declaradas:
  - La casa recibe la mitad de la niñez.
  - Para cada gemelo, la casa del hermano y X siguen sin haber sido vividas. Las
    lecturas de rigidez del §K4 conservan su sentido, y en T1 las dos crianzas
    ensayan desde la casa.
- Brazos: `error_x4` y `kernel` (sin sueño), en las dos crianzas.
- **Lecturas.** El costo es el de T1 en la casa del hermano (la media de los
  gemelos), la lectura de RIGIDEZ del §K4. La brecha es costo(`error_x4`) −
  costo(`kernel`): el precio del sueño.

| Lectura | Criterio (≥ 10/12) |
|---|---|
| ACHICA (primaria) | brecha(`dos`) < brecha(`una`), pareado por par |
| CONSERVA | H(T2) > 0 en `error_x4` bajo `dos` (el PERSISTE del §K4) |
| INVIERTE (secundaria) | bajo `dos`, costo(`error_x4`) < costo(`kernel`): el sueño pasa de precio a ventaja |

Veredicto:
- sin ACHICA → **LA RIGIDEZ SE QUEDA**;
- ACHICA sin CONSERVA → **MENOS RÍGIDO, SIN IDENTIDAD**;
- ACHICA y CONSERVA → **MENOS RÍGIDO, CON IDENTIDAD**, y se agrega "y la
  invierte" si pasa INVIERTE.

Se reportan, sin ser veredictos:
- FLEXIBLE: costo(`error_x4`, `dos`) < costo(`error_x4`, `una`), y lo mismo en
  `kernel`. Sería un efecto genérico de haber practicado cambios de régimen.
- El primer bloque del exilio (`e_early` del bloque 18, media de los gemelos) y
  los bloques atascados, por crianza.
- H en T1, Tm y T2; PERSISTE en `kernel` bajo `dos`; la sonda (casa, hermano, X
  y escuela).

**P2 — deriva.** Cada gemelo `error_x4` del §K4 (crianza `una`) se vuelve a vivir
con OTROS DADOS. Mantiene los mismos pesos al nacer, la misma casa, el mismo
exilio y el mismo azar en los ensayos. Cambian dos cosas: `torch` se vuelve a
sembrar después de construirlo (50000 + par), y las pruebas y el balbuceo salen
de otro azar (58000 + par). Es la misma vida salvo el azar, y diverge desde el
tick 0, igual que los gemelos del §K4.
- d_mundo(T) = ‖yo_A − yo_B‖: los gemelos del §K4, otro mundo y el mismo azar.
- d_dados(T) = media(‖yo_A − yo_A'‖, ‖yo_B − yo_B'‖): el mismo mundo y otro azar.

| Lectura | Criterio (≥ 10/12) |
|---|---|
| CONTROL (la vara lee) | la misma comparación sobre el perfil de la sonda del modelo del mundo (las 4 sondas del bloque anterior al ensayo): d_mundo > d_dados en T1 |
| LLEVA | d_mundo > d_dados en el `self_embedding` en T1: lleva algo del mundo más allá del azar |
| NIÑEZ | lo mismo en T2, después del exilio: lleva la identidad |

Veredicto:
- sin CONTROL → **LA VARA NO LEE**;
- sin LLEVA → **DERIVA**;
- LLEVA sin NIÑEZ → **LLEVA LA VIDA, NO LA NIÑEZ**;
- las dos → **EL YO LLEVA LA NIÑEZ**.

Se reportan el CONTROL en T2, las medianas y el control de conducta de los
gemelos con otros dados (`e_late`).

**Prueba de humo** (`humo`, par 0, vida corta).
- El camino `una` reproduce la vida guardada del §K4 con diferencia 0.
- El gemelo con otros dados nace con el mismo `self_embedding` (diferencia 0) y
  su vida diverge.
- El calendario de `dos` es casa, escuela, casa, y después el exilio.

**Predicciones, escritas antes de correr:**
- P1:
  - ACHICA pasa. Con dos regímenes, el modelo del mundo aprende a leer su error
    como "cambió el régimen", como en el §K3. Un mundo nuevo pasa a ser un
    contexto nuevo y no un error confiado.
  - CONSERVA pasa: 9 bloques en casa siguen entrando en el buffer del sueño.
  - INVIERTE falla: el sueño sigue repasando los mundos viejos mientras entra a
    uno nuevo.
- P2:
  - CONTROL pasa.
  - DERIVA. El `self_embedding` es un EMA, con τ de unos 100 ticks, del estado
    reflejado, y un kernel que controla bien ve un estado cercano a C en
    cualquier mundo.
  - La prueba de humo ya mostró d_mundo > d_dados en un par corto (3.6 contra
    1.3). La predicción queda como estaba escrita.
- **Nota agregada con el test ya corriendo y antes de ver su resultado.** El
  razonamiento de la predicción de P2 estaba mal. El auto-modelo no refleja lo
  que el kernel observa: con `action_dim == obs_dim`, el `self_state` que entra
  en `reflect()` es la acción que el kernel elige (`conscious_kernel.py`, paso
  ACT). En mundos distintos, la acción que lleva a C es otra coordenada. La
  regla y la predicción escrita no cambian. Lo que ahora espero es que LLEVA
  pase en T1 y que NIÑEZ sea incierta, porque en el exilio los dos gemelos eligen
  la misma acción.

**Réplica, pre-registrada junto con el test.** Pares 12–23, reutilizando las
vidas de la réplica del §K4 para `una`, con la misma regla. Se lanza apenas
termine el test, salvo que aparezca un bug (todo cambio se registra). Cada
pregunta queda REPLICADA si su veredicto se repite.

Cada corrida tiene 72 vidas nuevas más una de verificación, en 3 procesos de CPU
con 1 hilo cada uno (la excepción declarada del kernel). Unos 95 min.

## §K6 — un repertorio robusto: contextos al estilo COIN (pre-registrado el 2026-10-26, después de la calibración y antes de correr)

El tercer paso que pidió Fran. El §K3 le dio al kernel un repertorio: viendo su
propio error y con 4× sueño, el modelo del mundo infiere en qué régimen está.
Pero el repertorio no se replicó por la letra (8/12). La razón, vista en una
lectura posterior: la única visita NUEVA pisa los regímenes conocidos. El cociente
de la sonda pasa de 0.47 y 0.36 a 1.06 y 1.07, y el sueño tarda unos dos ciclos
en reconstruirlo. COIN (Heald, Lengyel y Wolpert, 2021) evita esa interferencia
creando una memoria nueva para un contexto nuevo.

**El mecanismo** (`src/zeta_life/kernel/contextual_world_model.py`, activado con
`ConsciousKernel(wm_contexts=K)`, probado en `tests/test_contextual_world_model.py`).
- K expertos (cada uno un `WorldModel`) se crean al nacer, vacíos. Al principio
  se usa uno solo.
- Todos los expertos en uso predicen cada tick, con la misma acción ejecutada, y
  siguen el flujo con su propia recurrencia. Sólo el activo aprende.
- Cada uno lleva un error corriente: un EMA de ‖obs − pred‖ con τ de 10 ticks.
- **Cambio:** pasa al experto que mejor explica cuando le gana al activo por un
  margen del 20 %.
- **Contexto nuevo:** nace cuando ninguno explica (error > 0.08) durante 30 ticks
  seguidos. Arranca con los pesos actuales del activo, así hereda la física
  general.
- **Protección:** cuando un experto establecido deja de explicar, se guarda una
  foto de sus pesos. Si otro toma el control, el viejo vuelve a esa foto y las
  transiciones de la racha pasan al buffer del que tomó el control.
- **Establecido** quiere decir que alguna vez explicó el flujo. Mientras un
  experto aprende su primer contexto, no saca foto ni da lugar a uno nuevo.
- **Sueño:** cada experto duerme sobre su propio buffer. La dosis total es la del
  kernel, repartida según el tamaño de cada buffer.
- **Verificaciones:**
  - Con `wm_contexts=0` es idéntico byte a byte: una vida `error_x4` del §K4 se
    reproduce con diferencia 0.
  - Pasan los 803 tests.
  - Con un solo experto, la sonda contextual da lo mismo que la del §K3.

**El experimento** (`experiments/kernel/exp_mundo_propio_coin.py`).
- El brazo `coin` es `error_x4` con `wm_contexts=6`.
- El mundo, el calendario, los ticks de prueba, la sonda, las lecturas y la regla
  del §K1 son los del §K3.
- Se reutilizan de disco las vidas `error_x4` (§K3) y las de `kernel`,
  `secuencia`, `congelado` y `reactivo` (§K2).
- Declarado: `coin` crea 6 expertos al nacer, así que sus pesos iniciales y su
  azar difieren de los de `error_x4` en la misma semilla. El contraste es
  pareado por semilla, pero no comparte el azar.
- **La sonda con contextos.** Todos los expertos en uso recorren cada secuencia
  de prueba. En cada secuencia, el paso j lo predice el experto con menor error
  medio en los pasos anteriores; en el paso 0, el activo. Es el régimen inferido
  con los primeros ticks. Se reporta también el oráculo: el mejor experto por
  secuencia.

**Manos declaradas.**
- 6 lugares para expertos.
- Las constantes de inferencia (τ, umbral, margen, persistencia y gracias) salieron
  de una sola vida de exploración (semilla 100, nunca de test) y de los tests
  unitarios.
- La condición de "establecido" se agregó cuando el driver de los tests mostró
  que un experto recién nacido sacaba foto de sus pesos vacíos.
- No se cambió nada después de la calibración.

**Calibración** (`calibracion`, semillas 100–102, vida actuando del §K3, `coin` y
`error_x4`; `results/mundo_propio_coin_calibracion_run.txt`).

| | Sonda de los conocidos / promedio exacto, al final de la visita NUEVA | Desde qué ciclo baja |
|---|---|---|
| `coin` | 0.13–0.14 (oráculo igual) | 0.10–0.15 desde el ciclo 2 |
| `error_x4` | 1.02–1.10: la fragilidad del §K3, reproducida | 1.0 hasta los ciclos 4–6 |

- Contextos: 4–5 para 4 regímenes; uno espurio en dos semillas.
- Lo NUEVO tiene su propio experto en 3/3; en la semilla 101 se reparte 0.53.
- Control al final de las visitas: mejor (`e_late` 0.04, contra 0.06–0.10). Fin
  de lo NUEVO: 0.04–0.07, contra 0.10–0.17.
- La re-entrada a lo conocido NO es mejor: `e_early` 0.18 / 0.11 / 0.12, contra
  0.12 / 0.26 / 0.09. El cambio espera al error corriente.
- Una entrada a lo NUEVO fue mala: 0.82, en la semilla 101.

**La regla** (tests de signo sobre 12 semillas, ≥ 10/12):

| Lectura | Criterio |
|---|---|
| ROBUSTO (primaria) | sonda de los conocidos / promedio exacto al FINAL de la visita NUEVA < 0.9 en `coin`: el momento en que se rompía el repertorio del §K3 |
| CONTEXTO | la primaria del §K3 en `coin` (ciclos 7–8, < 0.9) |
| CONDUCTA | la regla del §K1 en `coin` |
| PAREADO (secundaria) | cociente al final de lo NUEVO, `coin` < `error_x4`: la robustez es del mecanismo |

Veredicto:
- ROBUSTO y CONTEXTO → **REPERTORIO ROBUSTO**. Si la conducta no es APRENDE Y
  RECUERDA, se agrega "SIN CONDUCTA (…)".
- Sólo CONTEXTO → **REPERTORIO FRÁGIL**.
- Sólo ROBUSTO → **ROBUSTO SIN CONTEXTO**.
- Ninguno → **SIN REPERTORIO**.

Se reportan: el oráculo, los contextos por vida, la proporción del experto
mayoritario por régimen, si lo NUEVO tiene su propio experto, los costos de
entrada pareados contra `error_x4` (conocidos de los ciclos 7–8 y NUEVO),
ESPECIFICIDAD, DISTINGUE y los atascos.

**Predicciones (después de la calibración, antes del test):**
- ROBUSTO 12/12, CONTEXTO 12/12 y PAREADO 12/12.
- CONDUCTA: APRENDE Y RECUERDA.
- La re-entrada a lo conocido no mejora contra `error_x4`: el pareado queda en el
  azar o peor.
- Contextos espurios en algunas vidas.
- Lo NUEVO con su propio experto en ≥ 10/12.

**Réplica, pre-registrada junto con el test.** Semillas 12–23 (`error_x4` de la
réplica del §K3, el resto de la del §K2), con la misma regla. Se lanza apenas
termine el test, salvo que aparezca un bug, y todo cambio se registra. Queda
REPLICADO si el veredicto se repite.

## §K7 — las casas: identidad con repertorio (pre-registrado el 2026-10-27, después de la calibración y antes de correr)

Decisión de Fran tras el §K5 y el §K6: "sigue con lo que recomiendas". La
recomendación era juntar el repertorio del §K6 con la identidad del §K4 y la
crianza del §K5.

**Por qué.** Las dos líneas del programa llegaron a un punto en común.
- §K4: gemelos criados en mundos distintos siguen distintos después de un
  exilio compartido (IDENTIDAD, por el sueño, 24/24). La identidad vive en el
  modelo del mundo y cuesta rigidez: el que conserva su niñez entra peor a un
  mundo nunca vivido (12/12).
- §K5: con una crianza plural (casa y escuela) la rigidez se achica sin perder
  la identidad.
- §K6: un repertorio al estilo COIN (un experto por contexto inferido) conserva
  los regímenes conocidos a través de uno nunca visto (24/24).
- Las preguntas: un kernel con repertorio, ¿sigue teniendo identidad? ¿Sigue
  siendo rígido? ¿Su identidad pasa a ser **qué experto elige al volver a
  casa**?

**Diseño** (`experiments/kernel/exp_mundo_propio_casas.py`).
- La vida, los papeles, el exilio y los ensayos (T1, Tm, T2) son los del §K4.
  Las crianzas son las del §K5: `una` (sólo la casa) y `dos` (casa y escuela
  alternadas, termina en casa).
- Un brazo nuevo: `coin` = `error_x4` + `wm_contexts=6`, el brazo del §K6.
  `error_x4` y `kernel` se leen del disco: `una` del §K4 y `dos` del §K5.
- Se guarda, además, el experto activo en cada tick de la vida y de los
  ensayos, los eventos de contexto y la sonda con inferencia de contexto (la
  `sonda_ctx` del §K6, más el oráculo).
- El loop es el de `exp_mundo_propio_gemelos.vivir`. Se verifica re-corriendo
  `error_x4` (primer par, gemelo A, `una`): tiene que reproducir la vida
  guardada del §K4 con diferencia 0. En el humo dio 0.
- `clonar()` se generalizó: ahora desconecta el latente previo de todos los
  expertos, no sólo el del activo, porque los inactivos también guardan su
  grafo entre ticks. Para un modelo único queda igual.
- Mano declarada: `coin` crea 6 expertos al nacer, así que sus pesos y su azar
  difieren de los de `error_x4` en el mismo par. Los gemelos siguen
  compartiendo los suyos.

**Los expertos.**
- Experto de casa h: la moda del experto activo en los últimos 5 bloques de la
  niñez en casa.
- Experto del exilio e: la moda en los últimos 5 bloques del exilio.
- En un ensayo, el experto ASENTADO es la moda en los ticks 100–299, después de
  la ventana de re-entrada.
- **ELIGE(par)**, en un ensayo: en los dos gemelos e ≠ h (el exilio tuvo su
  propia memoria) y, en casa, el asentado es h (volvió a la suya).

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola), en
`coin` bajo `una`:

| Lectura | Criterio (≥ 10/12) |
|---|---|
| SE DIFERENCIA (control positivo) | H(T1) > 0 |
| PERSISTE (primaria) | H(T2) > 0, la lectura del §K4 |
| ELIGE (primaria) | ELIGE(par) en T2 |

Veredicto:
- sin SE DIFERENCIA → **NO SE DIFERENCIA**;
- PERSISTE y ELIGE → **IDENTIDAD EN EL REPERTORIO**: la identidad es a qué
  experto vuelve;
- sólo PERSISTE → **IDENTIDAD, SIN ELEGIR**;
- sólo ELIGE → **ELIGE SIN PERSISTIR**;
- ninguna → **IDENTIDAD FRÁGIL**.

Secundarias:
- PAREADO: H(T2) de `coin` > el de `error_x4`. El repertorio conserva mejor la
  identidad.
- RIGIDEZ, el criterio del §K4: el costo en T1 en la casa del hermano (la media
  de los gemelos) de `coin` > el de `kernel`.
- ACHICA: el costo en T1 de `coin` < el de `error_x4`.
- EXILIO, agregada después de la calibración y antes del test: el `e_early` del
  primer bloque del exilio (la media de los gemelos) de `coin` < el de
  `error_x4`.
- Bajo `dos`, las mismas lecturas contra las vidas del §K5: CONSERVA (H(T2) >
  0), ELIGE, RIGIDEZ, ACHICA y EXILIO.

Se reportan, sin ser veredictos: H en Tm; ELIGE en T1 y Tm; la latencia del
cambio a h en casa en T2; NO CONFUNDE (en T2, el asentado en la casa del hermano
no es h); los contextos en uso; la sonda por papel; los bloques atascados; el
primer bloque del exilio; RECONOCE (el cruce de la energía libre del §K4) y la
distancia entre los `self_embedding` de los gemelos.

**Prueba de humo** (`humo`, par 0, vida corta).
- El loop reproduce la vida guardada del §K4 con diferencia 0.
- Los gemelos `coin` recién nacidos dan ensayos idénticos (H(T0) = 0 exacto).
- En las dos crianzas, el exilio tiene su propio experto y, en casa, el clon
  vuelve a h.

**Predicciones, escritas antes de la calibración** (commit `21b6806`):
- SE DIFERENCIA 12/12.
- PERSISTE y PAREADO pasan. El exilio tiene su propio experto, así que el de la
  niñez se restaura y no se sobrescribe. H(T2) queda debajo de H(T1), porque en
  T2 el clon primero tiene que volver a cambiar de experto, y el cambio espera
  al error corriente: unos 10–30 de los 100 ticks de re-entrada.
- ELIGE pasa.
- RIGIDEZ sigue pasando y ACHICA falla. En la niñez, `coin` tiene un solo
  experto (un `error_x4`), y en un mundo nunca vivido su experto nuevo arranca
  como copia de ése. En el §K6, `coin` no entraba más rápido a lo NUEVO (13/24).
- Bajo `dos`: CONSERVA y ELIGE pasan; el costo en T1 de `coin` queda como el de
  `error_x4`.

**Calibración** (`calibracion`, pares 100–102, nunca pares de test;
`results/mundo_propio_casas_calibracion_run.txt`, 31.2 min). No se ajustó nada.
Bajo `dos` no hay vidas guardadas de `error_x4` ni de `kernel` en esos pares.
- Verificación: diferencia 0.
- `una`: H(T1) +1.47 y H(T2) +1.09 (3/3; `error_x4`, +0.74). ELIGE 3/3 en
  todos los ensayos. Cada gemelo usa 2 contextos, casa y exilio (e ≠ h en 6/6),
  y en T2 vuelve a h en casa en 10 ticks.
- El costo en T1 en la casa del hermano: `coin` 0.77, `error_x4` 0.91 y
  `kernel` 0.44 (ACHICA 3/3, RIGIDEZ 3/3). La predicción escrita de ACHICA ya
  parece equivocada y queda como se escribió.
- El primer bloque del exilio: `coin` 0.26 contra 0.72 de `error_x4`; 0
  atascos contra 2.
- `dos`: 3 contextos (casa, escuela y exilio; un gemelo, 4) y ELIGE 3/3, pero
  H(T2) da sólo +0.10 (3/3), con una latencia de 42 ticks.
- La sonda de `coin` conserva la casa en 0.005–0.015 a lo largo del exilio.

**Predicciones agregadas después de la calibración, antes de los pares de
test:**
- PERSISTE, ELIGE y PAREADO pasan. RIGIDEZ pasa.
- ACHICA es incierta; la predicción escrita queda.
- EXILIO pasa. Hipótesis: cada experto sueña sobre su propio buffer, así que
  repasar la niñez ya no arrastra hacia la casa lo que aprende en el exilio.
- Bajo `dos`: CONSERVA está en riesgo (H(T2) chico) y ELIGE pasa.

**Réplica, pre-registrada junto con el test.** Pares 12–23, leyendo las réplicas
del §K4 y del §K5, con la misma regla. Se lanza apenas termine el test, salvo que
aparezca un bug (cualquier cambio queda registrado). Queda REPLICADO si el
veredicto se repite.

## §K8 — ¿sueño o separación? De dónde viene la identidad del repertorio (pre-registrado el 2026-10-27, después de la calibración y antes de correr)

Decisión de Fran tras el §K7: "push todo, luego vamos con tu siguiente
recomendacion". La recomendación era un `coin` sin sueño.

**Por qué.**
- En el §K4 la identidad es POR EL SUEÑO. El kernel sin sueño la conserva al
  azar (15/24), y el pareado da 23/24.
- En el §K7, un kernel con repertorio también la conserva (PERSISTE 24/24). Su
  identidad pasa a ser a qué experto vuelve (ELIGE 22/24).
- Pero en el §K7 no había un `coin` sin sueño. No se sabe si esa identidad sigue
  siendo del sueño o si alcanza con separar el exilio en su propio experto. El
  experto de casa vuelve a su foto y deja de aprender mientras está inactivo,
  con sueño o sin él.

**Diseño** (`experiments/kernel/exp_mundo_propio_separacion.py`). Un 2 × 2 de
sueño × separación, todo bajo la crianza `una` del §K7:

| Brazo | Sueño | Expertos | De dónde |
|---|---|---|---|
| `coin` | sí | sí | leído del §K7 |
| `error_x4` | sí | no | leído del §K4 |
| `coin_sin_sueno` | no | sí | nuevo: `coin` con `wm_sleep_replay = 0` |
| `error_sin_sueno` | no | no | nuevo: `error_x4` con `wm_sleep_replay = 0` |

- El `kernel` del §K4 (sin sueño y sin ver su error) se lee como referencia.
- Los brazos nuevos difieren de los leídos SÓLO en el sueño del modelo del
  mundo. El sueño del `DreamEngine`, que nunca toca el modelo del mundo, corre en
  todos.
- La vida, los papeles, el exilio y los ensayos son los del §K4. El loop es el
  `vivir` del §K7, re-corrido sobre `coin` (par 0, gemelo A): tiene que
  reproducir la vida guardada del §K7 con diferencia 0. En el humo dio 0.
- `elige` y `confunde` del §K7 se generalizaron para recibir el brazo; para
  `coin` quedan iguales.
- Manos declaradas: no se corre `dos`. `error_sin_sueno` tiene un solo modelo,
  así que sus lecturas de expertos son triviales (h = e = 0).

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola):

| Lectura | Criterio (≥ 10/12) |
|---|---|
| SE DIFERENCIA (control positivo) | H(T1) de `coin_sin_sueno` > 0 |
| PERSISTE_SS (primaria) | H(T2) de `coin_sin_sueno` > 0 |
| SEPARA (primaria) | H(T2) `coin_sin_sueno` > `error_sin_sueno`, pareado |
| SUEÑO (primaria) | H(T2) `coin` > `coin_sin_sueno`, pareado |

Veredicto:
- sin SE DIFERENCIA → **NO SE DIFERENCIA**;
- PERSISTE_SS y SEPARA, sin SUEÑO → **POR LA SEPARACIÓN**;
- PERSISTE_SS, SEPARA y SUEÑO → **SEPARACIÓN Y SUEÑO**;
- PERSISTE_SS sin SEPARA → **PERSISTE SIN SUEÑO, SIN ATRIBUIR**;
- sin PERSISTE_SS, con SUEÑO → **POR EL SUEÑO**;
- el resto → **INDETERMINADO**.

Secundarias:
- ELIGE_SS: el ELIGE del §K7 sobre `coin_sin_sueno` en T2.
- EXILIO_SS: el `e_early` del primer bloque del exilio, `coin_sin_sueno` <
  `error_sin_sueno`.
- La lectura del §K4 sobre el brazo nuevo de un solo modelo: PERSISTE de
  `error_sin_sueno`.
- ERROR_SS, agregada después de la calibración y antes del test: H(T2)
  `error_sin_sueno` > `kernel`, pareado. Sin sueño, ¿ver su propio error le da
  identidad al modelo único?

Se reportan, sin ser veredictos: H en T1, Tm y T2 de cada brazo; los costos en
casa y afuera en T1 y T2; los bloques atascados; para los dos brazos con
expertos, los contextos en uso, (h, e), el asentado, NO CONFUNDE y la latencia;
la sonda de `coin_sin_sueno` por papel; el sueño con un solo modelo (H(T2)
`error_x4` > `error_sin_sueno`).

**Prueba de humo** (`humo`, par 0, vida corta).
- El loop reproduce la vida guardada del §K7 con diferencia 0.
- Los gemelos `coin_sin_sueno` recién nacidos dan ensayos idénticos
  (`ens_dist` igual en T0). H(T0) da 2.8e-17, que es redondeo de la suma.
- El exilio de `coin_sin_sueno` tiene su propio experto.

**Predicciones, escritas antes de la calibración:**
- SE DIFERENCIA 12/12: el kernel sin sueño del §K4 se diferenciaba en T1 12/12.
- PERSISTE_SS y SEPARA pasan; SUEÑO falla. Veredicto previsto: **POR LA
  SEPARACIÓN**.
- La razón: en el modelo de contextos sólo aprende el experto ACTIVO, y cuando
  nace el experto del exilio el de casa vuelve a sus pesos de antes de la racha.
  La niñez queda protegida sin ningún repaso. El modelo único sin sueño, en
  cambio, la sobrescribe en el exilio (§K4: 15/24).
- ELIGE_SS pasa.
- Riesgo: sin sueño, el error corriente del aprendiz en línea puede rondar el
  umbral absoluto (0.08) y abrir contextos espurios. Eso rompería ELIGE_SS: los
  dos fallos del §K7 tenían un tercer experto.
- PERSISTE de `error_sin_sueno`, al azar, como el kernel del §K4.

**Calibración** (`calibracion`, pares 100–102, nunca pares de test;
`results/mundo_propio_separacion_calibracion_run.txt`, 9.3 min). No se ajustó
nada.
- Verificación: diferencia 0.
- `coin_sin_sueno`:
  - H(T1) +0.88 y H(T2) +0.51, los dos 3/3.
  - ELIGE 3/3, con una latencia de 29 ticks en T2 (`coin`, 10).
  - Contextos: 2 en 5/6 gemelos y 3 en 1/6.
- La sonda de casa de `coin_sin_sueno` da 0.077–0.091, contra 0.005 de `coin`:
  sin sueño, el experto de casa queda impreciso.
- Costo en casa en T2: `coin` 0.143, `coin_sin_sueno` 0.279, `error_sin_sueno`
  0.475, `kernel` 0.507.
- SUEÑO 3/3 (+1.09 contra +0.51). SEPARA 2/3.
- Sorpresa: `error_sin_sueno` persiste 3/3 (+0.33), y el `kernel` da −0.51 en
  los mismos pares. Lo único que los distingue es que `error_sin_sueno` ve su
  propio error.

**Predicciones agregadas después de la calibración, antes de los pares de
test:**
- SE DIFERENCIA y PERSISTE_SS pasan.
- SUEÑO pasa. La predicción escrita (falla) queda como se escribió.
- SEPARA es incierta (2/3), porque el modelo único sin sueño también persiste.
- Veredicto más probable: SEPARACIÓN Y SUEÑO si SEPARA pasa; PERSISTE SIN
  SUEÑO, SIN ATRIBUIR si no.
- ELIGE_SS y EXILIO_SS pasan.
- PERSISTE de `error_sin_sueno`: incierta. La predicción escrita (al azar)
  queda.
- ERROR_SS: incierta. En la calibración da 3/3, leída al agregarla, recargando
  las vidas.

**Réplica, pre-registrada junto con el test.** Pares 12–23, leyendo las réplicas
del §K4 y del §K7, con la misma regla. Se lanza apenas termine el test, salvo que
aparezca un bug (cualquier cambio queda registrado). Queda REPLICADO si el
veredicto se repite.

## §K9 — el sueño de la niñez: ¿alcanza un experto preciso y congelado? (pre-registrado el 2026-10-27, antes de correr, sin calibración)

Decisión de Fran tras el §K8: "sigamos con eso". La recomendación era un `coin`
que duerme sólo en la niñez.

**Por qué.**
- En el §K8, la identidad del repertorio es del sueño.
- Sin sueño, el experto de casa queda congelado durante el exilio (39/48), pero
  impreciso (0.087 contra 0.005) y dañado al empezarlo. Al volver, el clon no lo
  distingue del experto del exilio.
- El sueño hace ahí dos cosas: vuelve preciso al experto de casa en la niñez y
  repasa a cada experto, también a los inactivos, durante el exilio.
- El §K9 las separa.

**Diseño** (`experiments/kernel/exp_mundo_propio_ninez.py`).
- **El brazo nuevo, `coin_ninez`:** es `coin`, pero su modelo del mundo deja de
  dormir cuando empieza el exilio (`k.wm_sleep_replay = 0`, justo después del
  ensayo T1). Los clones de los ensayos Tm y T2 lo heredan.
- **Se leen** `coin` (§K7, duerme toda la vida, ensayos incluidos) y
  `coin_sin_sueno` (§K8, nunca duerme).
- Crianza `una`; la vida, los papeles, el exilio y los ensayos son los del §K4.
- **El corte va en el loop del §K7** (`SUENO_SOLO_NINEZ`, vacío allí, así que
  ese loop no cambia).
- **Se verifica cada vida.** Hasta el exilio, `coin_ninez` es `coin`, así que
  cada niñez tiene que ser igual a la vida guardada del §K7 con diferencia 0:
  - las series por tick y las sondas;
  - los ensayos anteriores al exilio;
  - el `self_embedding`;
  - los eventos de contexto.
- **Manos declaradas:**
  - EXILIO mide todo el sueño posterior a la niñez: el del exilio y el de los
    ensayos Tm y T2, no sólo el del exilio.
  - No hay calibración: en el §K7 y el §K8 la de 3 pares engañó y no se ajustó
    nada. El humo verifica el mecanismo.

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola):

| Lectura | Criterio (≥ 10/12) |
|---|---|
| PERSISTE_N (primaria) | H(T2) de `coin_ninez` > 0 |
| NIÑEZ (primaria) | H(T2) `coin_ninez` > `coin_sin_sueno`, pareado: el sueño de la niñez |
| EXILIO (primaria) | H(T2) `coin` > `coin_ninez`, pareado: el sueño posterior |

Veredicto:
- PERSISTE_N y NIÑEZ, sin EXILIO → **BASTA LA NIÑEZ**: un experto preciso y
  congelado sostiene la identidad.
- PERSISTE_N, NIÑEZ y EXILIO → **LA NIÑEZ SOSTIENE, EL RESTO SUMA**.
- PERSISTE_N sin NIÑEZ → **PERSISTE SIN ATRIBUIR**.
- Sin PERSISTE_N, con EXILIO → **HACE FALTA SEGUIR DURMIENDO**.
- El resto → **INDETERMINADO**.

Secundaria: ELIGE_N, el ELIGE del §K7 sobre `coin_ninez` en T2.

Se reporta, para los tres brazos:
- H en T1, Tm y T2;
- los costos en casa y afuera;
- los atascos, los contextos, el asentado, NO CONFUNDE y la latencia;
- la sonda por papel;
- el oráculo de casa al final de la niñez y en el primer y el último bloque del
  exilio: DAÑO (el primero del exilio, peor que el fin de la niñez) y CONGELADO
  (el último igual al primero, ±0.002).

**Prueba de humo** (`humo`, par 0, vida corta).
- Las 2 niñeces son iguales a las del §K7 (diferencia 0).
- La vida entera difiere de la de `coin` (diferencia 40): el sueño se corta.

**Predicciones, escritas antes de cualquier par de test:**
- Cada niñez es igual a la de `coin`.
- PERSISTE_N y NIÑEZ pasan. El sueño de la niñez vuelve preciso al experto de
  casa (~0.005), y sin sueño queda congelado durante el exilio.
- EXILIO también pasa. Los primeros pasos del exilio, antes de la foto, dañan al
  experto de casa y después nada lo repara; además, el clon de T2 no duerme.
- Veredicto previsto: **LA NIÑEZ SOSTIENE, EL RESTO SUMA**.
- ELIGE_N pasa: un experto de casa preciso es fácil de distinguir del del
  exilio.
- DAÑO y CONGELADO, en la mayoría de los gemelos, como en el §K8.

**Nota después del humo, antes del test** (una vida corta y un par; no es
evidencia).
- Al empezar el exilio, el oráculo de casa de `coin_ninez` salta de 0.003 a
  0.184. El de `coin_sin_sueno` va de 0.087 a 0.169, y el de `coin`, de 0.003 a
  0.009.
- El experto preciso parece más frágil a los primeros pasos del exilio que el
  impreciso. Una explicación posible, sin probar: Adam (el optimizador del
  modelo del mundo) divide el paso por la magnitud reciente de los gradientes.
  Para un experto preciso esa magnitud es chica, así que los primeros errores
  grandes dan pasos grandes.
- Si se repite, PERSISTE_N y ELIGE_N corren riesgo. Las predicciones de arriba
  quedan como se escribieron.

**Réplica, pre-registrada junto con el test.** Pares 12–23, leyendo las réplicas
del §K7 y del §K8, con la misma regla. Se lanza apenas termine el test, salvo que
aparezca un bug (cualquier cambio queda registrado). Queda REPLICADO si el
veredicto se repite.

## §K10 — la foto a tiempo: ¿alcanza un experto preciso y congelado? (pre-registrado el 2026-10-27, antes de correr, sin calibración)

Decisión de Fran tras el §K9: "push todo a main, luego sigamos".

**Por qué.**
- El §K9 no pudo hacer su pregunta limpia.
- El error corriente del modelo de contextos es un promedio móvil y cruza el
  umbral 4–24 ticks después de empezar el exilio. La foto "previa a la racha" ya
  trae los primeros pasos del exilio.
- Al restaurarla, el experto de casa queda al nivel del que nunca durmió y se
  congela ahí.

**El mecanismo nuevo:** `ContextualWorldModel(snapshot_lag=L)`, con tests en
`tests/test_contextual_world_model.py`.
- Se guarda un checkpoint del experto activo al final de cada sueño, y cada L
  ticks si no hubo sueño en ese lapso.
- La foto es el checkpoint más reciente que tenga al menos L ticks de
  antigüedad al cruzar el umbral.
- Con L = 0 el comportamiento es el de antes, igual byte a byte; lo cubren los
  14 tests anteriores.
- `restores` registra (tick de la restauración, tick de la foto).
- **L = 50,** por encima del retraso máximo medido en el §K8 (24 ticks).

**Diseño** (`experiments/kernel/exp_mundo_propio_foto.py`). Dos brazos nuevos,
bajo la crianza `una`, con la vida, los papeles, el exilio y los ensayos del §K4:

| Brazo | Qué es |
|---|---|
| `coin_ninez_foto` | `coin_ninez` (§K9: el sueño del modelo del mundo se apaga en el exilio) + L |
| `coin_sin_sueno_foto` | `coin_sin_sueno` (§K8: nunca duerme) + L |

- Se leen `coin` (§K7), `coin_ninez` (§K9) y `coin_sin_sueno` (§K8).
- **Verificación.** El retraso sólo actúa al restaurar. Una vida sin
  restauraciones antes del exilio tiene que tener la niñez de su brazo de
  referencia con diferencia 0: las series por tick, las sondas, el
  `self_embedding` y los eventos. Los ensayos no se comparan, porque un clon de
  ensayo también restaura.
- **El loop del §K7 ahora guarda las restauraciones.** Es sólo un registro.

**Enmienda después del primer humo, antes de cualquier par de test.**
- **La primera versión fallaba.** Tomaba el checkpoint cada L ticks dentro del
  tick del modelo, antes del sueño de ese tick. En el humo, el experto de casa
  restaurado de `coin_ninez_foto` volvía en 0.086, el nivel del que nunca
  durmió.
- **Por qué, medido** (`exp_mundo_propio_entre_suenos.py`: re-corre `coin`, par 0, gemelo A, con la sonda de
  casa del experto activo en cada tick, después del paso en línea y antes del
  sueño): el experto que duerme es preciso sólo justo después de cada sueño.
  - En los últimos 150 ticks de la niñez marca 0.004–0.006 recién dormido.
  - La mediana es 0.012 y la media 0.046. Pasa de 0.05 en 44/151 ticks, con un
    máximo de 0.215.
  - Entre dos sueños, el aprendizaje en línea erosiona lo que el sueño
    consolidó: a veces de 0.004 a 0.2 en unos 25 ticks.
- **Las sondas de fin de bloque de todos los experimentos se toman justo
  después de un sueño,** porque los finales de bloque caen en ticks de sueño.
  El "0.005" de los §K7–§K9 es el estado recién dormido, no el de cualquier
  tick. Las lecturas de identidad (H) son ensayos de conducta y no dependen de
  esto.
- **Se cambió la regla** a checkpoints después de cada sueño. En el segundo humo,
  el experto de casa restaurado queda en 0.003–0.004 durante todo el exilio.

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola):

| Lectura | Criterio |
|---|---|
| FOTO A TIEMPO (chequeo de la manipulación) | en `coin_ninez_foto`, la restauración del nacimiento del exilio usa pesos de antes del exilio en ≥ 20/24 gemelos |
| PERSISTE_F (primaria) | H(T2) de `coin_ninez_foto` > 0, ≥ 10/12 |
| NIÑEZ_F (primaria) | H(T2) `coin_ninez_foto` > `coin_sin_sueno_foto`, ≥ 10/12 |
| RESTO_F (primaria) | H(T2) `coin` > `coin_ninez_foto`, ≥ 10/12: el sueño del exilio y el de los ensayos Tm y T2 |

Veredicto:
- sin FOTO A TIEMPO → **NO SE PUDO HACER**;
- PERSISTE_F y NIÑEZ_F, sin RESTO_F → **BASTA LA NIÑEZ**;
- PERSISTE_F, NIÑEZ_F y RESTO_F → **LA NIÑEZ SOSTIENE, EL RESTO SUMA**;
- PERSISTE_F sin NIÑEZ_F → **PERSISTE SIN ATRIBUIR**;
- sin PERSISTE_F, con RESTO_F → **HACE FALTA SEGUIR DURMIENDO**;
- el resto → **INDETERMINADO**.

Secundarias:
- REPARA_F: H(T2) `coin_ninez_foto` > `coin_ninez`.
- PERSISTE_SSF: H(T2) de `coin_sin_sueno_foto` > 0.
- ELIGE_F.
- FOTO A TIEMPO en `coin_sin_sueno_foto`.

Se reportan:
- H en T1, Tm y T2;
- los costos en casa y afuera;
- los atascos y los expertos;
- el oráculo de casa por bloque (DAÑO, CONGELADO);
- la antigüedad de la foto restaurada.

**Prueba de humo** (par 0, vida corta, con la regla enmendada).
- Las niñeces son iguales a las de referencia (diferencia 0, 2/2 en cada brazo).
- FOTO A TIEMPO: 2/2 en los dos brazos.
- El oráculo de casa de `coin_ninez_foto`: 0.003 al final de la niñez y 0.004
  en el primer y el último bloque del exilio. El de `coin_sin_sueno_foto`: 0.087
  → 0.050.

**Predicciones, escritas antes de cualquier par de test.** Quedan después de la
enmienda.
- FOTO A TIEMPO 24/24 en los dos brazos.
- El DAÑO desaparece en `coin_ninez_foto`: su oráculo de casa en el primer
  bloque del exilio queda cerca del de fin de la niñez (0.005–0.01) y se congela.
- PERSISTE_F y NIÑEZ_F pasan; RESTO_F falla. Veredicto previsto: **BASTA LA
  NIÑEZ**.
- REPARA_F y ELIGE_F pasan.
- `coin_sin_sueno_foto` conserva intacto su experto impreciso (~0.087).
  PERSISTE_SSF, incierta.

**Réplica, pre-registrada junto con el test.** Pares 12–23, leyendo las réplicas
del §K7, el §K8 y el §K9, con la misma regla. Se lanza apenas termine el test,
salvo que aparezca un bug (cualquier cambio queda registrado). Queda REPLICADO
si el veredicto se repite.

## §K11 — la vigilia que no borra: ¿una tasa menor despierto conserva lo que el sueño consolida? (pre-registrado el 2026-10-27, antes de correr, sin calibración)

Decisión de Fran tras el §K10: "push todo, luego sigamos con lo abierto". De lo
abierto, esto es lo más de fondo: la mayor parte del tiempo el kernel planea con un
modelo del mundo bastante peor que lo que dicen las sondas de fin de bloque.

**Por qué.**
- **La medición del §K10.** En una vida de `coin`, el experto de casa que
  duerme marca 0.004–0.006 justo después de cada sueño; mediana 0.012 y hasta
  0.215 entre sueños.
- **Una mirada posterior sobre esa misma vida** (un análisis posterior, no es evidencia).
  - Los ticks de prueba suben la sonda en promedio: +0.007, contra −0.0001 en
    los ticks comunes.
  - Pero 15 de los 21 saltos de más de +0.01 caen en ticks comunes y seguidos
    (0.037 → 0.069 → 0.110 → 0.152).
  - Lo que erosiona es el aprendizaje en línea entre dos sueños, no sólo las
    sorpresas.

**El mecanismo nuevo:** `ContextualWorldModel(wake_lr_scale=s)`, con tests en
`tests/test_contextual_world_model.py`.
- Los pasos en línea, despierto, del experto que aprende usan la tasa del
  optimizador por s. El sueño conserva la tasa entera.
- Con s = 1 el comportamiento es el de antes; los tests anteriores lo cubren.

**Diseño** (`experiments/kernel/exp_mundo_propio_vigilia.py`).
- **El brazo nuevo, `coin_vigilia`:** es `coin` con `wake_lr_scale` 0.1. Corre
  bajo la crianza `una`, con la vida, los papeles, el exilio y los ensayos del
  §K4.
- **`coin` se re-corre como control.** El loop ahora también mide la sonda un
  tick antes del último paso del bloque, es decir, 49 pasos en línea después de
  un sueño y antes del siguiente. La de fin de bloque viene justo después de ese
  sueño.
- **Verificación:** cada `coin` re-corrido tiene que reproducir su vida guardada
  del §K7 en las claves guardadas, con diferencia 0. La sonda sólo lee; se
  comprobó en el humo del §K8.
- **Ninguno de los dos brazos usa `snapshot_lag`:** se cambia una variable por
  vez.

**Lecturas por par** (la media de los gemelos):
- el oráculo de casa justo después de un sueño y "despierto", 49 pasos después,
  con la mediana de los últimos 5 bloques de la niñez;
- H;
- el `e_early` del primer bloque del exilio, es decir, cómo entra a un mundo
  nunca vivido.

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola):

| Lectura | Criterio |
|---|---|
| VERIFICACIÓN | cada `coin` re-corrido igual a su vida del §K7; si no, se para: es un bug |
| EROSIONA (control) | en `coin`, oráculo de casa despierto > justo después del sueño, ≥ 10/12 |
| PRECISA (primaria) | oráculo de casa despierto, `coin_vigilia` < `coin`, ≥ 10/12 |
| PERSISTE_V (primaria) | H(T2) de `coin_vigilia` > 0, ≥ 10/12 |
| LENTO (primaria, el precio) | primer bloque del exilio, `coin_vigilia` > `coin`, ≥ 10/12 |

Veredicto:
- sin EROSIONA → **NO HAY EROSIÓN**;
- sin PRECISA → **LA TASA NO LA EVITA**;
- PRECISA y PERSISTE_V, sin LENTO → **VIGILIA QUE NO BORRA**;
- PRECISA, PERSISTE_V y LENTO → **PRECISA PERO LENTA**;
- PRECISA sin PERSISTE_V → **PRECISA SIN IDENTIDAD**.

Secundarias:
- PAREADO: H(T2) en los dos sentidos.
- CONTROLA: el `e_late` medio de la niñez, `coin_vigilia` < `coin`.
- Los atascos y ELIGE.

Se reportan H, los costos en casa y afuera, los expertos y la tabla del oráculo:
casa al final de la niñez y experto del exilio al final del exilio.

**Prueba de humo** (par 0, vida corta).
- El `coin` re-corrido es igual a su vida del §K7, con diferencia 0.

**Predicciones, escritas antes de cualquier par de test:**
- VERIFICACIÓN 24/24.
- EROSIONA pasa.
- PRECISA pasa: un paso diez veces más chico erosiona menos.
- PERSISTE_V pasa.
- LENTO pasa. Aprender despierto el exilio nunca vivido va diez veces más lento,
  y el sueño solo, cada 50 ticks, no compensa el primer bloque.
- Veredicto previsto: **PRECISA PERO LENTA**.
- CONTROLA, incierta. Planea con un modelo más preciso, pero sigue más despacio
  su propio flujo.

**Nota después del humo, antes del test** (par 0, vida corta; no es evidencia).
- El oráculo de casa despierto: `coin` pasa de 0.004 a 0.061; `coin_vigilia`, de
  0.005 a 0.025. La erosión baja a menos de la mitad, pero no desaparece.
- El precio parece grande: el primer bloque del exilio da 0.982 contra 0.334
  (un gemelo atascado), y la casa del hermano en T1, 0.906 contra 0.362.
- Las predicciones quedan como se escribieron.

**Réplica, pre-registrada junto con el test.** Pares 12–23, con la misma regla.
Se lanza apenas termine el test, salvo que aparezca un bug (cualquier cambio
queda registrado). Queda REPLICADO si el veredicto se repite.

## §K12 — la madurez: ¿una vigilia lenta sólo mientras el experto explica su flujo da las dos cosas? (pre-registrado el 2026-10-28, antes de correr, sin calibración)

Pregunta de Fran tras el §K11: "¿cómo seguimos?". Lo abierto más directo del §K11:
una sola tasa despierta no da estabilidad y plasticidad a la vez.

**Por qué.**
- **El §K11, replicado (24/24 en todo).** Con lr × 0.1 despierto, el experto de casa
  conserva lo que el sueño consolida: oráculo despierto 0.009 contra 0.042 de `coin`.
  La identidad se sostiene.
- **El precio es la entrada a lo nunca vivido.** Los 59 bloques atascados caen en los
  dos primeros bloques del exilio (`coin`: 3); el primer bloque del exilio cuesta
  0.956–0.970 contra 0.497–0.601.
- **Una mirada posterior a las vidas guardadas del §K11.** En los dos brazos, el
  experto del exilio nace a unos 34 ticks del comienzo (medianas 35 y 34). En
  `coin_vigilia` nace como copia del de casa, aprende despierto a la décima parte, y
  su parte de cada sueño es mínima: la dosis se reparte por tamaño de buffer.

**El mecanismo nuevo:** `ContextualWorldModel(wake_lr_scale_learning=s_l)`, con tests
en `tests/test_contextual_world_model.py`.
- Un experto aprende despierto a lr × `wake_lr_scale` sólo mientras **explica su
  flujo**: está establecido (su error corrido bajó del umbral alguna vez) y su error
  corrido está ahora dentro del umbral.
- Si no lo explica (recién nacido, o fallando), aprende a lr × s_l. El sueño
  conserva la tasa entera.
- Aprender rápido mientras falla un experto establecido está protegido por la foto
  del §K6: un nacimiento o un cambio de experto lo restaura.
- Con `wake_lr_scale_learning = None` el comportamiento es el de antes (test).

**Diseño** (`experiments/kernel/exp_mundo_propio_madurez.py`).
- **El brazo nuevo, `coin_madurez`:** es `coin` con `wake_lr_scale` 0.1 y
  `wake_lr_scale_learning` 1.0. Corre bajo la crianza `una`, con la vida, los
  papeles, el exilio y los ensayos del §K4.
- **`coin` y `coin_vigilia` no se re-corren:** sus vidas del §K11 se cargan de
  `data/mundo_propio_vigilia`. Las dos ya tienen la sonda despierta, y cada `coin`
  del §K11 es igual a su vida del §K7.
- **Verificación:** en cada corrida se re-corre `coin_vigilia` del primer par,
  gemelo A, y tiene que ser igual a su vida guardada del §K11 en todas las claves,
  con diferencia 0. Si no, se para: es un bug.
- **Ninguno usa `snapshot_lag`:** se cambia una variable por vez.

**Enmienda después del humo, antes de este pre-registro** (par 0, vida corta; no es
evidencia).
- **El primer diseño** decidía la tasa sólo por "establecido": rápida para el experto
  recién nacido y lenta para siempre después.
- **Su humo:** el experto del exilio sí aprendió rápido, pero la entrada siguió siendo
  la de `coin_vigilia`.
  - El primer bloque del exilio dio 0.886, contra 0.334 de `coin` y 0.982 de
    `coin_vigilia`.
  - Entre los ticks 35 y 100 del exilio, 0.92 y 0.88, contra 0.21 y 0.14 de `coin`.
  - La casa del hermano en T1, 0.895 (`coin_vigilia` 0.906, `coin` 0.362).
  - El motivo: antes de que nazca el experto del exilio (a los 63 y 81 ticks), el que
    aprende es el de casa, establecido y lento.
- **El diseño enmendado** (el de arriba) aprende rápido también mientras el
  experto establecido falla.
- **Su humo:**
  - El gemelo A entra como `coin`: su experto nace a los 34 ticks, y los primeros
    35 / los 65 siguientes / los últimos 200 ticks del exilio dan 0.842 / 0.305 / 0.063
    (`coin` 0.848 / 0.215 / 0.053).
  - El gemelo B queda atascado antes del nacimiento (81 ticks; 0.957 en los primeros
    100, `coin` 0.41). Atascado, el error queda chico y la tasa lenta se sostiene.
  - Primer bloque del exilio 0.725. Casa del hermano en T1 0.493 (en T2 0.932;
    `coin_vigilia` 0.970, `coin` 0.623).
  - Oráculo de casa despierto 0.019 (`coin` 0.061, `coin_vigilia` 0.025). H(T2)
    +1.53. Casa en T2 0.166 (`coin` 0.490).
- La verificación pasó en los dos humos, con diferencia 0.

**Lecturas por par** (la media de los gemelos), como en el §K11: el oráculo de casa
justo después de un sueño y despierto (49 pasos después), mediana de los últimos 5
bloques de la niñez; H; el `e_early` del primer bloque del exilio.

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola). E =
`coin_madurez`, C = `coin`, V = `coin_vigilia`.

| Lectura | Criterio |
|---|---|
| VERIFICACIÓN | `coin_vigilia` re-corrido igual a su vida del §K11; si no, se para |
| PRECISA_M (primaria) | oráculo de casa despierto, E < C, ≥ 10/12 |
| ENTRA (primaria) | primer bloque del exilio, E < V, ≥ 10/12 |
| PERSISTE_M (primaria) | H(T2) de E > 0, ≥ 10/12 |
| LENTO_M (primaria, el precio) | primer bloque del exilio, E > C, ≥ 10/12 |

Veredicto:
- sin PRECISA_M → **NO CONSERVA**;
- PRECISA_M sin ENTRA → **SIGUE LENTA**;
- las dos sin PERSISTE_M → **SIN IDENTIDAD**;
- las tres sin LENTO_M → **VIGILIA QUE NO BORRA**;
- las tres y LENTO_M → **MEJOR PERO NO GRATIS**.

Secundarias:
- PAREADO: H(T2), E > C y E > V.
- CONTROLA: el `e_late` medio de la niñez, E < C.
- VUELVE: el costo en casa en T2, E < C. En el §K11 fue un análisis posterior para V
  (19/24); acá queda pre-registrado.
- AFUERA: el costo en la casa del hermano en T2, E < V.
- El oráculo despierto del experto del exilio al final del exilio, E < C.
- Los atascos y ELIGE.

Se reportan H en T1/Tm/T2, los costos en casa y afuera, la tabla del oráculo, los
expertos y, para E, el tick del nacimiento del experto del exilio.

**Predicciones, escritas después de los dos humos y antes de cualquier par de test:**
- VERIFICACIÓN 1/1 por corrida.
- PRECISA_M pasa: en la niñez el experto de casa establecido explica su flujo casi
  siempre.
- ENTRA pasa.
- PERSISTE_M pasa.
- LENTO_M, inclinada a pasar: los gemelos que se atascan antes del nacimiento (el B
  del humo) se quedan con la tasa lenta.
- Veredicto previsto: **MEJOR PERO NO GRATIS** (VIGILIA QUE NO BORRA si los
  atascados son raros).
- Atascos entre los de `coin` y los de `coin_vigilia`.
- VUELVE, inclinada a pasar. AFUERA, incierta: en el humo es mejor que `coin_vigilia`
  en T1 y no en T2.

**Réplica, pre-registrada junto con el test.** Pares 12–23, con la misma regla.
Se lanza apenas termine el test, salvo que aparezca un bug (cualquier cambio
queda registrado). Queda REPLICADO si el veredicto se repite.

## §K13 — el regreso: ¿proteger al experto que vuelve arregla la vuelta a casa sin perder lo del §K12? (pre-registrado el 2026-10-28, antes de correr, sin calibración)

Fran, tras el mecanismo del §K12: "sigamos con tu recomendacion".

**Por qué.**
- **El §K12, replicado** (24/24 en PRECISA_M, ENTRA y PERSISTE_M): la tasa por experto
  conserva lo que el sueño consolida y entra a lo nunca vivido mejor que `coin`.
- **Lo que falló es VUELVE (7/24):** después del exilio, la vuelta a casa cuesta más
  que en `coin` (0.165 contra 0.145).
- **El mecanismo** (`exp_mundo_propio_madurez_vuelta.py`, 16 vidas re-corridas con
  diferencia 0). El error corriente del experto de casa llega cargado con el exilio,
  porque todos los expertos predicen en cada tick, y el cambio de experto es por
  margen, no por el umbral. Bajo la madurez, el experto de casa vuelve "sin explicar"
  (7/8 gemelos arriba del umbral) y reaprende despierto a tasa entera. Eso le
  multiplica el error en casa por ~30 hasta el sueño siguiente. Lento o congelado, el
  costo extra desaparece (0.083 → 0.055 después del cambio, 7/8 y 6/8).

**El mecanismo nuevo:** `ContextualWorldModel(slow_return=True)`, con tests en
`tests/test_contextual_world_model.py`.
- Un experto establecido que vuelve a estar activo por un **cambio** aprende despierto
  a lr × `wake_lr_scale` hasta que explica su flujo, o como mucho `persist` ticks (30:
  la paciencia que el modelo ya usa antes de declarar un contexto nuevo). Después
  sigue la regla del §K12.
- Un nacimiento no es una vuelta.
- Necesita `wake_lr_scale_learning`. Con `False` el comportamiento es el de antes
  (test).

**Diseño** (`experiments/kernel/exp_mundo_propio_regreso.py`).
- **El brazo nuevo, `coin_regreso`:** es `coin_madurez` con `slow_return`. Corre
  bajo `una`, con la vida, los papeles, el exilio y los ensayos del §K4.
- **No se re-corre nada de antes:** `coin` y `coin_vigilia` se cargan del §K11
  (`data/mundo_propio_vigilia`) y `coin_madurez` del §K12 (`data/mundo_propio_madurez`).
- **Verificación:** en cada corrida se re-corre `coin_madurez` del primer par, gemelo
  A, y tiene que ser igual a su vida del §K12 en todas las claves, con diferencia 0. Si
  no, se para: es un bug.
- **MISMA VIDA.** En las vidas guardadas del §K12, 44/48 vidas principales no tienen
  ningún cambio de experto (sólo el nacimiento del experto del exilio). En ellas la
  vida principal de `coin_regreso` tiene que ser la de `coin_madurez`, y los brazos se
  distinguen sólo en los clones de los ensayos, que es donde están las vueltas.
  - En casa, en Tm y T2, hay una vuelta al experto de casa en 48/48 ensayos.
  - Afuera, en Tm y T2, el cambio es casi siempre un nacimiento (45–46/48), no una
    vuelta.

**Enmienda después del humo, antes de este pre-registro** (par 0, vida corta; no es
evidencia).
- **El primer diseño no tenía tope:** lento hasta que el experto que vuelve explica.
- **Su humo:** verificación con diferencia 0 y MISMA VIDA 2/2. Pero el gemelo B, en la
  casa del hermano en T1, volvió a `h` en el tick 52 y se quedó ahí, lento y sin
  explicar nunca, porque un nacimiento espera `grace_spawn` = 150 ticks. Costó 0.841
  en los primeros 100 ticks, contra 0.547 de `coin_madurez`, que alterna `h` y el
  experto nuevo cada 20 ticks. En las vidas guardadas del §K12, esa vuelta a `h` en la
  casa del hermano en T1 aparece en ~6/48 gemelos.
- **El diseño enmendado** pone el tope de `persist` ticks: en el mecanismo, el experto
  de casa protegido explicó en una mediana de 3–4 ticks; uno equivocado no explica
  nunca.
- **Su humo:** verificación con diferencia 0 y MISMA VIDA 2/2.
  - El mismo gemelo, 0.792: el precio se achica, no desaparece. Afuera en T1, 0.616
    contra 0.493.
  - En casa en T2, 0.165 contra 0.166. En la vida corta la vuelta no daña a `h` (en el
    humo del mecanismo, `lento_h` dio 0.064 → 0.062), así que el humo no puede mostrar
    la protección.
- Por eso la lectura del precio, RIGIDO_R, cubre también T1: cualquiera de los dos
  ensayos, el lado conservador para el veredicto.

**Lecturas por par** (la media de los gemelos): las del §K12; además, en cada ensayo de
casa, el costo después del cambio a `h` (el de los primeros 100 ticks desde el primer
tick en `h`; la lectura del mecanismo), y MISMA VIDA.

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola). E =
`coin_regreso`, M = `coin_madurez`, C = `coin`, V = `coin_vigilia`.

| Lectura | Criterio |
|---|---|
| VERIFICACIÓN | `coin_madurez` re-corrido igual a su vida del §K12; si no, se para |
| PROTEGE (primaria) | costo en casa en T2, E < M, ≥ 10/12 |
| VUELVE_R (primaria) | costo en casa en T2, E < C, ≥ 10/12 |
| CONSERVA_R (primaria) | oráculo de casa despierto E < C y primer bloque del exilio E < V, cada uno ≥ 10/12 |
| PERSISTE_R (primaria) | H(T2) de E > 0, ≥ 10/12 |
| RIGIDO_R (primaria, el precio) | costo afuera E > M en T1 o en T2, ≥ 10/12 en alguno |

Veredicto:
- sin CONSERVA_R o sin PERSISTE_R → **PIERDE LO DEL K12**;
- si no, sin PROTEGE → **NO PROTEGE**;
- PROTEGE sin VUELVE_R → **PROTEGE PERO NO ALCANZA**;
- las dos sin RIGIDO_R → **VUELVE A CASA**;
- las dos y RIGIDO_R → **VUELVE, MÁS RÍGIDO AFUERA**.

Secundarias:
- RECUPERA: el costo después del cambio en T2, E < M.
- PAREADO: H(T2), E > M y E > C.
- AFUERA: el costo afuera en T2, E < V.
- El costo en casa en Tm, E < M.
- ELIGE de E y los atascos.

Se reportan MISMA VIDA por gemelo (y si su vida principal tuvo cambios), H en
T1/Tm/T2, los costos, la tabla del oráculo, los expertos y la latencia a `h`.

**Predicciones, escritas después de los dos humos y antes de cualquier par de test:**
- VERIFICACIÓN 1/1 por corrida.
- MISMA VIDA en todos los gemelos cuya vida principal en `coin_madurez` no tiene
  cambios.
- CONSERVA_R pasa: esas vidas principales son las del §K12 (24/24 allí).
- PERSISTE_R pasa.
- PROTEGE pasa: en el mecanismo, sostener lento a `h` bajó el costo después del cambio
  en 7/8 gemelos (casa en T2, 0.163 → 0.105).
- VUELVE_R, inclinada a pasar: ese contrafactual dio 0.105 contra 0.147 de `coin` en 8
  gemelos, y el cambio a `h` del §K12 es más temprano (19/24 juntos).
- RIGIDO_R no pasa: afuera en T2 el cambio es un nacimiento en 45/48, y las vueltas en
  T1 son ~6/48.
- Veredicto previsto: **VUELVE A CASA**.
- Secundarias: RECUPERA pasa; PAREADO E > M inclinada a pasar y E > C no pasa (en el
  §K12, 4/24: el H de `coin` es sobre todo rigidez afuera); AFUERA pasa; casa en Tm
  E < M inclinada a pasar; ELIGE pasa; los atascos, los de `coin_madurez`.

**Réplica, pre-registrada junto con el test.** Pares 12–23, con la misma regla. Se
lanza apenas termine el test, salvo que aparezca un bug (cualquier cambio queda
registrado). Queda REPLICADO si el veredicto se repite.

## §K14 — la escuela: ¿aguantan las tres cosas del brazo completo la otra crianza? (pre-registrado el 2026-10-28, después del humo y la calibración, antes de correr)

Fran, tras la réplica del §K13: "sigamos con tu recomendacion" (probar el brazo
completo bajo la crianza `dos` antes de ajustar el tope del regreso).

**Por qué.**
- **Del §K11 al §K13 todo se midió bajo `una`,** con la niñez en casa. Ahí
  `coin_regreso` es el primer brazo que hace las tres cosas a la vez (§K13, replicado):
  - conserva lo que el sueño consolida: oráculo de casa despierto 0.008 contra 0.042
    de `coin`, 24/24;
  - entra a lo nunca vivido mejor que `coin`: primer bloque del exilio 0.367 contra
    0.560, 20/24;
  - vuelve a casa mejor que `coin`: casa en T2 0.111 contra 0.145, 22/24.
- **`dos` es la otra vida que tiene el programa** (§K5, §K7): casa y la escuela N
  alternadas durante la niñez, terminando en casa. Hay tres expertos en vez de dos, y
  el experto de casa vuelve de la escuela siete veces en la niñez. Con la regla del
  §K13 cada una de esas vueltas es lenta, algo que bajo `una` no pasaba nunca.
- **La pregunta:** ¿el brazo completo es una propiedad del kernel o de la única crianza
  en la que se construyó?

**Diseño** (`experiments/kernel/exp_mundo_propio_escuela.py`).
- **Dos brazos bajo `dos`,** con la vida, los papeles, el exilio y los ensayos del §K4
  y el bucle del §K7:
  - `coin`, re-corrido. Sus vidas del §K7 bajo `dos` no tienen la sonda despierta, que
    se agregó en el §K11. La sonda sólo lee, así que cada gemelo re-corrido tiene que
    ser igual a su vida guardada del §K7 en todas las claves guardadas: 24
    verificaciones por corrida.
  - `coin_regreso`, el brazo del §K13 sin cambios.
- **No se ajusta nada.**
- **Declarado:** no hay `coin_vigilia` ni `coin_madurez` bajo `dos`. La pregunta es el
  brazo completo contra el repertorio que mejora, no cuál de sus tres manos hace qué.
- **Cambio declarado en una lectura.** Bajo `dos` el experto de casa sólo se erosiona
  despierto en los bloques de casa: despierto aprende sólo el experto activo, y todos
  duermen. Por eso el oráculo de casa despierto es la mediana sobre los últimos 5
  bloques de la niñez vividos en casa. Bajo `una` son los mismos 5 bloques del §K11.

**Lecturas por par** (la media de los gemelos):
- el oráculo de casa despierto;
- el primer bloque del exilio (`e_early`);
- el costo en casa en T1, Tm y T2, y afuera (la casa del hermano) en T1 y T2;
- H en T1, Tm y T2;
- en cada ensayo de casa, el costo después del cambio a `h` (la lectura del §K13);
- **las vueltas de la niñez:** el `e_early` medio de los bloques de casa después del
  primero (7 vueltas desde la escuela) y de los de la escuela después del primero (6).

**Regla** (tests de signo sobre 12 pares; 10/12 = p 0.019 de una cola). E =
`coin_regreso`, C = `coin`, los dos bajo `dos`.

| Lectura | Criterio |
|---|---|
| VERIFICACIÓN | cada `coin` re-corrido igual a su vida del §K7; si no, se para |
| CONSERVA_D (primaria) | oráculo de casa despierto, E < C, ≥ 10/12 |
| ENTRA_D (primaria) | primer bloque del exilio, E < C, ≥ 10/12 |
| VUELVE_D (primaria) | costo en casa en T2, E < C, ≥ 10/12 |
| PERSISTE_D (primaria) | H(T2) de E > 0, ≥ 10/12 |
| RIGIDO_D (primaria, el precio) | costo afuera E > C en T1 o en T2, ≥ 10/12 en alguno |

Veredicto:
- sin PERSISTE_D → **SIN IDENTIDAD EN LA ESCUELA**;
- si no, si falta alguna de CONSERVA_D, ENTRA_D o VUELVE_D → **NO AGUANTA**, nombrando
  las que fallan;
- las tres sin RIGIDO_D → **AGUANTA LA ESCUELA**;
- las tres y RIGIDO_D → **AGUANTA, MÁS RÍGIDO AFUERA**.

Secundarias:
- NINEZ_D: las vueltas a casa en la niñez, E < C.
- ESCUELA_D: las vueltas a la escuela, E < C.
- El costo en casa en Tm, E < C.
- AFUERA: el costo afuera en T2, E < C.
- RECUPERA: el costo después del cambio en T2, E < C.
- PAREADO: H(T2), E > C.
- ELIGE de E en T2 y los atascos.

Se reportan EROSIONA (el oráculo de casa de `coin` despierto, peor que recién dormido:
la premisa de CONSERVA_D bajo `dos`), la tabla del oráculo (casa y escuela en la niñez,
el exilio al final), los expertos, `h` y `e`, la latencia a `h`, los cambios de experto
en la niñez y, agregado después de la calibración, el primer bloque del exilio por
gemelo.

**Predicciones escritas antes del humo y de la calibración:**
- VERIFICACIÓN 24/24.
- PERSISTE_D pasa: `coin` bajo `dos` da 22/24 juntos (§K7), y la vigilia lenta
  conserva al experto de casa como estaba.
- CONSERVA_D pasa: la vigilia lenta conserva lo que el sueño consolida, sea cual sea la
  crianza.
- VUELVE_D, inclinada a pasar: bajo `dos` la latencia de `coin` para volver a `h` en
  T2 es de 17 ticks, contra 11 bajo `una`, así que el regreso lento tiene más para
  proteger.
- ENTRA_D, incierta: bajo `dos` `coin` ya entra al exilio en 0.327 (§K7), contra 0.50
  bajo `una`, y eso es menos que el 0.367 de `coin_regreso` bajo `una`.
- RIGIDO_D no pasa.
- NINEZ_D pasa: cada vuelta desde la escuela está protegida.
- Veredicto previsto: **AGUANTA LA ESCUELA** o **NO AGUANTA: ENTRA_D**.

**Humo** (par 0, vida corta; no es evidencia).
- Verificación 2/2, con diferencia máxima 0.0.
- E contra C: oráculo de casa despierto 0.013 contra 0.028; primer bloque del exilio
  0.347 contra 0.418; casa en T2 0.143 contra 0.184; H(T2) +1.19 contra +0.84.
- Afuera, E paga más: 0.416 contra 0.287 en T1 y 0.736 contra 0.604 en T2.
- Las vueltas de la niñez no se pueden leer: hay un solo bloque de casa y uno de
  escuela.

**Calibración** (pares 100–102, nunca de test;
`results/mundo_propio_escuela_calibracion_run.txt`, 36.2 min). No se ajustó nada.
- Verificación 6/6, con diferencia máxima 0.0.
- CONSERVA_D 3/3 (oráculo de casa despierto 0.016 contra 0.049; EROSIONA 3/3).
- **ENTRA_D 1/3:** el primer bloque del exilio cuesta 0.476 contra 0.253.
- VUELVE_D 2/3 (casa en T2, 0.207 contra 0.341).
- PERSISTE_D 3/3 (H(T2) +0.37 contra +0.10).
- RIGIDO_D: T1 0/3, T2 2/3 (afuera en T2, 0.394 contra 0.345).
- Secundarias: NINEZ_D 2/3 (0.112 contra 0.107: no hay diferencia), ESCUELA_D 1/3,
  casa en Tm 0/3 (0.251 contra 0.250), ELIGE 3/3.
- **Análisis posterior de esas vidas.**
  - Al empezar el exilio los dos brazos hacen lo mismo: `h` activo 33–37 ticks y
    después nace un experto. El oráculo de X antes del exilio también es el mismo
    (0.17–0.19).
  - Los fallos de ENTRA_D son dos gemelos (100 B y 101 B). Su `coin_regreso` se atasca
    actuando unos 150 ticks del primer bloque del exilio (costo ~0.8–1.1).
  - Mientras tanto su modelo del mundo aprende X igual o mejor que el de `coin`: el
    oráculo de X al final del bloque da 0.055 contra 0.085 y 0.076 contra 0.058.

**Predicciones agregadas después de la calibración, antes de cualquier par de test**
(las de arriba quedan como se escribieron):
- VERIFICACIÓN 24/24.
- CONSERVA_D y PERSISTE_D pasan.
- ENTRA_D no pasa: bajo `dos` `coin` ya entra en 0.33, y `coin_regreso` puede quedar
  atascado ahí.
- VUELVE_D, inclinada a pasar.
- RIGIDO_D no pasa en T1; en T2, incierta.
- NINEZ_D no pasa (sin diferencia en la calibración).
- Veredicto previsto: **NO AGUANTA: ENTRA_D**.

**Réplica, pre-registrada junto con el test.** Pares 12–23, con la misma regla. Se
lanza apenas termine el test, salvo que aparezca un bug (cualquier cambio queda
registrado). Queda REPLICADO si el veredicto se repite.

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

### §K4 — IDENTIDAD por la letra, por el sueño; su propia sorpresa no reconoce la casa (2026-10-26)

`results/mundo_propio_gemelos_run.txt`: pares 0–11, 62.9 min.

- **SE DIFERENCIA: 12/12 en los dos brazos.** H(T1) da +1.36 en `error_x4` y
  +0.85 en `kernel`.
- **PERSISTE (primaria): 12/12.** Después de 4500 ticks de exilio compartido,
  H(T2) da +0.53, con mínimo +0.26.
  - Por gemelo, vuelve a su casa con un costo de 0.21, contra 0.55 en la del
    hermano. Pasa en 21/24 gemelos.
  - Entre Tm y T2, H no se mueve (+0.53 y +0.53): lo que queda a los 1500 ticks
    de exilio sigue ahí a los 4500. H(T1) no es comparable, porque en T1 el
    ensayo en casa no cambia de régimen.
- **ATRIBUCIÓN: PERSISTE en `kernel` da 9/12 (H +0.18) y el pareado, 11/12.**
  Veredicto pre-registrado: **IDENTIDAD (por el sueño).**
  - El kernel sin sueño no está en cero: 9/12 queda a un par del umbral.
  - Por gemelo, la ventaja de casa no es consistente. Las medianas dan 0.45 al
    volver a su casa contra 0.56 en la del hermano, pero sólo 11/24 gemelos
    andan mejor en su casa.
  - Su sonda olvidó la casa por completo (0.223, contra 0.224 en la del
    hermano) y aprendió el exilio (0.111).
- **La sonda de `error_x4`.** El modelo del mundo conserva la casa (0.012,
  contra 0.182 en la del hermano). El régimen del exilio nunca aparece en la
  sonda: da 0.181, igual que N.
  - La sonda usa acciones al azar, y el exilio no tuvo balbuceo: lo aprendió
    estrecho, sólo en las acciones que usa.
  - Lo que sostiene la identidad es el conocimiento amplio de la infancia, que
    el sueño repasa.
- **RECONOCE: 8/12, no pasa.** La energía libre del propio kernel al entrar no
  dice de forma confiable "esta es mi casa": cuatro pares dan negativo. Ψ se
  satura después de T1, y sus cruces dan 0.
- **Predicciones fallidas:**
  - DESVENTAJA da 3/12. La desventaja de la propia casa que se vio en la
    calibración no se sostuvo. Dos de los tres pares negativos son del patrón de
    la calibración (B − A = 2), pero con n = 4 por patrón eso no se cree.
  - El `self_embedding` no se achica: T2/T1 da una mediana de 0.92 con sueño y
    1.0 sin sueño. El módulo declarado conserva una diferencia, pero este diseño
    no puede decir si es sobre el mundo vivido o deriva (no tiene un nulo).
- **Posterior, no pre-registrado: la identidad tiene un precio.**
  - El kernel con sueño entra peor a un mundo que nunca vivió. En T1, el ensayo
    en la casa del hermano cuesta 0.71, contra 0.46 sin sueño (11/12 pares).
  - El primer bloque del exilio cuesta 0.58, contra 0.40 (21/24 gemelos).
  - 11 de los 24 gemelos con sueño se atascaron al empezar el exilio, contra 1
    sin sueño. Todos se recuperan en uno o dos bloques.
  - En el §K3, criado entre tres regímenes, entraba mejor a lo nuevo. Acá,
    criado en uno solo, se vuelve rígido.
  - Pre-registrado como secundaria (RIGIDEZ) en la réplica.

### §K4, réplica — REPLICADO; la atribución al sueño se afirma, y su precio también (2026-10-26)

`results/mundo_propio_gemelos_replica_run.txt`: pares 12–23, 62.2 min.

- **SE DIFERENCIA: 12/12 en los dos brazos.** H(T1) da +1.36 en `error_x4` y
  +0.91 en `kernel`.
- **PERSISTE (primaria): 12/12.** H(T2) da +0.72, con mínimo +0.38.
  - Por gemelo, vuelve a su casa con un costo de 0.22, contra 0.58 en la del
    hermano. Pasa en 23/24 gemelos.
  - Entre Tm y T2, H baja un poco: +0.91 y +0.72. En el test no se movía.
- **ATRIBUCIÓN: PERSISTE en `kernel` da 6/12 (H +0.01) y el pareado, 12/12.**
  Veredicto pre-registrado: **IDENTIDAD (por el sueño). REPLICADO.**
  - La moneda que se predijo cayó del lado favorable: el kernel sin sueño
    queda en el azar. Por gemelo, 11/24 vuelven mejor a su casa (0.47, contra
    0.45 en la del hermano).
  - Su sonda vuelve a olvidar la casa (0.243, contra 0.254 en la del hermano)
    y a aprender el exilio (0.137).
- **La sonda de `error_x4`** repite el test: casa 0.012, hermano 0.182, exilio
  0.178 y N 0.183. El exilio sigue sin aparecer en la sonda.
- **RECONOCE: 11/12, pasa en la réplica.** Falló la predicción, del lado bueno.
  Como en el test dio 8/12, no queda replicado por la letra. Juntando las dos
  corridas da 19/24 (p 0.003), lectura posterior.
- **RIGIDEZ (secundaria pre-registrada): 12/12. Pasa.** En T1, el ensayo en la
  casa del hermano cuesta 0.71 con sueño, contra 0.49 sin sueño.
  - El primer bloque del exilio cuesta 0.85, contra 0.38 (22/24 gemelos).
  - 15 de los 24 gemelos con sueño se atascan al empezar el exilio, en los
    bloques 18–19; sin sueño, ninguno. Todos se recuperan en uno o dos bloques.
  - **El precio de la identidad queda pre-registrado y replicado.**
- **DESVENTAJA: 6/12. Falla otra vez** (9/24 juntando las dos corridas).
- **El `self_embedding` crece en vez de achicarse.** T2/T1 da una mediana de
  1.21 con sueño y 1.15 sin sueño, y se achica sólo en 4/12 y 3/12 pares. La
  predicción falla otra vez, y sigue sin haber un nulo de deriva.

**Sobre los 24 pares juntos:**
- PERSISTE da 24/24 (mediana +0.59, mínimo +0.26).
- PERSISTE en `kernel` da 15/24 (p 0.15).
- El pareado da 23/24 (p ≈ 10⁻⁶).

**Lectura del §K4 completo.**
- **Identidad, en el sentido declarado.** Dos gemelos idénticos al nacer,
  criados en mundos distintos, quedan diferentes. La diferencia sobrevive a un
  exilio compartido tan largo como la niñez: cada uno vuelve más rápido a su
  propia casa que a la del hermano, en 24/24 pares. Es continuidad psicológica
  medida en conducta; no mide un sentido de sí.
- **Por el sueño.** Sin el repaso del sueño, el exilio borra la casa (15/24,
  en el azar), y el contraste pareado da 23/24. La sostiene el sueño, que repasa
  la niñez guardada en el buffer. Mano declarada: la vida entra entera en el
  buffer, y con una vida más larga la niñez se olvidaría por construcción.
- **Dónde vive.** Vive en el modelo del mundo y no en el módulo de identidad
  declarado. La sonda conserva la casa, y la distancia entre los
  `self_embedding` no se achica ni sigue a la vida de forma legible.
- **Su propia señal.** La energía libre al entrar reconoce la casa en 19/24
  pares, pero por la letra el test falló. Ψ, saturado, no la reconoce.
- **El precio.** Criado en un solo mundo, el kernel que conserva su niñez entra
  peor a uno que nunca vivió, y al principio se atasca. En el §K3, criado entre
  tres regímenes, entraba mejor a lo nuevo. La identidad y la rigidez salen del
  mismo mecanismo.
- **El exilio se aprende estrecho.** Sin balbuceo, el modelo del mundo aprende
  el exilio sólo en las acciones que usa, y la sonda de acciones al azar no lo
  ve.

**Lo que sigue abierto:**
- Un repertorio robusto a lo nuevo (COIN), que viene del §K3.
- La rigidez. ¿Una crianza en varios regímenes la evita sin perder la
  identidad? El §K3 sugiere que sí, pero no se midió.
- Un nulo de deriva para el `self_embedding`: ¿lleva algo de la vida, o sólo
  deriva?
- La identidad, como continuidad medida en conducta, ya no está abierta (§K4,
  replicado).

### §K6 — REPERTORIO ROBUSTO por la letra (2026-10-26)

`results/mundo_propio_coin_run.txt`: semillas 0–11, 18.0 min.

- **ROBUSTO (primaria): 12/12.** Al final de la visita NUEVA, la sonda de los
  regímenes conocidos vale 0.14 × el promedio exacto (rango 0.11–0.16).
  - `error_x4` vale 1.06 en las mismas semillas y ninguna baja de 0.9 (0/12): es
    la fragilidad del §K3, otra vez.
- **CONTEXTO: 12/12**, con 0.15 × (`error_x4` da 0.64).
  - Desde el ciclo 2, la sonda de los conocidos ya vale 0.010.
  - `error_x4` necesitaba hasta el ciclo 6 para bajar a 0.048.
- **CONDUCTA: APRENDE Y RECUERDA** (12/12, 12/12 y 12/12; 0 atascos).
  **PAREADO: 12/12.**
- Veredicto pre-registrado: **REPERTORIO ROBUSTO.** La réplica está más abajo.
- **La inferencia de contexto.** El oráculo da 0.14, igual que la selección: la
  inferencia encuentra al experto correcto.
  - Contextos: 4 en 7 vidas, y 5 o 6 en las otras 5 (espurios).
  - Lo NUEVO tiene su propio experto en 12/12. La proporción del experto
    mayoritario por régimen tiene mediana 1.00.
- **El control.** `e_late` vale 0.039 en todos los ciclos (`error_x4`, 0.06–0.08).
  Al final de lo NUEVO, 0.041 contra 0.133.
- **Predicción fallida, del lado bueno.** La re-entrada a lo conocido tiende a
  mejorar: 9/12, con 0.122 contra 0.134. No llega al umbral. La entrada a lo
  NUEVO da 6/12.
- **Lo que no cambió.**
  - ESPECIFICIDAD: 7/12 contra `secuencia` y 5/12 contra `error_x4`. Los ahorros
    no son más específicos de lo vivido.
  - DISTINGUE: 11/12; el pareado contra el kernel sin sueño da 8/12.

### §K6, réplica — REPLICADO: el repertorio sobrevive a lo nuevo (2026-10-26)

`results/mundo_propio_coin_replica_run.txt`: semillas 12–23, 19.0 min.

- **ROBUSTO: 12/12.** Al final de lo NUEVO, la sonda de los conocidos da 0.11
  (rango 0.10–0.15). `error_x4` da 1.07, con 0/12 debajo de 0.9.
- **CONTEXTO: 12/12**, con 0.13. Es la misma lectura que en la réplica del §K3
  daba 8/12 en `error_x4`.
- **CONDUCTA: APRENDE Y RECUERDA** (12/12 ×3, 0 atascos). **PAREADO: 12/12.**
- Veredicto pre-registrado: **REPERTORIO ROBUSTO. REPLICADO.**
- **Contextos:** 4 en 8 vidas, 5 o 6 en 4. Lo NUEVO tiene su propio experto en
  12/12. El oráculo da 0.11, igual que la selección.
- **Control:** `e_late` al final de lo NUEVO da 0.044, contra 0.161 de `error_x4`.
- Re-entrada a lo conocido, `coin` < `error_x4`: 7/12. Entrada a lo NUEVO: 7/12.
- ESPECIFICIDAD: 5/12 y 6/12. DISTINGUE: 12/12; el pareado contra el kernel sin
  sueño da 10/12.

**Sobre las 24 semillas juntas:**
- ROBUSTO, CONTEXTO y PAREADO: 24/24.
- Re-entrada a lo conocido mejor que `error_x4`: 16/24 (p 0.08). Entrada a lo
  NUEVO: 13/24.
- DISTINGUE: 23/24; el pareado contra el kernel sin sueño da 18/24 (p 0.01).

**Lectura del §K6 completo.**
- **El repertorio robusto existe y es del mecanismo.** Con un experto por
  contexto inferido, y uno nuevo para lo que ningún conocido explica, el kernel
  sabe en qué régimen está y una visita a lo nunca visto ya no le borra lo que
  sabía. En el §K3, la misma lectura daba 1.06–1.07; acá da 0.11–0.14, en 24/24
  semillas.
- **Lo hace desde temprano.** La sonda de los conocidos baja a ~0.01 desde el
  ciclo 2. El modelo único del §K3 necesitaba 4 o 5 ciclos y un sueño 4×.
- **Controla mejor dentro de cada visita** (`e_late` 0.04 en todos los ciclos) y
  aprende lo nuevo mejor (0.04 contra 0.13–0.16).
- **No vuelve más rápido.** El costo de re-entrada (`e_early`) a lo conocido y
  a lo nuevo casi no mejora (16/24 y 13/24). El cambio de contexto espera a que
  el error corriente lo justifique, unos 10–30 ticks; ese es su precio.
- **Los ahorros no son más específicos de lo vivido** (ESPECIFICIDAD no pasa en
  ninguna de las dos corridas). Re-entra a lo conocido como `error_x4`; la
  diferencia está en que no lo olvida.
- **Manos declaradas.** El mecanismo es modular y está diseñado a mano: 6
  lugares, un umbral absoluto y constantes que salieron de una vida de
  exploración. Hay contextos espurios en 9/24 vidas (5 o 6 para 4 regímenes).
  Lo que se crea en vida son los contextos y su contenido, no la arquitectura.

**Lo que sigue abierto:**
- Un umbral relativo (o una inferencia bayesiana del contexto, como en COIN) en
  lugar del absoluto, para no depender de la escala del error.
- Re-entrar más rápido: inferir el contexto antes de que el error lo confirme
  (por ejemplo, con la sorpresa de los primeros ticks o con señales del mundo).
- Juntar el §K6 con la identidad (§K4) y la crianza (§K5): un kernel con
  repertorio, ¿sigue teniendo identidad? ¿sigue siendo rígido?
- Un repertorio robusto ya no está abierto (§K6, replicado).

### §K5 — MENOS RÍGIDO, CON IDENTIDAD; el `self_embedding` lleva la vida, no la niñez (2026-10-27)

`results/mundo_propio_crianza_run.txt`: pares 0–11, 122.7 min. La corrida tardó
más que los 95 min previstos porque compartió la CPU con el §K6.
- Verificación: el camino `una` re-corrido sobre el par 0 reproduce la vida del
  §K4 con diferencia 0.

**P1 — crianza. Veredicto pre-registrado: MENOS RÍGIDO, CON IDENTIDAD.**
- **ACHICA (primaria): 10/12, justo en el umbral.** La brecha (costo en T1 de
  `error_x4` − el de `kernel`) baja de +0.26 a +0.03, en medianas.
- El cambio viene casi entero de `error_x4`. Su costo en la casa del hermano
  baja de 0.71 a 0.47 (FLEXIBLE 9/12). El del `kernel` sin sueño no baja: 0.46 y
  0.51 (6/12).
- **CONSERVA: 12/12**, con H(T2) de +0.38 (en `una`, +0.53). La identidad
  queda, algo más débil: la casa tuvo la mitad de la niñez.
- **INVIERTE: 5/12. No pasa.** Con niñez plural, el sueño deja de ser un precio
  pero no se vuelve una ventaja. Era la predicción.
- **El exilio.** El primer bloque del exilio de `error_x4` baja de 0.68 a 0.43
  (11/12). Los atascos al empezar el exilio pasan de 12 bloques (11/24 gemelos)
  a 1.
- **Lectura posterior: el que se atasca ahora es el kernel sin sueño.** En la
  crianza `dos` acumula 27 bloques atascados en 11/24 gemelos (en `una`, 1). 25
  de esos 27 caen en la niñez: 18 en la escuela y 7 en casa. Re-aprende en cada
  cambio de régimen, como en el §K1.
- **La sonda de `error_x4` bajo `dos`** conserva las dos casas de su niñez: casa
  0.025 y escuela 0.021. Hermano 0.17 y exilio 0.17: el exilio sigue aprendido
  estrecho.
- **Reportado, no veredicto: la atribución de la identidad al sueño se debilita
  bajo `dos`.** PERSISTE en `kernel` da 7/12, y el pareado `error_x4` > `kernel`
  en H(T2), 7/12. En `una` daba 11/12.

**P2 — deriva. Veredicto pre-registrado: LLEVA LA VIDA, NO LA NIÑEZ.**
- **CONTROL: 12/12, en T1 y en T2.** El perfil de la sonda separa con claridad
  a los gemelos de otro mundo (0.25) de los de otros dados (0.006–0.013).
- **LLEVA: 11/12.** En T1, el `self_embedding` de gemelos de mundos distintos
  está más lejos (2.75) que el de gemelos con otros dados (1.88).
- **NIÑEZ: 7/12. No pasa.** En el exilio compartido la diferencia se borra: Tm
  2.67 contra 2.57 (7/12) y T2 2.49 contra 2.45 (7/12).
- Por qué la distancia del §K4 "no se achicaba": la deriva sola también crece
  (d_dados va de 1.88 a 2.45). El `self_embedding` sigue el presente, es decir,
  la acción que el kernel elige, y acumula deriva. La niñez no queda en él.
- **La predicción escrita (DERIVA) falló.** La nota agregada antes del resultado
  ("LLEVA pasa en T1, NIÑEZ es incierta") acertó. La identidad del §K4 vive en
  el modelo del mundo.
- Los gemelos con otros dados controlan normal: `e_late` 0.046 al final del
  exilio.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K5, réplica — REPLICADO en las dos preguntas (2026-10-27)

`results/mundo_propio_crianza_replica_run.txt`: pares 12–23, 119.1 min.
- Verificación: el camino `una` re-corrido sobre el par 12 reproduce la vida de
  la réplica del §K4 con diferencia 0.

**P1 — crianza: MENOS RÍGIDO, CON IDENTIDAD. REPLICADO.**
- **ACHICA: 10/12 otra vez, en el umbral.** La brecha baja de +0.23 a +0.05.
- El cambio vuelve a ser de `error_x4`: su costo en la casa del hermano baja de
  0.71 a 0.55 (FLEXIBLE 9/12). El del `kernel` sin sueño, 0.49 y 0.47 (6/12).
- **CONSERVA: 11/12**, con H(T2) de +0.41 (en `una`, +0.72).
- **INVIERTE: 4/12. No pasa**, como en el test.
- **El exilio.** El primer bloque de `error_x4` baja de 0.71 a 0.43 (11/12). Sus
  atascos pasan de 16 bloques (15/24 gemelos) a 1.
- **Posterior, repetido: el que se atasca es el kernel sin sueño.** Bajo `dos`
  acumula 31 bloques atascados en 14/24 gemelos. 27 caen en la niñez (16 en la
  escuela y 11 en casa) y 4 en el exilio.
- **La sonda de `error_x4` bajo `dos`**, igual que en el test: casa 0.024 y
  escuela 0.021; hermano 0.175 y exilio 0.173.
- **La atribución al sueño, débil otra vez.** PERSISTE en `kernel` da 7/12, y el
  pareado `error_x4` > `kernel` en H(T2), 8/12.

**P2 — deriva: LLEVA LA VIDA, NO LA NIÑEZ. REPLICADO.**
- **CONTROL: 12/12** en T1 y en T2. El perfil de la sonda da 0.25 entre mundos
  y 0.005–0.011 entre dados.
- **LLEVA: 12/12** (2.45 contra 1.87).
- **NIÑEZ: 7/12. No pasa** (3.01 contra 2.65). En Tm daba 10/12 (3.03 contra
  2.60); en el test, 7/12.
- La deriva sola vuelve a crecer: d_dados va de 1.87 a 2.65.
- Los gemelos con otros dados controlan normal: `e_late` 0.043.

**Sobre los 24 pares juntos:**
- ACHICA 20/24 (p 0.0008): la brecha mediana baja de +0.24 a +0.04.
- CONSERVA 23/24. INVIERTE 9/24.
- FLEXIBLE: `error_x4` 18/24 (p 0.01); `kernel` 12/24.
- Primer bloque del exilio de `error_x4`, `dos` < `una`: 22/24.
- Atascos de `error_x4`: con una casa, 28 bloques en 26/48 gemelos, todos al
  empezar el exilio. Con dos, 2 en 2/48.
- Atascos del `kernel` sin sueño bajo `dos`: 58 bloques en 25/48 gemelos. 52
  caen en la niñez (34 en la escuela y 18 en casa).
- Bajo `dos`, el `kernel` PERSISTE en 14/24 (azar). El pareado `error_x4` >
  `kernel` da 15/24 (p 0.15); en el §K4 daba 23/24.
- P2: CONTROL 24/24, LLEVA 23/24, NIÑEZ 14/24 (p 0.27).

**Lectura del §K5 completo.**
- **La rigidez del §K4 era de la crianza, no de la identidad.** Criado entre su
  casa y una escuela, el kernel con sueño entra mejor a la casa del hermano
  (0.71 → 0.47–0.55) y entra al exilio sin atascarse (28 bloques → 2). Y sigue
  distinto de su gemelo después del exilio, en 23/24 pares. El precio se
  achica, pero no se vuelve ventaja (INVIERTE 9/24). ACHICA quedó en el umbral
  en las dos corridas; juntas dan 20/24.
- **La rigidez se mudó al kernel sin sueño.** Bajo la crianza alternada, el que
  se atasca es el que no repasa: 58 bloques, casi todos en la niñez. Re-aprende
  en cada cambio entre casa y escuela, como en el §K1. Es el sueño lo que le
  permite tener dos casas.
- **La identidad sobrevive, más débil y menos atribuible.** H(T2) baja de
  +0.53/+0.72 a +0.38/+0.41: la casa tuvo la mitad de la niñez. El kernel sin
  sueño sigue en el azar (14/24), pero el pareado contra él cae de 23/24 a
  15/24. Con media niñez en una escuela común, la parte de la diferencia que se
  le puede atribuir al sueño ya no es clara. Es una lectura reportada, no un
  veredicto.
- **Dónde vive.** En el modelo del mundo: el perfil de la sonda separa a los
  gemelos de mundos distintos en 24/24 pares en cada ensayo (0.23–0.25 contra
  0.005–0.013). El `self_embedding` lleva la vida, pero no la niñez. Separa a
  los gemelos al terminar la niñez (23/24) y no después del exilio (14/24).
  Sigue al presente, que es la acción elegida (`action_dim == obs_dim`), y su
  deriva sola crece de 1.87 a 2.45–2.65. La identidad del §K4 no está en el
  módulo que se llama identidad.
- **Predicciones fallidas.** DERIVA (que el `self_embedding` no llevara ni la
  vida) falló en las dos corridas. Acertó la nota agregada antes del resultado.
- **Manos declaradas.** La escuela es un régimen fijo (N) que comparten los dos
  gemelos. La vida entra entera en el buffer del sueño. INVIERTE y la
  atribución al sueño bajo `dos` no pasan.

**Lo que sigue abierto:**
- Juntar el §K6 con el §K4 y el §K5. Con un experto por casa (`wm_contexts`),
  la rigidez podría desaparecer sin achicar la identidad. O la identidad podría
  pasar a ser qué experto se elige al volver.
- Por qué INVIERTE no pasa: con dos casas, el sueño deja de costar, pero no
  ayuda a entrar a lo nunca vivido. ¿Haría falta una crianza más diversa, de
  tres o cuatro regímenes, como en el §K3?
- Un `self_embedding` que lleve la niñez. Hoy refleja la acción elegida. Que el
  modelo de sí lea el modelo del mundo, o dejar de llamarlo el portador de la
  identidad.
- Ya no está abierto si la rigidez es el precio inevitable de la identidad
  (§K5, replicado): con una crianza plural se achica sin perderla.

### §K7 — IDENTIDAD EN EL REPERTORIO por la letra; no conserva más identidad, pero cuesta menos (2026-10-27)

`results/mundo_propio_casas_run.txt`: pares 0–11, 137.2 min. Tardó más que los
100–110 min previstos: cada vida de `coin` llevó unos 8 min.
- Verificación: el loop re-corrido sobre `error_x4` (par 0, gemelo A, `una`)
  reproduce la vida del §K4 con diferencia 0.

**Veredicto pre-registrado (`una`): IDENTIDAD EN EL REPERTORIO.**
- **SE DIFERENCIA: 12/12**, con H(T1) +0.96.
- **PERSISTE: 12/12**, con H(T2) +0.69. Queda debajo de H(T1), como se predijo.
- **ELIGE: 11/12.** El exilio tuvo su propio experto en 24/24 gemelos. En T2,
  23/24 gemelos vuelven a h en casa. La latencia mediana es de 11 ticks; la
  predicción decía 10–30.
- **El par que falla es el 1, y falla en el gemelo A.** En la niñez abrió un
  segundo experto, así que h = 1. En T2 se asienta en el 0, que también es de su
  niñez: 222 de los 300 ticks en el 0 y 64 en el 1. Falla por la letra: vuelve a
  la niñez, pero no a su último experto.
- Contextos en uso: 2 en 18/24 gemelos y 3 en 6/24.
- NO CONFUNDE: 12/12 en T2, reportado.
- La sonda de `coin` en T2: casa 0.007, exilio 0.030 y casa del hermano 0.185.
  Conserva su casa a través del exilio; la del hermano nunca la vivió.

**Secundarias bajo `una`.**
- **PAREADO: 6/12. Falla.** Se había predicho que pasaba, antes y después de la
  calibración. En medianas `coin` queda arriba (+0.69 contra +0.53), pero par a
  par empata: las diferencias van de −0.35 a +1.28.
- **ACHICA: 10/12. Pasa.** La predicción escrita decía que fallaba, y la de
  después de la calibración la daba por incierta. El costo en T1 en la casa del
  hermano baja de 0.71 (`error_x4`) a 0.51.
- **RIGIDEZ: 7/12. Falla.** Se había predicho que pasaba, las dos veces. `coin`
  entra a la casa del hermano casi como el kernel sin sueño (0.51 contra 0.46).
  La calibración engañó: ahí dio 3/3 (0.77 contra 0.44).
- **EXILIO: 11/12. Pasa**, como se predijo. El primer bloque del exilio da 0.50
  contra 0.68. Bloques atascados: 2 (2/24 gemelos) contra 12 (11/24).
- RECONOCE (el cruce de la energía libre en T2): 8/12, reportado.

**Bajo `dos`, contra las vidas del §K5.**
- **SE DIFERENCIA 12/12.**
- **CONSERVA 12/12**, con H(T2) +0.46 (`error_x4`, +0.38). El riesgo que
  mostraba la calibración (+0.10) no apareció.
- **ELIGE 12/12**, con una latencia de 17 ticks en T2.
- PAREADO 8/12. ACHICA 7/12: el costo de `coin` (0.51) queda como el de
  `error_x4` (0.47), y ésa era la predicción escrita. RIGIDEZ 5/12. EXILIO 10/12
  (0.33 contra 0.43).
- Contextos: 3 en 19/24 gemelos y 4 en 5/24. El experto de casa es siempre el 1
  y el del exilio, el 2 o el 3.
- La sonda en T2: casa 0.014, escuela 0.011, exilio 0.033 y hermano 0.185.
- RECONOCE 2/12, reportado.

**Lectura posterior, no veredicto** (sobre las vidas guardadas).
- **`coin` se diferencia menos en T1 y pierde menos en el exilio.** H(T1) da
  +0.96 contra +1.36 de `error_x4`; `coin` queda abajo en 10/12 pares.
- **La retención H(T2)/H(T1) da 0.76 contra 0.43** (8/12, no llega al umbral).
  Por eso PAREADO empata: `coin` empieza con menos identidad y pierde menos.
- **La identidad en T1 es más chica porque `coin` paga menos afuera.** H es el
  cruce afuera − en casa. La diferencia de costo (0.71 − 0.51, por dos gemelos)
  da 0.40, la misma diferencia que en H(T1), en medianas.
- **Por qué paga menos: en la casa del hermano, el clon abre un experto nuevo.**
  En T1 se asienta en h en sólo 2/24 gemelos; en el resto, en un experto nuevo.
- **La predicción escrita (ACHICA falla) suponía que esa copia de h no ganaba
  nada, y ganó.** La hipótesis, sin probar, es la misma de EXILIO: la copia
  sueña sólo sobre lo nuevo, y la niñez no la arrastra hacia la casa.
- **En resumen, el repertorio no conserva más identidad que `error_x4`, pero
  casi no cobra el precio del §K4.** Lo nunca vivido va a un experto aparte, y
  la identidad pasa a ser a qué experto vuelve al volver a casa.

**Las predicciones, contra el resultado.**
- **Escritas antes de la calibración:**
  - Acertadas: SE DIFERENCIA; PERSISTE; H(T2) < H(T1); la latencia; ELIGE.
    También, bajo `dos`: CONSERVA, ELIGE y el costo como el de `error_x4`.
  - Fallidas: PAREADO, RIGIDEZ y "ACHICA falla".
- **Agregadas después de la calibración:**
  - Acertadas: PERSISTE, ELIGE y EXILIO.
  - Fallidas: PAREADO y RIGIDEZ.
  - La de CONSERVA "en riesgo" no se cumplió: pasó 12/12.

**Manos declaradas:**
- `coin` nace con 6 expertos, así que sus pesos y su azar no son los de
  `error_x4` en el mismo par.
- El cambio de experto usa un umbral absoluto sobre el error corriente (§K6).

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K7, réplica — REPLICADO: la identidad es a qué experto vuelve (2026-10-27)

`results/mundo_propio_casas_replica_run.txt`: pares 12–23.
- **Corrió en dos tramos.** El primero se cortó a las 12:56 por falta de memoria
  en el sistema, con 28 de las 48 vidas escritas. El segundo las cargó del disco
  (`replica reanudar`, commit `c6c60cd`) y corrió las 20 que faltaban en 42.2 min.
- Una vida guardada es la salida determinista del loop. El modo `reanudar` se
  validó recargando el test: el informe salió idéntico, salvo los minutos.
- Verificación: el loop re-corrido sobre `error_x4` (par 12, gemelo A) reproduce
  la vida de la réplica del §K4 con diferencia 0.

**Veredicto pre-registrado (`una`): IDENTIDAD EN EL REPERTORIO. REPLICADO.**
- **SE DIFERENCIA 12/12** (H(T1) +1.00) y **PERSISTE 12/12** (H(T2) +0.98).
- **ELIGE 11/12.** El exilio tuvo su propio experto en 24/24 gemelos, y en T2
  23/24 vuelven a h en casa, con una latencia de 11 ticks.
- **Falla el par 17, por el gemelo B.** Su vida abrió tres expertos; en T2 se
  asienta en el 1 (240 de 300 ticks), que no es ni el de casa ni el del exilio.
- Contextos en uso: 2 en 23/24 gemelos.
- La sonda en T2: casa 0.006, exilio 0.025 y hermano 0.186.
- RECONOCE 6/12, reportado.

**Secundarias bajo `una`.**
- **PAREADO 9/12.** No pasa por la letra (en el test, 6/12). Medianas: +0.98
  contra +0.72.
- **ACHICA 9/12.** No pasa por la letra (en el test, 10/12). Costo 0.53 contra
  0.71.
- **RIGIDEZ 8/12.** No pasa (en el test, 7/12): 0.53 contra 0.49 del `kernel`.
- **EXILIO 11/12. Pasa otra vez:** 0.60 contra 0.71. Atascos: 1 bloque contra
  16 (15/24 gemelos).

**Bajo `dos`.**
- **SE DIFERENCIA 12/12.**
- **CONSERVA 10/12, en el umbral:** H(T2) +0.66 (`error_x4`, +0.41).
- **ELIGE 12/12**, con una latencia de 18 ticks.
- PAREADO 7/12. ACHICA 10/12 (0.30 contra 0.55). EXILIO 10/12.
- RIGIDEZ 3/12: `coin` entra a la casa del hermano mejor que el kernel sin
  sueño en 9/12 pares (0.30 contra 0.47).
- Contextos: 3 en 22/24 gemelos. El de casa es siempre el 1.

**Sobre los 24 pares juntos** (tests de signo de una cola).
- `una`:
  - SE DIFERENCIA y PERSISTE: 24/24.
  - ELIGE: 22/24 (p < 0.0001).
  - PAREADO: 15/24 (p 0.15).
  - ACHICA: 19/24 (p 0.003).
  - RIGIDEZ: 15/24 (p 0.15).
  - EXILIO: 22/24.
  - Bloques atascados: 3 en 3/48 gemelos, contra 28 en 26/48 de `error_x4`.
- `dos`:
  - CONSERVA: 22/24.
  - ELIGE: 24/24.
  - PAREADO: 15/24.
  - ACHICA: 17/24 (p 0.03).
  - EXILIO: 20/24 (p 0.0008).
  - RIGIDEZ: 8/24; es decir, `coin` < `kernel` en 16/24 (p 0.08).
- Posterior: la retención H(T2)/H(T1), `coin` > `error_x4`, da 17/24 (p 0.03)
  en `una` y 16/24 en `dos`. H(T1) de `coin` queda por debajo en 19/24 y 17/24.
- Posterior: en T1, en la casa del hermano, el clon de `coin` se asienta en h en
  sólo 4/48 gemelos (`una`) y 1/48 (`dos`). En el resto abre un experto nuevo.
- Posterior, en medianas de los 24 pares, bajo `una`:

  | Brazo | Costo en casa en T2 | Afuera en T2 |
  |---|---|---|
  | `coin` | 0.145 | 0.523 |
  | `error_x4` | 0.248 | 0.613 |
  | `kernel` | 0.489 | 0.530 |

**Lectura del §K7 completo.**
- **La identidad sobrevive al repertorio y se vuelve una elección.**
  - En 24/24 pares los gemelos siguen distintos después del exilio.
  - En 96/96 gemelos (las dos crianzas, las dos corridas) el exilio tuvo su
    propio experto.
  - Al volver a casa, en 22/24 pares (`dos`: 24/24) los dos gemelos se asientan
    en el experto de su niñez, en 11–18 ticks.
  - La sonda conserva la casa a través del exilio: 0.006 contra 0.18 de la casa
    del hermano.
  - El §K4 decía que la identidad vive en el modelo del mundo. Con repertorio, es
    cuál de sus modelos elige al volver.
- **No conserva más identidad que `error_x4`, pero la conserva de otra forma.**
  - PAREADO 15/24.
  - Arranca con menos, porque paga menos en la casa del hermano.
  - Retiene más a través del exilio: 17/24, p 0.03, posterior.
  - En T2 vuelve mejor a su propia casa: 0.145 contra 0.248.
- **El precio del §K4 casi desaparece.**
  - Bajo `una`, ACHICA da 19/24 y RIGIDEZ cae al azar (15/24): `coin` entra a la
    casa del hermano casi como el kernel sin sueño.
  - Bajo `dos`, entra mejor que él en 16/24 (p 0.08). Es casi la inversión que
    el §K5 no logró con `error_x4` (INVIERTE 9/24).
  - Al exilio entra sin atascarse: 3 bloques contra 28.
  - El mecanismo, visto: lo nunca vivido va a un experto nuevo (en T1 sólo 5/96
    gemelos se quedan en el de casa).
  - La hipótesis, sin probar: el experto nuevo sueña sólo sobre lo suyo, y la
    niñez no lo arrastra.
- **Lo que el §K5 lograba con la crianza, el §K7 lo logra con la arquitectura.**
  Una crianza plural achicaba la rigidez en `error_x4`. Un experto por casa la
  achica aun con una sola casa.
- **Dónde falla la elección.** Los dos pares que fallan ELIGE tienen un gemelo
  con un tercer experto: uno abierto en la niñez, o uno que no es ni la casa ni
  el exilio. Son los contextos espurios del §K6, con su umbral absoluto.
- **Predicciones fallidas, en las dos corridas:**
  - PAREADO (6/12 y 9/12).
  - RIGIDEZ (7/12 y 8/12). La calibración engañó: dio 3/3.
  - "ACHICA falla": pasó, 19/24.
- **Manos declaradas:**
  - `coin` nace con 6 expertos.
  - El umbral de cambio es absoluto.
  - La réplica corrió en dos tramos.
  - No hay un brazo `coin` sin sueño, así que acá no se prueba que la identidad
    del repertorio sea del sueño.

**Lo que sigue abierto:**
- Un `coin` sin sueño. Sin él no se sabe si la identidad del repertorio es del
  sueño, como la del §K4, o de la sola separación en expertos.
- Una elección más limpia, con un umbral relativo o una inferencia bayesiana
  del contexto (el COIN completo): menos contextos espurios.
- Re-entrar más rápido: el cambio espera al error corriente, 11–18 ticks.
- INVIERTE bajo `dos` quedó en p 0.08. ¿Una crianza más diversa, con tres o
  cuatro regímenes como en el §K3, haría del repertorio una ventaja ante lo
  nunca vivido?
- Un `self_embedding` que lea el modelo del mundo, o el experto que elige, en
  vez de la acción.
- Ya no está abierto si un kernel con repertorio tiene identidad (§K7,
  replicado): la tiene, y su identidad es a qué experto vuelve.

### §K8 — POR EL SUEÑO por la letra; sin sueño, el repertorio olvida la casa (2026-10-27)

`results/mundo_propio_separacion_run.txt`: pares 0–11, 27.9 min.
- Verificación: el loop re-corrido sobre `coin` (par 0, gemelo A) reproduce la
  vida del §K7 con diferencia 0.

**Veredicto pre-registrado: POR EL SUEÑO.**
- **SE DIFERENCIA: 12/12** (H(T1) de `coin_sin_sueno`, +0.86).
- **PERSISTE_SS: 7/12. Falla.** H(T2) da +0.06: sin sueño, la identidad del
  repertorio queda al azar, como la del kernel sin sueño en el §K4.
- **SEPARA: 6/12.** Sin sueño, separar el exilio en su propio experto no
  conserva más identidad que el modelo único.
- **SUEÑO: 12/12.** H(T2) da +0.69 con sueño y +0.06 sin él.

**Secundarias.**
- **ELIGE_SS: 5/12. Falla.** El exilio sí tuvo su propio experto (24/24
  gemelos), pero al volver a casa sólo 13/24 gemelos se asientan en h.
  - En T2, la latencia mediana es de 90 ticks.
  - En Tm, 11/24 gemelos, con una latencia mediana de 300 ticks: la mitad
    nunca vuelve en el ensayo.
  - NO CONFUNDE: 12/12.
- **EXILIO_SS: 4/12** (0.44 contra 0.43).
- **PERSISTE de `error_sin_sueno`: 8/12** (+0.12). Queda al azar, como predijo
  la predicción escrita.
- **ERROR_SS: 6/12.** La sorpresa de la calibración no se sostuvo: sin sueño,
  ver su propio error no le da identidad al modelo único.
- **Reportado: el sueño con un solo modelo, `error_x4` > `error_sin_sueno`,
  10/12.** Es la atribución del §K4 con el error de entrada fijo. En el §K4,
  `error_x4` contra `kernel` cambiaba también el error de entrada; acá sólo
  cambia el sueño.

**Dónde se pierde.** Costos en medianas:

| Brazo | En casa T1 | En casa T2 | Afuera T2 |
|---|---|---|---|
| `coin` | 0.032 | 0.146 | 0.489 |
| `coin_sin_sueno` | 0.034 | 0.460 | 0.489 |
| `error_sin_sueno` | 0.033 | 0.428 | 0.522 |
| `kernel` | 0.033 | 0.474 | 0.554 |

- Sin sueño, la identidad se pierde porque vuelve mal a su propia casa. En la
  del hermano, en cambio, le va igual.

**Lectura posterior, no veredicto** (sobre las vidas guardadas).
- **El experto de casa de `coin_sin_sueno` empeora sin estar activo.**
  - El oráculo (el mejor experto, por secuencia) en casa pasa de 0.086 en T1 a
    0.131 en Tm y T2. En `coin` queda en 0.005–0.007.
  - Pero en el exilio el experto de casa está activo una mediana de 33 de los
    4500 ticks (0/24 gemelos pasan del 5 %), con una mediana de 0 cambios de
    experto.
- **Hipótesis, a verificar: la foto vieja.**
  - La foto del experto activo se toma cuando su error corriente pasa el umbral
    absoluto (0.08), y sólo se descarta si vuelve a bajar.
  - Sin sueño, el experto de casa queda apenas encima del umbral (sonda 0.086).
    La foto se tomaría en algún momento de la niñez y nunca se descartaría.
  - Al nacer el experto del exilio, el de casa se restaura a esa foto vieja y
    pierde lo que aprendió después.
  - Si es así, `coin_sin_sueno` no es "el repertorio sin sueño" a secas: es un
    mecanismo de protección calibrado para un modelo preciso, que sin sueño se
    dispara mal. El umbral absoluto es la mano declarada desde el §K6.

**Las predicciones, contra el resultado.**
- **Escritas antes de la calibración:**
  - Acertadas: SE DIFERENCIA 12/12; PERSISTE de `error_sin_sueno`, al azar.
  - Fallidas: el veredicto POR LA SEPARACIÓN; PERSISTE_SS; SEPARA; ELIGE_SS;
    "SUEÑO falla". La razón escrita (sólo aprende el activo, así que la niñez
    queda protegida) no tuvo en cuenta la foto.
- **Agregadas después de la calibración:**
  - Acertadas: SUEÑO.
  - Fallidas: PERSISTE_SS, ELIGE_SS y EXILIO_SS.
- La calibración de 3 pares volvió a engañar: PERSISTE_SS 3/3 → 7/12, ELIGE_SS
  3/3 → 5/12, ERROR_SS 3/3 → 6/12.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K8, réplica — REPLICADO: la identidad del repertorio es del sueño (2026-10-27)

`results/mundo_propio_separacion_replica_run.txt`: pares 12–23, 29.2 min.
- Verificación: el loop re-corrido sobre `coin` (par 12, gemelo A) reproduce la
  vida de la réplica del §K7 con diferencia 0.

**Veredicto pre-registrado: POR EL SUEÑO. REPLICADO.**
- **SE DIFERENCIA: 12/12** (+0.98).
- **PERSISTE_SS: 7/12**, otra vez (H(T2) +0.09).
- **SEPARA: 8/12.**
- **SUEÑO: 11/12** (+0.98 contra +0.09).
- Secundarias:
  - ELIGE_SS 7/12: 19/24 gemelos vuelven a h en T2, con una latencia de 32
    ticks.
  - EXILIO_SS 8/12.
  - PERSISTE de `error_sin_sueno` 5/12.
  - ERROR_SS 5/12.
- Reportado: el sueño con un solo modelo (`error_x4` > `error_sin_sueno`) da
  12/12.
- Costo en casa en T2: `coin` 0.141, `coin_sin_sueno` 0.378, `error_sin_sueno`
  0.646, `kernel` 0.504.

**Sobre los 24 pares juntos** (tests de signo de una cola):

| Lectura | 24 pares |
|---|---|
| SE DIFERENCIA | 24/24 |
| PERSISTE_SS | 14/24 (p 0.27) |
| SEPARA | 14/24 |
| SUEÑO | 23/24 (p < 0.0001) |
| ELIGE_SS | 12/24 |
| EXILIO_SS | 12/24 |
| PERSISTE de `error_sin_sueno` | 13/24 |
| ERROR_SS | 11/24 |
| Sueño con un solo modelo | 22/24 (p < 0.0001) |

- En T2 se asientan en h 32/48 gemelos sin sueño y 46/48 con sueño.

**La hipótesis de la foto vieja: REFUTADA**
(`experiments/kernel/exp_mundo_propio_separacion_foto.py`,
`results/mundo_propio_separacion_foto_run.txt`, posterior).
- Se re-corrieron 6 vidas de `coin_sin_sueno` (pares 0–2) y 2 de `coin` (par 0)
  registrando cuándo se toma, se descarta y se restaura cada foto. Las 8
  reprodujeron la vida guardada con diferencia 0.
- En las 6 vidas sin sueño, la foto que se restaura al nacer el experto del
  exilio se tomó 29 ticks antes, entre 4 y 24 ticks después de empezar el exilio.
- Al terminar la niñez, el error corriente estaba debajo del umbral, entre 0.003
  y 0.047. No hay una foto vieja de la niñez.

**Lo que sí pasa** (posterior, sobre el oráculo de casa de los 48 gemelos sin
sueño).
- **Durante el exilio, el experto de casa queda congelado.** El oráculo en el
  bloque 32 es igual al del bloque 18 en 39/48 gemelos. La lectura del test ("se
  degrada estando inactivo") estaba mal: el cambio ocurre entero al empezar el
  exilio.
- **Al empezar el exilio empeora.** El oráculo pasa de 0.087 (bloque 17, fin de
  la niñez) a 0.122 (bloque 18), y sube en 31/48 gemelos.
- **Por qué empeora.** El error corriente es un promedio móvil, así que cruza el
  umbral unos ticks tarde. La foto "previa a la racha" ya incluye los primeros
  pasos de aprendizaje del exilio, con errores grandes. Sin sueño, nada repara
  ese daño.
- **Además, es impreciso.** Sin sueño, el experto de casa queda en 0.087 (con
  sueño, 0.005), y en la niñez fluctúa 0.030 de un bloque al siguiente.
- **Con sueño pasa lo mismo, pero se repara.** En `coin`, la foto también se toma
  29 ticks antes del nacimiento del experto del exilio. Pero el sueño repasa a
  cada experto sobre su propio buffer, también a los inactivos, y el de casa se
  mantiene en 0.005–0.007 a lo largo del exilio.
- **Así, al volver, el experto de casa no se distingue del experto del exilio.**
  El clon tarda en volver a él (32–90 ticks) o no se asienta en él (16/48
  gemelos en T2), y
  vuelve mal a su propia casa.

**Lectura del §K8 completo.**
- **La identidad del repertorio es del sueño, como la del §K4.** Sin sueño, en
  el modelo de contextos o en el modelo único, la identidad después del exilio
  queda al azar (14/24 y 13/24). Con sueño, 24/24.
- **Separar no alcanza.** El exilio tiene su propio experto también sin sueño
  (48/48 gemelos), y el de casa queda congelado. Pero no se conserva más
  identidad que con un solo modelo (SEPARA 14/24).
- **Sin sueño, el experto de casa se conserva, pero no se distingue.** Queda
  impreciso, dañado por los primeros pasos del exilio, y el clon no lo elige al
  volver.
- **Lo que el sueño hace en el repertorio:** vuelve preciso al experto de la
  niñez y lo mantiene así mientras está inactivo. Con eso, al volver, la
  elección es clara.
- **La atribución del §K4, limpia.** Con el error de entrada fijo, el sueño solo
  da la identidad en 22/24 pares (`error_x4` > `error_sin_sueno`). En el §K4, la
  comparación con `kernel` cambiaba dos cosas a la vez.
- **Predicciones fallidas:**
  - POR LA SEPARACIÓN (la escrita).
  - PERSISTE_SS, ELIGE_SS y EXILIO_SS (las posteriores a la calibración).
  - La hipótesis de la foto vieja, del test.
  - La calibración de 3 pares volvió a engañar, como en el §K7.
- **Manos declaradas:**
  - No se corrió `dos`.
  - El umbral de cambio es absoluto.
  - La foto se toma con el retraso del promedio móvil.
  - `coin_sin_sueno` es `coin` sin el sueño del modelo del mundo; el resto del
    kernel no cambia.

**Lo que sigue abierto:**
- **¿El sueño de la niñez o el del exilio?** El sueño vuelve preciso al experto
  de casa en la niñez y lo mantiene en el exilio. Un `coin` que duerme sólo en
  la niñez separaría las dos cosas: si conserva la identidad, alcanza con un
  experto preciso congelado.
- La foto a tiempo: tomarla con la ventana del promedio móvil, unos ticks antes
  del cruce del umbral, o detectar el cambio más rápido. Es barato, pero
  probablemente no rescata la identidad sin sueño, porque el experto sigue
  impreciso.
- Lo que quedó del §K7: un umbral relativo, re-entrar más rápido, INVIERTE, y un
  `self_embedding` que lea el modelo del mundo.
- Ya no está abierto si la identidad del repertorio es de la separación (§K8,
  replicado): es del sueño.

### §K9 — INDETERMINADO por la letra; la precisión de la niñez no sobrevive al comienzo del exilio (2026-10-27)

`results/mundo_propio_ninez_run.txt`: pares 0–11, 31.1 min.
- Verificación: las 24 niñeces de `coin_ninez` son iguales a las vidas guardadas
  de `coin` del §K7, con diferencia 0.

**Veredicto pre-registrado: INDETERMINADO.**
- **PERSISTE_N: 9/12.** No pasa por la letra. H(T2) da +0.35, entre `coin`
  (+0.69) y `coin_sin_sueno` (+0.06).
- **NIÑEZ: 8/12.** No pasa.
- **EXILIO: 8/12.** No pasa.
- **ELIGE_N: 4/12. Falla.**
  - Al volver a casa, sólo 15/24 gemelos se asientan en h, con una latencia de
    36 ticks.
  - En 2/24 gemelos el exilio no tuvo su propio experto (e = h).

**La nota del humo se confirmó: DAÑO 23/24.**

| Brazo | Oráculo de casa al final de la niñez | Primer bloque del exilio | Último | DAÑO | CONGELADO |
|---|---|---|---|---|---|
| `coin` | 0.005 | 0.006 | 0.007 | 16/24 | 15/24 |
| `coin_ninez` | 0.005 | 0.121 | 0.121 | 23/24 | 21/24 |
| `coin_sin_sueno` | 0.086 | 0.131 | 0.131 | 15/24 | 20/24 |

- **El sueño de la niñez deja al experto de casa preciso** (0.005), igual que
  en `coin`.
- **En el primer bloque del exilio esa precisión se pierde casi entera:** queda
  en 0.121, cerca del experto impreciso del §K8 (0.131). Después queda
  congelado.
- **Los primeros pasos del exilio llevan a cualquier experto de casa a ~0.12–0.13,**
  sea preciso o impreciso. Con sueño (`coin`), el daño casi no se ve, porque el
  sueño lo repara durante el bloque.
- **Así, la pregunta del §K9 no se pudo hacer limpia.** El experto que se congela
  ya no es el preciso de la niñez, sino uno dañado por los primeros pasos del
  exilio.

**Costos en medianas.**

| Brazo | En casa T2 | Afuera T2 |
|---|---|---|
| `coin` | 0.146 | 0.489 |
| `coin_ninez` | 0.382 | 0.640 |
| `coin_sin_sueno` | 0.460 | 0.489 |

- Parte del H(T2) de `coin_ninez` viene de que le va peor afuera, no de que
  vuelva mejor a casa. Es una lectura, no un veredicto.

**Lectura posterior, no veredicto.**
- El daño ocurre antes de la foto. Según el §K8, la foto se toma entre 4 y 24
  ticks después de empezar el exilio, cuando el promedio móvil del error cruza
  el umbral. En esos pasos, el experto de casa aprende del exilio con errores
  grandes.
- La explicación de la nota (Adam y gradientes chicos) no se probó. El
  resultado sugiere algo más simple: no importa cuán preciso fuera, los
  primeros pasos lo llevan al mismo nivel.

**Las predicciones, contra el resultado.**
- Acertadas: la niñez igual a la de `coin` (24/24, diferencia 0); DAÑO y
  CONGELADO en la mayoría.
- Fallidas: PERSISTE_N, NIÑEZ, EXILIO, ELIGE_N y el veredicto LA NIÑEZ SOSTIENE,
  EL RESTO SUMA.
- La nota del humo, escrita antes del test, avisó el riesgo y se cumplió.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K9, réplica — HACE FALTA SEGUIR DURMIENDO; NO REPLICADO por la letra (2026-10-27)

`results/mundo_propio_ninez_replica_run.txt`: pares 12–23.
- **Corrió en dos tramos.** El primero se cortó por falta de memoria en el
  sistema, con 9 de las 24 vidas escritas. El segundo las cargó del disco
  (`replica reanudar`) y corrió las 15 restantes en 19.7 min.
- Verificación: las 24 niñeces son iguales a las del §K7, con diferencia 0.

**Veredicto pre-registrado: HACE FALTA SEGUIR DURMIENDO.**
- **PERSISTE_N: 8/12** (H(T2) +0.18).
- **NIÑEZ: 7/12.**
- **EXILIO: 11/12.**
- ELIGE_N: 4/12. En T2, 16/24 gemelos se asientan en h.
- **El test había dado INDETERMINADO** (EXILIO 8/12). El veredicto no se repite:
  **NO REPLICADO** por la letra.
- **DAÑO 23/24 otra vez.** El oráculo de casa pasa de 0.005 a 0.110 en el primer
  bloque del exilio y queda congelado (20/24). `coin_sin_sueno` queda en 0.111.

**Sobre los 24 pares juntos** (tests de signo de una cola):

| Lectura | 24 pares |
|---|---|
| PERSISTE_N | 17/24 (p 0.03) |
| NIÑEZ | 15/24 (p 0.15) |
| EXILIO | 19/24 (p 0.003) |
| ELIGE_N | 8/24 |
| DAÑO | 46/48 gemelos |
| CONGELADO | 41/48 gemelos |

- En T2 se asientan en h 31/48 gemelos de `coin_ninez`, 32/48 de
  `coin_sin_sueno` y 46/48 de `coin`.

**Lectura del §K9 completo.**
- **Dormir sólo en la niñez no sostiene la identidad del repertorio.**
  - Juntando las dos corridas, el sueño posterior a la niñez suma en 19/24 pares.
  - El de la niñez sola no se distingue de no dormir nunca (15/24).
  - Por la letra, el test quedó INDETERMINADO y la réplica dio HACE FALTA SEGUIR
    DURMIENDO: el veredicto no se replicó.
- **Por qué: la precisión de la niñez no llega al exilio.**
  - El sueño de la niñez deja al experto de casa preciso (0.005).
  - Los primeros pasos del exilio, antes de la foto, lo llevan a 0.110–0.121.
    Es lo mismo que el experto que nunca durmió (0.111–0.131), y queda
    congelado ahí.
  - Al volver, el clon lo elige tan poco como si nunca hubiera dormido (31/48
    contra 32/48).
- **Lo que el sueño del exilio hace en `coin`: repara ese daño durante el mismo
  bloque** (0.005 → 0.006). No es sólo mantener; es deshacer lo que los primeros
  pasos del exilio le hacen al experto de casa.
- **La pregunta limpia ("¿alcanza un experto preciso y congelado?") no se pudo
  hacer.** El experto que se congela no es el de la niñez. Para hacerla, la foto
  tiene que tomarse antes de que el experto aprenda del exilio.
- **Predicciones fallidas:**
  - LA NIÑEZ SOSTIENE, EL RESTO SUMA (la escrita).
  - PERSISTE_N, NIÑEZ y ELIGE_N.
  - Acertó la nota del humo, escrita antes del test: el experto preciso es frágil
    a los primeros pasos del exilio.
  - La explicación de esa nota (Adam) no se probó.
- **Manos declaradas:**
  - EXILIO mide todo el sueño posterior a la niñez, también el de los ensayos
    Tm y T2.
  - No hubo calibración.
  - La réplica corrió en dos tramos.

**Lo que sigue abierto:**
- **La foto a tiempo.** Guardar los pesos de unos ticks antes y restaurar ésos
  al nacer el experto nuevo, en vez de la foto que se toma cuando el promedio
  móvil ya cruzó el umbral. Recién así se puede preguntar si alcanza un experto
  preciso y congelado (`coin_ninez` con la foto a tiempo), y si sin sueño
  alguno el repertorio conserva algo más.
- Si el daño es de Adam (pasos grandes para un experto preciso) o de la sola
  tasa de aprendizaje: un control con SGD, o con la tasa reducida en los
  primeros pasos de una racha.
- Lo que quedó del §K7 y del §K8: un umbral relativo, re-entrar más rápido,
  INVIERTE y un `self_embedding` que lea el modelo del mundo.

### §K10 — BASTA LA NIÑEZ por la letra; con la foto a tiempo, también la separación sola sostiene la identidad (2026-10-27)

`results/mundo_propio_foto_run.txt`: pares 0–11, 42.4 min.
- **Verificación.** Las niñeces sin restauración antes del exilio son iguales a
  las de referencia, con diferencia 0. Son 21/24 vidas de `coin_ninez_foto` y
  20/24 de `coin_sin_sueno_foto`. Las demás tuvieron una restauración en la
  niñez, y pueden diferir.

**Chequeo de la manipulación: pasa.**
- FOTO A TIEMPO en `coin_ninez_foto`: 22/24 gemelos. En `coin_sin_sueno_foto`:
  24/24.
- La foto restaurada tiene una antigüedad mediana de 86 y 98 ticks.
- El oráculo de casa de `coin_ninez_foto` queda en 0.005 al final de la niñez, en
  el primer bloque del exilio y en el último (CONGELADO 22/24). El DAÑO del §K9
  (0.005 → 0.121) desaparece.

**Veredicto pre-registrado: BASTA LA NIÑEZ.**
- **PERSISTE_F: 12/12,** con H(T2) +1.02. En `coin`, que duerme toda la vida,
  +0.69.
- **NIÑEZ_F: 10/12, en el umbral.**
- **RESTO_F: 5/12.** El sueño posterior a la niñez no suma.
- Secundarias:
  - REPARA_F: 12/12. La foto a tiempo rescata al `coin_ninez` del §K9 (+0.35).
  - ELIGE_F: 8/12. No pasa: en T2, 20/24 gemelos se asientan en h, con una
    latencia de 11 ticks.

**La sorpresa: la separación sola, con la foto a tiempo.**
- `coin_sin_sueno_foto`, que nunca duerme, PERSISTE en 10/12 (H(T2) +0.43).
- **ELIGE 12/12:** en T2 se asienta en h en 24/24 gemelos, con una latencia de
  21 ticks. Elige mejor que `coin_ninez_foto`.
- Sin foto a tiempo, en el §K8, eso daba 7/12 y 5/12.
- Su experto de casa queda intacto, impreciso (0.066) y congelado (24/24).
- **El veredicto del §K8 (POR EL SUEÑO: "separar no alcanza") se obtuvo con la
  foto atrasada.** Con la foto a tiempo, separar sí sostiene la identidad, más
  débil que con sueño en la niñez (+0.43 contra +1.02; NIÑEZ_F 10/12). Queda
  pendiente de la réplica.

**Costos en medianas.**

| Brazo | En casa T2 | Afuera T2 |
|---|---|---|
| `coin` | 0.146 | 0.489 |
| `coin_ninez` | 0.382 | 0.640 |
| `coin_ninez_foto` | 0.138 | 0.707 |
| `coin_sin_sueno` | 0.460 | 0.489 |
| `coin_sin_sueno_foto` | 0.222 | 0.489 |

- `coin_ninez_foto` vuelve a su casa tan bien como `coin` (0.138 contra 0.146).
- Le va peor en la casa del hermano (0.707 contra 0.489): sus clones de los
  ensayos Tm y T2 no duermen. Parte de su H(T2) mayor viene de ahí. Es una
  lectura, no un veredicto.

**Las predicciones, contra el resultado.**
- Acertadas:
  - FOTO A TIEMPO (22/24, no 24/24).
  - El DAÑO desaparece.
  - PERSISTE_F y NIÑEZ_F pasan; RESTO_F falla.
  - El veredicto BASTA LA NIÑEZ.
  - REPARA_F.
- Fallidas:
  - ELIGE_F (8/12).
  - "`coin_sin_sueno_foto` conserva intacto su experto": lo conserva, pero
    PERSISTE_SSF, que se daba por incierta, pasó (10/12).

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K10, réplica — REPLICADO: un experto preciso y congelado sostiene la identidad (2026-10-27)

`results/mundo_propio_foto_replica_run.txt`: pares 12–23, 52.8 min.
- Verificación: las niñeces sin restauración antes del exilio son iguales a las
  de referencia, con diferencia 0 (22/24 y 23/24 vidas).

**Veredicto pre-registrado: BASTA LA NIÑEZ. REPLICADO.**
- FOTO A TIEMPO: 21/24 (`coin_sin_sueno_foto`, 24/24). El oráculo de casa de
  `coin_ninez_foto` queda en 0.005 durante todo el exilio (CONGELADO 23/24).
- **PERSISTE_F: 11/12** (H(T2) +0.80; `coin`, +0.98).
- **NIÑEZ_F: 10/12**, en el umbral otra vez.
- **RESTO_F: 7/12.**
- Secundarias:
  - REPARA_F: 11/12.
  - ELIGE_F: 10/12. Pasa esta vez: 21/24 gemelos se asientan en h, con una
    latencia de 12 ticks.
  - PERSISTE_SSF: 9/12. No pasa por la letra (H(T2) +0.35).
  - ELIGE de `coin_sin_sueno_foto`: 10/12. En T2, 22/24 gemelos se asientan en h.
- Costos en T2: `coin_ninez_foto` en casa 0.141 y afuera 0.522; `coin`, 0.141 y
  0.611. El "peor afuera" del test no se repite.

**Sobre los 24 pares juntos** (tests de signo de una cola):

| Lectura | 24 pares |
|---|---|
| FOTO A TIEMPO (`coin_ninez_foto`) | 43/48 gemelos |
| PERSISTE_F | 23/24 |
| NIÑEZ_F | 20/24 (p 0.0008) |
| RESTO_F | 12/24 |
| REPARA_F | 23/24 |
| ELIGE_F | 18/24 (p 0.01) |
| PERSISTE_SSF (sin sueño, foto a tiempo) | 19/24 (p 0.003) |
| ELIGE de `coin_sin_sueno_foto` | 22/24 |

- En el §K8, con la foto atrasada, `coin_sin_sueno` daba PERSISTE 14/24 y
  ELIGE 12/24.

**Lectura del §K10 completo.**
- **Un experto de casa preciso y congelado sostiene la identidad.**
  - Restaurado a tiempo, el experto que durmió en la niñez queda preciso (0.005)
    y congelado durante todo el exilio.
  - Sin volver a dormir, los gemelos siguen distintos en 23/24 pares.
  - Al volver a casa eligen su experto en 18/24 pares y vuelven a su casa tan
    bien como el kernel que duerme toda la vida (en casa en T2: 0.138–0.141
    contra 0.141–0.146).
  - El sueño posterior a la niñez no suma (RESTO_F 12/24).
- **Lo que en el §K9 parecía "hace falta seguir durmiendo" era la foto
  atrasada.** El sueño del exilio en `coin` reparaba un daño que la foto a
  tiempo directamente evita.
- **El veredicto del §K8 queda acotado.** POR EL SUEÑO se obtuvo con la foto
  atrasada.
  - Con la foto a tiempo, la separación sola, sin dormir nunca, sostiene la
    identidad en 19/24 pares y elige en 22/24.
  - Es más débil: H(T2) +0.35–0.43, contra +0.80–1.02 con sueño en la niñez.
  - El sueño de la niñez suma (NIÑEZ_F 20/24), porque vuelve al experto
    preciso.
  - Lo que el §K8 replicó sigue en pie con la foto del §K6: sin sueño, la
    identidad queda al azar.
- **En una frase:** con una memoria por casa protegida a tiempo, la identidad es
  de la separación; el sueño de la niñez la hace más precisa, y dormir después
  no hace falta.
- **El hallazgo de medición.** El experto que duerme es preciso sólo justo
  después de cada sueño (`exp_mundo_propio_entre_suenos.py`: 0.004–0.006
  recién dormido, mediana 0.012 y hasta 0.215 entre sueños). En todos los loops
  del programa la sonda se toma al final del bloque (D = 300), y el kernel
  duerme cada 50 pasos, así que en los brazos que duermen cae justo después de un
  sueño. Esto se verificó en el código de los §K1–§K10; la erosión se midió sólo
  en el loop del §K4. Las lecturas de identidad (H) son de conducta y no
  dependen de eso.
- **Predicciones:**
  - Acertadas: el veredicto BASTA LA NIÑEZ, en las dos corridas; FOTO A TIEMPO;
    el DAÑO desaparece; REPARA_F.
  - Fallidas: ELIGE_F en el test (8/12); "PERSISTE_SSF incierta", que pasó
    juntando las corridas.
- **Manos declaradas:**
  - L = 50.
  - La regla de la foto se enmendó después del primer humo, antes de cualquier
    par de test.
  - Los clones de los ensayos Tm y T2 de `coin_ninez_foto` no duermen.
  - No hubo calibración.

**Lo que sigue abierto:**
- Llevar la foto a tiempo al `coin` completo y a la crianza `dos`: ¿cambia algo
  donde el sueño ya reparaba?
- Por qué el aprendizaje en línea erosiona tan rápido lo que el sueño consolidó
  (¿la conducta propia es un flujo estrecho y el aprendizaje en línea se
  sobreajusta a él?), y si una tasa menor en vigilia lo evita.
- Lo que quedó de antes: un umbral relativo, re-entrar más rápido, INVIERTE, y
  un `self_embedding` que lea el modelo del mundo.

### §K11 — PRECISA PERO LENTA por la letra; la vigilia lenta no borra, pero entra tarde a lo nuevo (2026-10-27)

`results/mundo_propio_vigilia_run.txt`: pares 0–11, 121.8 min (la máquina se
compartía con procesos de otra sesión).
- **Verificación.** Los 24 `coin` re-corridos son iguales a sus vidas del §K7 en
  las claves guardadas: diferencia máxima 0.0.

**Veredicto pre-registrado: PRECISA PERO LENTA**, el previsto.
- **EROSIONA (control): 12/12.** El oráculo de casa de `coin` pasa de 0.005,
  justo después de un sueño, a 0.042 despierto, 49 pasos en línea después.
- **PRECISA: 12/12.** En `coin_vigilia`, de 0.004 a 0.009.
- **PERSISTE_V: 12/12,** con H(T2) +1.70. En `coin`, +0.69.
- **LENTO: 12/12.** El primer bloque del exilio cuesta 0.970 contra 0.497.
- Secundarias:
  - PAREADO: 12/12 a favor de `coin_vigilia`; al revés, 0/12.
  - CONTROLA: 12/12. El `e_late` medio de la niñez baja de 0.038 a 0.034.
  - ELIGE: 12/12. En T2 se asientan en h los 24 gemelos, con una latencia de 8
    ticks (`coin`: 23/24, 11 ticks).

**Tampoco se erosiona el experto del exilio.** Al final del exilio, `coin` pasa
de 0.031 a 0.062 despierto; `coin_vigilia`, de 0.023 a 0.022.

**Costos en medianas.**

| Brazo | En casa T1 | Afuera T1 | En casa T2 | Afuera T2 | 1.er bloque del exilio |
|---|---|---|---|---|---|
| `coin` | 0.032 | 0.512 | 0.146 | 0.489 | 0.497 |
| `coin_vigilia` | 0.032 | 0.937 | 0.109 | 0.969 | 0.970 |

**Dónde cae el precio** (un análisis posterior de las mismas vidas; no es
evidencia pre-registrada).
- Los 31 bloques atascados de `coin_vigilia` están todos en el exilio: 23 en
  el primer bloque y 8 en el segundo. Ninguno en la niñez. `coin` tiene 2, los
  dos en el primer bloque del exilio.
- Desde el tercer bloque del exilio el `e_late` es el de `coin`: 0.033–0.036 en
  los dos brazos.
- En los ensayos, la casa del hermano también es un mundo nunca vivido, y
  cuesta 0.94–0.97 (`coin`: 0.49–0.51).
- **Buena parte del H mayor es ese precio.** En casa, en T2, `coin_vigilia` es
  algo mejor (0.109 contra 0.146), pero la diferencia grande está afuera (0.969
  contra 0.489). El PAREADO 12/12 mide tanto la identidad como la rigidez.

**Lectura.**
- La erosión del §K10 era el aprendizaje en línea con la tasa entera: con un
  paso diez veces más chico despierto, lo que el sueño consolida queda casi
  intacto hasta el sueño siguiente (0.009 contra 0.042).
- El costo es la entrada a lo nunca vivido: 300–600 ticks atascado, hasta que
  el sueño, cada 50 ticks, le enseña al experto nuevo lo que la vigilia ya no
  alcanza a aprender.
- Es el dilema estabilidad–plasticidad, medido dentro del kernel: una sola tasa
  despierta no da las dos cosas.

**Las predicciones, contra el resultado.**
- Acertadas: VERIFICACIÓN 24/24, EROSIONA, PRECISA, PERSISTE_V, LENTO y el
  veredicto PRECISA PERO LENTA.
- CONTROLA, que se daba por incierta, pasó 12/12.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K11, réplica — REPLICADO: la vigilia lenta no borra, y entra tarde a lo nuevo (2026-10-28)

`results/mundo_propio_vigilia_replica_run.txt`: pares 12–23, 122.8 min.
- **Verificación.** Los 24 `coin` re-corridos son iguales a sus vidas del §K7:
  diferencia máxima 0.0.

**Veredicto pre-registrado: PRECISA PERO LENTA. REPLICADO.**
- **EROSIONA: 12/12.** El oráculo de casa de `coin` pasa de 0.005 a 0.042
  despierto.
- **PRECISA: 12/12.** En `coin_vigilia`, de 0.004 a 0.009.
- **PERSISTE_V: 12/12,** con H(T2) +1.56. En `coin`, +0.98.
- **LENTO: 12/12.** El primer bloque del exilio cuesta 0.956 contra 0.601.
- Secundarias: PAREADO 12/12 (al revés, 0/12), CONTROLA 12/12 (0.035 contra
  0.038), ELIGE 12/12.
- El experto del exilio, al final: `coin` 0.025 → 0.055 despierto;
  `coin_vigilia` 0.021 → 0.023.
- Costos en T2: `coin_vigilia` en casa 0.121 y afuera 0.979; `coin`, 0.141 y
  0.611.

**Sobre los 24 pares juntos** (tests de signo de una cola; 24/24 = p 6 × 10⁻⁸):

| Lectura | 24 pares |
|---|---|
| EROSIONA (control) | 24/24 |
| PRECISA | 24/24 |
| PERSISTE_V | 24/24 |
| LENTO | 24/24 |
| PAREADO, CONTROLA, ELIGE | 24/24 cada una |

**Análisis posteriores sobre las 96 vidas** (no son evidencia pre-registrada).
- **Dónde cae el precio.** Los 59 bloques atascados de `coin_vigilia` caen todos
  en los dos primeros bloques del exilio (44 en el primero y 15 en el segundo),
  en 44/48 gemelos; ninguno en la niñez. `coin` tiene 3. Desde el tercer bloque
  del exilio, el `e_late` de los dos brazos es el mismo (0.034–0.040).
- **En casa, después del exilio, `coin_vigilia` vuelve mejor.** Es mejor que
  `coin` en 21/24 pares en Tm y en 19/24 en T2. En T1, antes del exilio, 11/24.
  Afuera, en la casa del hermano, es peor en 23–24/24.
- El H mayor tiene dos partes: una ventaja real al volver a casa, más chica, y
  la rigidez ante lo nunca vivido, más grande.

**Lectura del §K11 completo.**
- **La erosión entre sueños es el paso en línea con la tasa entera.** Con una
  vigilia diez veces más lenta, lo que el sueño consolida llega casi intacto al
  sueño siguiente: el oráculo de casa despierto baja de 0.042 a 0.009 en 24/24
  pares. Lo mismo pasa con el experto del exilio (0.055–0.062 → 0.022–0.023).
- **El kernel planea con un modelo más preciso y controla mejor lo conocido:**
  CONTROLA 24/24, aunque la diferencia es chica (0.034–0.035 contra 0.038).
- **La identidad se sostiene y elige siempre** (ELIGE 24/24). Vuelve a su casa
  mejor que `coin` después del exilio (21/24 y 19/24, posterior).
- **El precio es la entrada a lo nunca vivido.** Pasa 300–600 ticks atascado
  en el exilio, y se atasca también en la casa del hermano en los ensayos. El
  experto nuevo nace como copia del activo y aprende despierto a la décima
  parte; sólo el sueño, cada 50 ticks, lo saca.
- **En una frase:** una sola tasa despierta no da estabilidad y plasticidad a la
  vez. La vigilia lenta conserva y la rápida entra; el dilema
  estabilidad–plasticidad quedó medido dentro del kernel.
- **Predicciones:** acertadas todas, en las dos corridas: VERIFICACIÓN 48/48,
  EROSIONA, PRECISA, PERSISTE_V, LENTO y el veredicto PRECISA PERO LENTA.
  CONTROLA, que se daba por incierta, pasó 24/24.
- **Manos declaradas:**
  - s = 0.1, un solo valor; no se barrió.
  - La sonda despierta se toma un tick antes del último paso del bloque: 49
    pasos en línea después de un sueño.
  - Ninguno de los dos brazos usa `snapshot_lag`.
  - No hubo calibración.

**Lo que sigue abierto:**
- **Una tasa por experto,** el paso siguiente natural: tasa entera para el
  experto nuevo, que todavía no durmió, y tasa chica para el que ya consolidó.
  Predicción: conserva PRECISA y pierde LENTO, es decir, VIGILIA QUE NO BORRA.
  Es la idea de la metaplasticidad y de la consolidación sináptica.
- Combinar la vigilia lenta con la foto a tiempo del §K10.
- Por qué el aprendizaje en línea erosiona, más allá del tamaño del paso (¿la
  conducta propia es un flujo estrecho y el modelo se sobreajusta a él?): sigue
  sin probarse directamente.
- La foto a tiempo en el `coin` completo y bajo la crianza `dos`.
- Lo que quedó de antes: un umbral relativo, re-entrar más rápido, INVIERTE, y
  un `self_embedding` que lea el modelo del mundo.

### §K12 — VIGILIA QUE NO BORRA por la letra: lenta mientras explica, rápida mientras aprende (2026-10-28)

`results/mundo_propio_madurez_run.txt`: pares 0–11, 72.2 min (la máquina se
compartía con procesos de otra sesión).
- **Verificación.** El `coin_vigilia` re-corrido (par 0, gemelo A) es igual a su
  vida del §K11 en todas las claves: diferencia máxima 0.0.

**Veredicto pre-registrado: VIGILIA QUE NO BORRA.** Es mejor que lo previsto (MEJOR
PERO NO GRATIS).
- **PRECISA_M: 12/12.** El oráculo de casa despierto queda en 0.009, como en
  `coin_vigilia` (0.009); `coin`, 0.042.
- **ENTRA: 12/12.** El primer bloque del exilio cuesta 0.367 contra 0.970 de
  `coin_vigilia`.
- **PERSISTE_M: 12/12,** con H(T2) +0.375.
- **LENTO_M: 3/12.** No pasa: el primer bloque del exilio de `coin` cuesta 0.497.
- **Atascos: 0** en 24 gemelos (`coin` 2, `coin_vigilia` 31). El experto del
  exilio nace entre los 31 y los 35 ticks en los 24 gemelos.
- Secundarias:
  - CONTROLA: 12/12. El `e_late` medio de la niñez, 0.034 contra 0.038.
  - AFUERA: 12/12. La casa del hermano en T2 cuesta 0.387 contra 0.969 de
    `coin_vigilia`.
  - El oráculo despierto del experto del exilio al final: 0.028 contra 0.062 de
    `coin` (12/12). Tampoco se gasta.
  - ELIGE: 12/12. En T2 se asientan en h los 24 gemelos, con una latencia de 8
    ticks.
  - **PAREADO no pasa:** H(T2) mayor que el de `coin` en 3/12, que el de
    `coin_vigilia` en 0/12.
  - **VUELVE no pasa:** 3/12. En casa en T2 cuesta 0.168 contra 0.146.

**Costos en medianas.**

| Brazo | En casa T1 | Afuera T1 | En casa T2 | Afuera T2 | 1.er bloque del exilio | Atascos |
|---|---|---|---|---|---|---|
| `coin` | 0.032 | 0.512 | 0.146 | 0.489 | 0.497 | 2 |
| `coin_vigilia` | 0.032 | 0.937 | 0.109 | 0.969 | 0.970 | 31 |
| `coin_madurez` | 0.032 | 0.347 | 0.168 | 0.387 | 0.367 | 0 |

**Análisis posteriores de las mismas vidas** (no son evidencia pre-registrada).
- **Entra antes que `coin`.** El primer bloque del exilio es más barato que el de
  `coin` en 9/12 pares. Por bloque del exilio (`e_early`, medianas): `coin`
  0.497 → 0.044; `coin_vigilia` 0.970 → 0.611 → 0.056; `coin_madurez` 0.367 →
  0.042. Desde el segundo bloque, `coin_madurez` queda donde está `coin`.
- **La casa del hermano también le cuesta menos que a `coin`:** en 11/12 pares en
  T1, 10/12 en Tm y 9/12 en T2.
- **El H más chico es menos rigidez afuera, no una casa más débil.** En casa es
  mejor que `coin` en Tm (9/12) y peor en T2 (9/12); afuera es mejor en los tres
  ensayos.

**Lectura.**
- **La tasa que sigue a si el experto explica resuelve el dilema del §K11.** Lento
  mientras explica conserva lo que el sueño consolida (0.009, igual que la
  vigilia lenta). Rápido mientras aprende (recién nacido o fallando) entra a lo
  nunca vivido como `coin` o mejor, y sin atascarse nunca.
- **El precio del §K11 era de la tasa única, no de la vigilia lenta.**
- **Por qué funciona:** el aprendizaje rápido mientras falla el experto de casa
  queda protegido por la foto del §K6. Al nacer el experto del exilio, el de
  casa se restaura y lo aprendido pasa a la copia.
- **La identidad se sostiene** (PERSISTE_M 12/12, ELIGE 12/12), con menos ventaja
  de casa que `coin` porque el kernel es menos rígido afuera.
- **Lo que no salió:** VUELVE. Después del exilio, la casa en T2 queda algo peor
  que en `coin`.

**Las predicciones, contra el resultado.**
- Acertadas: VERIFICACIÓN, PRECISA_M, ENTRA y PERSISTE_M.
- Erradas:
  - LENTO_M, que se daba inclinada a pasar: 3/12.
  - El veredicto previsto, MEJOR PERO NO GRATIS: fue VIGILIA QUE NO BORRA. El
    gemelo B del humo, atascado, no era representativo: en el test no se atascó
    ninguno.
  - Los atascos, previstos entre los de `coin` y los de `coin_vigilia`: 0.
  - VUELVE, inclinada a pasar: 3/12.
- AFUERA, que se daba por incierta, pasó 12/12.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K12, réplica — REPLICADO: lenta mientras explica, rápida mientras aprende (2026-10-28)

`results/mundo_propio_madurez_replica_run.txt`: pares 12–23, 68.8 min.
- **Verificación.** El `coin_vigilia` re-corrido (par 12, gemelo A) es igual a su
  vida del §K11: diferencia máxima 0.0.

**Veredicto pre-registrado: VIGILIA QUE NO BORRA. REPLICADO.**
- **PRECISA_M: 12/12.** El oráculo de casa despierto queda en 0.008; `coin`,
  0.042.
- **ENTRA: 12/12.** El primer bloque del exilio cuesta 0.348 contra 0.956 de
  `coin_vigilia`.
- **PERSISTE_M: 12/12,** con H(T2) +0.468.
- **LENTO_M: 1/12.** No pasa: el primer bloque del exilio de `coin` cuesta 0.601.
- **Atascos: 1** en 24 gemelos (`coin` 1, `coin_vigilia` 28).
- Secundarias:
  - CONTROLA 12/12 (0.034 contra 0.038).
  - AFUERA 12/12 (la casa del hermano en T2, 0.396 contra 0.979).
  - El oráculo despierto del experto del exilio al final: 11/12 (0.031 contra
    0.055).
  - ELIGE 12/12.
  - **No pasan:** PAREADO, 1/12 contra `coin` y 0/12 contra `coin_vigilia`, y
    VUELVE, 4/12 (en casa en T2, 0.163 contra 0.141).

**Sobre los 24 pares juntos** (tests de signo de una cola; 24/24 = p 6 × 10⁻⁸):

| Lectura | Test | Réplica | 24 pares |
|---|---|---|---|
| PRECISA_M | 12/12 | 12/12 | 24/24 |
| ENTRA | 12/12 | 12/12 | 24/24 |
| PERSISTE_M | 12/12 | 12/12 | 24/24 |
| LENTO_M | 3/12 | 1/12 | 4/24 |
| PAREADO (contra `coin` / `coin_vigilia`) | 3/12 / 0/12 | 1/12 / 0/12 | 4/24 / 0/24 |
| CONTROLA | 12/12 | 12/12 | 24/24 |
| VUELVE | 3/12 | 4/12 | 7/24 |
| AFUERA | 12/12 | 12/12 | 24/24 |
| Oráculo del experto del exilio al final | 12/12 | 11/12 | 23/24 |
| ELIGE | 12/12 | 12/12 | 24/24 |

**Costos en medianas, 24 pares.**

| Brazo | En casa T1 | Afuera T1 | En casa T2 | Afuera T2 | 1.er bloque del exilio | H(T2) | Atascos |
|---|---|---|---|---|---|---|---|
| `coin` | 0.032 | 0.526 | 0.145 | 0.523 | 0.560 | +0.788 | 3 |
| `coin_vigilia` | 0.032 | 0.937 | 0.115 | 0.977 | 0.959 | +1.664 | 59 |
| `coin_madurez` | 0.032 | 0.338 | 0.165 | 0.396 | 0.367 | +0.412 | 1 |

- El único atasco de `coin_madurez` es del par 14, gemelo A, en el primer bloque
  del exilio (`e_late` 0.593). Es el par en que su primer bloque cuesta más que el
  de `coin` (0.672 contra 0.659).
- El experto del exilio nace entre los 31 y los 35 ticks en los 48 gemelos.

**Análisis posteriores sobre las 72 vidas** (no son evidencia pre-registrada).
- **Entra antes que `coin`:** el primer bloque del exilio es más barato en 20/24
  pares (p 8 × 10⁻⁴ en esa dirección, que no se registró). Por bloque del exilio
  (`e_early`, medianas): `coin` 0.560 → 0.044 → 0.037; `coin_vigilia` 0.959 →
  0.544 → 0.055; `coin_madurez` 0.367 → 0.042 → 0.038. Desde el segundo bloque,
  igual que `coin`.
- **Afuera es mejor que `coin` en los tres ensayos:** 22/24 en T1, 19/24 en Tm y
  20/24 en T2.
- **En casa,** igual en T1 (0.032 los dos, 12/24), mejor en Tm (18/24) y peor en
  T2 (17/24 peor; 0.165 contra 0.145).
- **El experto de casa llega intacto al final del exilio.** El mejor experto para
  la casa de cada gemelo (el oráculo, despierto) cuesta 0.006–0.007 al final del
  exilio en los tres brazos. Entonces el costo de VUELVE no es un experto de casa
  dañado: está en la vuelta misma, en los primeros ticks en casa. Hay que
  instrumentarla para saber qué experto actúa y a qué tasa aprende en esos
  ticks.
- **El H más chico tiene dos partes.** La mayor es menos rigidez afuera (20/24).
  La menor, una vuelta a casa algo más cara en T2 (17/24). Esto corrige la lectura
  del test, que con 12 pares atribuía todo a lo de afuera.

**Lectura del §K12 completo.**
- **Una tasa despierta por experto da estabilidad y plasticidad a la vez,** en
  24/24 pares. El experto aprende lento mientras explica su flujo y rápido
  mientras es nuevo o está fallando. Así conserva lo que el sueño consolida, igual
  que la vigilia lenta (0.009 contra 0.042), y entra a lo nunca vivido mejor que
  `coin` (0.367 contra 0.560), con un atasco en 48 gemelos.
- **El dilema del §K11 era de la tasa única,** no de la vigilia lenta.
- **Por qué funciona:** el aprendizaje rápido mientras el experto de casa falla
  queda protegido por la foto del §K6. Al nacer el experto del exilio, el de casa
  se restaura a sus pesos de antes de la racha, y lo aprendido pasa a la copia.
  Por eso aprender rápido mientras falla no cuesta nada: el experto de casa
  termina el exilio a 0.007.
- **La identidad se sostiene** (PERSISTE_M 24/24, ELIGE 24/24), con la mitad de
  ventaja de casa que `coin` (+0.41 contra +0.79), sobre todo porque el kernel es
  menos rígido afuera.
- **Lo que no salió:** VUELVE (7/24). Después del exilio, la vuelta a casa cuesta
  algo más que en `coin`, y bastante más que en `coin_vigilia` (0.115).
- **Predicciones,** en las dos corridas:
  - Acertadas: VERIFICACIÓN 2/2, PRECISA_M, ENTRA y PERSISTE_M.
  - Erradas: LENTO_M, que se daba inclinada a pasar (4/24); el veredicto previsto,
    MEJOR PERO NO GRATIS; VUELVE, inclinada a pasar (7/24); y los atascos,
    previstos entre los de `coin` y los de `coin_vigilia` (1, menos que los 3 de
    `coin`).
  - AFUERA, que se daba por incierta, pasó 24/24.
- **Manos declaradas:**
  - s = 0.1 y s_l = 1.0, un solo valor cada una; no se barrieron.
  - El criterio de "explica" usa el mismo umbral que el cambio de contexto: el
    experto está establecido y su error corriente no pasa el umbral.
  - Ningún brazo usa `snapshot_lag`.
  - `coin` y `coin_vigilia` no se re-corrieron: se cargaron del §K11, con una vida
    re-corrida por corrida como verificación (diferencia 0 en las dos).
  - El primer diseño (tasa rápida sólo para el experto no establecido) se
    descartó después del humo y antes del pre-registro; está registrado.
  - No hubo calibración.

**Lo que sigue abierto:**
- **La vuelta a casa (VUELVE).** El experto de casa está intacto y la vuelta igual
  cuesta más que en `coin`. Paso siguiente: instrumentar los primeros ticks de T2
  (qué experto actúa, si "explica", a qué tasa aprende, cuánto tarda el cambio).
- Combinar la madurez con la foto a tiempo del §K10.
- La madurez bajo la crianza `dos`.
- Lo que quedó de antes: un umbral relativo o una inferencia bayesiana del
  contexto, INVIERTE, y un `self_embedding` que lea el modelo del mundo.

### §K12, mecanismo — la vuelta a casa: el experto de casa vuelve intacto y se daña reaprendiendo despierto (2026-10-28)

`experiments/kernel/exp_mundo_propio_madurez_vuelta.py`,
`results/mundo_propio_madurez_vuelta_run.txt`: posterior al test y a la réplica, 47.7
min. No es evidencia pre-registrada. La hipótesis y las predicciones quedaron escritas
en el docstring antes de correr.

**De dónde salió.** En las vidas guardadas (los 24 pares), en el ensayo de casa de T2
`coin_madurez` vuelve a su experto de casa `h` antes que `coin` (9 contra 12 ticks) y
paga menos hasta ese momento (0.054 contra 0.082). Pero paga más **después** (0.114
contra 0.064; ticks 20–40, 0.180 contra 0.070; 21/24 pares). `coin_vigilia` paga 0.034
en esa ventana.

**Qué se hizo.** Se re-corrieron 16 vidas: `coin` y `coin_madurez`, pares 0–3, los dos
gemelos. Los pares se eligieron sin mirar; en las vidas guardadas muestran el efecto
en 4/4. En los ensayos de casa Tm y T2 se lanzaron clones extra desde el mismo estado
y con la misma semilla:
- `instr`: lecturas tick a tick (experto activo, errores corrientes, si `h` explica).
- `sonda`: además, el error propio de `h` en la sonda de casa en ticks fijos.
- `lento_h`: `h` aprende despierto a lr × 0.1. Los demás expertos siguen la regla de su
  brazo.
- `congelado_h`: `h` no aprende despierto (lr × 0); sigue durmiendo.
- **Verificación.** Las 16 vidas dan diferencia 0 contra las guardadas. `instr`
  reproduce el ensayo guardado (0.0) y la sonda sólo lee (0.0).
- **Enmienda después del humo, antes de correr.** La primera versión de los
  contrafactuales pisaba `_explica` para todos los expertos. En `coin_madurez` eso
  ponía también al experto del exilio a tasa entera desde el primer tick en casa, y
  el cambio de experto en Tm se movía de 33 a 15 ticks. Se corrigió para que sólo
  cambie la tasa de `h`.

**Resultado en T2** (medianas de 8 gemelos por brazo).

| | `coin` | `coin_madurez` |
|---|---|---|
| Cambio a `h` (tick) | 12 | 8 |
| Error corriente de `h` al cambiar (umbral 0.08) | 0.105; arriba en 6/8 | 0.093; arriba en 7/8 |
| Costo antes del cambio | 0.087 | 0.046 |
| Costo después del cambio: `instr` | 0.058 | 0.083 |
| Costo después del cambio: `lento_h` | 0.055 | 0.055 |
| Costo después del cambio: `congelado_h` | 0.053 | 0.055 |
| Error propio de `h` en casa, ticks 0 → 20 → 40 → 50 | 0.008 → 0.059 → 0.090 → 0.011 | 0.007 → 0.157 → 0.230 → 0.010 |
| Lo mismo con `lento_h`, tick 40 | 0.013 | 0.017 |
| Lo mismo con `congelado_h` | 0.008 en todo el ensayo | 0.007 en todo el ensayo |

- En `coin_madurez`, `lento_h` baja el costo después del cambio en 7/8 gemelos y
  `congelado_h` en 6/8. En `coin`, 7/8 los dos.
- En Tm pasa lo mismo. El error propio de `h` en `coin_madurez` sube de 0.007 a 0.106,
  y los dos contrafactuales bajan el costo después del cambio en 7/8.

**Lectura.**
- **El experto de casa vuelve intacto y se daña al volver.** Despierto, aprende en
  línea de los primeros ticks en casa, y eso le multiplica el error en casa por 10–30
  en 20–40 ticks, hasta que el sueño del tick 50 lo repara. Lento o congelado
  despierto, no se daña, y el costo extra desaparece: `coin_madurez` queda en 0.055
  después del cambio, por debajo de `coin` (0.058). Con el experto de casa protegido,
  su costo en casa en T2 sería 0.105 contra 0.147 de `coin`. Es una cuenta sobre 8
  gemelos, no una corrida.
- **Por qué aprende rápido justo ahí.** Todos los expertos predicen en cada tick, así
  que el error corriente de `h` llega a casa cargado con el exilio, y el cambio de
  experto es relativo (por margen), no por el umbral. Al reactivarse, `h` no "explica"
  (7/8 gemelos arriba del umbral) y la madurez le da la tasa entera. En eso la
  hipótesis escrita antes de correr se confirma.
- **Pasa también en `coin`, pero menos.** `coin` aprende siempre a tasa entera y su
  experto de casa también se daña (0.090 a los 40 ticks); congelarlo le baja el costo
  en 7/8 gemelos.
- **En `coin_madurez` el daño es mayor y se concentra en la mitad de los gemelos,**
  con costos después del cambio de 0.10 a 0.35.
  - En 3 de ellos, `h` pasa 43–92 ticks seguidos sin explicar; en `coin`, 12 como
    mucho.
  - El cuarto (par 2, gemelo A) llega a 0.353 con un primer tramo de un tick. Sólo se
    midió el primer tramo sin explicar, no las recaídas.
- **Lo que no se probó:** por qué el daño es mayor en `coin_madurez` que en `coin` a la
  misma tasa entera. Hay dos candidatos sin probar:
  - el cambio más temprano le pasa a `h` el pico del transitorio (ticks 5–10, a 0.8–0.9
    de la preferencia);
  - un lazo en el que el daño mantiene el error arriba del umbral y la tasa entera
    sigue.
- **La foto no lo protege** (lectura del código, no medida). Al reactivarse con el
  error arriba del umbral se toma una foto de `h`. Pero esa foto se descarta sin
  restaurar cuando el error corriente baja del umbral; sólo un nuevo cambio o un
  nacimiento la restaurarían.
- **Predicciones:**
  - Acertadas: el error de `h` por arriba del umbral al cambiar en la mayoría (6/8 y
    7/8), y que los dos contrafactuales bajan el costo de `coin_madurez` después del
    cambio (7/8 y 6/8).
  - Lo que no se predijo: el tamaño del daño (×30) y que también aparezca en `coin`.

**Lo que sigue (propuesta de §K13): proteger al experto que vuelve.** Opciones, de la
más simple a la más fina:
- (a) Un experto establecido que se reactiva aprende despierto lento durante una
  gracia, o hasta que su error lo justifique. Es lo que hace `lento_h`.
- (b) El "explica" se decide con un error corriente que sólo cuenta los ticks en que el
  experto estuvo activo, guardado y restaurado con su foto.
- (c) La racha que empieza en una reactivación restaura la foto si el error de la sonda
  propia sube.

### §K13 — VUELVE A CASA por la letra: el experto que vuelve, protegido, ya no se daña (2026-10-28)

`results/mundo_propio_regreso_run.txt`: pares 0–11.
- **Corrió en dos tramos.** El sistema cortó el primero por falta de memoria, con 3
  vidas en disco (la máquina se compartía con procesos de otras sesiones). `reanudar`
  corrió las 22 restantes en 53.8 min.
- **Verificación.** El `coin_madurez` re-corrido (par 0, gemelo A) es igual a su vida
  del §K12 en todas las claves: diferencia máxima 0.0.
- **MISMA VIDA: 24/24 gemelos.** La vida principal de `coin_regreso` es la de
  `coin_madurez`, también en los dos gemelos cuya vida principal tiene cambios de
  experto (par 3 B, con 18, y par 8 A, con 6). Los brazos se distinguen sólo en los
  clones de los ensayos.

**Veredicto pre-registrado: VUELVE A CASA,** el previsto.
- **PROTEGE: 12/12.** La casa en T2 cuesta 0.117 contra 0.168 de `coin_madurez`.
- **VUELVE_R: 11/12.** Contra 0.146 de `coin` (`coin_vigilia`, 0.109).
- **CONSERVA_R: 12/12 y 12/12.** El oráculo de casa despierto (0.009) y el primer
  bloque del exilio (0.367) son los de `coin_madurez`, porque la vida principal es la
  misma.
- **PERSISTE_R: 12/12,** con H(T2) +0.567 (`coin_madurez` +0.375, `coin` +0.685).
- **RIGIDO_R: no pasa.** Afuera es peor que en `coin_madurez` en 3/12 pares en T1 y en
  1/12 en T2.
- Secundarias:
  - RECUPERA 12/12: después del cambio a `h` en T2 cuesta 0.054, contra 0.122 de
    `coin_madurez` y 0.061 de `coin`.
  - PAREADO: H(T2) mayor que el de `coin_madurez` en 12/12; que el de `coin`, en
    5/12.
  - AFUERA 12/12. La casa en Tm, 11/12 (0.113 contra 0.128). ELIGE 12/12. Atascos: 0.

**Costos en medianas.**

| Brazo | En casa T1 | Afuera T1 | En casa Tm | En casa T2 | Afuera T2 | Después del cambio, T2 | H(T2) |
|---|---|---|---|---|---|---|---|
| `coin` | 0.032 | 0.512 | 0.161 | 0.146 | 0.489 | 0.061 | +0.685 |
| `coin_vigilia` | 0.032 | 0.937 | 0.126 | 0.109 | 0.969 | 0.064 | +1.703 |
| `coin_madurez` | 0.032 | 0.347 | 0.128 | 0.168 | 0.387 | 0.122 | +0.375 |
| `coin_regreso` | 0.032 | 0.347 | 0.113 | 0.117 | 0.387 | 0.054 | +0.567 |

**Por par** (análisis posterior de las mismas vidas):
- **Después del cambio,** `coin_regreso` cuesta 0.049–0.060 en los 12 pares;
  `coin_madurez`, 0.055–0.335.
- **El par que falla VUELVE_R** (el 11: 0.185 contra 0.134) lo pierde antes del cambio,
  no después.
- **El precio son tres gemelos en la casa del hermano en T1,** uno en cada uno de los
  pares 4, 7 y 10: los que vuelven a `h` ahí. Cuestan 0.642, 0.755 y 0.773, contra
  0.425, 0.441 y 0.661. En el resto, la casa del hermano cuesta exactamente lo mismo
  que en `coin_madurez`.

**Lectura.**
- **Proteger al experto que vuelve arregla la vuelta a casa sin tocar nada más.** La
  vida principal es la misma; lo único que cambia es que, al volver, el experto de casa
  no reaprende a tasa entera. Después del cambio cuesta lo que cuesta un experto
  intacto (0.054), y la casa en T2 queda mejor que en `coin` (11/12) y cerca de
  `coin_vigilia`.
- **El kernel tiene ahora las tres cosas en el mismo brazo:**
  - conserva lo que el sueño consolida (0.009, como la vigilia lenta);
  - entra a lo nunca vivido mejor que `coin` (0.367, sin atascos);
  - vuelve a casa mejor que `coin`.
- **El precio es chico y está localizado:** cuando el clon vuelve al experto de casa
  en un mundo que no es el suyo, lo sostiene lento hasta 30 ticks. Pasa en 3 de 24
  gemelos.
- **La identidad crece:** H(T2) pasa de +0.375 a +0.567, todo por una casa mejor
  (afuera queda igual). Sigue por debajo de la de `coin` en 7/12 pares, porque `coin`
  es más rígido afuera.

**Las predicciones, contra el resultado.**
- Acertadas:
  - VERIFICACIÓN, MISMA VIDA (incluso en los dos gemelos con cambios), CONSERVA_R,
    PERSISTE_R, PROTEGE y VUELVE_R.
  - RIGIDO_R, que no pasa.
  - El veredicto VUELVE A CASA.
  - En las secundarias: RECUPERA, PAREADO (pasa contra `coin_madurez` y no contra
    `coin`), AFUERA, la casa en Tm, ELIGE y los atascos.
- Ninguna errada en este test.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K13, réplica — REPLICADO: el experto que vuelve, protegido, ya no se daña (2026-10-28)

`results/mundo_propio_regreso_replica_run.txt`: pares 12–23, 58.1 min, en un solo tramo.
- **Verificación.** El `coin_madurez` re-corrido (par 12, gemelo A) es igual a su vida
  del §K12: diferencia máxima 0.0.
- **MISMA VIDA: 23/24 gemelos,** y 23/23 de los que no tienen cambios de experto en la
  vida principal. El que difiere es el par 14, gemelo A, el del único atasco del §K12.
  En `coin_madurez` su vida principal salta entre expertos en el primer bloque del
  exilio (6 cambios); con `slow_return`, 2. El atasco del primer bloque es el mismo
  (`e_late` 0.593 y 0.612), pero el segundo bloque arranca en 0.065 contra 0.38
  (`e_early`).

**Veredicto pre-registrado: VUELVE A CASA. REPLICADO.**
- **PROTEGE: 12/12.** La casa en T2 cuesta 0.105 contra 0.163 de `coin_madurez`.
- **VUELVE_R: 11/12.** Contra 0.141 de `coin` (`coin_vigilia`, 0.121).
- **CONSERVA_R: 12/12 y 12/12.** El oráculo de casa despierto queda en 0.008 (`coin`,
  0.042) y el primer bloque del exilio en 0.348 (`coin_vigilia`, 0.956).
- **PERSISTE_R: 12/12,** con H(T2) +0.594 (`coin_madurez` +0.468, `coin` +0.983).
- **RIGIDO_R: no pasa.** Afuera es peor que en `coin_madurez` en 3/12 pares en T1 y en
  2/12 en T2.
- Secundarias:
  - RECUPERA 11/12: después del cambio a `h` en T2 cuesta 0.059, contra 0.106 de
    `coin_madurez` y 0.065 de `coin`.
  - PAREADO: H(T2) mayor que el de `coin_madurez` en 12/12; que el de `coin`, en
    2/12.
  - AFUERA 12/12. La casa en Tm, 10/12 (0.120 contra 0.126). ELIGE 12/12.
  - Atascos: 1, el mismo de `coin_madurez` (par 14 A, primer bloque del exilio).

**Por par** (análisis posterior de las mismas vidas):
- **Después del cambio,** `coin_regreso` cuesta 0.051–0.067 en los 12 pares;
  `coin_madurez`, 0.049–0.193.
- **El par que falla VUELVE_R** (el 15: 0.191 contra 0.150) lo pierde, otra vez, antes
  del cambio. Su gemelo A vuelve a `h` tarde, en el tick 28, y cuesta lo mismo en los
  dos brazos (0.281 contra 0.278).
- **El par que falla RECUPERA** (el 14: 0.054 contra 0.049) es uno en que
  `coin_madurez` ya volvía al nivel de un experto intacto.
- **El precio afuera,** gemelo por gemelo:
  - En T1, tres gemelos: 17 B (0.486 → 0.681), 18 B (0.771 → 0.814) y 20 A
    (0.341 → 0.594). Empiezan en `h`, lo dejan, vuelven a él y lo sostienen lento.
  - En T2, dos: 13 B (0.625 → 0.889), que vuelve a `h` en el tick 9 y se queda ahí 91
    de los 100 ticks (en `coin_madurez`, 20), y 14 A (0.238 → 0.365), que nunca pasa
    por `h`: es el gemelo cuya vida principal difiere.
  - En Tm, que no es una lectura de la regla, dos peores (21 A, 0.484 → 0.566; 23 A,
    0.661 → 0.916) y uno mejor (14 A, 0.455 → 0.344).
- **Corrección al test.** La entrada del test dice que, fuera de los tres gemelos de
  T1, la casa del hermano cuesta exactamente lo mismo. Es falso: había un cuarto, en
  T2, el par 5 B, que vuelve a `h` en el tick 81 y cuesta 0.742 contra 0.698. Es el
  1/12 de RIGIDO_R en T2. El docstring quedó corregido.

**Sobre los 24 pares juntos** (tests de signo de una cola; 24/24 = p 6 × 10⁻⁸):

| Lectura | Test | Réplica | 24 pares |
|---|---|---|---|
| PROTEGE | 12/12 | 12/12 | 24/24 |
| VUELVE_R | 11/12 | 11/12 | 22/24 |
| CONSERVA_R (oráculo / exilio) | 12/12 / 12/12 | 12/12 / 12/12 | 24/24 / 24/24 |
| PERSISTE_R | 12/12 | 12/12 | 24/24 |
| RIGIDO_R (T1 / T2) | 3/12 / 1/12 | 3/12 / 2/12 | 6/24 / 3/24 |
| RECUPERA | 12/12 | 11/12 | 23/24 |
| PAREADO (contra `coin_madurez` / `coin`) | 12/12 / 5/12 | 12/12 / 2/12 | 24/24 / 7/24 |
| AFUERA | 12/12 | 12/12 | 24/24 |
| Casa en Tm, contra `coin_madurez` | 11/12 | 10/12 | 21/24 |
| ELIGE | 12/12 | 12/12 | 24/24 |
| MISMA VIDA (gemelos) | 24/24 | 23/24 | 47/48 |

**Costos en medianas, 24 pares.**

| Brazo | En casa T1 | Afuera T1 | En casa Tm | En casa T2 | Afuera T2 | Después del cambio, T2 | 1.er bloque del exilio | H(T2) | Atascos |
|---|---|---|---|---|---|---|---|---|---|
| `coin` | 0.032 | 0.526 | 0.159 | 0.145 | 0.523 | 0.064 | 0.560 | +0.788 | 3 |
| `coin_vigilia` | 0.032 | 0.937 | 0.120 | 0.115 | 0.977 | 0.063 | 0.959 | +1.664 | 59 |
| `coin_madurez` | 0.032 | 0.338 | 0.128 | 0.165 | 0.396 | 0.114 | 0.367 | +0.412 | 1 |
| `coin_regreso` | 0.032 | 0.351 | 0.117 | 0.111 | 0.402 | 0.056 | 0.367 | +0.567 | 1 |

**Análisis posteriores sobre los 24 pares** (no son evidencia pre-registrada):
- **Después del cambio,** el experto de casa de `coin_regreso` cuesta menos que el de
  `coin` en 21/24 pares y que el de `coin_vigilia` en 19/24.
- **La casa en T2** queda al nivel de la vigilia lenta: 0.111 contra 0.115, mejor en
  14/24 pares.
- **El precio afuera:** 9 de los 96 ensayos de un gemelo en la casa del hermano (48
  gemelos, T1 y T2) cuestan más que en `coin_madurez`, y ninguno menos. Ocho son
  gemelos que sostienen a `h` lento en la casa del hermano (6 en T1, 2 en T2); el
  noveno es el 14 A, cuya vida principal difiere. Los otros 87 cuestan exactamente lo
  mismo.

**Lectura del §K13 completo.**
- **Proteger al experto que vuelve arregla la vuelta a casa, sin perder nada de lo del
  §K12.** La vuelta en T2 es mejor que en `coin_madurez` en 24/24 pares y que en `coin`
  en 22/24. Los dos pares que fallan contra `coin` (el 11 y el 15) lo pierden antes del
  cambio, por una vuelta tardía a `h`, no después. Lo del §K12 queda entero: la vida
  principal es la misma en 47/48 gemelos, y CONSERVA_R pasa 24/24 y 24/24.
- **Después del cambio, el experto de casa cuesta lo que cuesta uno intacto** (0.056,
  contra 0.114 sin protección). El daño que encontró el mecanismo del §K12 era eso:
  reaprender despierto a tasa entera al volver. Sacado eso, el costo extra de la
  vuelta desaparece.
- **El kernel tiene las tres cosas en el mismo brazo,** en 24 pares:
  - conserva lo que el sueño consolida, como la vigilia lenta (0.009);
  - entra a lo nunca vivido mejor que `coin` (0.367 contra 0.560), con un atasco en
    48 gemelos;
  - vuelve a casa mejor que `coin` y al nivel de la vigilia lenta (0.111 contra 0.145
    y 0.115).
- **El precio es chico, localizado y medido:** 9 de 96 ensayos afuera. Es el gemelo
  que, en un mundo que no es el suyo, vuelve a su experto de casa y lo sostiene lento
  hasta 30 ticks, porque ese experto no llega a explicar un flujo ajeno. El tope de
  `persist` lo acota; no lo elimina.
- **Un efecto que no se buscó:** en el gemelo 14 A, la protección también vale para el
  experto del exilio cuando vuelve a él dentro del exilio. Deja de saltar entre
  expertos, y su segundo bloque del exilio arranca en 0.065 contra 0.38.
- **La identidad crece** de +0.412 a +0.567 (24/24), por una casa mejor: afuera queda
  casi igual. Sigue por debajo de la de `coin` en 17/24 pares, porque `coin` es más
  rígido afuera.

**Las predicciones, contra el resultado,** en las dos corridas:
- Acertadas:
  - VERIFICACIÓN 2/2, y MISMA VIDA en todo gemelo sin cambios en la vida principal
    (45/45).
  - CONSERVA_R, PERSISTE_R, PROTEGE y VUELVE_R.
  - RIGIDO_R, que no pasa.
  - El veredicto VUELVE A CASA.
  - En las secundarias: RECUPERA, PAREADO (pasa contra `coin_madurez` y no contra
    `coin`), AFUERA, la casa en Tm, ELIGE y los atascos (los de `coin_madurez`).
- Ninguna errada.

**Manos declaradas:**
- s = 0.1 y s_l = 1.0, las del §K12, y el tope en `persist` = 30 ticks, la paciencia
  del modelo antes de un contexto nuevo. Un solo valor cada uno; no se barrieron.
- "Volver" es un cambio a un experto establecido; un nacimiento no lo es. "Explicar"
  usa el mismo umbral que el cambio de contexto, como en el §K12.
- Ningún brazo usa `snapshot_lag`.
- `coin` y `coin_vigilia` se cargaron del §K11 y `coin_madurez` del §K12, sin
  re-correrlos, con una vida re-corrida por corrida como verificación (diferencia 0 en
  las dos).
- El primer diseño, sin tope, se descartó después del humo y antes del pre-registro;
  está registrado.
- El test corrió en dos tramos: el sistema cortó el primero por falta de memoria.
- No hubo calibración.

**Lo que sigue abierto:**
- **El precio afuera.** Un experto que vuelve a un mundo ajeno se sostiene lento hasta
  30 ticks. El experto de casa protegido explicaba su flujo en una mediana de 3–4
  ticks (mecanismo del §K12), así que un tope más corto, o uno relativo a ese tiempo,
  podría achicar el precio sin tocar la vuelta.
- **Por qué el daño era mayor en `coin_madurez` que en `coin`** (0.23 contra 0.09 a
  los 40 ticks en el mecanismo).
- La madurez y el regreso con la foto a tiempo del §K10, y bajo la crianza `dos`.
- Lo que quedó de antes: un umbral relativo o una inferencia bayesiana del contexto,
  INVIERTE, y un `self_embedding` que lea el modelo del mundo.

### §K14 — NO AGUANTA: ENTRA_D por la letra; la escuela le da a `coin` la entrada que daba el brazo (2026-10-28)

`results/mundo_propio_escuela_run.txt`: pares 0–11.
- **Corrió en dos tramos.** El sistema cortó el primero por falta de memoria, con 18
  vidas en disco (la máquina se compartía con procesos de otras sesiones). `reanudar`
  corrió las 30 restantes en 80.9 min.
- **Verificación: 24/24.** Cada `coin` re-corrido es igual a su vida del §K7 bajo
  `dos` en todas las claves guardadas: diferencia máxima 0.0.

**Veredicto pre-registrado: NO AGUANTA: ENTRA_D,** el previsto después de la
calibración.
- **CONSERVA_D: 12/12.** El oráculo de casa despierto queda en 0.015, contra 0.046 de
  `coin` (recién dormidos, 0.012 y 0.013; EROSIONA 12/12).
- **ENTRA_D: 7/12.** El primer bloque del exilio cuesta 0.285 contra 0.327.
- **VUELVE_D: 11/12.** La casa en T2 cuesta 0.145 contra 0.203.
- **PERSISTE_D: 12/12,** con H(T2) +0.663 (`coin`, +0.464).
- **RIGIDO_D: no pasa.** Afuera es peor que en `coin` en 5/12 pares en T1 y en 4/12 en
  T2.
- Secundarias:
  - NINEZ_D 6/12 y ESCUELA_D 5/12: las vueltas de la niñez cuestan lo mismo en los dos
    brazos (0.116 contra 0.118 a casa, 0.124 contra 0.125 a la escuela).
  - La casa en Tm, 8/12 (0.148 contra 0.217). AFUERA 8/12. RECUPERA 8/12 (después del
    cambio a `h` en T2, 0.056 contra 0.067). PAREADO 6/12.
  - ELIGE 12/12 en los dos brazos. Atascos: 0 bloques en `coin_regreso`, 1 en `coin`.
- El oráculo al final del exilio, despierto: 0.031 contra 0.075.

**Costos en medianas.**

| Brazo | En casa T1 | Afuera T1 | En casa Tm | En casa T2 | Afuera T2 | Primer bloque del exilio | Después del cambio, T2 | H(T2) |
|---|---|---|---|---|---|---|---|---|
| `coin` | 0.033 | 0.510 | 0.217 | 0.203 | 0.432 | 0.327 | 0.067 | +0.464 |
| `coin_regreso` | 0.036 | 0.422 | 0.148 | 0.145 | 0.477 | 0.285 | 0.056 | +0.663 |

**Por par** (análisis posterior de las mismas vidas, junto con las de los mismos pares
bajo `una`: `coin` del §K11 y `coin_regreso` del §K13).
- **Lo que cambia es `coin`.** Bajo `dos` entra al exilio mejor que bajo `una` en los
  12 pares (0.327 contra 0.497). `coin_regreso` también mejora, en 9/12 (0.285 contra
  0.367).
- **La ventaja se achica:** la mediana por par de E − C pasa de −0.093 bajo `una` a
  −0.020 bajo `dos`. Bajo `una`, en estos mismos pares, E entraba mejor en 9/12.
- **Los atascos del primer bloque** (`e_early` > 0.6) bajan en los dos brazos: bajo
  `una`, 7 gemelos de `coin` y 3 de `coin_regreso`; bajo `dos`, 2 y 1.
- **El atasco de la calibración aparece una sola vez** (11 A, 0.77) y decide el par 11
  (0.613 contra 0.540).
- **Los cinco pares que fallan ENTRA_D** pierden por entre 0.000 y 0.075.
- **El par que falla VUELVE_D** es el 1 (0.231 contra 0.156).

**Lectura.**
- **Dos de las tres cosas aguantan la otra crianza.** El brazo conserva lo que el sueño
  consolida (12/12) y vuelve a casa mejor que `coin` (11/12), con identidad (12/12) y
  sin pagar más afuera. Esas dos son del kernel, no de la crianza en la que se
  construyeron.
- **La tercera no la pierde el brazo: la gana `coin`.** La crianza en casa y escuela ya
  achica la rigidez (§K5) y hace entrar mejor a `coin` en todos los pares, así que
  queda poco para mejorar. `coin_regreso` sigue entrando un poco mejor en la mediana,
  pero no de forma consistente (7/12).
- **Las vueltas de la niñez no cambian con el regreso lento** (6/12; 0.116 contra
  0.118). No se midió por qué.
- **La identidad crece** de +0.464 a +0.663, otra vez por una casa mejor (afuera queda
  igual o peor). Bajo `dos`, a diferencia de bajo `una`, H(T2) no queda por debajo de
  la de `coin` (PAREADO 6/12).

**Las predicciones, contra el resultado.**
- **Las escritas antes del humo:**
  - Acertadas: VERIFICACIÓN, PERSISTE_D, CONSERVA_D, VUELVE_D (inclinada a pasar),
    RIGIDO_D que no pasa, y el veredicto, una de las dos opciones previstas.
  - ENTRA_D era incierta: falló.
  - Errada: NINEZ_D (prevista pasar; 6/12).
- **Las agregadas después de la calibración:** acertadas todas.
  - VERIFICACIÓN 24/24, CONSERVA_D, PERSISTE_D y VUELVE_D.
  - ENTRA_D falla. **Acertada en el resultado, no en la razón:** el atasco de
    `coin_regreso` aparece en 1 gemelo de 24; lo que decide es que `coin` ya entra
    bien.
  - RIGIDO_D no pasa en T1; en T2, incierta, tampoco pasa (4/12).
  - NINEZ_D falla.
  - El veredicto NO AGUANTA: ENTRA_D.

La réplica (pares 12–23, pre-registrada) está más abajo.

### §K14, réplica — NO REPLICADO por la letra (VUELVE_D 9/12); juntos, el brazo conserva y vuelve, pero ya no entra mejor que `coin` (2026-10-29)

`results/mundo_propio_escuela_replica_run.txt`: pares 12–23, 120.7 min.
- **Verificación: 24/24,** con diferencia máxima 0.0. Sumando las dos corridas, las 48
  vidas de `coin` re-corridas son iguales a las del §K7.

**Veredicto pre-registrado: NO AGUANTA: ENTRA_D, VUELVE_D.** El del test fue NO
AGUANTA: ENTRA_D. Como el veredicto no se repite, queda **NO REPLICADO por la letra.**
- CONSERVA_D 12/12 (0.015 contra 0.048).
- ENTRA_D 8/12 (0.284 contra 0.334).
- **VUELVE_D 9/12** (0.157 contra 0.206).
- PERSISTE_D 10/12, justo en el umbral (H(T2) +0.430; `coin`, +0.657).
- RIGIDO_D no pasa: T1 6/12, T2 2/12.
- Secundarias: NINEZ_D 8/12, ESCUELA_D 6/12, la casa en Tm 8/12 (0.172 contra 0.188),
  AFUERA 10/12 (0.366 contra 0.545), RECUPERA 9/12 (0.056 contra 0.068), PAREADO 5/12,
  ELIGE 11/12 (`coin`, 12/12). Atascos: 0 en los dos brazos.

**Por par** (análisis posterior).
- **Los tres pares que fallan VUELVE_D.** El 13 (0.168 contra 0.139) y el 19 (0.186
  contra 0.183) pierden por poco. El 23 pierde por mucho (0.337 contra 0.215): su
  gemelo B tarda 64 ticks en volver a `h` en casa en T2, cuando la mediana del brazo es
  12.
- **Los dos que fallan PERSISTE_D.**
  - El 20 falla también en `coin` (H(T2) −0.212 y −0.225). La casa cuesta 0.56–0.65 en
    los dos brazos, y el gemelo B de `coin_regreso` no se asienta en `h` en 218 ticks.
  - El 23 falla por el mismo gemelo B.
- **Contra `una`** (los mismos pares, del §K11 y el §K13): `coin` entra mejor bajo
  `dos` en 11/12 (0.334 contra 0.601), y `coin_regreso` en 7/12 (0.284 contra 0.348).
  La mediana por par de E − C pasa de −0.275 a −0.044.

**Juntos, 24 pares.** No se registró regla para juntar. Como referencia, en un test de
signo de una cola 17/24 es p 0.032 y 20/24 es p 0.0008.

| Lectura | Test | Réplica | Juntos |
|---|---|---|---|
| CONSERVA_D | 12/12 | 12/12 | 24/24 |
| ENTRA_D | 7/12 | 8/12 | 15/24 |
| VUELVE_D | 11/12 | 9/12 | 20/24 |
| PERSISTE_D | 12/12 | 10/12 | 22/24 |
| RIGIDO_D, T1 y T2 | 5/12, 4/12 | 6/12, 2/12 | 11/24, 6/24 |
| NINEZ_D | 6/12 | 8/12 | 14/24 |
| AFUERA (T2, E < C) | 8/12 | 10/12 | 18/24 |
| RECUPERA | 8/12 | 9/12 | 17/24 |
| PAREADO | 6/12 | 5/12 | 11/24 |

| Brazo (juntos, medianas) | Oráculo de casa despierto | En casa T1 | Afuera T1 | En casa Tm | En casa T2 | Afuera T2 | Primer bloque del exilio | Después del cambio, T2 | H(T2) |
|---|---|---|---|---|---|---|---|---|---|
| `coin` | 0.047 | 0.033 | 0.376 | 0.189 | 0.206 | 0.534 | 0.334 | 0.068 | +0.547 |
| `coin_regreso` | 0.015 | 0.038 | 0.367 | 0.157 | 0.146 | 0.413 | 0.285 | 0.056 | +0.518 |

**Contra `una`, juntos** (análisis posterior):
- `coin` entra mejor bajo `dos` en 23/24 pares (0.334 contra 0.560), y `coin_regreso`
  en 16/24 (0.285 contra 0.367).
- E entra mejor que C en 20/24 pares bajo `una` y en 15/24 bajo `dos`. La mediana por
  par de E − C pasa de −0.125 a −0.035.
- Los atascos del primer bloque (`e_early` > 0.6): bajo `una`, 17 gemelos de `coin` y 4
  de `coin_regreso`; bajo `dos`, 4 y 1.

**Lectura.**
- **Lo que repite.** ENTRA_D falla en las dos corridas y por la misma razón: la crianza
  en casa y escuela ya hace entrar bien a `coin` (mejor que bajo `una` en 23/24 pares),
  y la ventaja del brazo se achica de −0.125 a −0.035. CONSERVA_D y PERSISTE_D pasan en
  las dos.
- **Lo que no repite.** VUELVE_D pasa en el test (11/12) y en la réplica queda a un par
  del umbral (9/12); dos de los tres fallos son por menos de 0.03. Juntos da 20/24: en
  el conjunto, la vuelta a casa mejor que `coin` aguanta la escuela, pero no por la
  letra de cada corrida.
- **Afuera no hay precio.** AFUERA, secundaria, da 18/24 juntos: el brazo paga menos que
  `coin` en la casa del hermano en T2 (0.413 contra 0.534), como bajo `una` (0.387
  contra 0.489 en el §K13).
- **La identidad es la de `coin`:** PERSISTE 22/24 en los dos brazos y PAREADO 11/24.
  Bajo `dos`, el brazo no la agranda.
- **El brazo completo es del kernel en dos de sus tres cosas:** conservar lo
  consolidado (24/24) y, en el conjunto, volver a casa (20/24). La tercera, entrar
  mejor que `coin` a lo nunca vivido, era relativa a la rigidez de `coin` criado en una
  sola casa, y la escuela ya se la saca.

**Las predicciones, contra el resultado.** La réplica no tenía predicciones propias; se
comparan las agregadas después de la calibración.
- Acertadas:
  - VERIFICACIÓN, CONSERVA_D y PERSISTE_D (esta, justo en el umbral).
  - ENTRA_D, que falla; RIGIDO_D, que no pasa; NINEZ_D, que falla (8/12).
- Erradas:
  - VUELVE_D, inclinada a pasar: dio 9/12.
  - El veredicto NO AGUANTA: ENTRA_D: salió ENTRA_D y VUELVE_D.

**Manos declaradas:**
- `coin` se re-corrió, en vez de cargarse, para tener la sonda despierta. Las 48 vidas
  son iguales a las del §K7.
- `coin_regreso` es el del §K13 sin cambios: s = 0.1, s_l = 1.0 y el tope de 30 ticks.
- Bajo `dos`, el oráculo de casa despierto se lee sólo en los bloques vividos en casa.
  Se declaró antes del humo.
- No se corrieron `coin_vigilia` ni `coin_madurez` bajo `dos`.
- El test corrió en dos tramos, porque el sistema cortó el primero por falta de
  memoria; la réplica, en uno solo.
- La comparación con `una` es análisis posterior.

**Lo que sigue abierto:**
- **Las vueltas de la niñez:** por qué el regreso lento no las cambia (NINEZ_D 14/24,
  0.116 contra 0.120).
- **El gemelo que tarda en volver a `h`:** el 23 B, con 64 ticks. No se midió si lo
  demora el regreso lento o el par.
- **Lo de antes:**
  - el precio afuera bajo `una`, con un tope más corto;
  - por qué el daño era mayor en `coin_madurez`;
  - la madurez con la foto del §K10;
  - un umbral relativo;
  - INVIERTE;
  - un `self_embedding` que lea el modelo del mundo;
  - la atribución bajo `dos`.

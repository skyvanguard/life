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

**Siguiente (§K2, decidido por Fran el 2026-10-26; ver arriba):** un solo cambio, con la misma regla. El sueño
repite al modelo del mundo transiciones `(s, a, s')` guardadas de visitas
pasadas, que es complementariedad propiamente dicha: la memoria rápida entrena
a la lenta. Reutiliza el `ReplayBuffer` que ya existe.

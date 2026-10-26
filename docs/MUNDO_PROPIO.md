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

**Siguiente (§K2, por decidir):** un solo cambio, con la misma regla. El sueño
repite al modelo del mundo transiciones `(s, a, s')` guardadas de visitas
pasadas, que es complementariedad propiamente dicha: la memoria rápida entrena
a la lenta. Reutiliza el `ReplayBuffer` que ya existe.

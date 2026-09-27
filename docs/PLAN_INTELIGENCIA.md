# Plan: del orden a la inteligencia — darle mundo a El Útero

*Escrito 2026-09-26, antes de tocar código. Fran pidió: "sigue avanzando hasta
que consigamos ver un vestigio de inteligencia". Este documento fija qué
contaría como vestigio ANTES de mirar, para que el hallazgo, si llega, no sea
una lectura generosa de un patrón.*

## 1. Diagnóstico

Diecinueve experimentos midieron **novedad**: cuántas formas nuevas acuña el
tejido y si persisten. Eso es orden, en el sentido de Conway. Un tejido puede
acuñar cien mil genomas sin ser más inteligente que una tormenta. Y hay una
razón estructural: **ninguna versión del Útero tiene mundo**. La única presión
es no ser ciego a la materia. Un organismo que no tiene nada que regular no
puede mostrar que regula.

## 2. Definición operativa (sin entrenamiento, sin maestro)

Adoptamos la línea Ashby → Conant y Ashby → Beer: **un sistema es inteligente
en la medida en que su estado interno modela su entorno y usa ese modelo para
seguir siendo.** Cuatro varas, cada una con su control:

| Vara | Pregunta | Cómo se mide | Control |
|---|---|---|---|
| **R. Regulación** | ¿el tejido se sostiene bajo un entorno que cambia? | vivas y novedad persistente a lo largo de los cambios de régimen; amortiguación: varianza de la materia interior / varianza del borde | mismo tejido sin sol; sombra (muertes al azar) |
| **A. Anticipación** | ¿el tejido reacciona ANTES del cambio, donde el cambio es regular? | en estaciones más largas que lo típico, actividad interna alrededor del instante en que el cambio *solía* ocurrir, sin que haya ocurrido | ventanas emparejadas antes de ese instante; sombra; tejido sin sol |
| **L. Aprendizaje por recurrencia** | ¿la respuesta a una estación que vuelve cambia con la repetición? | magnitud de la perturbación interna (muertes + reescrituras) en los primeros 100 ticks de cada ocurrencia de la misma estación: 1ª vs 2ª vs 3ª… | sombra; permutación del orden de ocurrencias |
| **O. Organización** | ¿las estructuras persistentes soportan perturbaciones sin desintegrarse? | dominio de perturbación (Beer): fracción de perturbaciones unicelda que la estructura absorbe | estructuras de la sombra |

**Vestigio** = al menos una de A o L positiva con su control, en ≥ 3 de 40
semillas, con R no negativa (el sol no mata al tejido). A y L son las que
distinguen inteligencia de orden: un cristal falla ambas; una tormenta falla R.

## 3. El sol: un entorno con estructura aprendible

No es una mano que dirige: es clima. La materia del *más allá* (los vecinos
fuera del mundo, que hoy valen 0) sigue una señal externa `s(t)` en `[0,1)`.
El tejido no puede leer el código del sol (no hay código) ni saber cuándo
cambia: sólo siente la materia de su borde.

Estructura de `s(t)`, deterministic y sembrada aparte (el observador la conoce,
el tejido no):
- **Estaciones** en orden fijo y cíclico: A (calma, nivel bajo), B (día largo,
  amplitud alta), C (día corto, nivel medio). El orden es la regularidad
  aprendible: después de A siempre viene B.
- **Duraciones** de cada estación tomadas de un mapa logístico (r=3.9) escalado
  a `[300, 900]` ticks: típicas pero impredecibles desde la señal. Eso hace
  medible la anticipación: en una estación *larga*, el instante típico de cambio
  pasa sin que el sol cambie; si el tejido "esperaba" el cambio, se nota.
- **Día**: dentro de cada estación, `s(t) = base + amp·(0.5+0.5·sin(2πt/T))`
  mod 1, con `T` propio de la estación.

Manos declaradas: la forma de `s(t)`, sus tres regímenes, el rango de
duraciones. Se barren en el control (§6).

## 4. Sustrato

Se parte de la mejor encarnación 1-D conocida (memoria + invasión asentada,
`eq_window=100`): es la que mantiene vivos los mundos (246 celdas contra 12)
y la más barata de correr con 40 semillas y sombra. El plano (v8) queda como
segunda etapa si el 1-D no muestra nada: tiene más estructura espacial y el
sondeo dio mucha más novedad, pero cuesta veinte veces más por corrida.

Flag `sol=Sol(...)` en `UteroCreciente` (y luego `UteroPlano`): el más allá
devuelve `s(t)` en vez de 0. `sol=None` byte-idéntico (test).

## 5. Fases

1. **Sol + varas** (`utero/sol.py`, `utero/inteligencia.py`, tests):
   generador de estaciones; extracción de series internas por tick (vivas,
   muertes, reescrituras, materia media interior y de borde, novedad); las
   cuatro medidas con sus controles.
2. **Experimento `exp_utero_sol.py`** (1-D, 40 semillas, 20000 ticks: ~25
   estaciones por corrida): brazos *sol* vs *sin sol*, sombra para *sol*;
   veredicto pre-registrado (§2). Si hay vestigio: replicar con otro sembrado
   del sol y con el orden de estaciones permutado (¿aprende ESE orden o
   cualquier cosa?).
3. **Si no hay vestigio en 1-D**: el plano con sol (una cara de la placa es el
   sol), 20 semillas.
4. **Si hay vestigio**: profundizar en el mecanismo (¿qué celdas lo portan?,
   ¿sobrevive a la ablación?) y buscar la vara O sobre las estructuras que lo
   portan.

## 6. Controles obligatorios antes de creer

- **Sombra**: muertes al azar en vez de sonda, mismo sol. Lo que la sombra
  "anticipa" es artefacto de la señal.
- **Tejido sin sol**: descarta que la "respuesta" sea dinámica interna
  periódica que coincide por azar.
- **Permutación**: para L, barajar el orden de las ocurrencias antes de medir
  la tendencia; para A, sembrar otro sol con otras duraciones.
- **Reflejo**: un modelo sin memoria del sol (`x_t = f(s_t)`) no puede pasar A
  ni L por construcción; si nuestras medidas se lo atribuyen, están mal.
- **Barrido de manos**: rango de duraciones y amplitudes del sol.

## 6b. Enmienda (2026-09-26, tras la réplica): la vara del vestigio era débil

La corrida 2 disparó "vestigio" con 3/40 al 5%: la tasa nominal ya da 2, y la
réplica lo mostró falso positivo (sol1 3, sol2 2, permutado 6, 8/120 contra 6
esperados). Para toda corrida posterior a esta enmienda:

- **Vestigio por conteo** exige p binomial < 0.05 contra la tasa nominal
  (≥ 5/40) Y ≥ 2× el máximo de los controles Y ≥ 2× el brazo con orden
  permutado (el control que quita la regularidad y deja todo lo demás igual).
- **Condición de contacto previa**: el estadístico de anticipación dispara en
  tejidos que no sienten el clima (muertes 0 en maduro). Antes de leer A o L,
  el brazo debe mostrar respuesta al inicio de estación (muertes post/pre ≥
  1.2 en mediana); si no, el resultado se lee como "sin contacto".
- Las corridas ya lanzadas conservan su regla pre-registrada; la enmienda se
  aplica a las siguientes y se declara en cada docstring.

## 7. Reglas de parada honestas

- Si tras las fases 2 y 3 no hay vestigio: se reporta como negativo con el
  mismo cuidado que los anteriores, y el paper cierra con "novedad sí,
  inteligencia no medible en este sustrato con este entorno".
- Nunca se relaja una vara después de mirar. Si una vara resulta mal
  diseñada, se declara (como la cuota de v6) y se corrige en un experimento
  nuevo, no en el mismo.


## 8. Estado al cierre de la sesión 2026-09-26

Fases 1–3 ejecutadas y extendidas: ocho diseños pre-registrados (sol visible,
sonda climática, réplica, calor, plano, disolución, metabolismo, percepción),
todos negativos por sus propias reglas; un falso positivo detectado por la
réplica; vara enmendada (§6b). Regla de parada de §7 aplicada: se reporta como
negativo con el mismo cuidado que los anteriores. Lo que un intento futuro
debería cambiar, según lo medido: (a) variables internas lentas y legibles
diseñadas desde el sustrato, no añadidas; (b) un régimen que no sea ni cristal
(sin costo) ni recambio total (con costo), calibrado por la escala temporal
interna frente a la del clima; (c) el plano, por su superficie de contacto y
su no-cristalización, como sustrato base del programa. Ver ledger en
`EL_UTERO.md` y `results/utero_sol_*_run.txt`.

## 9. Estado al segundo cierre (misma sesión, tras la orden de seguir)

Cuatro diseños más (v9 metabolismo, v10 percepción, v11 fotosíntesis ×2, v12
luz finita ×4). v12 —capacidad de carga estacional— dio por primera vez un
régimen intermedio real (población que sigue a la estación, muertes
concentradas en la hambruna) y dos lecturas tentadoras (ahorro antes de la
hambruna: 9/40 y 5/40) que sus réplicas y el brazo permutado desmontaron como
artefacto de acumulación. Trece corridas, cero vestigios. Lección de método
añadida a §6b: toda lectura sobre una serie que se acumula dentro de la
estación (energía, población) debe usarse SIN deriva (residuo respecto de la
tendencia previa) y compararse contra el brazo permutado, no sólo contra sin
sol y sombra.

## 10. Cierre definitivo de la sesión 2026-09-26

v13 (registros lentos, τ = 300, sobre la ecología de v12): NADA; la
anticipación sobre actividad dispara igual en el brazo permutado (7 vs 5) y las
lecturas de energía sólo en él (10 y 9). Catorce corridas, trece diseños, cero
vestigios, cuatro señales desmontadas. Lo que un programa futuro debería
cambiar no es un mecanismo más sino la pregunta: buscar la regulación en
entidades (estructuras itinerantes, Beer) y no en el tejido entero, con un
entorno cuya regularidad tenga la escala temporal de esas entidades; y
construir primero el POSITIVO CONTROL —un organismo diseñado a mano que sí
anticipe en este sustrato— para saber que las varas pueden verlo.

## 11. El control positivo (2026-09-26)

Un anticipador diseñado a mano (detector de estación en un registro lento +
SPAWN auto-reescrito según la estación) es viable (18/20), estable bajo
mutación y muere en la hambruna la mitad que el tejido evolucionado, y un 58%
menos bajo el orden regular que bajo el permutado. Las varas A/L no lo ven:
buscan cambios anclados al instante esperado y un reflejo estacional no los
produce. R2 (mortalidad en la hambruna, regular vs permutado) sí. Enmienda:
R2 pasa a ser la lectura PRIMARIA de regulación en esta ecología; A/L quedan
como lecturas de anticipación temporal fina. Siguiente y último paso: invasión
desde raro (¿la selección favorece al ahorrador frente al tejido
evolucionado bajo el orden regular y no bajo el permutado?).

## 12. Invasión desde raro y cierre (2026-09-26)

El ahorrador diseñado no es seleccionado frente al tejido evolucionado: toma
4–5/20 con y sin costo de parto, con y sin regularidad de orden, en las mismas
semillas (colapsos de la población aleatoria, no selección). La explicación de
los dieciséis negativos es mecánica: esta ecología no selecciona la
anticipación. Un entorno diseñado para seleccionarla equivaldría a elegir la
respuesta: es una decisión de programa, no de ejecución. Programa cerrado.

## 13. Evolución experimental bajo un régimen declarado (v14)

Corrijo un argumento propio de §12: elegir el régimen selectivo no es elegir
la respuesta, es elegir la PREGUNTA (evolución experimental). La respuesta
—¿un tejido de genomas aleatorios desarrolla comportamiento regulado por la
estación?— sigue abierta y se mide contra los mismos controles (sin sol,
sombra, orden permutado, segundo orden cíclico). El régimen: luz casi nula en
A (base 0.08, calibrada por viabilidad estacional en 6 semillas × 9
configuraciones: 5/6 viven, N cae en A y se recupera, partos en A ≈ 0) y
parto costoso (e_costo = 1.0). Nada sembrado. Lectura primaria: R2_A, la
mortalidad durante la hambruna bajo el orden regular contra el permutado,
pareada entre mundos vivos, con ciclo2 como control de tipos de transición.
Un tejido que regula según la estación previa muere menos cuando la hambruna
sigue siempre a la estación templada. Secundarias: estructura de partos A/B y
las lecturas de anticipación con la vara enmendada.
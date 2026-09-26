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

## 7. Reglas de parada honestas

- Si tras las fases 2 y 3 no hay vestigio: se reporta como negativo con el
  mismo cuidado que los anteriores, y el paper cierra con "novedad sí,
  inteligencia no medible en este sustrato con este entorno".
- Nunca se relaja una vara después de mirar. Si una vara resulta mal
  diseñada, se declara (como la cuota de v6) y se corrige en un experimento
  nuevo, no en el mismo.

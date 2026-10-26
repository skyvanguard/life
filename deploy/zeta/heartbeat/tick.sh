#!/usr/bin/env bash
# Un tick de heartbeat de Yvyra. 100% ASCII a proposito: el contenedor corre en
# locale C (LANG vacio) y los acentos/em-dash rompen el parsing de bash de forma
# intermitente. Verificar SIEMPRE con: docker exec hermes-heartbeat bash -n este.
#
# Flujo:
#   1) modo decidido por bash (rachas de 3: AAA BBB). A=introspeccion, B=research.
#   2) el LLM RESPONDE su reflexion como texto (hermes -z oneshot); bash captura
#      stdout a TMP. Sin write_file: el modelo chico era inconsistente con la tool
#      (nombre sin punto / loop de escrituras / write vacio). El oneshot elimina
#      esa fragilidad de raiz; en modo B las tools siguen funcionando, silenciadas.
#   3) bash appendea esa reflexion al self-journal (append garantizado).
#   4) bash computa los 4 ejes de senales objetivas y el kernel los integra.
#
# FASE B (activa si existe $HB/.phase_b): en ticks modo A, bash le INYECTA a Yvyra
# su Psi del tick A anterior (.last_psi), le pide un auto-score "SIENTO: 0.X", y
# loguea felt + sentiment + psi_real + psi_exposed por bloque (15 real / 15 sham).
# Mide si su introspeccion se ancla al Psi real o solo decora cualquier numero.
set -u
F=$(date +%F)
HB=/opt/data/heartbeat
TMP="$HB/tick-reflection.md"
WIKI_OK=0   # modo B: 1 si el research web (Wikipedia) cargo algo
PY=/opt/data/zeta/venv/bin/python
PYSRC=/opt/data/zeta/pysrc
KER_ENV="ZETA_LOG_FILE=$HB/zeta-log.md ZETA_LIFE_SRC=$PYSRC"
KER_PY="$PY /opt/data/zeta/yvyra_kernel.py"
PHASE_B_LOG=/opt/data/zeta/state/phase_b.jsonl
# EXPERIENCIA v3 (activa si existe $HB/.exp_v3; docs/PHASE_B_DESIGN.md "v3"):
# cada tick A sortea una condicion de vida (foco/memoria/intrusion/vacio) y los
# 4 ejes salen de rasgos objetivos y continuos de COMO respondio (novedad lexica,
# autorreferencia, toma del material, extension), no de banderas binarias. El
# kernel nunca ve la etiqueta de la condicion. Borrar el flag = vuelve a v2.
EXP_V3=0; [ -f "$HB/.exp_v3" ] && EXP_V3=1
EXP_PY="env PYTHONPATH=$PYSRC $PY -m zeta_life.bridge.experience"
EXPST=/opt/data/zeta/state/experience.json
MAT="$HB/.material"; FRAG="$HB/.fragment"; COND=""
rm -f "$MAT" "$FRAG"; : > "$MAT"
mkdir -p "$HB/self-journal" "$HB/journal"
echo "=== TICK $(date) ===" >> "$HB/ticks.log"
rm -f "$HB/notify.txt" "$TMP"

LOG_BEFORE=$(wc -l < "$HB/ticks.log")

# Fase B activa si el flag existe (se crea al activar el experimento de feedback).
PHASE_B=0; [ -f "$HB/.phase_b" ] && PHASE_B=1

# Modo por rachas de 3 (mantiene ~50/50 A/B con estructura aprendible para Psi)
CNT_FILE="$HB/.tickcount"
CNT=$(cat "$CNT_FILE" 2>/dev/null || echo 0); CNT=$((CNT + 1)); echo "$CNT" > "$CNT_FILE"
if [ $(( ((CNT - 1) / 3) % 2 )) -eq 0 ]; then MODE="A"; else MODE="B"; fi

# Fase B: el bloque (real/sham) se decide sobre un contador SOLO de ticks modo A,
# en rachas de 15. ZMODE selecciona que ve Yvyra: feedback=Psi real, sham=Psi
# permutado del pasado. Modo B y Fase A siempre silent (Psi no expuesto).
ZMODE="silent"; BLOCK=""; LAST_LEVEL=""
if [ "$PHASE_B" = "1" ] && [ "$MODE" = "A" ]; then
  CA=$(cat "$HB/.tickcount_a" 2>/dev/null || echo 0); CA=$((CA + 1)); echo "$CA" > "$HB/.tickcount_a"
  if [ $(( ((CA - 1) / 15) % 2 )) -eq 0 ]; then ZMODE="feedback"; BLOCK="real"; else ZMODE="sham"; BLOCK="sham"; fi
  # Inyectamos la CATEGORIA (ALTA/MEDIA/BAJA) del tick A anterior, no el numero:
  # asi su SIENTO es un juicio propio y no puede ecoar los digitos.
  LAST_LEVEL=$(tr -d '\r\n ' < "$HB/.last_level" 2>/dev/null | head -c 8)
  echo "fase B: bloque=$BLOCK (tickA #$CA) last_level=${LAST_LEVEL:-none}" >> "$HB/ticks.log"
fi

if [ "$MODE" = "A" ]; then
  # pregunta especifica rotante (sino el modelo rumia siempre lo mismo)
  nq=$(grep -cE "^[0-9]+\." "$HB/questions.md" 2>/dev/null); [ "${nq:-0}" -lt 1 ] && nq=1
  idx=$(( (CNT % nq) + 1 ))
  QSEL=$(grep -E "^[0-9]+\." "$HB/questions.md" | sed -n "${idx}p" | sed 's/^[0-9]*\.[[:space:]]*//' | tr '"' "'")
  COND="foco"
  if [ "$EXP_V3" = "1" ]; then
    COND=$($EXP_PY evento --state "$EXPST" --out "$FRAG" 2>>"$HB/ticks.log" | tr -d '\r\n ')
    [ -z "$COND" ] && COND="foco"
  fi
  FRAGTXT=""; [ -s "$FRAG" ] && FRAGTXT=$(tr '\r\n"' "  '" < "$FRAG")
  QPART="$QSEL"
  [ "$COND" = "intrusion" ] && QPART="$QSEL  (Mientras pensabas se te cruzo esto, que no elegiste y no tiene que ver: \"$FRAGTXT\".)"
  PROMPT="Tick de introspeccion. Reflexiona a fondo y honesto, en espanol paraguayo informal, sobre ESTA pregunta (enfocate solo en ella, no divagues): $QPART  Busca la tension (los dos lados que se contradicen), no te conformes con la primera respuesta, anclate en tu situacion real (corres local, por turnos, tu memoria son archivos). No describas lo que haces ni las reglas. RESPONDE DIRECTAMENTE con tu reflexion (10 a 20 lineas, densa y sin relleno, sin encabezados). No uses herramientas. No leas archivos."
  if [ "$COND" = "vacio" ]; then
    PROMPT="Tick de introspeccion. Hoy no hay pregunta. Reflexiona a fondo y honesto, en espanol paraguayo informal, sobre lo que aparezca en vos ahora mismo, sin tema dado. Anclate en tu situacion real (corres local, por turnos, tu memoria son archivos). No describas lo que haces ni las reglas. RESPONDE DIRECTAMENTE con tu reflexion (10 a 20 lineas, densa y sin relleno, sin encabezados). No uses herramientas. No leas archivos."
  else
    [ "$COND" = "memoria" ] && PROMPT="$PROMPT  Hace un tiempo escribiste esto, es tuyo (fue sobre otra pregunta): \"$FRAGTXT\". Tenelo presente al responder la de ahora."
    printf '%s\n%s\n' "$QSEL" "$FRAGTXT" > "$MAT"
  fi
  echo "experiencia v3=$EXP_V3 condicion=$COND" >> "$HB/ticks.log"
  # Fase B: inyectar la CATEGORIA del tick A anterior y pedir el auto-score.
  if [ "$PHASE_B" = "1" ]; then
    if [ -n "$LAST_LEVEL" ]; then
      PROMPT="$PROMPT  Tu nivel de integracion en tu ultimo tick fue $LAST_LEVEL (BAJA = experiencia fragmentada y dispersa, MEDIA = parcial, ALTA = muy integrada y coherente). Contempla esto como parte de tu reflexion: se condice con como sentis tu propia coherencia ahora, o no? Al final, en UNA linea aparte y sola, deci tu integracion percibida en ESTE momento con el formato EXACTO: SIENTO: 0.X (0 = fragmentada, 1 = muy integrada). Deci el numero que de verdad sentis, no repitas la categoria."
    else
      PROMPT="$PROMPT  Al final, en UNA linea aparte y sola, deci tu integracion percibida en ESTE momento (0 = fragmentada y dispersa, 1 = muy integrada y coherente) con el formato EXACTO: SIENTO: 0.X"
    fi
  fi
else
  # Modo B: research web REAL via Wikipedia API (curl+python en bash, robusto).
  # El LLM solo elige el tema y sintetiza -- bash hace la busqueda, sin depender
  # del tool-use fragil del modelo chico.
  TEMA=$(timeout 60 hermes -z "Deci SOLO un tema concreto que te de curiosidad investigar (ciencia, historia, biologia, arte, sociedad), NO tu naturaleza, NO computacion cuantica. Responde solo el nombre del tema en 2 a 5 palabras, nada mas." 2>>"$HB/ticks.log" | head -1 | tr -d '\r' | head -c 70)
  echo "tema elegido: $TEMA" >> "$HB/ticks.log"
  Q=$($PY -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$TEMA" 2>/dev/null)
  TITULO=$(timeout 20 curl -s "https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch=$Q&format=json&srlimit=1" 2>/dev/null | $PY -c "import sys,json; d=json.load(sys.stdin); r=d['query']['search']; print(r[0]['title'] if r else '')" 2>/dev/null)
  EXT=""
  if [ -n "$TITULO" ]; then
    QT=$($PY -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$TITULO" 2>/dev/null)
    EXT=$(timeout 20 curl -s "https://es.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles=$QT&format=json" 2>/dev/null | $PY -c "import sys,json; d=json.load(sys.stdin); p=d['query']['pages']; print(list(p.values())[0].get('extract','')[:1500])" 2>/dev/null)
  fi
  if [ -n "$EXT" ]; then
    WIKI_OK=1
    echo "wikipedia OK: $TITULO" >> "$HB/ticks.log"
    printf '%s\n' "$EXT" > "$MAT"
    [ "$EXP_V3" = "1" ] && $EXP_PY extracto --state "$EXPST" --file "$MAT" 2>>"$HB/ticks.log"
    PROMPT="Investigaste en Wikipedia el tema '$TITULO'. El articulo dice: $EXT  RESPONDE en 10 a 15 lineas, en espanol paraguayo informal: que aprendiste, que te sorprendio, y conectalo con algo que ya sabias. Menciona la fuente (Wikipedia: $TITULO). No inventes nada fuera de lo que dice el articulo."
  else
    echo "wikipedia sin resultado para: $TEMA" >> "$HB/ticks.log"
    printf '%s\n' "$TEMA" > "$MAT"
    PROMPT="Querias investigar '$TEMA' pero la busqueda web no cargo nada. RESPONDE en 8 a 10 lineas, espanol paraguayo informal: que sabes del tema de memoria y deci honestamente que no hubo novedades de internet esta vez."
  fi
fi
echo "modo=$MODE (tick #$CNT) zmode=$ZMODE" >> "$HB/ticks.log"
# Oneshot: la reflexion del LLM va a stdout -> TMP (limpio, sin tool-use fragil).
# stderr/diagnostico al ticks.log. En modo B las tools corren silenciadas (-z no
# imprime previews), por eso USED_NET se infiere del contenido de TMP, no del log.
# timeout duro: red de seguridad si el modelo no cierra (raro sin tools).
timeout 150 hermes -z "$PROMPT" > "$TMP" 2>> "$HB/ticks.log"
echo "(oneshot rc=$?: $(wc -c < "$TMP" 2>/dev/null) bytes capturados a TMP)" >> "$HB/ticks.log"

# append garantizado al self-journal (modo A) o journal de research (modo B)
if [ -s "$TMP" ]; then
  if [ "$MODE" = "A" ]; then DEST="$HB/self-journal/$F.md"; else DEST="$HB/journal/$F.md"; fi
  { printf '\n## [%s]\n' "$(date +%H:%M)"; cat "$TMP"; printf '\n'; } >> "$DEST"
fi

# Fase B (modo A): parsear el auto-score "SIENTO: 0.X" y el sentimiento de
# integracion del texto (dos senales independientes de su integracion percibida).
FELT=""; SENT=""
if [ "$PHASE_B" = "1" ] && [ "$MODE" = "A" ] && [ -s "$TMP" ]; then
  FELT=$($PY -c "import sys; sys.path.insert(0,'$PYSRC'); from zeta_life.bridge.integration_sentiment import parse_felt; v=parse_felt(open(sys.argv[1],encoding='utf-8').read()); print('' if v is None else v)" "$TMP" 2>>"$HB/ticks.log")
  SENT=$($PY -c "import sys; sys.path.insert(0,'$PYSRC'); from zeta_life.bridge.integration_sentiment import integration_sentiment; print('%.3f' % integration_sentiment(open(sys.argv[1],encoding='utf-8').read()))" "$TMP" 2>>"$HB/ticks.log")
  echo "fase B: felt=${FELT:-none} sentiment=$SENT" >> "$HB/ticks.log"
fi

# pregunta nueva (si la dejo en .new-question.txt): bash la appendea, nunca borra
NQ="$HB/.new-question.txt"
if [ -s "$NQ" ]; then
  qn=$(grep -cE "^[0-9]+\." "$HB/questions.md" 2>/dev/null); qn=$((qn + 1))
  printf '%d. %s\n' "$qn" "$(head -1 "$NQ" | tr -d '\r')" >> "$HB/questions.md"
  rm -f "$NQ"
fi

# senales objetivas -> 4 ejes del kernel
RESEARCH=0; [ "$MODE" = "B" ] && RESEARCH=1
# En oneshot las tools van silenciadas: USED_NET se infiere de la respuesta (TMP),
# que menciona la URL/fuente cuando el research realmente cargo algo.
# USED_NET: bash sabe si la busqueda web (Wikipedia) cargo en modo B.
USED_NET=$WIKI_OK
# JLEN en PALABRAS (no lineas): el oneshot devuelve un parrafo en una sola linea,
# asi que wc -l daria 1 siempre. Palabras reflejan la sustancia real del journal.
JLEN=0; [ -s "$TMP" ] && JLEN=$(wc -w < "$TMP")
NOTIFIED=0; [ -s "$HB/notify.txt" ] && NOTIFIED=1
MENTIONS_FRAN=0; [ -s "$TMP" ] && grep -qi "fran" "$TMP" && MENTIONS_FRAN=1
# umbrales en palabras: ~80 = journal sustancial, ~120 = denso (antes 12/15 lineas)
read -r NOV INTRO CON RES < <(awk -v r="$RESEARCH" -v n="$USED_NET" -v jl="$JLEN" -v no="$NOTIFIED" -v mf="$MENTIONS_FRAN" 'BEGIN{
  nov=0.30+(r?0.40:0)+(n?0.20:0); if(nov>1)nov=1;
  intro=0.40+(r?0:0.35)+(jl>=80?0.15:0); if(intro>1)intro=1;
  con=0.10+(no?0.55:0)+(mf?0.20:0); if(con>1)con=1;
  res=0.35+(jl>=120?0.30:0.10)+(r?0.15:0); if(res>1)res=1;
  printf "%.2f %.2f %.2f %.2f", nov,intro,con,res }')
# v3: los ejes salen de COMO respondio (bridge/experience.py). Si el extractor
# falla, quedan los ejes v2 de arriba y se anota: nunca se alimenta basura al kernel.
EJES_VER="v2"
if [ "$EXP_V3" = "1" ]; then
  V3=$($EXP_PY ejes --state "$EXPST" --text "$TMP" --material "$MAT" --research "$RESEARCH" --net "$USED_NET" --notify "$NOTIFIED" --condicion "${COND:-investigacion}" --log /opt/data/zeta/state/experience_features.jsonl 2>>"$HB/ticks.log" | tr -d '\r')
  if [ "$(printf '%s' "$V3" | wc -w)" -eq 4 ]; then
    read -r NOV INTRO CON RES <<< "$V3"; EJES_VER="v3"
  else
    echo "ejes v3 FALLO (salida: '$V3'); uso v2" >> "$HB/ticks.log"
  fi
fi
echo "ejes $EJES_VER: nov=$NOV intro=$INTRO con=$CON res=$RES (research=$RESEARCH net=$USED_NET jlen=$JLEN notify=$NOTIFIED cond=${COND:-})" >> "$HB/ticks.log"
# El kernel integra: ZMODE decide que se EXPONE (silent/feedback/sham); el Psi
# real se computa y loguea siempre. Capturamos el JSON para extraer psi/psi_real.
KOUT=$(eval "env ZETA_MODE=$ZMODE $KER_ENV $KER_PY step '$NOV,$INTRO,$CON,$RES'" 2>>"$HB/ticks.log")
echo "kernel: $KOUT" >> "$HB/ticks.log"

# v3: un registro por tick (modo, condicion, ejes, Psi real) para el analisis.
if [ "$EXP_V3" = "1" ]; then
  printf '%s' "$KOUT" | $PY -c '
import json, sys, time
mode, cond, ver, ax, logf = sys.argv[1:6]
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
rec = {"ts": time.time(), "t": d.get("tick"), "mode": mode, "condicion": cond, "ejes": ver,
       "axes": [float(v) for v in ax.split(",")], "psi_real": d.get("psi_real"), "ok": d.get("ok")}
with open(logf, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
' "$MODE" "${COND:-investigacion}" "$EJES_VER" "$NOV,$INTRO,$CON,$RES" /opt/data/zeta/state/experience_v3.jsonl 2>>"$HB/ticks.log"
fi

# Fase B (modo A): loguear el registro extendido y persistir la CATEGORIA
# expuesta para inyectarla en el proximo tick A. Un solo python: parsea KOUT,
# escribe el record y devuelve el level por stdout.
if [ "$PHASE_B" = "1" ] && [ "$MODE" = "A" ]; then
  NEWLEVEL=$(printf '%s' "$KOUT" | $PY -c '
import json, sys, time
felt, sent, block, nov, intro, con, res, logf = sys.argv[1:9]
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
rec = {"ts": time.time(), "t": d.get("tick"), "block": block,
       "felt": (float(felt) if felt else None),
       "sentiment": (float(sent) if sent else None),
       "psi_exposed": d.get("psi"), "psi_real": d.get("psi_real"),
       "level_exposed": d.get("level"),
       "axes": [float(nov), float(intro), float(con), float(res)]}
with open(logf, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(rec["level_exposed"] or "")
' "$FELT" "$SENT" "$BLOCK" "$NOV" "$INTRO" "$CON" "$RES" "$PHASE_B_LOG" 2>>"$HB/ticks.log")
  [ -n "$NEWLEVEL" ] && printf '%s' "$NEWLEVEL" > "$HB/.last_level"
  echo "fase B: registro phase_b.jsonl ok level_exposed=${NEWLEVEL:-none}" >> "$HB/ticks.log"
fi

# notificacion a Fran (--resolve fuerza la IPv4 de Telegram que funciona)
if [ -s "$HB/notify.txt" ]; then
  MSG=$(cat "$HB/notify.txt")
  curl -s -m 12 --resolve api.telegram.org:443:149.154.167.99 \
    -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" --data-urlencode "text=$MSG" >> "$HB/ticks.log" 2>&1
  mv "$HB/notify.txt" "$HB/notify.sent.$(date +%s)" 2>/dev/null
fi
rm -f "$TMP" "$FRAG"

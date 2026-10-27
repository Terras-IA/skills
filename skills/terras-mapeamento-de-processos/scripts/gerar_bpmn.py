#!/usr/bin/env python3
"""Gera BPMN 2.0 XML (.bpmn) a partir do processo.json, com o diagrama (BPMNDI).

O .bpmn é o formato de troca das ferramentas de modelagem (Camunda Modeler,
Bizagi, bpmn.io, Signavio). Sem o bloco bpmndi elas abrem o arquivo vazio, por
isso todo nó e toda seta saem com coordenadas.

Uso:
  python3 gerar_bpmn.py --json processo.json --saida as-is.bpmn
  python3 gerar_bpmn.py --json processo-to-be.json --saida to-be.bpmn

Tradução do schema (só stdlib):
  ator -> lane do pool do processo       tarefa -> userTask (com sistema) / task
  sistema -> serviceTask                 aprovacao -> userTask
  documento -> task                      espera -> intermediateCatchEvent (timer)
  decisao -> exclusiveGateway            gatilho/fim -> startEvent/endEvent

Campos opcionais do JSON que só o BPMN usa:
  passo.desvios = [{"para": "P5" | "FIM", "rotulo": "retornou"}]
      saída condicional (retrabalho, atalho). Em passo que não é decisão, o
      script cria o gateway exclusivo logo depois da tarefa.
  passo.grupo_paralelo = "A"
      passos consecutivos com o mesmo valor rodam em paralelo (parallelGateway
      abre e fecha o grupo).
  "bpmn": {"externos": ["Cliente"]}
      esses atores viram pool próprio (caixa-preta); os passos deles saem do
      fluxo e viram messageFlow entre os pools.
  layout.rotulos["P4->P5"] dá o nome da seta do caminho principal.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerar_mermaid import limpar, rotulo  # noqa: E402

NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
for _p, _u in NS.items():
    ET.register_namespace(_p, _u)

TAREFAS = ("task", "userTask", "serviceTask", "manualTask")
EVENTOS = ("startEvent", "endEvent", "intermediateCatchEvent", "intermediateThrowEvent")
GATEWAYS = ("exclusiveGateway", "parallelGateway")
TAM = {"tarefa": (120, 80), "evento": (36, 36), "gateway": (50, 50)}

# geometria (px): pool com faixa de título de 30, lane com faixa de 30
POOL_X = 160
COL_W = 170
LANE_H = 150
EXTERNO_H = 60
GAP_POOL = 50
X0 = POOL_X + 30 + 30 + 40


def q(prefixo, nome):
    return "{%s}%s" % (NS[prefixo], nome)


def familia(kind):
    if kind in TAREFAS:
        return "tarefa"
    if kind in GATEWAYS:
        return "gateway"
    return "evento"


def sem_timestamp(texto):
    """'[00:00:15] Supervisor: O cliente manda...' -> 'O cliente manda...'."""
    t = re.sub(r"^\s*\[\d{1,2}:\d{2}(:\d{2})?\]\s*", "", str(texto or ""))
    t = re.sub(r"^[^:]{1,30}:\s+", "", t)
    t = limpar(t)
    return t if len(t) <= 45 else t[:44].rstrip() + "…"


def tipo_bpmn(p):
    tipo = p.get("tipo", "tarefa")
    if tipo == "decisao":
        return "exclusiveGateway"
    if tipo == "espera":
        return "intermediateCatchEvent"
    if tipo == "sistema":
        return "serviceTask"
    if tipo == "aprovacao" or (tipo == "tarefa" and p.get("sistema")):
        return "userTask"
    return "task"


def documentacao(p):
    partes = []
    if p.get("sistema"):
        partes.append("Sistemas: " + ", ".join(p["sistema"]))
    if p.get("tempo_execucao_min"):
        partes.append("Execução: {} min".format(p["tempo_execucao_min"]))
    if p.get("tempo_espera_min"):
        partes.append("Espera: {} min".format(p["tempo_espera_min"]))
    if p.get("excecoes"):
        partes.append("Exceções: " + "; ".join(p["excecoes"]))
    if p.get("evidencia"):
        partes.append("Evidência: " + p["evidencia"])
    return "\n".join(partes)


class Modelo:
    def __init__(self, dados):
        self.dados = dados
        self.nos = {}          # id -> {kind, nome, lane, col, doc, timer}
        self.ordem = []
        self.fluxos = []       # {id, de, para, nome, cond, principal}
        self.mensagens = []    # {id, de, para, nome}
        self.default = {}      # gateway -> fluxo default
        self.col = 0

    def no(self, nid, kind, nome, lane, col=None, **extra):
        if col is None:
            col = self.col
            self.col += 1
        self.nos[nid] = dict(kind=kind, nome=nome, lane=lane, col=col, **extra)
        self.ordem.append(nid)
        return nid

    def fluxo(self, de, para, nome="", cond=None, principal=True):
        fid = "Flow_{}_{}".format(de, para)
        while any(f["id"] == fid for f in self.fluxos):
            fid += "_"
        self.fluxos.append(dict(id=fid, de=de, para=para, nome=nome, cond=cond, principal=principal))
        return fid


def montar(dados):
    passos = dados.get("passos") or []
    if not passos:
        raise SystemExit("JSON sem passos — revise a extração antes de gerar o BPMN.")
    externos = set((dados.get("bpmn") or {}).get("externos") or [])
    rotulos = (dados.get("layout") or {}).get("rotulos") or {}
    internos = [p for p in passos if (p.get("ator") or "Processo") not in externos]
    if not internos:
        raise SystemExit("Todos os atores estão em bpmn.externos — sobra processo vazio.")
    por_id = {p["id"]: p for p in passos}

    m = Modelo(dados)
    lane_inicio = internos[0].get("ator") or "Processo"
    lane_fim = internos[-1].get("ator") or "Processo"

    # passos externos antes do primeiro interno disparam o processo por mensagem
    i = 0
    abertura = []
    while passos[i]["id"] not in {p["id"] for p in internos}:
        abertura.append(passos[i])
        i += 1
    nome_ini = sem_timestamp(dados.get("gatilho")) or "Início"
    m.no("StartEvent_1", "startEvent", nome_ini, lane_inicio,
         doc="Gatilho: " + str(dados.get("gatilho") or ""), mensagem=bool(abertura))
    if abertura:
        m.mensagens.append(dict(de=abertura[0]["ator"], para="StartEvent_1",
                                nome=" / ".join(limpar(p["nome"]) for p in abertura)))

    anterior = "StartEvent_1"
    rotulo_pendente = ""
    pendentes_externos = []   # passos externos entre dois internos
    desvios = []              # (origem, alvo, rotulo)
    resto = passos[i:]
    j = 0
    while j < len(resto):
        p = resto[j]
        ator = p.get("ator") or "Processo"
        if ator in externos:
            pendentes_externos.append(p)
            j += 1
            continue

        grupo = p.get("grupo_paralelo")
        bloco = [p]
        if grupo:
            while (j + len(bloco) < len(resto) and resto[j + len(bloco)].get("grupo_paralelo") == grupo
                   and (resto[j + len(bloco)].get("ator") or "Processo") not in externos):
                bloco.append(resto[j + len(bloco)])

        if pendentes_externos:
            anterior = mensagens_externas(m, anterior, pendentes_externos, ator)
            pendentes_externos = []

        if len(bloco) > 1:
            fork = m.no("Gateway_{}_abre".format(grupo), "parallelGateway", "", ator)
            m.fluxo(anterior, fork, rotulo_pendente)
            col = m.col
            usadas = {}
            for b in bloco:
                lane = b.get("ator") or "Processo"
                c = col
                while (c, lane) in usadas:
                    c += 1
                usadas[(c, lane)] = True
                no_passo(m, b, lane, c)
                m.fluxo(fork, b["id"])
            m.col = max(c for c, _ in usadas) + 1
            join = m.no("Gateway_{}_fecha".format(grupo), "parallelGateway", "", ator)
            for b in bloco:
                m.fluxo(b["id"], join)
                desvios += [(b["id"], d) for d in b.get("desvios") or []]
            anterior, rotulo_pendente = join, ""
            ultimo_id = bloco[-1]["id"]
        else:
            no_passo(m, p, ator)
            m.fluxo(anterior, p["id"], rotulo_pendente)
            anterior, rotulo_pendente = p["id"], ""
            ultimo_id = p["id"]
            if p.get("desvios"):
                if p.get("tipo") != "decisao":
                    anterior = m.no(p["id"] + "_resultado", "exclusiveGateway", "", ator)
                    m.fluxo(p["id"], anterior)
                desvios += [(anterior, d) for d in p["desvios"]]
        # nome da seta do caminho principal (layout.rotulos), ex.: "P4->P5": "não urgente"
        seguinte = proximo_interno(resto, j + len(bloco), externos)
        chave = "{}->{}".format(ultimo_id, seguinte["id"] if seguinte else "FIM")
        rotulo_pendente = limpar(rotulos.get(chave, ""))
        j += len(bloco)

    if pendentes_externos:
        anterior = mensagens_externas(m, anterior, pendentes_externos, lane_fim, fim=True)
    nome_fim = sem_timestamp(dados.get("fim")) or "Concluído"
    m.no("EndEvent_1", "endEvent", nome_fim, m.nos[anterior]["lane"],
         doc="Fim: " + str(dados.get("fim") or ""))
    m.fluxo(anterior, "EndEvent_1", rotulo_pendente)

    for origem, d in desvios:
        alvo = d.get("para")
        alvo = "EndEvent_1" if alvo in ("FIM", "fim", None) else alvo
        if alvo not in m.nos:
            dono = por_id.get(alvo)
            motivo = "é de ator externo" if dono else "não existe"
            raise SystemExit("Desvio de {} para {}: o passo {}.".format(origem, d.get("para"), motivo))
        nome = limpar(d.get("rotulo") or "")
        m.fluxo(origem, alvo, nome, cond=nome or "desvio", principal=False)
    # o caminho principal que sai de um gateway com desvio é o default ("senão")
    for g in {o for o, _ in desvios}:
        principal = [f for f in m.fluxos if f["de"] == g and f["principal"]]
        if principal:
            m.default[g] = principal[0]["id"]
            principal[0]["default"] = True
            principal[0]["nome"] = principal[0]["nome"] or "senão"
    return m, externos


def proximo_interno(resto, k, externos):
    for p in resto[k:]:
        if (p.get("ator") or "Processo") not in externos:
            return p
    return None


def no_passo(m, p, lane, col=None):
    kind = tipo_bpmn(p)
    nome = rotulo(p)
    if kind == "exclusiveGateway" and not nome.endswith("?") and "?" not in nome:
        nome += "?"
    m.no(p["id"], kind, nome, lane, col, doc=documentacao(p),
         timer=p.get("tempo_espera_min") if kind == "intermediateCatchEvent" else None,
         timer_vazio=kind == "intermediateCatchEvent")


def mensagens_externas(m, anterior, externos_passos, lane_seguinte, fim=False):
    """Passos de ator externo entre dois internos: envio e retorno por messageFlow.

    Gateway e evento intermediário não enviam nem recebem mensagem no BPMN; nesse
    caso entra um evento de mensagem (throw/catch) para ancorar o messageFlow.
    """
    ator = externos_passos[0]["ator"]
    nomes = " / ".join(limpar(p["nome"]) for p in externos_passos)
    origem = anterior
    if m.nos[origem]["kind"] not in TAREFAS:
        origem = m.no("Event_envia_{}".format(externos_passos[0]["id"]), "intermediateThrowEvent",
                      "Aciona " + limpar(ator), m.nos[anterior]["lane"], mensagem=True)
        m.fluxo(anterior, origem)
    m.mensagens.append(dict(de=origem, para=ator, nome=""))
    if fim:
        destino = m.no("Event_recebe_{}".format(externos_passos[-1]["id"]), "intermediateCatchEvent",
                       nomes, lane_seguinte, mensagem=True)
        m.fluxo(origem, destino)
        m.mensagens.append(dict(de=ator, para=destino, nome=nomes))
        return destino
    destino = m.no("Event_recebe_{}".format(externos_passos[-1]["id"]), "intermediateCatchEvent",
                   nomes, lane_seguinte, mensagem=True)
    m.fluxo(origem, destino)
    m.mensagens.append(dict(de=ator, para=destino, nome=""))
    return destino


# ---------------------------------------------------------------------------
def layout(m, externos, atores_ordem):
    lanes = []
    for a in atores_ordem + [n["lane"] for n in m.nos.values()]:
        if a not in lanes and a not in externos and any(n["lane"] == a for n in m.nos.values()):
            lanes.append(a)
    ext = [a for a in atores_ordem if a in externos] + \
          sorted({x["de"] for x in m.mensagens if x["de"] in externos} - set(atores_ordem))
    largura = (X0 - POOL_X) + m.col * COL_W + 40
    y = 80
    pools = {}
    for a in ext:
        pools[a] = (POOL_X, y, largura, EXTERNO_H)
        y += EXTERNO_H + GAP_POOL
    principal_y = y
    lane_y = {}
    for i, a in enumerate(lanes):
        lane_y[a] = principal_y + i * LANE_H
    pools["__principal__"] = (POOL_X, principal_y, largura, LANE_H * len(lanes))

    for nid, n in m.nos.items():
        w, h = TAM[familia(n["kind"])]
        cx = X0 + n["col"] * COL_W + 60
        cy = lane_y[n["lane"]] + LANE_H / 2
        n["b"] = (cx - w / 2, cy - h / 2, w, h)
    return lanes, lane_y, pools, largura


def bordas(n):
    x, y, w, h = n["b"]
    return dict(l=(x, y + h / 2), r=(x + w, y + h / 2), t=(x + w / 2, y), bt=(x + w / 2, y + h),
                cx=x + w / 2, cy=y + h / 2)


def rota(m, f, lane_y, desvio_idx):
    a, b = bordas(m.nos[f["de"]]), bordas(m.nos[f["para"]])
    ca, cb = m.nos[f["de"]]["col"], m.nos[f["para"]]["col"]
    if f["principal"] and cb > ca:
        if abs(a["cy"] - b["cy"]) < 1:
            return [a["r"], b["l"]]
        meio = b["l"][0] - (COL_W - 120) / 2 if familia(m.nos[f["para"]]["kind"]) == "tarefa" \
            else b["cx"] - COL_W / 2
        if m.nos[f["de"]]["kind"] in GATEWAYS:
            # gateway abre por cima/baixo e corre na horizontal até o alvo
            sai = a["t"] if b["cy"] < a["cy"] else a["bt"]
            return [sai, (a["cx"], b["cy"]), b["l"]]
        if m.nos[f["para"]]["kind"] in GATEWAYS:
            entra = b["t"] if a["cy"] < b["cy"] else b["bt"]
            return [a["r"], (b["cx"], a["cy"]), entra]
        return [a["r"], (meio, a["cy"]), (meio, b["cy"]), b["l"]]
    # desvio: desce até a margem de baixo da lane de origem, corre e sobe/desce no alvo
    base = lane_y[m.nos[f["de"]]["lane"]] + LANE_H - 14 - 7 * (desvio_idx % 4)
    fim = b["bt"] if b["cy"] <= a["cy"] else b["t"]
    return [a["bt"], (a["cx"], base), (b["cx"], base), fim]


def rotulo_bounds(pontos, texto):
    if not texto:
        return None
    (x1, y1), (x2, y2) = pontos[0], pontos[1]
    w = min(110, 7 * len(texto) + 10)
    if abs(x1 - x2) < 1:   # primeiro trecho vertical
        return (x1 + 6, (y1 + y2) / 2 - 7, w, 14 * (1 + len(texto) // 18))
    return ((x1 + x2) / 2 - w / 2, y1 - 22, w, 14)


def xml(m, externos, dados):
    atores_ordem = list(dados.get("atores") or [])
    lanes, lane_y, pools, largura = layout(m, externos, atores_ordem)
    titulo = limpar((dados.get("layout") or {}).get("titulo") or dados.get("processo") or "Processo")

    defs = ET.Element(q("bpmn", "definitions"), {
        "id": "Definitions_1", "targetNamespace": "http://terras.ia/bpmn",
        "exporter": "terras-mapeamento-de-processos/gerar_bpmn.py", "exporterVersion": "1.0"})
    collab = ET.SubElement(defs, q("bpmn", "collaboration"), id="Collaboration_1")
    pid = {}
    ET.SubElement(collab, q("bpmn", "participant"), id="Participant_processo", name=titulo,
                  processRef="Process_1")
    for k, a in enumerate(a for a in pools if a != "__principal__"):
        pid[a] = "Participant_ext_{}".format(k + 1)
        ET.SubElement(collab, q("bpmn", "participant"), id=pid[a], name=limpar(a))
    for k, msg in enumerate(m.mensagens):
        msg["id"] = "MessageFlow_{}".format(k + 1)
        de = pid.get(msg["de"], msg["de"])
        para = pid.get(msg["para"], msg["para"])
        attrs = {"id": msg["id"], "sourceRef": de, "targetRef": para}
        if msg["nome"]:
            attrs["name"] = msg["nome"]
        ET.SubElement(collab, q("bpmn", "messageFlow"), attrs)

    proc = ET.SubElement(defs, q("bpmn", "process"), id="Process_1", name=titulo, isExecutable="false")
    if dados.get("objetivo"):
        ET.SubElement(proc, q("bpmn", "documentation")).text = str(dados["objetivo"])
    ls = ET.SubElement(proc, q("bpmn", "laneSet"), id="LaneSet_1")
    lane_id = {}
    for k, a in enumerate(lanes):
        lane_id[a] = "Lane_{}".format(k + 1)
        el = ET.SubElement(ls, q("bpmn", "lane"), id=lane_id[a], name=limpar(a))
        for nid in m.ordem:
            if m.nos[nid]["lane"] == a:
                ET.SubElement(el, q("bpmn", "flowNodeRef")).text = nid

    entra, sai = {}, {}
    for f in m.fluxos:
        sai.setdefault(f["de"], []).append(f["id"])
        entra.setdefault(f["para"], []).append(f["id"])
    for nid in m.ordem:
        n = m.nos[nid]
        attrs = {"id": nid}
        if n["nome"]:
            attrs["name"] = n["nome"]
        if nid in m.default:
            attrs["default"] = m.default[nid]
        el = ET.SubElement(proc, q("bpmn", n["kind"]), attrs)
        if n.get("doc"):
            ET.SubElement(el, q("bpmn", "documentation")).text = n["doc"]
        for fid in entra.get(nid, []):
            ET.SubElement(el, q("bpmn", "incoming")).text = fid
        for fid in sai.get(nid, []):
            ET.SubElement(el, q("bpmn", "outgoing")).text = fid
        if n.get("mensagem"):
            ET.SubElement(el, q("bpmn", "messageEventDefinition"), id="MessageEventDefinition_" + nid)
        elif n.get("timer_vazio"):
            ted = ET.SubElement(el, q("bpmn", "timerEventDefinition"), id="TimerEventDefinition_" + nid)
            if n.get("timer"):
                ET.SubElement(ted, q("bpmn", "timeDuration"), {q("xsi", "type"): "bpmn:tFormalExpression"}
                              ).text = "PT{}M".format(int(float(n["timer"])))
    for f in m.fluxos:
        attrs = {"id": f["id"], "sourceRef": f["de"], "targetRef": f["para"]}
        if f["nome"]:
            attrs["name"] = f["nome"]
        el = ET.SubElement(proc, q("bpmn", "sequenceFlow"), attrs)
        if f.get("cond") and not f.get("default"):
            ET.SubElement(el, q("bpmn", "conditionExpression"), {q("xsi", "type"): "bpmn:tFormalExpression"}
                          ).text = f["cond"]

    # ---- diagrama ----------------------------------------------------------
    diag = ET.SubElement(defs, q("bpmndi", "BPMNDiagram"), id="BPMNDiagram_1", name=titulo)
    plano = ET.SubElement(diag, q("bpmndi", "BPMNPlane"), id="BPMNPlane_1", bpmnElement="Collaboration_1")

    def shape(elem, b, horizontal=None, label=None):
        attrs = {"id": elem + "_di", "bpmnElement": elem}
        if horizontal is not None:
            attrs["isHorizontal"] = "true"
        s = ET.SubElement(plano, q("bpmndi", "BPMNShape"), attrs)
        bounds(s, b)
        if label:
            bounds(ET.SubElement(s, q("bpmndi", "BPMNLabel")), label)

    def bounds(pai, b):
        x, y, w, h = b
        ET.SubElement(pai, q("dc", "Bounds"), x=str(round(x)), y=str(round(y)),
                      width=str(round(w)), height=str(round(h)))

    shape("Participant_processo", pools["__principal__"], True)
    for a in lanes:
        shape(lane_id[a], (POOL_X + 30, lane_y[a], largura - 30, LANE_H), True)
    for a, p in pid.items():
        shape(p, pools[a], True)
    for nid in m.ordem:
        n = m.nos[nid]
        x, y, w, h = n["b"]
        label = None
        if familia(n["kind"]) != "tarefa" and n["nome"]:
            lw = 120
            linhas = 1 + len(n["nome"]) // 20
            if n["kind"] == "exclusiveGateway":   # acima: por baixo saem os desvios
                label = (x + w / 2 - lw / 2, y - 8 - 14 * linhas, lw, 14 * linhas)
            else:
                label = (x + w / 2 - lw / 2, y + h + 5, lw, 14 * linhas)
        shape(nid, n["b"], label=label)

    k = 0
    for f in m.fluxos:
        pts = rota(m, f, lane_y, k)
        if not f["principal"]:
            k += 1
        e = ET.SubElement(plano, q("bpmndi", "BPMNEdge"), id=f["id"] + "_di", bpmnElement=f["id"])
        for x, y in pts:
            ET.SubElement(e, q("di", "waypoint"), x=str(round(x)), y=str(round(y)))
        lb = rotulo_bounds(pts, f["nome"])
        if lb:
            bounds(ET.SubElement(e, q("bpmndi", "BPMNLabel")), lb)

    desloc = {}
    for msg in m.mensagens:
        no = msg["para"] if msg["de"] in pools else msg["de"]
        ext = msg["de"] if msg["de"] in pools else msg["para"]
        bx = bordas(m.nos[no])
        dx = desloc.get(no, 0)
        desloc[no] = dx + 16
        px = bx["cx"] - 8 + dx if len([1 for x in m.mensagens if no in (x["de"], x["para"])]) > 1 else bx["cx"]
        _, py, _, ph = pools[ext]
        ponta_pool = (px, py + ph)
        ponta_no = (px, bx["t"][1])
        pts = [ponta_pool, ponta_no] if msg["de"] == ext else [ponta_no, ponta_pool]
        e = ET.SubElement(plano, q("bpmndi", "BPMNEdge"), id=msg["id"] + "_di", bpmnElement=msg["id"])
        for x, y in pts:
            ET.SubElement(e, q("di", "waypoint"), x=str(round(x)), y=str(round(y)))
        if msg["nome"]:
            bounds(ET.SubElement(e, q("bpmndi", "BPMNLabel")),
                   (px + 6, py + ph + 8, 120, 14 * (1 + len(msg["nome"]) // 18)))

    ET.indent(defs, "  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(defs, encoding="unicode") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="processo.json -> BPMN 2.0 XML (.bpmn) com diagrama")
    ap.add_argument("--json", required=True)
    ap.add_argument("--saida", required=True)
    args = ap.parse_args()
    with open(args.json, encoding="utf-8") as f:
        dados = json.load(f)
    m, externos = montar(dados)
    with open(args.saida, "w", encoding="utf-8") as f:
        f.write(xml(m, externos, dados))
    kinds = {}
    for n in m.nos.values():
        kinds[n["kind"]] = kinds.get(n["kind"], 0) + 1
    resumo = ", ".join("{} {}".format(v, k) for k, v in sorted(kinds.items()))
    print("BPMN gerado: {} ({}; {} sequenceFlow, {} messageFlow)".format(
        args.saida, resumo, len(m.fluxos), len(m.mensagens)))
    print("Confira o desenho: node \"$SKILL_DIR/scripts/render_bpmn.mjs\" {}".format(args.saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())

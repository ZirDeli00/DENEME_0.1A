"""Hakan ÇELİK için yerel AI API sunucusu (harici bağımlılık olmadan)."""
from __future__ import annotations

import json
import random
import re
try:
    import requests
except Exception:  # fallback shim
    import urllib.request

    class _Resp:
        def __init__(self, code: int, text: str):
            self.status_code = code
            self._text = text

        def json(self):
            return json.loads(self._text)

    class requests:  # type: ignore
        @staticmethod
        def post(url, json=None, timeout=45):
            data = __import__("json").dumps(json or {}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return _Resp(r.getcode(), r.read().decode("utf-8"))
from dataclasses import asdict, dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "Hakan_CELIK_Chat.html"
KB_DIR = BASE_DIR / "knowledge_base"
MEMORY_FILE = BASE_DIR / ".hakan_memory.json"
MAX_HISTORY = 10
HOST = "0.0.0.0"
PORT = 8000
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


@dataclass
class SessionState:
    history: list[dict[str, str]] = field(default_factory=list)
    name: str | None = None
    preferences: list[str] = field(default_factory=list)
    goal: str | None = None
    mood: str | None = None
    last_intent: str | None = None
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


def _normalize(text: str) -> str:
    mapping = str.maketrans("çğıöşü", "cgiosu")
    return re.sub(r"\s+", " ", text.lower().translate(mapping)).strip()


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9çğıöşüÇĞİÖŞÜ]{3,}", _normalize(text)))


def _load_kb_chunks() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    for file in KB_DIR.glob("*.txt"):
        content = file.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            line = line.strip()
            if len(line) > 20:
                chunks.append({"source": file.name, "text": line})
    return chunks


KB_CHUNKS = _load_kb_chunks()


def _rank_relevant_chunks(query: str, top_k: int = 3) -> list[dict[str, str]]:
    q_tokens = _tokenize(query)
    scored: list[tuple[int, dict[str, str]]] = []
    for chunk in KB_CHUNKS:
        score = len(q_tokens & _tokenize(chunk["text"]))
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def _intent_scores(text: str) -> dict[str, float]:
    n = _normalize(text)
    scores = {
        "planning": 0.1,
        "decision": 0.1,
        "emotional": 0.1,
        "memory": 0.1,
        "knowledge": 0.2,
        "calculation": 0.1,
        "general": 0.3,
    }
    patterns = {
        "planning": ["plan", "hedef", "duzen", "program", "calisma"],
        "decision": ["karars", "secem", "hangisi", "karar"],
        "emotional": ["uzgun", "stres", "kaygi", "bunald", "yorgun"],
        "memory": ["hatir", "adim", "beni taniyor"],
        "knowledge": ["nedir", "nasil", "acikla", "anlat", "python", "yapay zeka"],
        "calculation": ["hesapla", "kac eder"],
    }
    for intent, kws in patterns.items():
        for kw in kws:
            if kw in n:
                scores[intent] += 0.35
    if re.search(r"\d+\s*[+\-*/]", n):
        scores["calculation"] += 0.6
    for key in scores:
        scores[key] += random.uniform(0, 0.05)
    return scores


def _pick_intent(text: str) -> tuple[str, float]:
    n = _normalize(text)
    if any(k in n for k in ["plan", "hedef", "program", "duzen"]):
        return "planning", 0.9
    if any(k in n for k in ["karars", "secem", "karar"]):
        return "decision", 0.9
    if any(k in n for k in ["uzgun", "stres", "kaygi", "bunald"]):
        return "emotional", 0.88
    if re.search(r"\d+\s*[+\-*/]", n):
        return "calculation", 0.95

    scores = _intent_scores(text)
    intent = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = scores[intent] / total if total else 0.0
    return intent, confidence


def _extract_name(text: str) -> str | None:
    m = re.search(r"(?:benim adim|adim|ismim)\s+([A-Za-zÇĞİÖŞÜçğıöşü]{2,})", text, flags=re.IGNORECASE)
    if not m:
        return None
    name = m.group(1)
    return name[:1].upper() + name[1:].lower()


def _calculate(text: str) -> str | None:
    expr_match = re.findall(r"[0-9+\-*/().\s]+", text)
    if not expr_match:
        return None
    expr = "".join(expr_match).strip()
    if not expr or not any(c.isdigit() for c in expr):
        return None
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
        return None
    try:
        result = eval(expr, {"__builtins__": {}}, {})
    except Exception:
        return "İşlemi çözerken bir hata oldu. Örn: (12+8)/2"
    if isinstance(result, (int, float)):
        return f"Sonuç: {result}"
    return "İşlem sonucunu yorumlayamadım."


def _load_memories() -> dict[str, Any]:
    if not MEMORY_FILE.exists():
        return {}
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_memories(data: dict[str, Any]) -> None:
    MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


SESSION_STORE: dict[str, SessionState] = {}
for sid, payload in _load_memories().items():
    SESSION_STORE[sid] = SessionState(**payload)


def _session(session_id: str) -> SessionState:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = SessionState()
    return SESSION_STORE[session_id]


def _persist_all() -> None:
    _save_memories({sid: asdict(state) for sid, state in SESSION_STORE.items()})


def _build_prompt(message: str, state: SessionState, intent: str, chunks: list[dict[str, str]]) -> str:
    history_lines = []
    for item in state.history[-(MAX_HISTORY * 2):]:
        role = "Kullanıcı" if item["role"] == "user" else "Asistan"
        history_lines.append(f"{role}: {item['content']}")
    history_text = "\n".join(history_lines) if history_lines else "(geçmiş yok)"

    kb_text = "\n".join(f"- {c['text']}" for c in chunks) if chunks else "(ilgili bilgi bulunamadı)"

    return f"""Sen Hakan ÇELİK isimli Türkçe konuşan yardımcı AI asistansın.
- Kısa, net ve faydalı cevap ver.
- Kullanıcının niyetini dikkate al (intent: {intent}).
- Uydurma bilgi verme; varsa verilen bilgi tabanını kullan.
- Cevabında debug/teknik etiketler veya [Niyet analizi: ...] gibi metinler kullanma.

Kullanıcı profili:
- Ad: {state.name or 'bilinmiyor'}
- Hedef: {state.goal or 'bilinmiyor'}
- Duygu durumu: {state.mood or 'bilinmiyor'}
- Tercihler: {', '.join(state.preferences[-3:]) if state.preferences else 'yok'}

Son konuşma bağlamı:
{history_text}

Bilgi tabanı alıntıları (RAG):
{kb_text}

Yeni kullanıcı mesajı:
{message}

Sadece nihai cevabı üret."""


def _call_ollama(prompt: str) -> str | None:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=45,
        )
        if response.status_code != 200:
            return None
        data = response.json()
        text = str(data.get("response", "")).strip()
        return text or None
    except Exception:
        return None


def _fallback_reply(message: str, intent: str, state: SessionState, chunks: list[dict[str, str]]) -> str:
    if intent == "memory":
        return f"Evet, seni hatırlıyorum. Adın: {state.name or 'henüz paylaşılmadı'}. Son hedefin: {state.goal or 'henüz kaydedilmedi'}."
    if intent == "calculation":
        return _calculate(message) or "Hesaplama için bir ifade göremedim."
    if intent == "planning":
        return "Bunu 3 adımda planlayalım:\n1) Net hedefi tek cümleye indir.\n2) İlk 25 dakikalık görevi seç.\n3) Bittiğinde sonucu yaz, bir sonraki adımı optimize edelim."
    if intent == "decision":
        return "Kararı netleştirmek için A/B seçeneklerini yaz. Her biri için + fayda / - maliyet / risk puanı ver."
    if intent == "emotional":
        return "Seni anlıyorum. Önce 4-4-6 nefes döngüsü yap, sonra tek bir küçük göreve odaklanalım."
    if chunks:
        return "Sorunu buna göre yorumladım:\n" + "\n".join(f"- {c['text']}" for c in chunks[:2])
    return "Sorunu anladım. Biraz daha hedefini yazarsan daha güçlü cevap verebilirim."


def _reason_and_respond(message: str, state: SessionState) -> tuple[str, str, float, list[dict[str, str]]]:
    intent, confidence = _pick_intent(message)
    chunks = _rank_relevant_chunks(message)

    name = _extract_name(message)
    if name:
        state.name = name
    if "severim" in _normalize(message) or "tercih" in _normalize(message):
        state.preferences.append(message[:120])
        state.preferences = state.preferences[-8:]
    if intent == "planning":
        state.goal = message
    if intent == "emotional":
        state.mood = "destek_istiyor"

    prompt = _build_prompt(message, state, intent, chunks)
    llm_answer = _call_ollama(prompt)
    answer = llm_answer or _fallback_reply(message, intent, state, chunks)

    reasoning_summary = f"Niyet analizi: {intent}, güven: %{round(confidence * 100)}"
    state.last_intent = intent
    state.updated_at = datetime.now().isoformat(timespec="seconds")
    state.history.append({"role": "user", "content": message})
    state.history.append({"role": "assistant", "content": answer})
    state.history = state.history[-(MAX_HISTORY * 2):]
    return answer, reasoning_summary, confidence, chunks


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html: str, status: int = 200) -> None:
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path or "/"
        if route in ("", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path or "/"
        if route in ("", "/"):
            self._send_html(HTML_PATH.read_text(encoding="utf-8"))
            return
        if route.startswith("/api/memory/"):
            sid = unquote(route.rsplit("/", 1)[-1])
            state = _session(sid)
            self._send_json(
                {
                    "name": state.name,
                    "goal": state.goal,
                    "mood": state.mood,
                    "preferences": state.preferences[-3:],
                    "last_intent": state.last_intent,
                    "history_items": len(state.history),
                    "updated_at": state.updated_at,
                }
            )
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path or "/"
        if route != "/api/chat":
            self._send_json({"error": "Not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw)
        except Exception:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return
        session_id = str(body.get("session_id", "")).strip()
        message = str(body.get("message", "")).strip()
        if not session_id or not message:
            self._send_json({"error": "session_id and message are required"}, status=400)
            return

        state = _session(session_id)
        answer, reasoning, confidence, chunks = _reason_and_respond(message, state)
        _persist_all()
        self._send_json(
            {
                "reply": answer,
                "reasoning_summary": reasoning,
                "confidence": round(confidence, 3),
                "memory": {
                    "name": state.name,
                    "goal": state.goal,
                    "mood": state.mood,
                    "preferences": state.preferences[-3:],
                    "last_intent": state.last_intent,
                    "history_items": len(state.history),
                },
                "sources": chunks,
            }
        )


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Hakan ÇELİK server running at http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

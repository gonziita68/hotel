import json
from urllib import request as urlrequest
from urllib.error import URLError
from django.conf import settings


class IAServiceError(Exception):
    pass


class IAServiceNotConfigured(IAServiceError):
    pass


def call_n8n_ia_analyst(payload: dict) -> dict:
    url = getattr(settings, "N8N_IA_WEBHOOK_URL", None)
    if not url:
        raise IAServiceNotConfigured("N8N_IA_WEBHOOK_URL not configured")
    body = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urlrequest.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            ctype = (resp.headers.get("Content-Type", "") or "").lower()
    except URLError as exc:
        raise IAServiceError(f"Error calling n8n: {exc}")

    # Intentar parseo JSON estricto
    data = None
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            # Si no es JSON, evaluar texto
            text = raw.strip()
            if "workflow was started" in text.lower():
                raise IAServiceError("El webhook respondió inmediatamente. Configura 'Respond to Webhook' al final del flujo para devolver JSON.")
            # Si el texto parece ser JSON con comillas simples, intentar normalizar
            if text.startswith("{") and "'" in text and '"' not in text:
                try:
                    data = json.loads(text.replace("'", '"'))
                except Exception:
                    pass
    # Si tenemos JSON, buscar claves comunes
    if isinstance(data, dict):
        def pick(d: dict, keys):
            for k in keys:
                if k in d and d[k] is not None:
                    return d[k]
            return None
        answer = pick(data, ["answer", "message", "text", "data", "output", "body"])
        recos = pick(data, ["recommendations", "recs", "suggestions", "tips"])
        if isinstance(recos, str):
            recos = [recos] if recos else []
        if answer is not None:
            return {"answer": str(answer), "recommendations": recos or []}
        # Quizás anidado en 'result'
        result = data.get("result") if isinstance(data.get("result"), dict) else None
        if result:
            answer = pick(result, ["answer", "message", "text"])
            recos = pick(result, ["recommendations", "recs", "suggestions", "tips"]) or []
            if answer is not None:
                if isinstance(recos, str):
                    recos = [recos]
                return {"answer": str(answer), "recommendations": recos}
    raise IAServiceError("El webhook no devolvió JSON utilizable (faltan claves como 'answer').")
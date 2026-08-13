"""Agent orchestrator — ReAct-style loop with a visible step log."""

from __future__ import annotations
import sqlite3
from datetime import datetime
from .. import config
from . import tools, translate

INTENT_RUNNERS = {
    "find_messages_mentioning": lambda c, p: tools.find_messages_mentioning(
        c, p.get("entity", ""), p.get("since"), p.get("until")
    ),
    "most_active_contact": lambda c, p: tools.most_active_contact(
        c, p.get("since"), p.get("until"), bool(p.get("night_only"))
    ),
    "find_files_similar_to": lambda c, p: tools.find_files_similar_to(
        c, int(p.get("file_id") or 0)
    ),
    "files_modified_after": lambda c, p: tools.files_modified_after(
        c, p.get("ts", config.SEIZURE_ISO)
    ),
}

def _fmt_ts(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %H:%M")
    except ValueError:
        return iso

def _format_results(intent: str, results) -> dict:
    if intent == "find_messages_mentioning":
        n = len(results)
        convs = sorted({r["conversation"] for r in results})
        summary = f"{n} message(s) found across {len(convs)} conversation(s)." if results else "No messages matched."
        return {"summary": summary, "items": results}
    if intent == "most_active_contact":
        return {
            "summary": f"Most active contact: {results[0]['contact']} ({results[0]['count']} messages)." if results else "No message activity.",
            "items": results,
        }
    if intent == "find_files_similar_to":
        return {
            "summary": f"{len(results)} similar image(s) found." if results else "No similar images.",
            "items": results,
        }
    if intent == "files_modified_after":
        return {
            "summary": f"{len(results)} file(s) modified after the cutoff.",
            "items": results,
        }
    if intent == "unsupported":
        return {"summary": "This system doesn't have a rule for that type of question yet", "items": []}
    return {"summary": "Case summary.", "items": []}

def run_query(conn: sqlite3.Connection, question: str, llm_client=None) -> dict:
    reasoning_log = []
    
    plan = translate.template_translate(conn, question)
    for i, step in enumerate(plan.get("steps", [])):
        reasoning_log.append({"step": i+1, "phase": "plan", "title": "Plan", "detail": step})
        
    intent = plan["intent"]
    runner = INTENT_RUNNERS.get(intent)
    
    results = []
    if runner:
        try:
            results, step_desc = runner(conn, plan.get("params", {}))
            reasoning_log.append({"step": len(reasoning_log)+1, "phase": "execute", "title": step_desc, "detail": f"Tool returned {len(results)} result(s)."})
        except Exception as exc:
            reasoning_log.append({"step": len(reasoning_log)+1, "phase": "execute", "title": "Tool failed", "detail": str(exc)})
            intent = "case_summary"
            
    formatted = _format_results(intent, results)
    reasoning_log.append({"step": len(reasoning_log)+1, "phase": "answer", "title": "Answer", "detail": formatted["summary"]})
    
    return {
        "question": question,
        "answer": formatted["summary"],
        "results": formatted["items"],
        "reasoning_log": reasoning_log,
        "source": "template",
        "intent": intent,
    }

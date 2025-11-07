import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

DEFAULT_STATE_FILENAME = "signal_state.json"

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def _parse_iso8601(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        logging.warning(f"Unable to parse timestamp: {value}")
        return None

def load_signal_state(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        logging.error(f"Signal state file {path} is corrupted. Starting fresh.")
        return {}
    except Exception as exc:
        logging.error(f"Failed to load signal state from {path}: {exc}")
        return {}

def save_signal_state(state: Dict[str, Any], path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    try:
        with open(path, "w") as handle:
            json.dump(state, handle, indent=2)
    except Exception as exc:
        logging.error(f"Failed to persist signal state to {path}: {exc}")

def get_previous_state(state_store: Dict[str, Any], symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
    return state_store.get(symbol, {}).get(timeframe)

def update_state(state_store: Dict[str, Any], symbol: str, timeframe: str, info: Dict[str, Any]) -> None:
    state_store.setdefault(symbol, {})[timeframe] = info

def should_send_notification(previous: Optional[Dict[str, Any]],
                             current: Optional[Dict[str, Any]],
                             cooldown_hours: float) -> bool:
    if current is None or current.get("state") == "neutral":
        return False
    
    if previous is None:
        return True
    
    state_changed = previous.get("state") != current.get("state")
    fresh_cross_now = current.get("is_fresh_cross", False)
    was_fresh = previous.get("is_fresh_cross", False)
    
    if state_changed or (fresh_cross_now and not was_fresh):
        return True
    
    if cooldown_hours and cooldown_hours > 0:
        last_notified = _parse_iso8601(previous.get("last_notified_at"))
        if not last_notified:
            return True
        if _utcnow() - last_notified >= timedelta(hours=cooldown_hours):
            return True
    
    return False

def format_timeframe_label(timeframe: str) -> str:
    mapping = {
        "1d": "Daily",
        "4h": "4-Hour"
    }
    return mapping.get(timeframe, timeframe)

def build_signal_message(symbol: str,
                         timeframe: str,
                         state_info: Dict[str, Any],
                         near_threshold_pct: float) -> str:
    headline = "Golden cross active"
    if state_info.get("state") == "near":
        headline = f"SMAs within {state_info.get('spread_pct', 0):.2f}%"
    if state_info.get("is_fresh_cross"):
        headline = "Fresh golden cross 🔔"
    
    slope = state_info.get("sma128_slope", "flat")
    spread = state_info.get("spread_pct", 0.0)
    close = state_info.get("close", 0.0)
    sma50 = state_info.get("sma50", 0.0)
    sma128 = state_info.get("sma128", 0.0)
    
    timeframe_label = format_timeframe_label(timeframe)
    lines = [
        f"{symbol} {timeframe_label}: {headline}",
        f"Close {close:.2f} | SMA50 {sma50:.2f} vs SMA128 {sma128:.2f}",
        f"Spread {spread:.2f}% (near ≤ {near_threshold_pct:.2f}%) | 128 SMA {slope}"
    ]
    return "\n".join(lines)

def build_alignment_message(symbol: str,
                            fast_timeframe: str,
                            fast_state: Dict[str, Any],
                            slow_timeframe: str,
                            slow_state: Dict[str, Any]) -> str:
    fast_label = format_timeframe_label(fast_timeframe)
    slow_label = format_timeframe_label(slow_timeframe)
    return (
        f"{symbol}: {fast_label} signal aligns with {slow_label} trend.\n"
        f"{fast_label}: {fast_state.get('state')} | {slow_label}: {slow_state.get('state')}"
    )

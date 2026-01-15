import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


class FFProbeError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProbeResult:
    duration: timedelta | None
    creation_time: datetime | None


def _parse_creation_time(value: str) -> datetime | None:
    """
    Parses ffprobe's string and returns datetime for creation_time.
    """
    value = value.strip()
    if not value:
        return None

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def probe_video(path_or_url: str, timeout_s: float = 20.0) -> ProbeResult:
    """
    Extract duration and creation time via ffprobe.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:format_tags=creation_time",
        "-of",
        "json",
        path_or_url,
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        raise FFProbeError(f"ffprobe failed to run: {e}") from e

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        raise FFProbeError(f"ffprobe returned {proc.returncode}: {stderr}")

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise FFProbeError(f"ffprobe output is not valid JSON: {e}") from e

    fmt = payload.get("format") or {}
    duration_raw = fmt.get("duration")
    tags = fmt.get("tags") or {}
    creation_time_raw = tags.get("creation_time")

    duration: timedelta | None = None
    if duration_raw is not None:
        try:
            duration = timedelta(seconds=float(duration_raw))
        except (TypeError, ValueError):
            duration = None

    creation_time = None
    if isinstance(creation_time_raw, str):
        creation_time = _parse_creation_time(creation_time_raw)

    return ProbeResult(duration=duration, creation_time=creation_time)

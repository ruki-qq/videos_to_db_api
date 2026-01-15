import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_video(client: AsyncClient):
    payload = {
        "video_path": "/videos/camera1/clip1.mp4",
        "start_time": "2024-01-01T00:00:00Z",
        "duration": 120,
        "camera_number": 1,
        "location": "Gate A",
    }

    response = await client.post("/videos", json=payload)
    assert response.status_code == 201
    created = response.json()

    assert created["status"] == "new"
    assert created["video_path"] == payload["video_path"]

    fetched = await client.get(f"/videos/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_create_video_without_start_time_and_duration_uses_ffprobe(
    client: AsyncClient, monkeypatch
):
    from datetime import datetime, timedelta, timezone

    from app.utils.ffprobe import ProbeResult

    def fake_probe(_path: str):
        return ProbeResult(
            duration=timedelta(seconds=10),
            creation_time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

    monkeypatch.setattr("app.services.video.probe_video", fake_probe)

    payload = {
        "video_path": "http://example.com/video.mp4",
        "camera_number": 1,
        "location": "Net",
    }

    response = await client.post("/videos", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["duration"] == "PT10S"
    # SQLite may lose timezone info
    assert created["start_time"] in (
        "2024-01-01T12:00:00",
        "2024-01-01T12:00:00Z",
        "2024-01-01T12:00:00+00:00",
    )


@pytest.mark.asyncio
async def test_filters_and_status_update(client: AsyncClient):
    base_payload = {
        "video_path": "/videos/camera{cam}/clip{idx}.mp4",
        "duration": 60,
        "location": "Gate B",
    }

    video1 = {
        "video_path": base_payload["video_path"].format(cam=1, idx=1),
        "start_time": "2024-01-01T01:00:00Z",
        "duration": base_payload["duration"],
        "camera_number": 1,
        "location": base_payload["location"],
    }
    video2 = {
        "video_path": base_payload["video_path"].format(cam=2, idx=2),
        "start_time": "2024-01-02T01:00:00Z",
        "duration": base_payload["duration"],
        "camera_number": 2,
        "location": "Lobby",
    }

    created1 = (await client.post("/videos", json=video1)).json()
    created2 = (await client.post("/videos", json=video2)).json()

    update_resp = await client.patch(
        f"/videos/{created2['id']}/status", json={"status": "recognized"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "recognized"

    status_filtered = await client.get("/videos", params={"status": ["recognized"]})
    assert status_filtered.status_code == 200
    assert len(status_filtered.json()) == 1
    assert status_filtered.json()[0]["id"] == created2["id"]

    camera_filtered = await client.get(
        "/videos", params={"camera_number": [created1["camera_number"]]}
    )
    assert camera_filtered.status_code == 200
    assert len(camera_filtered.json()) == 1
    assert camera_filtered.json()[0]["id"] == created1["id"]

    time_filtered = await client.get(
        "/videos",
        params={
            "start_time_from": "2024-01-02T00:00:00Z",
            "start_time_to": "2024-01-02T02:00:00Z",
        },
    )
    assert time_filtered.status_code == 200
    assert len(time_filtered.json()) == 1
    assert time_filtered.json()[0]["id"] == created2["id"]


@pytest.mark.asyncio
async def test_not_found_status_update(client: AsyncClient):
    response = await client.patch("/videos/999/status", json={"status": "transcoded"})
    assert response.status_code == 404

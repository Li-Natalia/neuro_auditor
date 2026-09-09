"""Unit tests for the Yandex AI Studio client (Responses API wrapper)."""
from types import SimpleNamespace

import pytest

openai = pytest.importorskip("openai")
httpx = pytest.importorskip("httpx")

from app.ai.yandex_client import Artifact, YandexGPTClient, YandexReply  # noqa: E402


def _resp(text="ok", rid="resp_1", output=None):
    return SimpleNamespace(output_text=text, id=rid, output=output or [])


def _client():
    return YandexGPTClient(
        api_key="key",
        folder_id="b1gtest",
        base_url="https://ai.api.cloud.yandex.net/v1",
        model="yandexgpt/latest",
        ci_model="qwen3-235b-a22b-fp8/latest",
    )


def test_client_uses_project_and_no_folder_header():
    c = _client()
    assert c._client.project == "b1gtest"
    assert "x-folder-id" not in {k.lower() for k in c._client.default_headers}
    assert c._model_uri == "gpt://b1gtest/yandexgpt/latest"
    assert c._ci_model_uri == "gpt://b1gtest/qwen3-235b-a22b-fp8/latest"


def test_respond_passes_previous_response_id(monkeypatch):
    c = _client()
    calls = []

    def fake_create(**params):
        calls.append(params)
        return _resp("привет", "resp_9")

    monkeypatch.setattr(c._client.responses, "create", fake_create)
    reply = c.respond("вопрос", "системный промпт", "resp_8")

    assert reply == YandexReply("привет", "resp_9", False, ())
    params = calls[0]
    assert params["previous_response_id"] == "resp_8"
    assert params["instructions"] == "системный промпт" and params["input"] == "вопрос"
    assert params["model"] == "gpt://b1gtest/yandexgpt/latest"


def test_stale_previous_id_retries_without_it(monkeypatch):
    c = _client()
    calls = []

    def fake_create(**params):
        calls.append(params)
        if "previous_response_id" in params:
            raise openai.NotFoundError(
                "stale",
                response=httpx.Response(404, request=httpx.Request("POST", "https://example")),
                body=None,
            )
        return _resp("свежий ответ", "resp_new")

    monkeypatch.setattr(c._client.responses, "create", fake_create)
    reply = c.respond("вопрос", "sys", "resp_old")

    assert reply.text == "свежий ответ" and reply.response_id == "resp_new"
    assert reply.context_reset is True
    assert "previous_response_id" in calls[0] and "previous_response_id" not in calls[1]


def test_upload_file_sends_original_filename(monkeypatch, tmp_path):
    c = _client()
    calls = []
    stored = tmp_path / "20260908122303_sample_rsbu_c21a0ecc.xlsx"
    stored.write_bytes(b"xlsx")

    def fake_create(**params):
        calls.append(params)
        return SimpleNamespace(id="file_1")

    monkeypatch.setattr(c._client.files, "create", fake_create)

    assert c.upload_file(str(stored), purpose="user_data", filename="sample_rsbu.xlsx") == "file_1"
    assert calls[0]["file"][0] == "sample_rsbu.xlsx" and calls[0]["purpose"] == "user_data"
    # without an explicit name the on-disk (storage) name is used
    c.upload_file(str(stored), purpose="user_data")
    assert calls[1]["file"][0] == stored.name


def test_code_interpreter_tools_and_artifacts(monkeypatch):
    c = _client()
    calls = []
    annotation = SimpleNamespace(type="container_file_citation", file_id="file_a", filename="chart.png")
    message = SimpleNamespace(type="message", content=[SimpleNamespace(annotations=[annotation])])
    call = SimpleNamespace(type="code_interpreter_call", code="print(1)")

    def fake_create(**params):
        calls.append(params)
        return _resp("готово", "resp_ci", output=[call, message])

    monkeypatch.setattr(c._client.responses, "create", fake_create)
    reply = c.respond_with_code_interpreter("вопрос", "sys", file_ids=["file_0"])

    params = calls[0]
    assert params["model"] == "gpt://b1gtest/qwen3-235b-a22b-fp8/latest"
    assert params["tools"] == [
        {"type": "code_interpreter", "container": {"type": "auto", "file_ids": ["file_0"]}}
    ]
    assert params["include"] == ["code_interpreter_call.outputs"]
    assert reply.artifacts == (Artifact("file_a", "chart.png"),)

from pathlib import Path

from dataforge.ingestion.readers import discover_sources, read_source


def test_discover_sources_returns_stable_supported_file_list(tmp_path: Path):
    (tmp_path / "z.csv").write_text("value\n1\n", encoding="utf-8")
    (tmp_path / "a.jsonl").write_text('{"value":2}\n', encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("ignored", encoding="utf-8")

    sources = discover_sources(tmp_path)

    assert [source.path.name for source in sources] == ["a.jsonl", "z.csv"]
    assert all(len(source.sha256) == 64 for source in sources)
    assert all(source.size_bytes > 0 for source in sources)


def test_read_csv_and_jsonl(tmp_path: Path):
    csv_path = tmp_path / "records.csv"
    jsonl_path = tmp_path / "records.jsonl"
    csv_path.write_text("id,value\n1,alpha\n", encoding="utf-8")
    jsonl_path.write_text('{"id":2,"value":"beta"}\n', encoding="utf-8")

    sources = discover_sources(tmp_path)
    csv_source = next(source for source in sources if source.format == "csv")
    jsonl_source = next(source for source in sources if source.format == "jsonl")

    assert read_source(csv_source).iloc[0]["value"] == "alpha"
    assert read_source(jsonl_source).iloc[0]["value"] == "beta"

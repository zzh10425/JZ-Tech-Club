#!/usr/bin/env python3
"""Generate static member sections from the CSV source files."""

from __future__ import annotations

import csv
import html
import os
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PEOPLE_CSV = ROOT / "data" / "people.csv"
HIDE_CSV = ROOT / "data" / "people_hide.csv"
INDEX_HTML = ROOT / "index.html"
PEOPLE_HTML = ROOT / "people.html"
DIST = ROOT / "dist"
PUBLIC_HTML_FILES = (
    Path("404.html"),
    Path("awcyvan.html"),
    Path("clock.html"),
    Path("eyes.html"),
    Path("memorygame.html"),
    Path("zen.html"),
)
PRIVATE_OUTPUT_DIRS = (Path("data"), Path("scripts"), Path(".git"))
PRIVATE_OUTPUT_FILES = (Path("README.md"), Path(".gitignore"))
PRIVATE_OUTPUT_BASENAMES = {"people.csv", "people_hide.csv"}


def private_artifacts(output_dir: Path) -> list[Path]:
    """Return known source/private paths found under the generated output."""
    found: set[Path] = set()
    for directory in PRIVATE_OUTPUT_DIRS:
        target = output_dir / directory
        if target.exists():
            if directory == Path("data"):
                for path in target.rglob("*"):
                    if path.is_file():
                        found.add(path.relative_to(output_dir))
            else:
                found.add(directory)

    for relative in PRIVATE_OUTPUT_FILES:
        if (output_dir / relative).exists():
            found.add(relative)
    for path in output_dir.rglob("*.py"):
        if path.is_file():
            found.add(path.relative_to(output_dir))
    for path in output_dir.rglob("*"):
        if path.is_file() and path.name in PRIVATE_OUTPUT_BASENAMES:
            found.add(path.relative_to(output_dir))
    return sorted(found, key=lambda path: path.as_posix())


def check_private_artifacts(output_dir: Path) -> None:
    """Warn locally or remove and verify private paths in Cloudflare builds."""
    is_cloudflare = os.environ.get("JZ_CLOUDFLARE_BUILD", "").lower() == "true"
    artifacts = private_artifacts(output_dir)
    if is_cloudflare:
        print("Cloudflare build mode enabled.")
        print("Cleaning private build artifacts...")
        # All deletion targets are constructed beneath output_dir; never touch source paths.
        for artifact in artifacts:
            target = output_dir / artifact
            if not target.resolve().is_relative_to(output_dir.resolve()):
                raise RuntimeError(f"Refusing to clean a path outside the build output: {target}")
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()

        data_dir = output_dir / "data"
        if data_dir.is_dir() and not any(data_dir.iterdir()):
            data_dir.rmdir()

        remaining = private_artifacts(output_dir)
        if remaining:
            paths = ", ".join(path.as_posix() for path in remaining)
            raise RuntimeError(f"Private build artifacts remain after Cloudflare cleanup: {paths}")
        print("Private build artifacts: none")
        return

    if artifacts:
        print("WARNING: Private build artifacts detected:")
        for artifact in artifacts:
            print(f"  - {output_dir.name}/{artifact.as_posix()}")
        print("WARNING: private source data exists in the build output.")
        print("This is not a Cloudflare build, so no files were removed.")
        print("Set JZ_CLOUDFLARE_BUILD=true only in the Cloudflare Pages build environment")
        print("to enable automatic cleanup.")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return [
            {key.strip(): (value or "").strip() for key, value in row.items() if key}
            for row in csv.DictReader(source)
        ]


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def visible(record: dict[str, str], hidden: dict[str, str], field: str) -> bool:
    return hidden.get(field) != "hide"


def record_year(record: dict[str, str], hidden: dict[str, str]) -> str:
    if not visible(record, hidden, "年级"):
        return "未注明年份"
    year = record.get("年级", "")
    if year:
        return year
    if visible(record, hidden, "补充信息"):
        match = re.search(r"\d{4}级", record.get("补充信息", ""))
        if match:
            return match.group(0)
    return "未注明年份"


def descriptor(record: dict[str, str], hidden: dict[str, str]) -> str:
    values = []
    for field in ("年级", "职位"):
        value = record.get(field, "")
        if value and visible(record, hidden, field):
            values.append(value)
    return " · ".join(values)


def info_html(record: dict[str, str], hidden: dict[str, str], *, old: bool) -> str:
    paragraphs: list[str] = []
    fields = (("自述", "旧站自述：" if old else ""), ("补充信息", ""), ("QQ", "QQ: "), ("Email", "Email: "))
    for field, prefix in fields:
        value = record.get(field, "")
        if value and visible(record, hidden, field):
            paragraphs.append(f"<p>{escape(prefix + value)}</p>")
    url = record.get("链接", "")
    if url and visible(record, hidden, "链接"):
        label = record.get("链接说明", "") if visible(record, hidden, "链接说明") else ""
        label = label or url
        external = url.startswith(("http://", "https://"))
        attributes = ' target="_blank" rel="noopener"' if external else ""
        paragraphs.append(f'<p><a href="{escape(url)}"{attributes}>{escape(label)}</a></p>')
    if not paragraphs:
        return ""
    return '<div class="archive-info">' + "".join(paragraphs) + "</div>"


def past_record_html(record: dict[str, str], hidden: dict[str, str]) -> str:
    name = record.get("姓名", "") if visible(record, hidden, "姓名") else ""
    name = name or "成员"
    desc = descriptor(record, hidden)
    suffix = f" <span>{escape(desc)}</span>" if desc else ""
    return (
        '<details class="archive-person">'
        f"<summary>{escape(name)}{suffix}</summary>"
        f"{info_html(record, hidden, old=True)}"
        "</details>"
    )


def current_record_html(record: dict[str, str], hidden: dict[str, str]) -> str:
    name = record.get("姓名", "") if visible(record, hidden, "姓名") else ""
    name = name or "成员"
    return (
        '<div class="archive-person">'
        f'<p class="member-entry-heading">{escape(name)}</p>'
        f"{info_html(record, hidden, old=False)}"
        "</div>"
    )


def year_sort_key(year: str) -> tuple[int, int | str]:
    match = re.fullmatch(r"(\d{4})级", year)
    if match:
        return (0, -int(match.group(1)))
    return (1, year)


def render_current(records: list[dict[str, str]], hide_by_id: dict[str, dict[str, str]], current_year: int) -> str:
    groups: dict[str, list[dict[str, str]]] = {"社长": [], "副社长": [], "特殊成员": [], "普通成员": []}
    for record in records:
        hidden = hide_by_id.get(record.get("序号", ""), {})
        if hidden.get("类别") == "hide" or record_year(record, hidden) != f"{current_year}级":
            continue
        role = record.get("职位", "") if visible(record, hidden, "职位") else ""
        if role in ("社长", "副社长"):
            groups[role].append(record)
        elif role == "特殊":
            groups["特殊成员"].append(record)
        else:
            groups["普通成员"].append(record)

    output: list[str] = []
    for label in ("社长", "副社长", "特殊成员"):
        if not groups[label]:
            continue
        output.append(f"<h3>{escape(label)}</h3>")
        output.append('<div class="archive-list">')
        for record in groups[label]:
            hidden = hide_by_id.get(record.get("序号", ""), {})
            output.append(current_record_html(record, hidden))
        output.append("</div>")

    ordinary = groups["普通成员"]
    if ordinary:
        output.append('<details class="archive-year">')
        output.append(f"<summary>普通成员（{len(ordinary)}）</summary>")
        output.append('<div class="archive-list">')
        for record in ordinary:
            hidden = hide_by_id.get(record.get("序号", ""), {})
            output.append(current_record_html(record, hidden))
        output.append("</div></details>")
    return "\n        ".join(output)


def render_past(
    records: list[dict[str, str]], hide_by_id: dict[str, dict[str, str]], current_year: int
) -> str:
    years: dict[str, list[dict[str, str]]] = {}
    for record in records:
        hidden = hide_by_id.get(record.get("序号", ""), {})
        if hidden.get("类别") == "hide":
            continue
        year = record_year(record, hidden)
        match = re.fullmatch(r"(\d{4})级", year)
        if match and int(match.group(1)) >= current_year:
            continue
        years.setdefault(year, []).append(record)

    output: list[str] = []
    for year in sorted(years, key=year_sort_key):
        output.append('<details class="archive-year">')
        output.append(f"<summary>{escape(year)}</summary>")
        output.append('<div class="archive-list">')
        for record in years[year]:
            hidden = hide_by_id.get(record.get("序号", ""), {})
            output.append(past_record_html(record, hidden))
        output.append("</div></details>")
    return "\n        ".join(output)


def replace_region(document: str, name: str, content: str) -> str:
    start = f"<!-- PEOPLE:{name}:START -->"
    end = f"<!-- PEOPLE:{name}:END -->"
    if document.count(start) != 1 or document.count(end) != 1:
        raise ValueError(f"Expected exactly one marker pair for {name}")
    start_at = document.index(start) + len(start)
    end_at = document.index(end, start_at)
    return document[:start_at] + "\n        " + content + "\n        " + document[end_at:]


def replace_leader(document: str, role: str, name: str) -> str:
    start = f"<!-- PEOPLE:{role}:START -->"
    end = f"<!-- PEOPLE:{role}:END -->"
    if document.count(start) != 1 or document.count(end) != 1:
        raise ValueError(f"Expected exactly one marker pair for {role}")
    start_at = document.index(start) + len(start)
    end_at = document.index(end, start_at)
    return document[:start_at] + escape(name or "待补充") + document[end_at:]


def generate(output_dir: Path = DIST) -> int:
    """Generate the deployable site into ``output_dir`` and return the period year."""
    output_dir = Path(output_dir)
    if DIST.is_symlink() or output_dir.resolve() != DIST.resolve():
        raise ValueError(f"output_dir must be the dist directory: {DIST}")
    is_cloudflare = os.environ.get("JZ_CLOUDFLARE_BUILD", "").lower() == "true"
    if is_cloudflare and output_dir.exists():
        print("Cloudflare build mode enabled; preparing a clean dist directory.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = read_csv(PEOPLE_CSV)
    hidden_records = read_csv(HIDE_CSV) if HIDE_CSV.exists() else []
    hide_by_id = {row.get("序号", ""): row for row in hidden_records}
    years = [
        int(match.group(1))
        for record in records
        if (match := re.fullmatch(r"(\d{4})级", record_year(record, hide_by_id.get(record.get("序号", ""), {}))))
    ]
    if not years:
        raise ValueError("No year-like 年级 values found in people.csv")
    current_year = max(years)
    current = [
        record
        for record in records
        if record_year(record, hide_by_id.get(record.get("序号", ""), {})) == f"{current_year}级"
        and hide_by_id.get(record.get("序号", ""), {}).get("类别") != "hide"
    ]

    president = next((r for r in current if r.get("职位") == "社长"), None)
    vice = next((r for r in current if r.get("职位") == "副社长"), None)
    president_name = president.get("姓名", "") if president else ""
    vice_name = vice.get("姓名", "") if vice else ""
    if president and hide_by_id.get(president.get("序号", ""), {}).get("姓名") == "hide":
        president_name = ""
    if vice and hide_by_id.get(vice.get("序号", ""), {}).get("姓名") == "hide":
        vice_name = ""

    index_html = INDEX_HTML.read_text(encoding="utf-8")
    index_html = replace_leader(index_html, "PRESIDENT", president_name)
    index_html = replace_leader(index_html, "VICE-PRESIDENT", vice_name)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    people_html = PEOPLE_HTML.read_text(encoding="utf-8")
    people_html = replace_region(people_html, "CURRENT", render_current(records, hide_by_id, current_year))
    people_html = replace_region(people_html, "PAST", render_past(records, hide_by_id, current_year))
    (output_dir / "people.html").write_text(people_html, encoding="utf-8")
    for relative_path in PUBLIC_HTML_FILES:
        shutil.copy2(ROOT / relative_path, output_dir / relative_path.name)
    shutil.copytree(ROOT / "static", output_dir / "static", dirs_exist_ok=True)
    check_private_artifacts(output_dir)
    return current_year


def main() -> None:
    current_year = generate(DIST)
    print(f"Generated dist for {current_year} from {PEOPLE_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

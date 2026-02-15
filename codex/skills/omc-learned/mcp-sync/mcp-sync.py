#!/usr/bin/env python3
import argparse
import copy
import datetime
import json
import os
import re
import shutil
import sys
from difflib import unified_diff

MCP_TABLE_RE = re.compile(r"^\[mcp_servers\.([A-Za-z0-9_-]+)(?:\.([A-Za-z0-9_-]+))?\]")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Sync MCP settings from .mcp.json style file into ~/.codex/config.toml"
    )
    p.add_argument("--source", default=".mcp.json", help="Path to .mcp.json (default: .mcp.json in cwd)")
    p.add_argument("--target", default=os.path.expanduser("~/.codex/config.toml"), help="Path to codex config toml")
    p.add_argument("--dry-run", action="store_true", help="Print diff only")
    p.add_argument("--apply", action="store_true", help="Write changes to target")
    p.add_argument("--no-backup", action="store_true", help="Do not create backup when applying")
    return p.parse_args()


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def to_toml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(to_toml_value(v) for v in value) + "]"
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def to_toml_key(key: str) -> str:
    if re.match(r"^[A-Za-z0-9_-]+$", key):
        return key
    escaped = str(key).replace('"', '\\"')
    return f'"{escaped}"'


def render_server_block(name: str, conf: dict) -> str:
    lines = []
    lines.append(f"[mcp_servers.{name}]")
    for key in ["command", "url", "type"]:
        if key in conf:
            lines.append(f"{key} = {to_toml_value(conf[key])}")
    if "args" in conf and isinstance(conf["args"], list):
        lines.append(f"args = {to_toml_value(conf['args'])}")
    if "startup_timeout_sec" in conf:
        lines.append(f"startup_timeout_sec = {to_toml_value(conf['startup_timeout_sec'])}")
    if "enabled" in conf:
        lines.append(f"enabled = {to_toml_value(conf['enabled'])}")

    if "env" in conf and isinstance(conf["env"], dict):
        lines.append(f"\n[mcp_servers.{name}.env]")
        for k in sorted(conf["env"].keys()):
            v = conf["env"][k]
            if v is None:
                continue
            lines.append(f"{to_toml_key(k)} = {to_toml_value(v)}")

    if "http_headers" in conf and isinstance(conf["http_headers"], dict):
        lines.append(f"\n[mcp_servers.{name}.http_headers]")
        for k in sorted(conf["http_headers"].keys()):
            v = conf["http_headers"][k]
            if v is None:
                continue
            lines.append(f"{to_toml_key(k)} = {to_toml_value(v)}")

    lines.append("")
    return "\n".join(lines)


def normalize_servers(raw: dict) -> dict:
    servers = raw.get("mcpServers") or raw.get("mcp_servers") or {}
    if not isinstance(servers, dict):
        raise ValueError("invalid config: missing mcpServers object")

    out = {}
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue
        cfg = copy.deepcopy(cfg)
        if "headers" in cfg and "http_headers" not in cfg:
            cfg["http_headers"] = cfg.pop("headers")
        out[name] = cfg
    return out


def strip_or_keep_existing_mcp_sections(content: str, replace_names: set[str]) -> str:
    """Keep non-source MCP sections, remove only source MCP sections for replacement."""
    lines = content.splitlines()
    out = []
    in_skip = False

    for line in lines:
        if line.startswith("["):
            m = MCP_TABLE_RE.match(line.strip())
            if m:
                name = m.group(1)
                in_skip = name in replace_names
                if in_skip:
                    continue
            else:
                in_skip = False

        if not in_skip:
            out.append(line)

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    source = os.path.expanduser(args.source)
    target = os.path.expanduser(args.target)

    if not os.path.exists(source):
        print(f"[error] source not found: {source}", file=sys.stderr)
        return 1
    if not os.path.exists(target):
        print(f"[error] target not found: {target}", file=sys.stderr)
        return 1

    raw = json.loads(read_file(source))
    servers = normalize_servers(raw)
    replace_names = set(servers.keys())

    original = read_file(target)
    base = strip_or_keep_existing_mcp_sections(original, replace_names)
    rendered = "\n".join(render_server_block(name, servers[name]) for name in sorted(servers.keys())).rstrip() + "\n"

    # keep one blank line at end of static sections
    if base.strip():
        if not base.endswith("\n\n"):
            base = base.rstrip("\n") + "\n\n"
    new_content = base + rendered
    new_content = new_content.rstrip("\n") + "\n"

    if args.dry_run and not args.apply:
        for line in unified_diff(original.splitlines(), new_content.splitlines(), fromfile=target, tofile=f"{target} (synced)", lineterm=""):
            print(line)
        return 0

    if not args.apply:
        print(new_content)
        return 0

    if not args.no_backup:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup = f"{target}.backup-{timestamp}"
        shutil.copy2(target, backup)
        print(f"[info] backup: {backup}")

    with open(target, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[ok] synced: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

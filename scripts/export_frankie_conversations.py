"""Export conversation IDs and messages. Python 3 standard library only.

Schemas verified against the deployment's OpenAPI document on 2026-10-13.
Authenticated responses still need live verification.
Authentication: --session-prompt or FRANKIE_COOKIE (sessionid cookie header).
Legacy FRANKIE_TOKEN support is not documented by this deployment.
Secrets are never saved.
"""

import argparse
from getpass import getpass
import json
import math
import os
from pathlib import Path
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def count(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid or missing {name}: expected a non-negative integer")
    return value


def collect(fetch, path, params, key, identity, directory):
    """Require stable totals and unique users or (message ID, timestamp) pairs."""
    directory.mkdir(parents=True, exist_ok=True)
    records, seen = [], set()
    expected = None
    effective_size = None
    for page in range(1, 100001):
        data = fetch(path, {**params, "page": page})
        save(directory / f"page-{page:05}.json", data)
        if not isinstance(data, dict) or not isinstance(data.get(key), list):
            raise ValueError(f"{path}: expected a JSON object with '{key}' list; inspect saved page")
        items = data[key]
        total = data.get("total", data.get("total_messages"))
        total = count(total, "total")
        returned_page = count(data.get("page"), "page")
        size = count(data.get("per_page"), "per_page")
        if returned_page != page or size < 1 or len(items) > size:
            raise ValueError(f"{path}: inconsistent pagination metadata at page {page}")
        if expected is None:
            expected, effective_size = total, size
        if total != expected or size != effective_size:
            raise ValueError(f"{path}: total/page size changed during export; use a stable snapshot")
        for item in items:
            item_id = item.get(identity) if isinstance(item, dict) else None
            if not isinstance(item_id, str) or not item_id.strip():
                raise ValueError(f"{path}: missing string '{identity}'")
            record_key = message_key(item) if key == "messages" else item_id
            if record_key in seen:
                raise ValueError(f"{path}: repeated record identity on page {page}; export may be shifting")
            seen.add(record_key)
            records.append(item)
        if len(records) > expected:
            raise ValueError(f"{path}: returned more records than total")
        if len(records) == expected:
            return records
        if not items or page >= max(1, math.ceil(expected / size)):
            raise ValueError(f"{path}: incomplete results ({len(records)} of {expected})")
    raise ValueError("Pagination safety limit reached")


def message_key(message):
    # Live data contains distinct occurrences with the same message_id.
    timestamp = message.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise ValueError("Missing message timestamp; cannot distinguish message occurrences")
    return message["message_id"], timestamp


def replay_pages(directory):
    def fetch(path, params):
        source = directory / f"page-{params['page']:05}.json"
        return json.loads(source.read_text(encoding="utf-8"))
    return fetch


def verify_message_count(messages, expected, index, warnings=None):
    expected = count(expected, "list total_messages")
    unique_ids = len({message["message_id"] for message in messages})
    # Observed API behavior: list totals may count distinct IDs while the
    # detail endpoint counts timestamped occurrences. Preserve every occurrence.
    if expected not in (len(messages), unique_ids):
        # The list and detail calls are not a shared snapshot. collect() has
        # already validated all pages against the detail endpoint's own total.
        if warnings is not None:
            warnings.append({"user_index": index, "list_total": expected,
                             "detail_records": len(messages), "unique_ids": unique_ids})
        print(f"Warning: user {index}: list count {expected}, detail records {len(messages)} "
              f"({unique_ids} unique IDs); keeping all detail records", flush=True)
    return unique_ids


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def client(base_url, delay, session_id=None):
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an HTTPS base URL without embedded credentials")
    token = None if session_id else os.environ.get("FRANKIE_TOKEN")
    cookie = "sessionid=" + session_id if session_id else os.environ.get("FRANKIE_COOKIE")
    if bool(token) == bool(cookie):
        raise ValueError("Set exactly one of FRANKIE_COOKIE or FRANKIE_TOKEN locally")
    headers = {"Accept": "application/json"}
    headers.update({"Authorization": f"Bearer {token}"} if token else {"Cookie": cookie})
    opener = build_opener(NoRedirect())

    def fetch(path, params):
        url = base_url.rstrip("/") + "/" + path.lstrip("/") + "?" + urlencode(params)
        for attempt in range(4):
            time.sleep(delay if attempt == 0 else 2 ** attempt)
            try:
                with opener.open(Request(url, headers=headers), timeout=90) as response:
                    return json.load(response)
            except HTTPError as error:
                if (error.code == 429 or 500 <= error.code < 600) and attempt < 3:
                    retry_after = error.headers.get("Retry-After", "")
                    if retry_after.isdigit():
                        time.sleep(int(retry_after))
                    continue
                raise RuntimeError(f"HTTP {error.code}; check authentication, permissions and endpoint") from None
            except URLError:
                if attempt < 3:
                    continue
                raise RuntimeError("Connection failed after four attempts") from None
            except (ValueError, UnicodeError):
                raise RuntimeError("API did not return valid JSON; verify authentication and endpoint") from None
    return fetch


def local_ids(paths, output):
    ids, details = set(), []
    for source in paths:
        data = json.loads(Path(source).read_text(encoding="utf-8-sig"))
        rows = data["conversations"]
        ids.update(row["user_id"] for row in rows)
        details.append({"file": Path(source).name, "page": data.get("page"),
                        "total": data.get("total"), "returned_conversations": len(rows)})
    output.mkdir(parents=True, exist_ok=False)
    save(output / "user_ids.json", sorted(ids))
    save(output / "report.json", {"scope": "supplied pages only, NOT all users",
                                 "unique_users": len(ids), "sources": details})
    print(f"Saved {len(ids)} unique user IDs from supplied pages to {output}")


def export(args):
    previous = None
    if args.resume_from:
        previous = json.loads((args.resume_from / "report.json").read_text(encoding="utf-8"))
        if previous.get("base_url", "https://crm.frankie.mindsmiths.io/api/v1").rstrip("/") != args.base_url.rstrip("/"):
            raise ValueError("Resume source belongs to a different API base URL")
        # A resumed export must use exactly the source export's scope.
        args.start_time = previous["start_time"]
        args.end_time = previous["end_time"]
        args.include_personal_data = not previous["anonymize"]
        count(previous.get("users_completed"), "checkpoint users_completed")
    session_id = None
    if args.session_prompt:
        session_id = getpass("Paste sessionid cookie value (hidden): ").strip()
        if not session_id or any(char in session_id for char in "\r\n;"):
            raise ValueError("Enter only the non-empty sessionid value")
    fetch = client(args.base_url, args.delay, session_id)
    args.output.mkdir(parents=True, exist_ok=False)
    report = {"status": "in_progress", "users_completed": 0, "messages": 0,
              "unique_message_ids_within_conversations": 0,
              "users_with_repeated_message_ids": 0,
              "list_count_changes": [],
              "start_time": args.start_time, "end_time": args.end_time,
              "anonymize": not args.include_personal_data,
              "base_url": args.base_url,
              "resumed_from": str(args.resume_from) if args.resume_from else None,
              "scope": "conversations accessible to the authenticated account and selected filters",
              "limitation": "Count checks do not prove snapshot consistency or coverage of inaccessible/deleted data"}
    save(args.output / "report.json", report)
    try:
        params = {"per_page": args.per_page,
                  "anonymize": "false" if args.include_personal_data else "true"}
        for key in ("start_time", "end_time"):
            if getattr(args, key):
                params[key] = getattr(args, key)
        list_fetch = replay_pages(args.resume_from / "conversation_pages") if previous else fetch
        users = collect(list_fetch, "conversations", params, "conversations", "user_id",
                        args.output / "conversation_pages")
        save(args.output / "user_ids.json", [row["user_id"] for row in users])
        save(args.output / "conversations.json", users)
        report["users_discovered"] = len(users)
        if previous and previous["users_completed"] > len(users):
            raise ValueError("Invalid resume checkpoint: completed users exceeds user list")
        print(f"Discovered {len(users)} users", flush=True)
        if args.users_only:
            report["status"] = "user_list_count_verified; messages_not_exported"
        else:
            message_total = 0
            unique_total = 0
            repeated_id_users = 0
            with (args.output / "messages.jsonl").open("w", encoding="utf-8") as stream:
                for index, user in enumerate(users, 1):
                    uid = user["user_id"]
                    # Numeric local directories avoid using API-controlled IDs as filesystem paths.
                    folder = args.output / "message_pages" / f"user-{index:06}"
                    cached = previous and index <= previous["users_completed"]
                    message_fetch = replay_pages(args.resume_from / "message_pages" / f"user-{index:06}") if cached else fetch
                    messages = collect(message_fetch, "conversations/" + quote(uid, safe=""), params,
                                       "messages", "message_id", folder)
                    unique_ids = verify_message_count(messages, user.get("total_messages"), index,
                                                      report["list_count_changes"])
                    for message in messages:
                        if message.get("user_id") not in (None, uid):
                            raise ValueError(f"User {index}: message user_id does not match requested user")
                        # ApiMessage.user_id is optional/nullable. Retain the
                        # requested conversation identity without changing it.
                        stream.write(json.dumps({**message, "conversation_user_id": uid},
                                                ensure_ascii=False) + "\n")
                    stream.flush()
                    message_total += len(messages)
                    unique_total += unique_ids
                    repeated_id_users += int(unique_ids < len(messages))
                    report.update(users_completed=index, messages=message_total,
                                  unique_message_ids_within_conversations=unique_total,
                                  users_with_repeated_message_ids=repeated_id_users)
                    save(args.output / "report.json", report)
                    print(f"Users {index}/{len(users)}; messages {message_total}" + (" (cached)" if cached else ""), flush=True)
            report["status"] = ("export_finished_with_list_count_changes" if report["list_count_changes"]
                                else "export_finished_count_checks_passed")
            print(f"Finished: {message_total} records in {args.output}; "
                  f"list/detail count differences: {len(report['list_count_changes'])}. "
                  "This export is not a single-time snapshot.", flush=True)
    except Exception as error:
        report.update(status="INCOMPLETE", error=str(error))
        raise
    finally:
        save(args.output / "report.json", report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    local = sub.add_parser("local-ids", help="Extract IDs from supplied list JSON files")
    local.add_argument("files", nargs="+")
    local.add_argument("--output", required=True, type=Path)
    remote = sub.add_parser("export", help="Discover all users, then paginate each user's messages")
    remote.add_argument("--base-url", default="https://crm.frankie.mindsmiths.io/api/v1")
    remote.add_argument("--output", type=Path, default=Path("output") / ("frankie-export-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    remote.add_argument("--per-page", type=int, default=100)
    remote.add_argument("--start-time", help="Optional API-format date; omit for all historical data")
    remote.add_argument("--end-time", help="Fixed cutoff in the API's documented time zone; not a database snapshot")
    remote.add_argument("--delay", type=float, default=0.2)
    remote.add_argument("--users-only", action="store_true")
    remote.add_argument("--session-prompt", action="store_true",
                        help="Ask for the sessionid cookie value without echoing or saving it")
    remote.add_argument("--resume-from", type=Path,
                        help="Reuse verified users from this export in a NEW output folder; inherits its date/anonymization filters")
    remote.add_argument("--include-personal-data", action="store_true",
                        help="Send anonymize=false; default uses the API's anonymization")
    args = parser.parse_args()
    try:
        if args.command == "local-ids":
            local_ids(args.files, args.output)
        else:
            if args.per_page < 1 or args.delay < 0:
                raise ValueError("per-page must be positive and delay non-negative")
            export(args)
    except Exception as error:
        parser.exit(1, f"Stopped: {error}\nPartial output, if any, is not a complete export.\n")


if __name__ == "__main__":
    main()

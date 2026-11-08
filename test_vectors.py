#!/usr/bin/env python3
"""Independent decode fixtures for id-when. Run: python3 test_vectors.py"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
GREGORIAN_100NS = 0x01B21DD213814000  # 1582-10-15 to 1970-01-01
KSUID_EPOCH = 1_400_000_000  # 2014-05-13T16:53:20Z
TWITTER_EPOCH = 1_288_834_974_657
TS_MS = 1_700_000_000_000  # 2023-11-14T22:13:20.000Z

UUIDV7 = "018bcfe5-6800-7000-8000-000000000001"
ULID = "01HF7YAT000123456789ABCDEF"
KSUID = "2YBXZHsLO8MUtQ9MmLrFm4Unt79"
SNOWFLAKE = ((TS_MS - TWITTER_EPOCH) << 22) | (1 << 12) | 1
OBJECTID = "507f1f77bcf86cd799439011"
UUIDV4 = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
UUIDV1 = "04afc000-833b-11ee-8001-000000000001"
UUIDV6 = "1ee833b0-4afc-6000-8001-000000000001"


def iso_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )[:-3] + "Z"


def decode_crockford(text: str) -> int:
    n = 0
    for ch in text.upper().replace("I", "1").replace("L", "1").replace("O", "0"):
        n = n * 32 + CROCKFORD.index(ch)
    return n


def decode_uuid_version(text: str) -> int:
    raw = text.replace("-", "").lower()
    return int(raw[12], 16)


def decode_uuidv7_ms(text: str) -> int:
    raw = text.replace("-", "").lower()
    if raw[12] != "7":
        raise ValueError("not uuidv7")
    return int(raw[:12], 16)


def decode_uuidv1_ms(text: str) -> int:
    raw = text.replace("-", "").lower()
    time_low = int(raw[0:8], 16)
    time_mid = int(raw[8:12], 16)
    time_hi = int(raw[12:16], 16) & 0x0FFF
    uuid_ts = (time_hi << 48) | (time_mid << 32) | time_low
    return (uuid_ts - GREGORIAN_100NS) // 10_000


def decode_uuidv6_ms(text: str) -> int:
    raw = text.replace("-", "").lower()
    time_high = int(raw[0:8], 16)
    time_mid = int(raw[8:12], 16)
    time_low = int(raw[12:16], 16) & 0x0FFF
    uuid_ts = (time_high << 28) | (time_mid << 12) | time_low
    return (uuid_ts - GREGORIAN_100NS) // 10_000


def decode_ulid_ms(text: str) -> int:
    return decode_crockford(text[:10])


def decode_objectid_ms(text: str) -> int:
    return int(text[:8], 16) * 1000


def decode_ksuid_ms(text: str) -> int:
    n = 0
    for ch in text:
        n = n * 62 + BASE62.index(ch)
    raw = n.to_bytes(20, "big")
    return (int.from_bytes(raw[:4], "big") + KSUID_EPOCH) * 1000


def decode_snowflake(sid: int, epoch: int) -> tuple[int, int, int]:
    ts = (sid >> 22) + epoch
    worker = (sid >> 12) & 0x3FF
    seq = sid & 0xFFF
    return ts, worker, seq


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"ok  {name}")
        return
    print(f"FAIL  {name}  {detail}")
    raise SystemExit(1)


def test_fixtures() -> None:
    oid_ms = decode_objectid_ms(OBJECTID)
    check(
        "ObjectId 507f1f77bcf86cd799439011 timestamp",
        oid_ms == 1_350_508_407_000 and iso_ms(oid_ms) == "2012-10-17T21:13:27.000Z",
        iso_ms(oid_ms),
    )
    # Common mis-addition yields 2012-10-23T00:39:19Z from unix 1350952759.
    # First 4 bytes 0x507f1f77 are 1350508407 = 2012-10-17T21:13:27Z.

    v7_ms = decode_uuidv7_ms(UUIDV7)
    check("constructed UUIDv7 first 48 bits", v7_ms == TS_MS, str(v7_ms))
    check("UUIDv7 ISO", iso_ms(v7_ms) == "2023-11-14T22:13:20.000Z", iso_ms(v7_ms))
    check("UUIDv7 form starts 018bcfe5-6800-7", UUIDV7.startswith("018bcfe5-6800-7"))

    ulid_ms = decode_ulid_ms(ULID)
    check("constructed ULID timestamp", ulid_ms == TS_MS, str(ulid_ms))
    check("ULID length 26", len(ULID) == 26)

    sid = SNOWFLAKE
    ts, worker, seq = decode_snowflake(sid, TWITTER_EPOCH)
    check("Twitter Snowflake timestamp", ts == TS_MS, str(ts))
    check("Twitter Snowflake worker", worker == 1, str(worker))
    check("Twitter Snowflake sequence", seq == 1, str(seq))
    check("Snowflake ISO", iso_ms(ts) == "2023-11-14T22:13:20.000Z", iso_ms(ts))
    check("Snowflake constructed id", sid == 1_724_551_110_456_250_369, str(sid))

    check("UUIDv4 version nibble is 4", decode_uuid_version(UUIDV4) == 4)
    check("UUIDv4 has no timestamp rule", decode_uuid_version(UUIDV4) not in (1, 6, 7))

    check("UUIDv1 timestamp", decode_uuidv1_ms(UUIDV1) == TS_MS, str(decode_uuidv1_ms(UUIDV1)))
    check("UUIDv6 timestamp", decode_uuidv6_ms(UUIDV6) == TS_MS, str(decode_uuidv6_ms(UUIDV6)))
    check("KSUID timestamp", decode_ksuid_ms(KSUID) == TS_MS, str(decode_ksuid_ms(KSUID)))


def test_html_smoke() -> None:
    html = (Path(__file__).resolve().parent / "index.html").read_text(encoding="utf-8")
    lower = html.lower()
    check("no TODO", "TODO" not in html)
    check("no FIXME", "FIXME" not in html)
    check("no lorem", "lorem" not in lower)
    check("lang zh-CN", 'lang="zh-CN"' in html)
    check("privacy note", "全部在本机解码，不发网络请求" in html)

    for sample in (
        OBJECTID,
        UUIDV7,
        ULID,
        KSUID,
        str(SNOWFLAKE),
        UUIDV4,
    ):
        check(f"sample present {sample[:20]}…", sample in html)

    for label in ("ObjectId", "UUIDv7", "ULID", "KSUID", "Snowflake", "UUIDv4"):
        check(f"sample control {label}", label in html)

    srcs = re.findall(r"""<(?:script|img|link)\b[^>]+(?:src|href)\s*=\s*['"]([^'"]+)""", html, re.I)
    for url in srcs:
        check(f"no third-party asset {url}", False, url)

    for url in re.findall(r"""href\s*=\s*['"](https?://[^'"]+)""", html, re.I):
        ok = (
            "github.com/temptation2017" in url
            or "temptation2017.github.io" in url
        )
        check(f"href allowlist {url}", ok, url)

    check("no npm/cdn markers", "cdn." not in lower and "unpkg" not in lower and "googleapis" not in lower)


def main() -> None:
    test_fixtures()
    test_html_smoke()
    print("all tests passed")


if __name__ == "__main__":
    sys.exit(main())

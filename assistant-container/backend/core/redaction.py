"""Strip secrets out of user text before it is ever written to disk.

People paste connection strings, tokens and keys into questions ("почему
не коннектится: psql -h db01 -U admin -W Passw0rd!"). Two rules follow
from that:

1. The redacted form is what gets stored -- a secret that was never
   written to disk cannot leak from it later.
2. Replacements are typed placeholders ([PASSWORD], [TOKEN]) rather than a
   blanket "***", so the sentence still reads as a question afterwards and
   stays useful for clustering and triage.

Regexes miss things -- that is a given, not a bug to fix here. This is the
second line of defence; the first is structural: raw user text is never
published to the showcase, only LLM-written generic topic titles are (see
docs/feedback-architecture.md).
"""
import re

# Order matters: the more specific patterns run first, so a JWT is tagged
# [TOKEN] rather than swallowed by the generic long-base64 rule.
_RULES: list[tuple[re.Pattern, str]] = [
    # -----BEGIN RSA PRIVATE KEY----- ... -----END ...-----
    (re.compile(r"-----BEGIN[^-]{0,50}-----.*?-----END[^-]{0,50}-----", re.DOTALL), "[PRIVATE_KEY]"),
    # JWT: three base64url segments separated by dots
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "[TOKEN]"),
    # Authorization: Bearer <token>
    (re.compile(r"\b(Bearer|Basic)\s+[A-Za-z0-9._\-+/=]{12,}", re.IGNORECASE), r"\1 [TOKEN]"),
    # AWS access key id
    (re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"), "[AWS_KEY]"),
    # GitHub / GitLab style tokens
    (re.compile(r"\b(gh[pousr]|glpat)[-_][A-Za-z0-9_-]{16,}\b"), "[TOKEN]"),
    # user:password@host in URLs and connection strings
    (re.compile(r"\b([A-Za-z][A-Za-z0-9+.-]*://[^\s:/@]+):[^\s/@]{1,200}@"), r"\1:[PASSWORD]@"),
    # key=value / key: value forms for well-known secret keys, quoted or not
    (
        re.compile(
            r"\b(password|passwd|pwd|pass|secret|api[_-]?key|apikey|access[_-]?key|"
            r"private[_-]?key|client[_-]?secret|token|auth)\b"
            r"(\s*[:=]\s*)"
            r"(\"[^\"]{1,200}\"|'[^']{1,200}'|[^\s,;&]{1,200})",
            re.IGNORECASE,
        ),
        r"\1\2[SECRET]",
    ),
    # psql/mysql style credential flags: -W Passw0rd, -p secret, --password=x
    (
        re.compile(r"(--password[= ]|--pass[= ]|\s-[WwPp]\s+)(?!\s)([^\s,;]{1,200})"),
        r"\1[PASSWORD]",
    ),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    # Long opaque blobs left over: 40+ chars of base64/hex with no spaces.
    # Deliberately last and deliberately long -- shorter thresholds start
    # eating legitimate identifiers, file hashes people ask about, etc.
    (re.compile(r"\b[A-Za-z0-9+/=_-]{40,}\b"), "[REDACTED]"),
]


def redact(text: str) -> str:
    """Replace anything that looks like a credential with a typed placeholder."""
    if not text:
        return text
    for pattern, replacement in _RULES:
        text = pattern.sub(replacement, text)
    return text


def redact_if(text: str, enabled: bool) -> str:
    return redact(text) if enabled else text

#!/usr/bin/env bash
# Enforce commit message conventions:
#   - Subject line <= 50 characters
#   - A blank line separates the subject from the body
#   - Body lines (if present) start with "- ", or are Git trailers
#     ("Closes: #12", "Signed-off-by: A Name <a@example.com>") or bare issue
#     references such as "Closes #12"
#   - Body lines do not exceed 100 characters
#   - BREAKING CHANGE: footer lines are permitted
#
# The message is normalized once, up front, and every check below then reads the
# same content. Normalization is where the input space is actually wide: a
# commit-msg hook is handed whatever the editor left on disk, which may carry a
# byte order mark, CRLF line endings, git's own template comments, and — under
# `git commit -v` — a raw diff that git strips only after this hook has run.
# Limits are counted in characters, not bytes.
set -euo pipefail

# Byte semantics for every pattern match and every ${#...}, so a verdict never
# depends on the locale the hook happens to inherit. A commit-msg hook runs
# under whatever environment invoked git, and a minimal CI container or a cron
# job commonly supplies LC_ALL=C or no locale variables at all. Forcing a UTF-8
# locale instead is not portable — macOS ships no C.UTF-8 — so the character
# count is recovered from the bytes by char_len below.
export LC_ALL=C

commit_msg_file="${1:-}"

if [ -z "${commit_msg_file}" ]; then
    echo "Usage: ${0##*/} <commit-msg-file>"
    exit 1
fi

if [ ! -f "${commit_msg_file}" ]; then
    echo "Commit message file not found: ${commit_msg_file}"
    exit 1
fi

# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

# The comment character is configurable, and git writes BOTH the scissors line
# and its own template comments with whatever it is set to. Reading it once
# here, and deriving both patterns from that one value, is what keeps the two
# in step: hardcoding "#" left every commit in a repo with, say,
# `core.commentChar = ;` rejected — the scissors line did not cut, so the diff
# below it was read as prose, which is precisely the failure the truncation
# exists to prevent. `core.commentString` is git 2.45's name for the same
# setting and may be several characters ("//"), so nothing below assumes a
# length of one. An unset value, a git that predates the rename, and no git on
# PATH at all each leave this empty and fall back to git's own default.
comment_char="$(git config --get core.commentString 2>/dev/null || git config --get core.commentChar 2>/dev/null || true)"

if [ -z "${comment_char}" ]; then
    comment_char='#'
fi

# `auto` is a real, supported value, not a character: git picks the first of
# these candidates that begins no line already in the message, so the literal
# string "auto" must never be used as the prefix. Which one it picked is
# recoverable from the message git wrote — the scissors line carries it — and
# the common case, where nothing forced git off "#", resolves there anyway.
if [[ "${comment_char}" == [Aa][Uu][Tt][Oo] ]]; then
    auto_scissors_re='^([#;@!$%^&|:]) -+ >8 -+$'
    comment_char='#'
    while IFS= read -r probe || [ -n "${probe}" ]; do
        if [[ "${probe%$'\r'}" =~ ${auto_scissors_re} ]]; then
            comment_char="${BASH_REMATCH[1]}"
            break
        fi
    done < "${commit_msg_file}"
fi

# Interpolated into a regular expression below, so every character that is a
# metacharacter there is escaped first. Without this, a configured "|" makes
# the scissors pattern an alternation matching every line — the whole message
# is truncated away — and "*" makes it a pattern the regex engine rejects
# outright.
comment_char_re=''
escape_index=0
while [ "${escape_index}" -lt "${#comment_char}" ]; do
    escape_char="${comment_char:${escape_index}:1}"
    case "${escape_char}" in
        '.'|'['|']'|'\'|'('|')'|'*'|'+'|'?'|'{'|'}'|'^'|'$'|'|') escape_char="\\${escape_char}" ;;
    esac
    comment_char_re="${comment_char_re}${escape_char}"
    escape_index=$((escape_index + 1))
done

# Git's scissors line, written as the comment character, a space, then the cut
# line. `git commit -v` appends the diff below it and strips everything from
# here down only AFTER the commit-msg hook runs, so without this the hook sees
# "diff --git ...", "@@ -0,0 +1 @@" and "+hello" as body prose and rejects a
# perfectly good commit. Truncating here mirrors git's own cleanup boundary.
# The dash runs are matched loosely rather than pinned to git's 24 so a
# hand-written or reflowed marker still cuts.
scissors_re='^'"${comment_char_re}"' -+ >8 -+$'

# A UTF-8 byte order mark, which Windows Notepad's "UTF-8" save, some Windows
# Git GUIs and PowerShell's Out-File default all write. Only its 0xBB and 0xBF
# bytes look like UTF-8 continuation bytes, so the 0xEF survived as one extra
# character and a 50-character subject was rejected as 51.
byte_order_mark=$'\357\273\277'

# Read the file once: strip the BOM, normalize line endings, cut at the
# scissors line, drop git's own template comments, and keep everything else.
# The surviving lines are collected into an array rather than concatenated into
# one string, so a large message costs linear rather than quadratic time: a
# 250 KB message took over eight seconds to append line by line.
normalized=()
has_content=0
first_line=1
while IFS= read -r raw || [ -n "${raw}" ]; do
    if [ "${first_line}" -eq 1 ]; then
        raw="${raw#"${byte_order_mark}"}"
        first_line=0
    fi

    # A trailing CR is the line ending, not content. Left in place it inflated
    # every length by one — a visibly 50-character subject was rejected as 51 —
    # and stopped the blank separator line from reading as blank.
    raw="${raw%$'\r'}"

    if [[ "${raw}" =~ ${scissors_re} ]]; then
        break
    fi

    # Drop git's own template comments, and only those. Git writes them as the
    # comment character alone or followed by whitespace, which covers the status
    # lines and the two notes under the scissors line. Dropping every
    # hash-prefixed line instead removed body content too: a "#277" reference or
    # a "## Changes" heading was neither checked nor rejected, which made it a
    # silent bypass rather than a verdict.
    #
    # Matched by stripping the prefix rather than by a case pattern, because the
    # configured value is data: a "*" written into a glob would match every line
    # and strip none of it.
    after_comment_char="${raw#"${comment_char}"}"
    if [ "${after_comment_char}" != "${raw}" ]; then
        case "${after_comment_char}" in
            ''|[[:space:]]*) continue ;;
        esac
    fi

    normalized[${#normalized[@]}]="${raw}"
    case "${raw}" in
        *[![:space:]]*) has_content=1 ;;
    esac
done < "${commit_msg_file}"

# A message of nothing but comments used to end the run here. The filter was a
# `grep -v` for the comment character, which exits 1 when it matches nothing, so
# under `set -e` the script died before any check ran: exit 1 with no output at
# all, indistinguishable from a crash and unlike every other rejection below,
# each of which names what it rejected.
if [ "${has_content}" -eq 0 ]; then
    echo "Commit message is empty (only blank lines and template comments)"
    exit 1
fi

# ---------------------------------------------------------------------------
# Character counting
# ---------------------------------------------------------------------------

# Whole-string test for well-formed UTF-8, as RFC 3629 defines it: no overlong
# encoding, no surrogate, nothing above U+10FFFF. The ASCII branch is written as
# "not a high byte" because bash 3.2's regex engine does not match a bracket
# range whose low endpoint is a control character.
utf8_sequence_re=$'^([^\200-\377]|[\302-\337][\200-\277]|\340[\240-\277][\200-\277]|[\341-\354][\200-\277][\200-\277]|\355[\200-\237][\200-\277]|[\356-\357][\200-\277][\200-\277]|\360[\220-\277][\200-\277][\200-\277]|[\361-\363][\200-\277][\200-\277][\200-\277]|\364[\200-\217][\200-\277][\200-\277])*$'

# Characters, not bytes. Under LC_ALL=C ${#s} counts bytes, so discarding the
# UTF-8 continuation bytes (0x80-0xBF) leaves exactly one byte per codepoint and
# "José" measures 4.
#
# That subtraction is only a character count when the bytes really are UTF-8.
# A run of raw 0xBF is not: every byte is in the stripped range, so 150 of them
# measured 0 and a 152-byte line was accepted with no "too long" at all. The
# well-formedness test above gates the strip, and invalid input falls back to
# its byte length — which can only over-count, so it never accepts a line the
# character count would have rejected.
#
# Sets CHAR_LEN rather than printing, so no check in this script needs a
# subshell, a pipeline, or an external command.
CHAR_LEN=0
char_len() {
    local s="${1}"
    local stripped
    if [[ "${s}" =~ ${utf8_sequence_re} ]]; then
        stripped="${s//[$'\200'-$'\277']/}"
        CHAR_LEN=${#stripped}
    else
        CHAR_LEN=${#s}
    fi
}

errors=0

# ---------------------------------------------------------------------------
# Body line grammar
# ---------------------------------------------------------------------------

# Each body line is classified as exactly one shape from its content, then
# validated in full against that shape's grammar. A colon is what marks a line
# as a Git trailer, and that decides the precedence. In order:
#
#   1. bullet            "- text"
#   2. BREAKING CHANGE   "BREAKING CHANGE: value" — token is two words, so it is
#                        not a Git trailer token and needs its own shape
#   3. general trailer   "Token-Name: value" as Git defines a trailer — a token
#                        of word characters and hyphens, a colon, a space, then
#                        a free-text value. A colon-qualified issue reference
#                        such as "Closes: #12" is one of these, whose value
#                        happens to start with "#", so free text after the
#                        reference is fine: "Refs: #1234 see the design doc".
#   4. issue reference   no colon, and the value after the token begins with
#                        "#" — the bare convenience form this repo writes
#   5. prose             anything else, always an error
#
# A line that fails its own shape's grammar is an error, never a candidate for
# the next shape: there is no fallback to a laxer rule.
#
# The two spellings of a reference deliberately reach different verdicts. With a
# colon the line is a trailer and its value is unconstrained. Without one there
# is nothing marking it as a trailer, so rule 4's grammar is anchored at both
# ends — its token is any capitalized word, and an unbounded tail would accept
# any sentence shaped "Reverted #42 because the migration was wrong". Whole
# line:
#     TOKEN (" " "#" DIGITS [","])* " " "#" DIGITS [trailing spaces]
# So "Closes #12", "Closes #12, #13" and "Fixes #12 #13" are accepted, while
# "Closes #12 and also the other thing", "Closes #12oops", "Closes #12," and
# "Closes #" are rejected — write any of those as a trailer with a colon.
#
# Rule 4's shape test and grammar both require a literal space, not any
# whitespace: a shape test matching a tab claimed "Refs<TAB>#1234" for a
# grammar that could never accept it, so the line was rejected under the wrong
# rule. A tab after a colon likewise fails rule 3's grammar, which is reported
# as the malformed trailer it is.
bullet_re='^- '
breaking_change_shape_re='^BREAKING CHANGE:'
breaking_change_grammar_re='^BREAKING CHANGE: +[^[:space:]]'
trailer_shape_re='^[A-Za-z][A-Za-z0-9-]*:'
trailer_grammar_re='^[A-Za-z][A-Za-z0-9-]*: +[^[:space:]]'
issue_reference_shape_re='^[A-Za-z][A-Za-z0-9-]* +#'
issue_reference_grammar_re='^[A-Za-z][A-Za-z0-9-]*( +#[0-9]+,?)* +#[0-9]+ *$'

report_malformed_trailer() {
    echo "Malformed Git trailer: needs 'Token-Name: value' with a space after the colon"
    echo "  Offending line: ${1}"
    errors=$((errors + 1))
}

report_malformed_issue_reference() {
    echo "Malformed issue reference: a colonless 'Closes #12' or 'Closes #12, #13' needs"
    echo "  '#' followed by digits and nothing after the last reference. For a value with"
    echo "  free text, write it as a trailer instead: 'Closes: #12 and the rest'"
    echo "  Offending line: ${1}"
    errors=$((errors + 1))
}

report_prose() {
    echo "Body line is not a bullet or a Git trailer: start it with '- ',"
    echo "  or use a trailer such as 'Closes: #12' or 'Signed-off-by: A Name <a@example.com>'"
    echo "  Offending line: ${1}"
    errors=$((errors + 1))
}

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

# Walk the normalized message by position. Line 2 used to be discarded outright
# by a `tail -n +3`, which assumed it was the blank separator; a non-blank line 2
# was dropped from the body and escaped both the shape check and the length
# check. Conventional Commits requires the blank line and no commit in this
# repository's history has a non-blank line 2, so it is rejected on its own
# terms rather than folded into the body.
line_count=${#normalized[@]}
line_index=0
while [ "${line_index}" -lt "${line_count}" ]; do
    line="${normalized[${line_index}]}"
    line_index=$((line_index + 1))
    line_no=${line_index}

    if [ "${line_no}" -eq 1 ]; then
        char_len "${line}"
        if [ "${CHAR_LEN}" -gt 50 ]; then
            echo "Subject line too long (${CHAR_LEN} > 50 chars): ${line}"
            errors=$((errors + 1))
        fi
        continue
    fi

    if [ "${line_no}" -eq 2 ]; then
        if [ -n "${line}" ]; then
            echo "Subject and body must be separated by a blank line"
            echo "  Offending line: ${line}"
            errors=$((errors + 1))
        fi
        continue
    fi

    [ -z "${line}" ] && continue

    if [[ "${line}" =~ ${bullet_re} ]]; then
        :
    elif [[ "${line}" =~ ${breaking_change_shape_re} ]]; then
        [[ "${line}" =~ ${breaking_change_grammar_re} ]] || report_malformed_trailer "${line}"
    elif [[ "${line}" =~ ${trailer_shape_re} ]]; then
        [[ "${line}" =~ ${trailer_grammar_re} ]] || report_malformed_trailer "${line}"
    elif [[ "${line}" =~ ${issue_reference_shape_re} ]]; then
        [[ "${line}" =~ ${issue_reference_grammar_re} ]] || report_malformed_issue_reference "${line}"
    else
        report_prose "${line}"
    fi

    # Line length
    char_len "${line}"
    if [ "${CHAR_LEN}" -gt 100 ]; then
        echo "Body line too long (${CHAR_LEN} > 100 chars): ${line}"
        errors=$((errors + 1))
    fi
done

if [ "${errors}" -gt 0 ]; then
    exit 1
fi

# Reminders for conventions that cannot be automated
echo "Reminder: verify manually —"
echo "  - Subject uses imperative mood (\"add feature\", not \"adds feature\")"
echo "  - Code, filenames, and identifiers are wrapped in backticks"

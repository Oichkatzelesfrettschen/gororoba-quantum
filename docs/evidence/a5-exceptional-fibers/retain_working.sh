#!/bin/sh
# Copy the local fiber working directory into working/, scrubbed, with files above 50 MB split into 45 MB parts.
# Usage: sh retain_working.sh SOURCE_DIR [--dry-run]
# A file is copied when its scrubbed bytes differ from the retained copy; the script prints each copied path and a
# count. Scrubbing replaces the home directory with ~, the session scratch root with SCRATCH (or TMP, PROJECT and
# SESSION where a line break splits it), UUIDs with UUID, the
# owner's mail handle with OWNER, the build host's name with build-host and the login name with USER.
set -eu
src=${1:?usage: retain_working.sh SOURCE_DIR [--dry-run]}
mode=${2:-copy}
here=$(cd "$(dirname "$0")" && pwd)
dst="$here/working"
split_list="$here/split.txt"
host=$(uname -n)
user=$(id -un)
tmp=$(mktemp -d)
trap 'trash-put "$tmp" 2>/dev/null || true' EXIT
trap 'exit 130' INT TERM HUP
scrub() {
	LC_ALL=C sed -e "s#$HOME#~#g" \
		-e 's#/tmp/claude-[0-9]*/[^ /"]*/[0-9a-f-]*/scratchpad#SCRATCH#g' \
		-e 's#/tmp/claude-[0-9]*#TMP#g' -e 's#-home-[A-Za-z0-9_]*-Projects-IBMQuantum#PROJECT#g' \
		-e 's#[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}/scratchpad#SESSION/scratchpad#g' \
		-e 's#[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}#UUID#g' \
		-e 's#hilga007#OWNER#g' -e "s#$host#build-host#g" -e "s#\b$user\b#USER#g" "$1"
}
copied=0
cd "$src"
find . -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | LC_ALL=C sort > "$tmp/list"
while IFS= read -r f; do
	rel=${f#./}
	out="$tmp/one"
	if LC_ALL=C grep -Iq . "$f" 2>/dev/null || [ ! -s "$f" ]; then scrub "$f" > "$out"; else cp "$f" "$out"; fi
	size=$(wc -c < "$out")
	if [ "$size" -gt 52428800 ]; then
		if [ -e "$dst/$rel.part00" ] && cat "$dst/$rel".part* | cmp -s - "$out"; then continue; fi
		copied=$((copied + 1)); echo "split $rel"
		[ "$mode" = --dry-run ] && continue
		mkdir -p "$dst/$(dirname "$rel")"
		for p in "$dst/$rel".part*; do [ -e "$p" ] && trash-put "$p"; done
		split -b 45M -d -a 2 "$out" "$dst/$rel.part"
		grep -qxF "$rel" "$split_list" 2>/dev/null || echo "$rel" >> "$split_list"
		continue
	fi
	if [ -e "$dst/$rel" ] && cmp -s "$out" "$dst/$rel"; then continue; fi
	copied=$((copied + 1)); echo "copy $rel"
	[ "$mode" = --dry-run ] && continue
	mkdir -p "$dst/$(dirname "$rel")"
	cp "$out" "$dst/$rel"
done < "$tmp/list"
echo "retain_working: $copied file(s) $([ "$mode" = --dry-run ] && echo to copy || echo copied)"

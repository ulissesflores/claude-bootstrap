# detect.tape — source for docs/assets/detect.gif: `detect` mapping four project types to
# their profile. Run: `vhs docs/assets/detect.tape` (needs `claude-bootstrap` on PATH).

Output docs/assets/detect.gif

Set Shell bash
Set FontSize 20
Set Width 1080
Set Height 420
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 45ms

# hidden setup: four throwaway sample projects, one per type. Fixed dir name, not `mktemp -d`
# — same reason as demo.tape: keep any machine-specific temp path out of a public artifact.
Hide
Type `D=/tmp/claude-bootstrap-detect; rm -rf "$D"; mkdir -p "$D"; cd "$D"; mkdir fe ds ops paper`
Enter
Type `echo '{}'>fe/package.json; echo '{}'>fe/tsconfig.json; printf '[project]\ndependencies=["torch","pandas"]\n'>ds/pyproject.toml`
Enter
Type `mkdir ops/app ops/k8s-specifications; echo FROM>ops/app/Dockerfile; echo k:v>ops/k8s-specifications/d.yaml`
Enter
Type `printf '\\documentclass{article}'>paper/main.tex; echo '@book{x}'>paper/refs.bib; clear`
Enter
Show

Type "# claude-bootstrap detect — same tool, four project types:"
Enter
Sleep 800ms
Type `for p in fe ds ops paper; do printf "  %-7s -> " "$p"; claude-bootstrap detect $p --quiet; done`
Sleep 400ms
Enter
Sleep 3s

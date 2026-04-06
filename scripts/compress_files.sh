for f in *; do
  [ -f "$f" ] && zip "${f%.*}.zip" "$f"
done
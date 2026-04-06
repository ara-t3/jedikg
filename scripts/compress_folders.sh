for d in */ ; do
  zip -r "${d%/}.zip" "$d"
done
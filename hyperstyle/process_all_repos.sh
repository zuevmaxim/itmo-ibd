echo "Start processing!"
for d in /data/*/ ; do
  echo "Process $d"
  mkdir -p "/output/$(basename $d)/"
  rm "/output/$(basename $d)/result.json"
  python /review/hyperstyle/src/python/review/run_tool.py d > "/output/$(basename $d)/result.json"
  echo "Result saved to /output/$(basename $d)/result.json"
done
echo "Finish processing!"
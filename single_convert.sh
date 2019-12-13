

start=$(date +%s.%N)

convert $1 -resize "300x150" "test.png"
rm "test.png"

dur=$(echo "$(date +%s.%N) - $start" | bc)
printf "Execution time: %.6f seconds" $dur
echo ""

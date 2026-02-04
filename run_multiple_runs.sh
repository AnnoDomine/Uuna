runs=10
for i in $(seq 1 $runs); do
    echo "--- Starting Run $i of $runs ---"
    AI_DEBUG=1 .venv/bin/python3 Tools/ai_researcher_agent.py --start 7.3.5.25600 --end 7.3.5.25600 --limit 10
done

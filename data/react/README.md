# Data files

Episode JSON files contain per-step state, prompt, response, and outcome for a ReAct agent playing the NetSecGame attacker role. All JSON files are gzip-compressed.

| File | Network | Episodes | Win rate |
|------|---------|----------|----------|
| `episode_data_new_ips_1.json.gz` | 1 | 200 (1–200) | 89.5% |
| `episode_data_new_ips_2.json.gz` | 2 | 100 (1–100) | 98.0% |
| `episode_data_new_ips_2b.json.gz` | 2 | 100 (101–200) | 88.0% |
| `episode_data_new_ips_3.json.gz` | 3 | 200 (1–200) | 92.0% |
| `episode_data_new_ips_4.json.gz` | 4 | 200 (1–200) | 99.5% |
| `episode_data_new_ips_5.json.gz` | 5 | 100 (1–100) | 45.0% |
| `episode_data_new_ips_5b.json.gz` | 5 | 100 (101–200) | 97.0% |

Networks 2 and 5 are split across two files; `json_to_csv.py` (repo root) merges them into `episodes.csv`.

**`episodes.csv`** — flat table aggregated from all files: columns `network`, `episode`, `outcome` (win/fail).

**`topology_6.jsonl.gz`** — JSONL trajectory file for topology 6 in the standard NetSecGame format (states, actions, rewards).

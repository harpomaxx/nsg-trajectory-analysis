# Analyze NetSecGame Trajectories

**Skill Name:** `analyze-trajectories`

**Description:** Analyze NetSecGame episode trajectories stored in JSONL format to extract performance metrics, identify patterns, and investigate specific episodes.

## Purpose

This skill provides comprehensive analysis of AI agent performance in NetSecGame episodes. It helps users understand win rates, action patterns, failure modes, and episode-specific behaviors across one or more trajectory files.

## What It Does

When invoked, this skill:

1. **Identifies trajectory files** - Locates JSONL files in the current directory or accepts specific file paths
2. **Provides performance summary** - Shows win rate, average rewards, average steps to win/loss
3. **Analyzes episode patterns** - Identifies common success/failure patterns
4. **Investigates specific episodes** - Deep dives into individual episodes when requested
5. **Exports results** - Can output analysis in human-readable or JSON format

## Usage Examples

```bash
# Analyze all trajectories in current directory
/analyze-trajectories

# Analyze specific file
/analyze-trajectories 2025-09-26_BaseAgent_Attacker.jsonl

# Analyze with episode details
/analyze-trajectories topology_6.jsonl --detailed

# Investigate specific episodes
/analyze-trajectories topology_6.jsonl --episodes 1 5 10

# Export as JSON
/analyze-trajectories *.jsonl --json
```

## Arguments

- **File path(s)** (optional): One or more JSONL files to analyze. If omitted, analyzes all `*.jsonl` in current directory
- `--detailed`: Include per-episode breakdown
- `--episodes N [M ...]`: Deep dive into specific episode numbers
- `--json`: Output results in JSON format for programmatic use
- `--max-lines N`: Limit schema analysis to first N lines (default: 100)

## Implementation Steps

When this skill is invoked:

### 1. Validate Input Files
- Check if trajectory files exist
- Verify JSONL format is valid
- Identify file paths (use glob pattern if needed)

### 2. Run Summary Analysis
Execute: `python3 summary.py <files>`

This provides:
- Total episodes analyzed
- Win rate (%)
- Average reward
- Average steps to win
- Average steps to loss

### 3. Run Episode Count Analysis (if --detailed)
Execute: `python3 count_episodes.py <files>`

This adds:
- Per-episode win/loss indicators
- Episode-by-episode breakdown
- Total wins vs losses

### 4. Investigate Specific Episodes (if --episodes specified)
Execute: `python3 investigate_end_condition.py <file> --episodes <N...>`

This shows:
- Full episode trajectory
- Action sequence
- State evolution
- Final state and reward

### 5. Schema Analysis (if new file format)
Execute: `python3 analyze_jsonl.py <file> --max-lines 100`

This reveals:
- JSONL structure
- Available fields
- Data types
- Sample values

### 6. Present Results
- Format output in readable tables
- Highlight key insights (win rate, common failure points)
- Suggest next steps based on findings

## Expected Output Format

### Summary Output
```
=== NetSecGame Trajectory Analysis ===

Files analyzed: 2025-09-26_BaseAgent_Attacker.jsonl
Total episodes: 150
Valid episodes: 142 (excluded 8 no-action episodes)

Performance Metrics:
- Win rate: 31.0% (44 wins / 142 episodes)
- Average reward: 12.45
- Average steps to win: 33.2
- Average steps to loss: 72.1

Common Patterns:
- All wins end with ExfiltrateData action
- Most losses hit step limit (~100 steps)
- Step penalty: -1 per action
```

### Detailed Episode Breakdown
```
Episode Analysis:
  Episode 1: WIN (reward: 99, steps: 28)
  Episode 2: LOSS (reward: -1, steps: 98)
  Episode 3: WIN (reward: 99, steps: 45)
  ...
```

### Deep Investigation
```
=== Episode 5 Deep Dive ===

Outcome: WIN (reward: 99, steps: 32)

Action Sequence:
  1. ScanNetwork -> discovered 3 networks
  2. FindServices(192.168.1.5) -> found 2 services
  3. ExploitService(192.168.1.5, ssh) -> gained control
  ...
  32. ExfiltrateData(192.168.2.10, data_object_5) -> SUCCESS

Final State:
- Controlled hosts: 5
- Known networks: 4
- Data exfiltrated: data_object_5
```

## Available Tools in Directory

This skill leverages these analysis scripts:

- `summary.py` - Primary metrics (win rate, rewards, steps)
- `count_episodes.py` - Episode counting with win/loss breakdown
- `analyze_jsonl.py` - Schema and structure analysis
- `investigate_end_condition.py` - Deep episode investigation
- `find_short_losses.py` - Identify early termination episodes
- `check_all_early_terminations.py` - Analyze all early failures

## Episode Data Structure

Each JSONL line represents one episode:
```json
{
  "agent_name": "BaseAgent",
  "agent_role": "Attacker",
  "end_reason": null,
  "trajectory": {
    "states": [...],    // Game states (length N+1)
    "actions": [...],   // Actions taken (length N)
    "rewards": [...]    // Rewards received (length N)
  }
}
```

## Key Metrics Interpretation

- **Win**: Final reward >= 50 (typically 99)
- **Loss**: Final reward = -1 (step limit or failed objective)
- **No Action**: Empty actions array (excluded from analysis)
- **Step Penalty**: -1 per action taken
- **Win Reward**: +99 for successful data exfiltration

## Tips for Users

- Use summary for quick performance overview
- Use detailed mode to identify specific failing episodes
- Use episode investigation to understand why specific episodes failed
- Compare multiple trajectory files to track improvement over time
- Use JSON output for automated analysis pipelines

## Error Handling

The skill should handle:
- Missing or malformed JSONL files
- Empty episodes (no actions)
- Incomplete episode data
- Invalid episode numbers for investigation
- Permission errors when reading files

## Notes for Claude

When implementing this skill:
1. Always exclude episodes with `len(actions) == 0` from performance metrics
2. Use existing Python scripts rather than rewriting analysis logic
3. Present results in clear, tabular format
4. Highlight actionable insights (e.g., "Most losses occur at step limit - agent may need better goal detection")
5. Suggest specific episodes to investigate based on interesting patterns
6. If multiple files are analyzed, provide per-file and aggregate statistics

#!/usr/bin/env python3
"""
Find and analyze short losing episodes to understand why they end early.
"""

import json
import sys
from pathlib import Path

def find_short_losses(filepaths, max_steps=50):
    """Find losing episodes that end before max_steps."""

    for filepath in filepaths:
        filepath = Path(filepath)

        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    episode = json.loads(line)
                    trajectory = episode.get('trajectory', {})
                    actions = trajectory.get('actions', [])
                    rewards = trajectory.get('rewards', [])
                    states = trajectory.get('states', [])

                    # Skip no-action episodes
                    if len(actions) == 0:
                        continue

                    num_actions = len(actions)
                    final_reward = rewards[-1] if rewards else None

                    # Check if it's a loss (not a win)
                    is_loss = final_reward is not None and final_reward < 50

                    # Check if it's unusually short
                    if is_loss and num_actions <= max_steps:
                        print(f"\n{'='*80}")
                        print(f"File: {filepath}")
                        print(f"Line: {line_num}")
                        print(f"{'='*80}")
                        print(f"Number of actions: {num_actions}")
                        print(f"Final reward: {final_reward}")
                        print(f"Total reward: {sum(rewards)}")
                        print(f"End reason: {episode.get('end_reason')}")
                        print(f"\nLast 5 actions:")
                        for i, action in enumerate(actions[-5:], start=len(actions)-4):
                            print(f"  {i}. {action.get('action_type')} - reward: {rewards[i-1] if i-1 < len(rewards) else 'N/A'}")

                        print(f"\nFinal state info:")
                        final_state = states[-1] if states else {}
                        print(f"  Controlled hosts: {len(final_state.get('controlled_hosts', []))}")
                        print(f"  Known hosts: {len(final_state.get('known_hosts', []))}")
                        print(f"  Known data: {len(final_state.get('known_data', {}))}")

                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num} in {filepath}: {e}")
                except Exception as e:
                    print(f"Error processing line {line_num} in {filepath}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 find_short_losses.py <file.jsonl> [file2.jsonl ...]")
        sys.exit(1)

    find_short_losses(sys.argv[1:])

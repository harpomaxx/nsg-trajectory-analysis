#!/usr/bin/env python3
"""
Check all episodes for early terminations (non-wins that end before max steps).
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def check_early_terminations(filepaths, step_threshold=95):
    """Find all episodes that end early (not wins, but also not at max steps)."""

    all_early = []
    all_losses = []
    all_wins = []

    for filepath in filepaths:
        filepath = Path(filepath)
        print(f"\nAnalyzing: {filepath}")
        print("="*80)

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

                    # Skip no-action episodes
                    if len(actions) == 0:
                        continue

                    num_actions = len(actions)
                    final_reward = rewards[-1] if rewards else None
                    end_reason = episode.get('end_reason')

                    # Classify episode
                    is_win = final_reward is not None and final_reward >= 50
                    is_early_termination = (not is_win) and num_actions < step_threshold

                    episode_info = {
                        'file': str(filepath),
                        'line': line_num,
                        'num_actions': num_actions,
                        'final_reward': final_reward,
                        'total_reward': sum(rewards) if rewards else 0,
                        'end_reason': end_reason,
                        'final_action': actions[-1].get('action_type') if actions else None,
                    }

                    if is_win:
                        all_wins.append(episode_info)
                    elif is_early_termination:
                        all_early.append(episode_info)
                    else:
                        all_losses.append(episode_info)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                except Exception as e:
                    print(f"Error processing line {line_num}: {e}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal episodes analyzed:")
    print(f"  Wins: {len(all_wins)}")
    print(f"  Normal losses (>= {step_threshold} steps): {len(all_losses)}")
    print(f"  Early terminations (< {step_threshold} steps, non-wins): {len(all_early)}")

    if all_early:
        print(f"\n{'='*80}")
        print("EARLY TERMINATIONS DETAILS")
        print("="*80)

        # Sort by number of actions
        all_early.sort(key=lambda x: x['num_actions'])

        for ep in all_early:
            print(f"\nFile: {ep['file']}, Line: {ep['line']}")
            print(f"  Actions: {ep['num_actions']}")
            print(f"  Final reward: {ep['final_reward']}")
            print(f"  Total reward: {ep['total_reward']}")
            print(f"  End reason: {ep['end_reason']}")
            print(f"  Final action: {ep['final_action']}")

        # Statistics
        print(f"\n{'='*80}")
        print("EARLY TERMINATION STATISTICS")
        print("="*80)
        action_counts = [ep['num_actions'] for ep in all_early]
        print(f"  Count: {len(all_early)}")
        print(f"  Min actions: {min(action_counts)}")
        print(f"  Max actions: {max(action_counts)}")
        print(f"  Avg actions: {sum(action_counts)/len(action_counts):.1f}")

        # End reason distribution
        end_reasons = defaultdict(int)
        for ep in all_early:
            end_reasons[ep['end_reason']] += 1

        print(f"\n  End reason distribution:")
        for reason, count in sorted(end_reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"    {reason}: {count}")

        # Final action distribution
        final_actions = defaultdict(int)
        for ep in all_early:
            final_actions[ep['final_action']] += 1

        print(f"\n  Final action distribution:")
        for action, count in sorted(final_actions.items(), key=lambda x: x[1], reverse=True):
            print(f"    {action}: {count}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 check_all_early_terminations.py <file.jsonl> [file2.jsonl ...]")
        sys.exit(1)

    check_early_terminations(sys.argv[1:])

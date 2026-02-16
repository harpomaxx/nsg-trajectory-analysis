#!/usr/bin/env python3
"""
Episode Summary Statistics
Provides a concise summary of episode performance metrics.
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict


def analyze_episodes(filepaths, step_limit_threshold=100):
    """Analyze episodes and compute summary statistics.

    Args:
        filepaths: List of JSONL files to analyze
        step_limit_threshold: Number of steps to classify as "step limit reached" (default: 100)
    """

    all_episodes = []
    win_episodes = []
    loss_episodes = []
    loss_step_limit = []
    loss_invalid_actions = []

    # Read all episodes from all files
    for filepath in filepaths:
        filepath = Path(filepath)

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    episode = json.loads(line)
                    trajectory = episode.get('trajectory', {})
                    actions = trajectory.get('actions', [])
                    rewards = trajectory.get('rewards', [])
                    states = trajectory.get('states', [])

                    # Skip episodes with no actions
                    if len(actions) == 0:
                        continue

                    episode_data = {
                        'num_actions': len(actions),
                        'num_states': len(states),
                        'total_reward': sum(rewards) if rewards else 0,
                        'final_reward': rewards[-1] if rewards else None,
                        'final_action': actions[-1].get('action_type') if actions else None,
                        'agent_name': episode.get('agent_name'),
                        'agent_role': episode.get('agent_role'),
                    }

                    # Determine outcome
                    if rewards and rewards[-1] >= 50:
                        episode_data['outcome'] = 'win'
                        win_episodes.append(episode_data)
                    else:
                        episode_data['outcome'] = 'loss'
                        loss_episodes.append(episode_data)

                        # Categorize loss type
                        if len(actions) >= step_limit_threshold:
                            episode_data['loss_type'] = 'step_limit'
                            loss_step_limit.append(episode_data)
                        else:
                            episode_data['loss_type'] = 'invalid_actions'
                            loss_invalid_actions.append(episode_data)

                    all_episodes.append(episode_data)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line in {filepath}: {e}")
                except Exception as e:
                    print(f"Error processing line in {filepath}: {e}")

    return all_episodes, win_episodes, loss_episodes, loss_step_limit, loss_invalid_actions


def print_summary(all_episodes, win_episodes, loss_episodes, loss_step_limit, loss_invalid_actions):
    """Print summary statistics."""

    total = len(all_episodes)
    wins = len(win_episodes)
    losses = len(loss_episodes)

    print("\n" + "="*80)
    print("EPISODE SUMMARY")
    print("="*80 + "\n")

    print(f"Total Episodes (with actions): {total}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"  - Step Limit Reached: {len(loss_step_limit)}")
    print(f"  - Invalid Actions Exhausted: {len(loss_invalid_actions)}")
    print(f"Win Rate: {wins/total*100:.1f}%" if total > 0 else "Win Rate: N/A")

    print("\n" + "-"*80)
    print("OVERALL STATISTICS")
    print("-"*80 + "\n")

    if all_episodes:
        avg_actions = sum(ep['num_actions'] for ep in all_episodes) / len(all_episodes)
        avg_reward = sum(ep['total_reward'] for ep in all_episodes) / len(all_episodes)
        min_actions = min(ep['num_actions'] for ep in all_episodes)
        max_actions = max(ep['num_actions'] for ep in all_episodes)

        print(f"Average Steps: {avg_actions:.1f}")
        print(f"Average Total Reward: {avg_reward:.2f}")
        print(f"Min Steps: {min_actions}")
        print(f"Max Steps: {max_actions}")

    print("\n" + "-"*80)
    print("WINNING EPISODES")
    print("-"*80 + "\n")

    if win_episodes:
        avg_win_actions = sum(ep['num_actions'] for ep in win_episodes) / len(win_episodes)
        avg_win_reward = sum(ep['total_reward'] for ep in win_episodes) / len(win_episodes)
        min_win_actions = min(ep['num_actions'] for ep in win_episodes)
        max_win_actions = max(ep['num_actions'] for ep in win_episodes)

        print(f"Number of Wins: {wins}")
        print(f"Average Steps to Win: {avg_win_actions:.1f}")
        print(f"Average Total Reward: {avg_win_reward:.2f}")
        print(f"Fastest Win: {min_win_actions} steps")
        print(f"Slowest Win: {max_win_actions} steps")

        # Final action breakdown for wins
        final_actions = {}
        for ep in win_episodes:
            action = ep['final_action']
            final_actions[action] = final_actions.get(action, 0) + 1

        print(f"\nFinal Actions in Winning Episodes:")
        for action, count in sorted(final_actions.items(), key=lambda x: x[1], reverse=True):
            print(f"  {action}: {count}")
    else:
        print("No winning episodes found.")

    print("\n" + "-"*80)
    print("LOSING EPISODES")
    print("-"*80 + "\n")

    if loss_episodes:
        avg_loss_actions = sum(ep['num_actions'] for ep in loss_episodes) / len(loss_episodes)
        avg_loss_reward = sum(ep['total_reward'] for ep in loss_episodes) / len(loss_episodes)
        min_loss_actions = min(ep['num_actions'] for ep in loss_episodes)
        max_loss_actions = max(ep['num_actions'] for ep in loss_episodes)

        print(f"Number of Losses: {losses}")
        print(f"Average Steps in Loss: {avg_loss_actions:.1f}")
        print(f"Average Total Reward: {avg_loss_reward:.2f}")
        print(f"Min Steps: {min_loss_actions} steps")
        print(f"Max Steps: {max_loss_actions} steps")

        # Final action breakdown for losses
        final_actions = {}
        for ep in loss_episodes:
            action = ep['final_action']
            final_actions[action] = final_actions.get(action, 0) + 1

        print(f"\nFinal Actions in Losing Episodes:")
        for action, count in sorted(final_actions.items(), key=lambda x: x[1], reverse=True):
            print(f"  {action}: {count}")

        # Loss type breakdown
        print("\n" + "-"*40)
        print("LOSS TYPE: STEP LIMIT REACHED")
        print("-"*40 + "\n")

        if loss_step_limit:
            avg_steps = sum(ep['num_actions'] for ep in loss_step_limit) / len(loss_step_limit)
            avg_reward = sum(ep['total_reward'] for ep in loss_step_limit) / len(loss_step_limit)

            print(f"Count: {len(loss_step_limit)}")
            print(f"Average Steps: {avg_steps:.1f}")
            print(f"Average Total Reward: {avg_reward:.2f}")

            # Final action breakdown
            final_actions = {}
            for ep in loss_step_limit:
                action = ep['final_action']
                final_actions[action] = final_actions.get(action, 0) + 1

            print(f"\nFinal Actions:")
            for action, count in sorted(final_actions.items(), key=lambda x: x[1], reverse=True):
                print(f"  {action}: {count}")
        else:
            print("No step-limit losses found.")

        print("\n" + "-"*40)
        print("LOSS TYPE: INVALID ACTIONS EXHAUSTED")
        print("-"*40 + "\n")

        if loss_invalid_actions:
            avg_steps = sum(ep['num_actions'] for ep in loss_invalid_actions) / len(loss_invalid_actions)
            avg_reward = sum(ep['total_reward'] for ep in loss_invalid_actions) / len(loss_invalid_actions)
            min_steps = min(ep['num_actions'] for ep in loss_invalid_actions)
            max_steps = max(ep['num_actions'] for ep in loss_invalid_actions)

            print(f"Count: {len(loss_invalid_actions)}")
            print(f"Average Steps: {avg_steps:.1f}")
            print(f"Average Total Reward: {avg_reward:.2f}")
            print(f"Min Steps: {min_steps} steps")
            print(f"Max Steps: {max_steps} steps")

            # Final action breakdown
            final_actions = {}
            for ep in loss_invalid_actions:
                action = ep['final_action']
                final_actions[action] = final_actions.get(action, 0) + 1

            print(f"\nFinal Actions:")
            for action, count in sorted(final_actions.items(), key=lambda x: x[1], reverse=True):
                print(f"  {action}: {count}")
        else:
            print("No invalid-action losses found.")
    else:
        print("No losing episodes found.")

    print("\n" + "="*80 + "\n")


def print_compact_summary(all_episodes, win_episodes, loss_episodes, loss_step_limit, loss_invalid_actions):
    """Print a compact one-line summary."""

    total = len(all_episodes)
    wins = len(win_episodes)
    losses = len(loss_episodes)
    win_rate = wins/total*100 if total > 0 else 0

    avg_reward = sum(ep['total_reward'] for ep in all_episodes) / len(all_episodes) if all_episodes else 0
    avg_win_steps = sum(ep['num_actions'] for ep in win_episodes) / len(win_episodes) if win_episodes else 0

    print(f"Episodes: {total} | Wins: {wins} ({win_rate:.1f}%) | Losses: {losses} (StepLimit: {len(loss_step_limit)}, InvalidActions: {len(loss_invalid_actions)}) | Avg Reward: {avg_reward:.1f} | Avg Steps to Win: {avg_win_steps:.1f}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate summary statistics for episode data'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='JSONL files to analyze'
    )
    parser.add_argument(
        '--compact',
        action='store_true',
        help='Print compact one-line summary'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--step-limit',
        type=int,
        default=100,
        help='Threshold for classifying loss as "step limit reached" (default: 100)'
    )

    args = parser.parse_args()

    all_episodes, win_episodes, loss_episodes, loss_step_limit, loss_invalid_actions = analyze_episodes(args.files, args.step_limit)

    if args.json:
        import json as json_module
        output = {
            'total_episodes': len(all_episodes),
            'wins': len(win_episodes),
            'losses': len(loss_episodes),
            'losses_step_limit': len(loss_step_limit),
            'losses_invalid_actions': len(loss_invalid_actions),
            'win_rate': len(win_episodes)/len(all_episodes)*100 if all_episodes else 0,
            'overall': {
                'avg_steps': sum(ep['num_actions'] for ep in all_episodes) / len(all_episodes) if all_episodes else 0,
                'avg_reward': sum(ep['total_reward'] for ep in all_episodes) / len(all_episodes) if all_episodes else 0,
            },
            'wins_stats': {
                'avg_steps': sum(ep['num_actions'] for ep in win_episodes) / len(win_episodes) if win_episodes else 0,
                'avg_reward': sum(ep['total_reward'] for ep in win_episodes) / len(win_episodes) if win_episodes else 0,
                'min_steps': min(ep['num_actions'] for ep in win_episodes) if win_episodes else 0,
                'max_steps': max(ep['num_actions'] for ep in win_episodes) if win_episodes else 0,
            },
            'loss_stats': {
                'avg_steps': sum(ep['num_actions'] for ep in loss_episodes) / len(loss_episodes) if loss_episodes else 0,
                'avg_reward': sum(ep['total_reward'] for ep in loss_episodes) / len(loss_episodes) if loss_episodes else 0,
            },
            'loss_step_limit_stats': {
                'count': len(loss_step_limit),
                'avg_steps': sum(ep['num_actions'] for ep in loss_step_limit) / len(loss_step_limit) if loss_step_limit else 0,
                'avg_reward': sum(ep['total_reward'] for ep in loss_step_limit) / len(loss_step_limit) if loss_step_limit else 0,
            },
            'loss_invalid_actions_stats': {
                'count': len(loss_invalid_actions),
                'avg_steps': sum(ep['num_actions'] for ep in loss_invalid_actions) / len(loss_invalid_actions) if loss_invalid_actions else 0,
                'avg_reward': sum(ep['total_reward'] for ep in loss_invalid_actions) / len(loss_invalid_actions) if loss_invalid_actions else 0,
                'min_steps': min(ep['num_actions'] for ep in loss_invalid_actions) if loss_invalid_actions else 0,
                'max_steps': max(ep['num_actions'] for ep in loss_invalid_actions) if loss_invalid_actions else 0,
            }
        }
        print(json_module.dumps(output, indent=2))
    elif args.compact:
        print_compact_summary(all_episodes, win_episodes, loss_episodes, loss_step_limit, loss_invalid_actions)
    else:
        print_summary(all_episodes, win_episodes, loss_episodes, loss_step_limit, loss_invalid_actions)


if __name__ == '__main__':
    main()

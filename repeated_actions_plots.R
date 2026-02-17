#!/usr/bin/env Rscript
# repeated_actions_plots.R
# Usage: Rscript repeated_actions_plots.R <input.csv> [output_prefix]
#
# Generates four publication-quality PNG plots from the CSV exported by
# repeated_actions.py --csv.
#
# Input CSV columns:
#   episode              - episode number
#   outcome              - "win" or "loss"
#   total_actions        - total actions in episode
#   unique_actions       - distinct action types used
#   num_repeated_actions - distinct actions executed more than once
#   total_repetitions    - total number of extra (repeated) action executions
#   repeat_percentage    - total_repetitions / total_actions * 100

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
})

# --------------------------------------------------------------------------- #
# Parse command-line arguments
# --------------------------------------------------------------------------- #
args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  cat("Usage: Rscript repeated_actions_plots.R <input.csv> [output_prefix]\n")
  quit(status = 1)
}

input_csv     <- args[1]
output_prefix <- if (length(args) >= 2) args[2] else "repeated_actions"

# --------------------------------------------------------------------------- #
# Load data
# --------------------------------------------------------------------------- #
df <- read.csv(input_csv, stringsAsFactors = FALSE)

# Validate required columns
required_cols <- c("episode", "outcome", "total_actions", "unique_actions",
                   "num_repeated_actions", "total_repetitions", "repeat_percentage")
missing <- setdiff(required_cols, names(df))
if (length(missing) > 0) {
  stop("Missing columns in CSV: ", paste(missing, collapse = ", "))
}

# Make outcome a factor with a fixed order (All added below where needed)
df$outcome <- factor(df$outcome, levels = c("win", "loss"))

# Counts for annotation
n_all  <- nrow(df)
n_win  <- sum(df$outcome == "win")
n_loss <- sum(df$outcome == "loss")

# Shared theme
base_theme <- theme_bw(base_size = 13) +
  theme(
    plot.title   = element_text(face = "bold", size = 14),
    panel.grid.minor = element_blank()
  )

outcome_colours <- c("win" = "#2ecc71", "loss" = "#e74c3c")
outcome_fills   <- c("win" = "#2ecc71", "loss" = "#e74c3c")

# --------------------------------------------------------------------------- #
# Helper: build a "long" data frame that includes an "all" group
# --------------------------------------------------------------------------- #
make_long <- function(data, value_col) {
  all_rows  <- data
  all_rows$group <- "all"
  win_rows  <- data[data$outcome == "win",  ]
  win_rows$group  <- "win"
  loss_rows <- data[data$outcome == "loss", ]
  loss_rows$group <- "loss"
  combined  <- rbind(all_rows, win_rows, loss_rows)
  combined$group  <- factor(combined$group, levels = c("all", "win", "loss"))
  combined$value  <- combined[[value_col]]
  combined
}

group_colours <- c("all" = "#3498db", "win" = "#2ecc71", "loss" = "#e74c3c")
group_labels  <- c(
  all  = sprintf("All\n(n=%d)",  n_all),
  win  = sprintf("Win\n(n=%d)",  n_win),
  loss = sprintf("Loss\n(n=%d)", n_loss)
)

# --------------------------------------------------------------------------- #
# Plot 1 – Boxplot: total_repetitions by outcome group
# --------------------------------------------------------------------------- #
long1 <- make_long(df, "total_repetitions")

p1 <- ggplot(long1, aes(x = group, y = value, fill = group)) +
  geom_boxplot(outlier.shape = 21, outlier.size = 1.5, alpha = 0.7,
               show.legend = FALSE) +
  stat_summary(fun = mean, geom = "point", shape = 23,
               size = 3, fill = "white", colour = "black") +
  scale_fill_manual(values = group_colours) +
  scale_x_discrete(labels = group_labels) +
  labs(
    title = "Total Repetitions by Outcome",
    x     = NULL,
    y     = "Total repetitions"
  ) +
  base_theme

out1 <- paste0(output_prefix, "_boxplot_total_reps.png")
ggsave(out1, p1, width = 7, height = 5, dpi = 300)
cat("Saved:", out1, "\n")

# --------------------------------------------------------------------------- #
# Plot 2 – Boxplot: num_repeated_actions by outcome group
# --------------------------------------------------------------------------- #
long2 <- make_long(df, "num_repeated_actions")

p2 <- ggplot(long2, aes(x = group, y = value, fill = group)) +
  geom_boxplot(outlier.shape = 21, outlier.size = 1.5, alpha = 0.7,
               show.legend = FALSE) +
  stat_summary(fun = mean, geom = "point", shape = 23,
               size = 3, fill = "white", colour = "black") +
  scale_fill_manual(values = group_colours) +
  scale_x_discrete(labels = group_labels) +
  labs(
    title = "Distinct Repeated Actions by Outcome",
    x     = NULL,
    y     = "Distinct repeated actions"
  ) +
  base_theme

out2 <- paste0(output_prefix, "_boxplot_num_repeated.png")
ggsave(out2, p2, width = 7, height = 5, dpi = 300)
cat("Saved:", out2, "\n")

# --------------------------------------------------------------------------- #
# Plot 3 – Histogram: total_repetitions faceted by outcome
# --------------------------------------------------------------------------- #
p3 <- ggplot(df, aes(x = total_repetitions, fill = outcome)) +
  geom_histogram(binwidth = 1, colour = "white", alpha = 0.85) +
  facet_wrap(~ outcome,
             labeller = labeller(outcome = c(win  = sprintf("Win (n=%d)",  n_win),
                                             loss = sprintf("Loss (n=%d)", n_loss)))) +
  scale_fill_manual(values = outcome_fills, guide = "none") +
  labs(
    title = "Distribution of Total Repetitions",
    x     = "Total repetitions",
    y     = "Number of episodes"
  ) +
  base_theme

out3 <- paste0(output_prefix, "_hist_total_reps.png")
ggsave(out3, p3, width = 9, height = 4.5, dpi = 300)
cat("Saved:", out3, "\n")

# --------------------------------------------------------------------------- #
# Plot 4 – Scatter: total_actions vs total_repetitions, coloured by outcome
# --------------------------------------------------------------------------- #
p4 <- ggplot(df, aes(x = total_actions, y = total_repetitions, colour = outcome)) +
  geom_point(alpha = 0.55, size = 1.8) +
  geom_smooth(method = "lm", se = TRUE, linewidth = 0.9) +
  scale_colour_manual(
    values = outcome_colours,
    labels = c(win  = sprintf("Win (n=%d)",  n_win),
               loss = sprintf("Loss (n=%d)", n_loss))
  ) +
  labs(
    title  = "Total Actions vs. Total Repetitions",
    x      = "Total actions",
    y      = "Total repetitions",
    colour = "Outcome"
  ) +
  base_theme +
  theme(legend.position = "inside", legend.position.inside = c(0.02, 0.98),
        legend.justification = c(0, 1))

out4 <- paste0(output_prefix, "_scatter.png")
ggsave(out4, p4, width = 7, height = 5, dpi = 300)
cat("Saved:", out4, "\n")

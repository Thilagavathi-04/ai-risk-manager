# Design Guide

## Product style

The interface is designed to look and feel like a modern merchant-risk operations console. It should communicate trust, clarity, and decision support without feeling like a raw ML demo.

## Core UI principles

- clear risk labels
- visible business thresholds
- explainable decisions
- minimal clutter
- review-oriented workflow

## Layout structure

The main dashboard uses a dominant top navigation, KPI cards, and clear panels for transactions, evaluation, and model metadata.

Typical sections include:

- summary statistics
- transaction queue
- flagged transaction detail
- model comparison table
- threshold/cost analysis
- decision settings
- CSV and manual test input forms

## Risk semantics

Use consistent risk labeling:

- LOW: normal or low-risk path
- MEDIUM: verification path
- HIGH: manual review path

These states should always appear with both a textual label and a numeric score.

## Inputs and actions

The UI supports two test flows:

1. CSV upload validation for dataset checks
2. manual single-row transaction test for direct model evaluation

This gives operators both dataset-scale and row-level testing without requiring a separate tool.

## Accessibility and clarity

- use descriptive labels on every form field
- keep actions obvious and near the form they act on
- show model reasoning as readable bullet points
- maintain strong visual separation between data and actions

## Implementation note

The current implementation uses server-rendered Jinja templates with a shared base layout and a consistent panel/card style.

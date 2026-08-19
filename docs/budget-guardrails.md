# Budget guardrails

**Status:** Specified. Live AWS budget actions are **Deferred**. Default `BUDGET_DRY_RUN=true`.

Planned beta thresholds:

| Threshold | Planned action |
| --- | --- |
| 50% | Notify |
| 70% | Reduce noncritical worker capacity |
| 80% | Disable new media uploads |
| 90% | Maintenance mode; scale down optional workloads |

Requirements:

- Log planned and completed actions
- Require explicit `BUDGET_LIVE_ACTIONS_ENABLED=true` before live actions
- Never publish unmoderated media
- Never automatically delete the production database
- Never delete user content outside retention policy
- Never disable security logging to reduce cost

Recovery: re-enable flags after the budget owner approves; restore worker replicas from last known Helm values.

# Dashboard Module Integration — Pixel AI Office / Mission Control

## Purpose

Surface secret-recon findings inside the existing cyberpunk Pixel AI Office dashboard (sirinx.co / GhostClaw control plane).

## Required UI Components

1. **Severity Distribution** (pie / donut)
   - Critical / High / Medium / Low / Info
   - Color map: Critical=#ff0033, High=#ff6600, Medium=#ffcc00, Low=#00cc66, Info=#888

2. **Open Findings Table**
   - Columns: Fingerprint (truncated), Type, Severity, Repo, File, Status, First Seen, Assigned
   - Click → detail drawer (no raw secret ever shown)

3. **Last Scan Status**
   - Source, Target, Duration, Findings count, Timestamp
   - “Re-scan now” button → triggers n8n or GhostClaw task

4. **Remediation Pipeline**
   - Open → Triaged → Remediated / False Positive / Wont Fix
   - Critical items show “Require Human Approval” badge

## Data Source

- Supabase table `secret_recon_findings` + `secret_recon_scans`
- Real-time via Supabase Realtime or polling every 30–60s
- Never hydrate raw secret values into React state or localStorage

## GhostClaw Hook

When a Critical finding is opened in the dashboard:

```ts
// Pseudo
dispatchGhostClawTask({
  type: 'secret-recon-critical',
  findingId: id,
  severity: 'Critical',
  requiresApproval: true,
  payload: { fingerprint, repo, file } // no secret value
});
```

## 3D / Motionsites Extension (Optional)

If the dashboard already uses the Motionsites.ai / 3D solar design system capital:

- Mount a floating “Security Hygiene” orb that glows red on Critical count > 0
- Click → expand findings panel with same cyberpunk aesthetic

## Implementation Notes

- Place under `dashboard/modules/secret-recon/`
- Follow existing module function pattern used for other SIRINX dashboard modules
- Use OmniRoute only for classification side-panels, never for displaying secrets

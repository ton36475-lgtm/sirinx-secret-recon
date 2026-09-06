output "protected_repos" {
  description = "Repos declared for secret-scanning enablement"
  value       = var.repos_to_protect
}

output "github_owner" {
  value = var.github_owner
}

output "next_steps" {
  value = <<-EOT
    1. Enable Secret Scanning + Push Protection in GitHub UI (GHAS) on each owned repo.
    2. Deploy .github/workflows/secret-scan.yml from this package.
    3. Import n8n/secret-recon-orchestrator.json and run dry-run first.
    4. Apply supabase/schema.sql (fingerprints only).
    5. Wire findings into GhostClaw a2a — human gate for High/Critical.
    6. Never search public GitHub for third-party API keys.
  EOT
}

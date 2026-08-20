# SIRINX / GhostClaw — Secret Recon Terraform Skeleton
# Declarative enablement of secret scanning, alerting, and optional runners.
# Apply only after human review. Scope: own assets only.

terraform {
  required_version = ">= 1.5"
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    # Optional: cloudflare, aws for runners/alerting
  }
}

provider "github" {
  # Token via GITHUB_TOKEN env or GitHub App installation
  owner = var.github_owner
}

variable "github_owner" {
  type        = string
  description = "GitHub owner (user or org) — must be ton36475-lgtm or controlled"
  default     = "ton36475-lgtm"
}

variable "repos_to_protect" {
  type        = list(string)
  description = "Repositories to enable secret scanning + push protection"
  default = [
    "sirinx-os",
    "sirinx-co",
    "sirinx-skills-kit",
    "ghost-claw-os",
    "oz-corp-omega-dual-node",
    "hermes-os",
    "sirinx-solar-energy",
    "sirinx-sovereign-swarm",
    "automation-dashboard",
    "automation-system-backend",
  ]
}

# Note: Full secret-scanning enablement via Terraform may require GitHub Enterprise
# or the newer github_repository_security_and_analysis resource.
# This skeleton documents the intent and can be extended.

resource "github_repository" "protected" {
  for_each = toset(var.repos_to_protect)

  name                   = each.value
  # Assume repos already exist — do not create
  # Use data source in production for existing repos
  lifecycle {
    ignore_changes = all
  }
}

# Example: enable vulnerability alerts (proxy for security posture)
# For full secret scanning, prefer GitHub UI or API until provider supports it fully.

output "protected_repos" {
  value = var.repos_to_protect
}

output "next_steps" {
  value = <<-EOT
    1. Manually enable Secret Scanning + Push Protection on each repo via GitHub UI.
    2. Deploy .github/workflows/secret-scan.yml from this package.
    3. Configure n8n webhook receivers for security events.
    4. Wire findings into GhostClaw a2a dispatch.
  EOT
}

variable "github_owner" {
  type    = string
  default = "ton36475-lgtm"
}

variable "scan_repos" {
  type = list(string)
  default = [
    "sirinx-secret-recon",
    "sirinx-os",
    "ghost-claw-os",
    "sirinx-co",
    "sirinx-skills-kit",
    "sirinx-sovereign-swarm",
  ]
}

variable "alert_webhook_url" {
  type      = string
  default   = ""
  sensitive = true
}

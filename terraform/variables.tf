variable "github_owner" {
  type        = string
  description = "GitHub owner (user or org)"
  default     = "ton36475-lgtm"
}

variable "repos_to_protect" {
  type        = list(string)
  description = "List of repository names under the owner to protect"
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
    "automated-marketing-agency",
    "chokma-growth-os",
  ]
}

variable "enable_push_protection" {
  type        = bool
  description = "Whether to enable push protection (recommended)"
  default     = true
}

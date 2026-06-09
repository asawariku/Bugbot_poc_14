output "environment" {
  description = "Deployed environment."
  value       = module.app.environment
}

output "project_name" {
  description = "Project name for this environment."
  value       = module.app.project_name
}

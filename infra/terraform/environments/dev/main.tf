locals {
  environment = "dev"
}

module "app" {
  source = "../../modules/app"

  environment  = local.environment
  project_name = var.project_name
  tags         = var.tags
}

# Terraform Infrastructure

This directory contains Terraform configuration organized by environment and reusable modules.

## Layout

```text
infra/terraform/
  environments/
    dev/
    prod/
  modules/
    app/
```

## Usage

From an environment directory:

```bash
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

Copy `terraform.tfvars.example` to `terraform.tfvars` and fill in environment-specific values before applying.

## Notes

- Backend configuration is intentionally left as a placeholder in each environment.
- Provider-specific resources should be added inside modules and wired from each environment.
- Do not commit real `*.tfvars` files or Terraform state files.

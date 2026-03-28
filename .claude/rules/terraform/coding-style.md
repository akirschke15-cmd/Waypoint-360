# Terraform Coding Style

## File Organization

```
terraform/
├── main.tf           # Primary resources
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── locals.tf         # Local values
├── terraform.tfvars  # Variable values
├── versions.tf       # Terraform and provider versions
└── modules/          # Reusable modules
    └── vpc/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Naming Conventions

- Resource names: `snake_case` - `aws_instance.app_server`
- Variable names: `snake_case` - `var.instance_count`
- Output names: `snake_case` - `output.instance_id`
- Data source names: `snake_case` - `data.aws_ami.ubuntu`

## Resource Naming

Always use descriptive names with context:

```hcl
# WRONG: Too generic
resource "aws_instance" "main" {
  ami = "ami-12345"
}

# CORRECT: Descriptive
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
}
```

## Variables

Define all inputs clearly:

```hcl
variable "instance_count" {
  description = "Number of EC2 instances to create"
  type        = number
  default     = 1

  validation {
    condition     = var.instance_count > 0
    error_message = "Instance count must be positive."
  }
}
```

## Outputs

Export all important values:

```hcl
output "instance_ids" {
  description = "IDs of created instances"
  value       = aws_instance.app_server[*].id
}
```

## Locals

Use locals for computed values:

```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }

  instance_name = "${var.project_name}-${var.environment}-instance"
}
```

## State Management

- Never commit terraform.tfstate to git
- Use remote state (S3, Terraform Cloud)
- Enable state locking for team environments
- Regular backups of state

## Best Practices

1. **DRY Principle**: Extract common patterns to modules
2. **Sensitive Data**: Use sensitive flag for passwords/keys
3. **Validation**: Add validation blocks for variables
4. **Documentation**: Describe all variables and outputs
5. **Dependencies**: Use explicit `depends_on` when needed
6. **Count vs. For-Each**: Prefer for_each for maps, count for simple iteration

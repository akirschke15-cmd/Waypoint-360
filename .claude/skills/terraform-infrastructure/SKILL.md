---
name: terraform-infrastructure
description: Terraform infrastructure as code patterns for multi-cloud deployments, state management, security best practices, module development, and automation workflows.
origin: Boiler 3.0
version: 1.0
---

# Terraform Infrastructure as Code Skill

## Overview
This skill provides comprehensive guidance for Terraform infrastructure provisioning, covering best practices for multi-cloud deployments, state management, security, and automation workflows.

## When This Skill Activates
- Working with `.tf` or `.tfvars` files
- Infrastructure provisioning tasks
- Cloud resource management (AWS, Azure, GCP)
- Infrastructure as Code (IaC) projects
- DevOps automation

## Quick Reference

### Project Structure
```text
terraform-project/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── production/
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── compute/
│   └── database/
├── .terraform.lock.hcl
└── README.md
```

### Basic Terraform Configuration

#### Provider Configuration
```hcl
# versions.tf
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }
  }
}
```

#### Variables and Outputs
```hcl
# variables.tf
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid CIDR block."
  }
}

variable "instance_count" {
  description = "Number of instances to create"
  type        = number
  default     = 2

  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

# outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}
```

### State Management Best Practices

#### Remote Backend Configuration (S3 + DynamoDB)
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "production/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT:key/KEY-ID"
    dynamodb_table = "terraform-state-locks"

    # Workspace support
    workspace_key_prefix = "workspaces"
  }
}

# Create backend resources
resource "aws_s3_bucket" "terraform_state" {
  bucket = "company-terraform-state"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform_state.arn
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### Security Best Practices

#### Secrets Management
```hcl
# Use AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "production/database/password"
}

locals {
  db_credentials = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)
}

resource "aws_db_instance" "main" {
  # ...
  username = local.db_credentials.username
  password = local.db_credentials.password
}

# Or use sensitive variables (mark as sensitive in terraform.tfvars)
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

#### Least Privilege IAM
```hcl
data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "web" {
  name               = "${var.environment}-web-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

data "aws_iam_policy_document" "web_permissions" {
  statement {
    sid = "S3Access"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.assets.arn,
      "${aws_s3_bucket.assets.arn}/*"
    ]
  }

  statement {
    sid = "CloudWatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:log-group:/aws/ec2/${var.environment}*"]
  }
}

resource "aws_iam_role_policy" "web" {
  name   = "${var.environment}-web-policy"
  role   = aws_iam_role.web.id
  policy = data.aws_iam_policy_document.web_permissions.json
}
```

### Module Development

#### Reusable VPC Module
```hcl
# modules/vpc/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Enable NAT gateways for private subnets"
  type        = bool
  default     = true
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# Usage in root module
module "vpc" {
  source = "./modules/vpc"

  environment        = var.environment
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  enable_nat_gateway = true
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

## Terraform Workflow

```bash
# Initialize (download providers, setup backend)
terraform init

# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Plan changes (see what will change)
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Show current state
terraform show

# List resources
terraform state list

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0

# Destroy all resources
terraform destroy
```

## CI/CD Integration

```yaml
# GitLab CI example
.terraform_template:
  image: hashicorp/terraform:1.6
  before_script:
    - terraform init

stages:
  - validate
  - plan
  - apply

validate:
  extends: .terraform_template
  stage: validate
  script:
    - terraform fmt -check -recursive
    - terraform validate
    - tflint

plan:
  extends: .terraform_template
  stage: plan
  script:
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - tfplan
    expire_in: 1 week

apply:
  extends: .terraform_template
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  when: manual
  only:
    - main
```

## Best Practices Summary

1. **Remote State**: Always use remote state with locking
2. **Modules**: Create reusable modules for common patterns
3. **Variables**: Use validation and descriptions
4. **Outputs**: Expose necessary information
5. **Versioning**: Pin provider versions
6. **Security**: Never commit secrets, use secret managers
7. **Naming**: Use consistent naming conventions
8. **Tags**: Tag all resources for cost allocation
9. **State Files**: Never edit state manually
10. **Documentation**: Document modules with README

## Common Pitfalls to Avoid

- Not using remote state
- Hardcoding values instead of using variables
- Not pinning provider versions
- Committing `.tfstate` files or secrets
- Not using workspaces or separate state files for environments
- Overly complex single files (use modules)
- Not using data sources for existing resources
- Ignoring security group rules
- Not enabling encryption
- Skipping `terraform plan` before `apply`

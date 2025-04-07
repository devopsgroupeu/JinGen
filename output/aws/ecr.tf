locals {
  ecr_repositories = [
    "${var.global_prefix}example-app",
  ]
}

module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.3"

  for_each        = toset(var.ecr_repositories)
  repository_type = "private"
  repository_name = each.value

  repository_encryption_type      = "AES256"
  repository_image_tag_mutability = "MUTABLE"
  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last 25 images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["v"],
          countType     = "imageCountMoreThan",
          countNumber   = 25
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

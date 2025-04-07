module "alb" {
  source  = "gitlab.devops-cloud.io/devopsgroupsk/alb/aws"
  version = "0.1.1"

  name = "${var.global_prefix}default-lb"

  vpc_id  = module.vpc.vpc_id
  subnets = module.vpc.public_subnets

  enable_access_logs      = false
  access_logs_bucket_name = ""

  cluster_name      = module.eks.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.cluster_oidc_issuer_url

  lb_tags = {
    "ingress.k8s.aws/stack"    = "default"
    "ingress.k8s.aws/resource" = "LoadBalancer"
    "elbv2.k8s.aws/cluster"    = module.eks.cluster_name
  }
}
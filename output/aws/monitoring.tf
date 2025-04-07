module "loki_aws" {
  source  = "gitlab.devops-cloud.io/devopsgroupsk/loki-aws/aws"
  version = "0.2.0"

  cluster_name      = module.eks.cluster_name
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.cluster_oidc_issuer_url

  namespace            = "monitoring"
  service_account_name = "loki-sa"
}

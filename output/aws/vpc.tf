data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, var.availability_zones_count)
  nat_gateway = {
    enable_nat_gateway     = coalesce(var.nat_gateway_strategy == "NO_NAT" ? false : true)
    single_nat_gateway     = coalesce(var.nat_gateway_strategy == "SINGLE" ? true : false)
    one_nat_gateway_per_az = coalesce(var.nat_gateway_strategy == "ONE_PER_AZ" ? true : false)
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.19"

  name = "${var.global_prefix}vpc-${var.environment_short}"
  cidr = var.vpc_cidr

  azs              = local.azs
  private_subnets  = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k)]
  public_subnets   = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k + 4)]
  database_subnets = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k + 8)]
  intra_subnets    = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k + 12)]

  enable_dns_hostnames   = true
  enable_dns_support     = true
  enable_nat_gateway     = local.nat_gateway.enable_nat_gateway
  single_nat_gateway     = local.nat_gateway.single_nat_gateway
  one_nat_gateway_per_az = local.nat_gateway.one_nat_gateway_per_az

  create_database_subnet_group = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                      = "1"
  }

  private_subnet_tags = {
    "karpenter.sh/discovery"                      = local.cluster_name
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"             = "1"
  }
}

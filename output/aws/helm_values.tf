locals {
  helm_charts = {

    karpenter = {
      template_values_file = "${path.module}/../../helm/karpenter/values.yaml.tftpl"
      values = {
        cluster_name     = module.eks.cluster_name
        cluster_endpoint = module.eks.cluster_endpoint
        queue_name       = module.karpenter.queue_name
      }
    }

    promtail = {
      template_values_file = "${path.module}/../../helm/promtail/values.yaml.tftpl"
      values = {
        logLevel = "info"
      }
    }

    aws_load_balancer_controller = {
      template_values_file = "${path.module}/../../helm/aws-load-balancer-controller/values.yaml.tftpl"
      values = {
        service_account_name = module.alb.service_account_name
        lb_role_arn          = module.alb.lb_role_arn
        cluster_name         = module.eks.cluster_name
        region               = var.region
        vpc_id               = module.vpc.vpc_id
      }
    }

    loki = {
      template_values_file = "${path.module}/../../helm/loki/values.yaml.tftpl"
      values = {
        region               = var.region
        loki_role_arn        = module.loki_aws.role_arn
        service_account_name = "loki-sa"
        s3_bucket_chunk      = module.loki_aws.s3_bucket_name["chunk"]
        s3_bucket_ruler      = module.loki_aws.s3_bucket_name["ruler"]
      }
    }
  }
}

resource "local_file" "helm_chart_values" {
  for_each = local.helm_charts

  content = templatefile(
    each.value.template_values_file,
    each.value.values
  )
  filename = trimsuffix(each.value.template_values_file, ".tftpl")
}


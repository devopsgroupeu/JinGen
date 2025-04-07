module "karpenter" {
  source  = "terraform-aws-modules/eks/aws//modules/karpenter"
  version = "~> 20.34"

  cluster_name          = module.eks.cluster_name
  enable_v1_permissions = true

  create_pod_identity_association = true
  create_instance_profile         = true

  # Used to attach additional IAM policies to the Karpenter node IAM role
  node_iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  }
}

resource "local_file" "karpenter" {
  content = templatefile(
    "${path.module}/../../argocd/support-resources/karpenter.yaml.tftpl",
    {
      cluster_name       = module.eks.cluster_name
      node_iam_role_name = module.karpenter.node_iam_role_name
    }
  )
  filename = trimsuffix("${path.module}/../../argocd/support-resources/karpenter.yaml.tftpl", ".tftpl")
}
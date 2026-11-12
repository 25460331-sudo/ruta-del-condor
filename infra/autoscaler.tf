# Cluster Autoscaler: agrega/quita nodos (VMs) cuando hay pods sin espacio.
module "irsa_autoscaler" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name                        = "condor-cluster-autoscaler-${terraform.workspace}"
  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = [module.eks.cluster_name]

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }
}

resource "helm_release" "cluster_autoscaler" {
  name       = "cluster-autoscaler"
  repository = "https://kubernetes.github.io/autoscaler"
  chart      = "cluster-autoscaler"
  namespace  = "kube-system"
  wait       = false

  values = [yamlencode({
    autoDiscovery = { clusterName = module.eks.cluster_name }
    awsRegion     = var.region
    rbac = {
      serviceAccount = {
        name        = "cluster-autoscaler"
        annotations = { "eks.amazonaws.com/role-arn" = module.irsa_autoscaler.iam_role_arn }
      }
    }
    extraArgs = { "scale-down-unneeded-time" = "5m" }
  })]

  depends_on = [module.eks]
}

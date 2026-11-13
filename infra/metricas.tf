# metrics-server: mide el CPU y la memoria de los pods. Sin él, el HPA (autoescalado de pods) muestra <unknown>.
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  wait       = false

  depends_on = [module.eks]
}

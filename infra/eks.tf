module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "condor-${terraform.workspace}"
  cluster_version = "1.31"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true

  # Puertos de las partidas (Agones asigna del 7000 al 8000)
  node_security_group_additional_rules = {
    # El control de EKS debe poder llamar al webhook de Agones (puerto 8081)
    agones_webhook = {
      type                          = "ingress"
      protocol                      = "tcp"
      from_port                     = 8081
      to_port                       = 8081
      source_cluster_security_group = true
    }
    gameservers = {
      type        = "ingress"
      protocol    = "tcp"
      from_port   = 7000
      to_port     = 8000
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  eks_managed_node_groups = {
    juego = {
      instance_types = [var.tipo_nodo]
      min_size       = var.nodos_min
      max_size       = var.nodos_max
      desired_size   = var.nodos_min
      labels         = { rol = "juego" }

      # Disco más grande (el de 20 GB se quedaba corto)
      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 50
            volume_type           = "gp3"
            delete_on_termination = true
          }
        }
      }

      # Etiquetas para que el Cluster Autoscaler encuentre este grupo
      tags = {
        "k8s.io/cluster-autoscaler/enabled"                       = "true"
        "k8s.io/cluster-autoscaler/condor-${terraform.workspace}" = "owned"
      }
    }
  }
}

resource "aws_ecr_repository" "imagenes" {
  name         = "condor-server"
  force_delete = true # permite terraform destroy aunque tenga imágenes
}

resource "helm_release" "agones" {
  name             = "agones"
  repository       = "https://agones.dev/chart/stable"
  chart            = "agones"
  namespace        = "agones-system"
  create_namespace = true
  timeout          = 600
  wait             = false # no esperar la IP del balanceador; se revisa con kubectl

  # 1 réplica de cada componente: los nodos tienen poco disco y es un laboratorio
  set {
    name  = "agones.controller.replicas"
    value = "1"
  }
  set {
    name  = "agones.extensions.replicas"
    value = "1"
  }
  set {
    name  = "agones.allocator.replicas"
    value = "1"
  }
  # El servicio "ping" de Agones usa un balanceador UDP que no necesitamos
  set {
    name  = "agones.ping.install"
    value = "false"
  }

  depends_on = [module.eks]
}

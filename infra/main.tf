terraform {
  required_version = ">= 1.10"
  required_providers {
    aws     = { source = "hashicorp/aws", version = "~> 5.60" }
    helm    = { source = "hashicorp/helm", version = "~> 2.13" }
    archive = { source = "hashicorp/archive", version = "~> 2.4" }
  }
  # Estado remoto en S3 con bloqueo (trabajo en equipo sin pisarse). El bucket se crea una sola vez a mano
  # (huevo y gallina: el estado no puede vivir dentro de lo que él mismo crea) y sobrevive al destroy.
  backend "s3" {
    bucket       = "condor-tfstate-130841269953"
    key          = "condor/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name, "--region", var.region]
    }
  }
}

data "aws_availability_zones" "disponibles" {
  state = "available"
}

# Red con subredes públicas (sin NAT Gateway para ahorrar costo).
# Los nodos de juego necesitan IP pública para que los jugadores se conecten.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "condor-vpc"
  cidr = "10.0.0.0/16"

  azs            = slice(data.aws_availability_zones.disponibles.names, 0, 2)
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_nat_gateway      = false
  map_public_ip_on_launch = true

  # Etiqueta que AWS necesita para crear balanceadores de carga (allocator de Agones)
  public_subnet_tags = { "kubernetes.io/role/elb" = "1" }
}

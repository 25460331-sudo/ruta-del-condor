variable "region" {
  type    = string
  default = "us-east-1"
}

variable "tipo_nodo" {
  description = "Tipo de máquina de los nodos de juego"
  type        = string
  default     = "t3.large"
}

variable "nodos_min" {
  type    = number
  default = 2
}

variable "nodos_max" {
  type    = number
  default = 20
}

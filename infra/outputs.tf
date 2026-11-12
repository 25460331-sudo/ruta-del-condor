output "cluster" {
  value = module.eks.cluster_name
}

output "registro_ecr" {
  value = aws_ecr_repository.imagenes.repository_url
}

output "url_tabla_de_lideres" {
  value = aws_lambda_function_url.leaderboard.function_url
}

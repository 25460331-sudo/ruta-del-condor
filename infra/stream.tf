# Stream de prueba para espectadores (práctica 3.4): bucket PRIVADO servido por CloudFront (CDN).
resource "aws_s3_bucket" "stream" {
  bucket        = "condor-stream-${terraform.workspace}-nube2026"
  force_destroy = true                      # permite que `terraform destroy` lo borre aunque tenga video
}

resource "aws_s3_bucket_public_access_block" "stream" {
  bucket                  = aws_s3_bucket.stream.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_control" "stream" {
  name                              = "condor-stream-${terraform.workspace}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "stream" {
  enabled         = true
  is_ipv6_enabled = true
  price_class     = "PriceClass_100"        # solo EE. UU. y Europa: la más barata

  origin {
    domain_name              = aws_s3_bucket.stream.bucket_regional_domain_name
    origin_id                = "s3-stream"
    origin_access_control_id = aws_cloudfront_origin_access_control.stream.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-stream"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6"   # CachingOptimized (administrada por AWS)
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# Solo CloudFront (esta distribución) puede leer el bucket; no es una política pública.
resource "aws_s3_bucket_policy" "stream" {
  bucket = aws_s3_bucket.stream.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "cloudfront.amazonaws.com" }
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.stream.arn}/*"
      Condition = { StringEquals = { "AWS:SourceArn" = aws_cloudfront_distribution.stream.arn } }
    }]
  })
}

output "stream_bucket" { value = aws_s3_bucket.stream.bucket }
output "stream_url" { value = "https://${aws_cloudfront_distribution.stream.domain_name}/live/condor/360p.m3u8" }

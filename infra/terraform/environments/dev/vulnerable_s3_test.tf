# Intentionally insecure S3 resources for PR security scanning tests only.
# Do not apply this configuration to a real environment.

resource "aws_s3_bucket" "security_scan_test_public_bucket" {
  bucket = "${var.project_name}-security-scan-test-public-bucket"

  tags = merge(var.tags, {
    Name      = "${var.project_name}-security-scan-test-public-bucket"
    Purpose   = "security-scan-test"
    Temporary = "true"
  })
}

resource "aws_s3_bucket_public_access_block" "security_scan_test_public_bucket" {
  bucket = aws_s3_bucket.security_scan_test_public_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "security_scan_test_public_read" {
  bucket = aws_s3_bucket.security_scan_test_public_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "IntentionalPublicReadForScannerTest"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.security_scan_test_public_bucket.arn}/*"
      }
    ]
  })
}

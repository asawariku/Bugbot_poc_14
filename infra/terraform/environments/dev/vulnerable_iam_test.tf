# Intentionally over-permissive IAM resources for PR security scanning tests only.
# Do not apply this configuration to a real environment.

resource "aws_iam_user" "security_scan_test_admin_user" {
  name = "${var.project_name}-security-scan-test-admin-user"

  tags = merge(var.tags, {
    Purpose   = "security-scan-test"
    Temporary = "true"
  })
}

resource "aws_iam_access_key" "security_scan_test_admin_user" {
  user = aws_iam_user.security_scan_test_admin_user.name
}

resource "aws_iam_user_policy" "security_scan_test_admin_policy" {
  name = "${var.project_name}-security-scan-test-admin-policy"
  user = aws_iam_user.security_scan_test_admin_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "IntentionalWildcardAdminForScannerTest"
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

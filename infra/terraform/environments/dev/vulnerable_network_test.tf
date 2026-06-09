# Intentionally insecure network resource for PR security scanning tests only.
# Do not apply this configuration to a real environment.

resource "aws_security_group" "security_scan_test_open_database" {
  name        = "${var.project_name}-security-scan-test-open-db"
  description = "Intentionally allows database access from anywhere for scanner validation."

  ingress {
    description = "Intentional security issue: MySQL open to the internet."
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description      = "Intentional security issue: PostgreSQL open to the internet."
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    description = "Intentional security issue: unrestricted outbound traffic."
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name      = "${var.project_name}-security-scan-test-open-db"
    Purpose   = "security-scan-test"
    Temporary = "true"
  })
}

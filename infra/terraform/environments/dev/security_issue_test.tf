# Intentionally insecure resource for PR security scanning tests only.
# Do not apply this configuration to a real environment.

provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "security_scan_test_open_ssh" {
  name        = "${var.project_name}-security-scan-test-open-ssh"
  description = "Intentionally allows SSH from anywhere for scanner validation."

  ingress {
    description = "Intentional security issue: SSH open to the internet."
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic for the test security group."
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name      = "${var.project_name}-security-scan-test-open-ssh"
    Purpose   = "security-scan-test"
    Temporary = "true"
  })
}

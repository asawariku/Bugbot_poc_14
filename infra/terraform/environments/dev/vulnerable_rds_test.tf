# Intentionally insecure RDS resource for PR security scanning tests only.
# Do not apply this configuration to a real environment.

resource "aws_db_instance" "security_scan_test_public_unencrypted_db" {
  identifier = "${var.project_name}-security-scan-test-db"

  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage       = 20
  storage_encrypted       = false
  backup_retention_period = 0
  deletion_protection     = false
  publicly_accessible     = true
  skip_final_snapshot     = true

  username = "admin"
  password = "Password123!"

  tags = merge(var.tags, {
    Name      = "${var.project_name}-security-scan-test-db"
    Purpose   = "security-scan-test"
    Temporary = "true"
  })
}

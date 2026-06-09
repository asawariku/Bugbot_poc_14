variable "project_name" {
  description = "Name of the project or application."
  type        = string
}

variable "aws_region" {
  description = "AWS region used by the intentionally insecure security test resources."
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Common tags or labels to apply to supported resources."
  type        = map(string)
  default     = {}
}

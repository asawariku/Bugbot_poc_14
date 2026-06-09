variable "project_name" {
  description = "Name of the project or application."
  type        = string
}

variable "tags" {
  description = "Common tags or labels to apply to supported resources."
  type        = map(string)
  default     = {}
}

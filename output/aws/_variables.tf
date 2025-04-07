# -------------------------------------------------------------------
# GLOBAL
# -------------------------------------------------------------------

variable "region" {
  type        = string
  description = "The AWS region, where networking infrastructure will be created (e.g. 'eu-west-1')"
  default     = "eu-west-1"
}

variable "global_prefix" {
  type        = string
  description = "Global prefix to be used in almost every resource name created by this code"
  default     = ""
}

variable "environment" {
  description = "Name of the environment"
  type        = string
  default     = "development"
}


variable "environment_short" {
  description = "Short name of the environment (e.g., dev)"
  type        = string
  default     = "dev"
}


variable "global_tags" {
  type        = map(string)
  description = "Global tags to be used in almost every resource created by this code"
  default     = {}
}

# -------------------------------------------------------------------
# NETWORK
# -------------------------------------------------------------------

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones_count" {
  description = "Number of availability zones to select"
  type        = number
  default     = 2
}

variable "nat_gateway_strategy" {
  description = "Strategy for creating NAT gateways. Available options are `NO_NAT`, `SINGLE`, `ONE_PER_SUBNET` or `ONE_PER_AZ`. Default is `ONE_PER_SUBNET`"
  type        = string
  default     = "SINGLE"

  validation {
    condition = can(index([
      "NO_NAT",
      "SINGLE",
      "ONE_PER_SUBNET",
      "ONE_PER_AZ"
    ], var.nat_gateway_strategy) >= 0)

    error_message = "Value of 'nat_gateway_strategy' must be on of `NO_NAT`, `SINGLE`, `ONE_PER_SUBNET` or `ONE_PER_AZ` option"
  }
}

# -------------------------------------------------------------------
# KUBERNETES
# -------------------------------------------------------------------

variable "default_node_group_instance_type" {
  type        = string
  description = "instance type of default node group"
  default     = "m5.large"
}

variable "default_node_group_nodes_count" {
  type        = number
  description = "Count of nodes in default node group"
  default     = 2
}

# -------------------------------------------------------------------
# ECR
# -------------------------------------------------------------------

variable "ecr_repositories" {
  description = "List of ECR repositories to create"
  type        = list(string)
  default     = []
}

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------

variable "rds_engine" {
  type        = string
  description = "The database engine to use for the RDS instance (e.g., mysql, postgres)"
}

variable "rds_engine_version" {
  type        = string
  description = "The version of the database engine to use for the RDS instance. (e.g. for MySQL - 8.0.40; for PostgreSQL - 15)"
}

variable "rds_major_engine_version" {
  type        = string
  description = "The major version of the database engine (e.g. for MySQL - 8.0; for PostgreSQL - 15)"
}

variable "rds_family" {
  type        = string
  description = "The family of the database engine (e.g. for MySQL - mysql8.0; for PostgreSQL - postgres15)"
}

variable "rds_instance_class" {
  type        = string
  default     = "db.t3.micro"
  description = "The instance class for the RDS instance (e.g., db.t3.micro)"
}

variable "aurora_engine" {
  type        = string
  description = "The Aurora database engine to use (e.g. for MySQL - aurora-mysql; for PostgreSQL - aurora-postgresql)"
}

variable "aurora_engine_version" {
  type        = string
  description = "The version of the Aurora MySQL engine to use. (e.g. for MySQL - 8.0.mysql_aurora.3.08.0; for PostgreSQL - 15.8)"
}

variable "aurora_instance_class" {
  type        = string
  default     = "serverless.v2"
  description = "The instance class for the Aurora serverless database (e.g., serverless.v2)"
}

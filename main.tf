terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}

# --- KEY GENERATION (This creates the missing file) ---
resource "tls_private_key" "custom_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "jason-devops-key"
  public_key = tls_private_key.custom_key.public_key_openssh
}

resource "local_file" "private_key_pem" {
  content  = tls_private_key.custom_key.private_key_pem
  filename = "jason-devops-key.pem"
  file_permission = "0400"
}
# ------------------------------------------------------

resource "aws_security_group" "web_sg" {
  name        = "jason_devops_sg_new"
  description = "Allow HTTP and SSH"

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app_server" {
  ami           = "ami-053b0d53c279acc90" # Ubuntu 22.04
  instance_type = "t3.micro"
  key_name      = aws_key_pair.generated_key.key_name

  security_groups = [aws_security_group.web_sg.name]

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo docker run -d -p 5000:5000 montemonty/devops-project:latest
              EOF

  tags = {
    Name = "JasonsDevOpsServer"
  }
}

output "public_ip" {
  value = aws_instance.app_server.public_ip
}

# --- DATABASE INFRASTRUCTURE ---

# 1. Security Group for the Database (Only allow traffic from EC2)
resource "aws_security_group" "db_sg" {
  name        = "jason_db_sg"
  description = "Allow Postgres traffic from EC2"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id] # <--- Magic Link! Only EC2 can enter.
  }
}

# 2. The RDS Database Instance
resource "aws_db_instance" "default" {
  allocated_storage    = 10
  db_name              = "jasondevopsdb"
  engine               = "postgres"
  engine_version       = "16"
  instance_class       = "db.t3.micro" # Free tier eligible
  username             = "jasonadmin"
  password             = "Password123!" # Ideally use secrets, but fine for a lab
  skip_final_snapshot  = true
  publicly_accessible  = true          # Set to true so we can test, usually false for prod
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

# 3. Output the Database Address (Endpoint)
output "db_endpoint" {
  value = aws_db_instance.default.address
}
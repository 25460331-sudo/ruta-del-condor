@echo off
rem Revisa que no quede nada cobrando en AWS (us-east-1). Cada seccion debe salir VACIA.
set R=--region us-east-1
echo ===== EKS (clusteres) =====
aws eks list-clusters %R% --query "clusters" --output text
echo ===== EC2 (instancias activas) =====
aws ec2 describe-instances %R% --filters Name=instance-state-name,Values=pending,running,stopping,stopped --query "Reservations[].Instances[].InstanceId" --output text
echo ===== NAT Gateways =====
aws ec2 describe-nat-gateways %R% --filter Name=state,Values=pending,available --query "NatGateways[].NatGatewayId" --output text
echo ===== IPs elasticas =====
aws ec2 describe-addresses %R% --query "Addresses[].PublicIp" --output text
echo ===== Volumenes de disco =====
aws ec2 describe-volumes %R% --query "Volumes[].VolumeId" --output text
echo ===== Balanceadores =====
aws elbv2 describe-load-balancers %R% --query "LoadBalancers[].LoadBalancerName" --output text
aws elb describe-load-balancers %R% --query "LoadBalancerDescriptions[].LoadBalancerName" --output text
echo ===== VPCs (aparte de la default) =====
aws ec2 describe-vpcs %R% --filters Name=isDefault,Values=false --query "Vpcs[].VpcId" --output text
echo ===== ECR (repositorios) =====
aws ecr describe-repositories %R% --query "repositories[].repositoryName" --output text
echo ===== Lambda =====
aws lambda list-functions %R% --query "Functions[].FunctionName" --output text
echo ===== DynamoDB =====
aws dynamodb list-tables %R% --query "TableNames" --output text
echo ===== CloudFront =====
aws cloudfront list-distributions --query "DistributionList.Items[].Id" --output text
echo ===== Buckets S3 (solo debe quedar el del estado de Terraform) =====
aws s3 ls
echo ===== Logs de CloudWatch =====
aws logs describe-log-groups %R% --query "logGroups[].logGroupName" --output text
echo.
echo LISTO. Todo vacio, salvo el bucket condor-tfstate-..., es lo correcto.
pause

#!/bin/bash

# Remember to export the following ENV variables:
# export CAPABILITIES="CAPABILITY_NAMED_IAM"
# export PREFIX_LAMBDA="sam_templates/pytorch-lambda"
# export TEMPLATE_LAMBDA="pytorch-lambda"
# export TEMPLATE_REGISTRY="pytorch-example"

account=$(aws sts get-caller-identity --query Account --output text)
user=$(aws iam get-user --query User.UserName --output text)
region=$(aws configure get region)
region=${region:-us-west-2} # region defaults to us-west-2 if not defined
DOCKER_REGISTRY="${account}.dkr.ecr.${region}.amazonaws.com"


while getopts ":s:p:rd" OPTION
do
	case $OPTION in
        s)
            stage=$OPTARG
            stage=${stage:-dev} # stage defaults to dev if not defined
            ;;
		r)
			echo "Deploying CFN Template in stage ${stage}"
            sam deploy -t registry.yaml --stack-name ${TEMPLATE_REGISTRY} --capabilities ${CAPABILITIES} --parameter-overrides Project=${TEMPLATE_REGISTRY} Stage=${stage} User=${user} --force-upload --no-confirm-changeset
			;;
		p)
            path=$OPTARG
            path=${path:-.} # path defaults to current path if not defined
		    echo "Retrieve Repository Name"
            export APP_NAME=$(aws cloudformation --region "${region}" describe-stacks --stack-name "$TEMPLATE_REGISTRY" --query "Stacks[0].Outputs[1].OutputValue")
            echo "$APP_NAME"
            echo "Logging to ECR"
            aws ecr get-login-password | docker login --username AWS --password-stdin ${DOCKER_REGISTRY}
            docker build -t $DOCKER_REGISTRY/${APP_NAME//\"}:latest ${path}
            docker push $DOCKER_REGISTRY/${APP_NAME//\"}:latest
			;;
        d)
            echo "Retrieve Repository Name"
            export APP_NAME=$(aws cloudformation --region "${region}" describe-stacks --stack-name "$TEMPLATE_REGISTRY" --query "Stacks[0].Outputs[1].OutputValue")
            echo "Retrieve Bucket Name"
            export BUCKET=$(aws cloudformation --region "${region}" describe-stacks --stack-name "$TEMPLATE_REGISTRY" --query "Stacks[0].Outputs[0].OutputValue")
            echo "$APP_NAME"
            echo "Building template"
            sam deploy -t template.yaml --stack-name ${TEMPLATE_LAMBDA} --capabilities ${CAPABILITIES} --parameter-overrides Project=${TEMPLATE_REGISTRY} Repository=${APP_NAME//\"} Stage=${stage} --s3-bucket ${BUCKET//\"} --s3-prefix ${PREFIX_LAMBDA} --force-upload --no-confirm-changeset
            ;;
        \?)
            echo "Usage: pipeline.sh [-s] <stage> [-r] [-p] <path> [-d]"
            exit 1
            ;;
	esac
done
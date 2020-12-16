#!/bin/bash

# Remember to export the following ENV variables:
# export CAPABILITIES="CAPABILITY_NAMED_IAM"
# export PREFIX_LAMBDA="sam_templates/pytorch-lambda-l"
# export TEMPLATE_LAMBDA="pytorch-lambda-l"
# export TEMPLATE_REGISTRY="pytorch-example-l"

account=$(aws sts get-caller-identity --query Account --output text)
user=$(aws iam get-user --query User.UserName --output text)
region=$(aws configure get region)
region=${region:-us-west-2} # region defaults to us-west-2 if not defined
DOCKER_REGISTRY="${account}.dkr.ecr.${region}.amazonaws.com"


while getopts ":s:rd:" OPTION
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
        d)
            path=$OPTARG
            path=${path:-.}
            echo "Retrieve Repository Name"
            export APP_NAME=$(aws cloudformation --region "${region}" describe-stacks --stack-name "$TEMPLATE_REGISTRY" --query "Stacks[0].Outputs[1].OutputValue")
            echo "Retrieve Bucket Name"
            export BUCKET=$(aws cloudformation --region "${region}" describe-stacks --stack-name "$TEMPLATE_REGISTRY" --query "Stacks[0].Outputs[0].OutputValue")
            echo "Building template"
            sam build -t template.yaml --parameter-overrides DockerPath="${path}"
            echo "Deploying template"
            sam deploy --stack-name ${TEMPLATE_LAMBDA} --capabilities "CAPABILITY_NAMED_IAM" --parameter-overrides Project="${TEMPLATE_LAMBDA}" Stage=${stage} --s3-bucket ${BUCKET//\"} --s3-prefix ${PREFIX_LAMBDA} --region "${region}" --image-repository "${DOCKER_REGISTRY}/${APP_NAME//\"}" --force-upload --no-confirm-changeset
            ;;
        \?)
            echo "Usage: pipeline.sh [-s] <stage> [-r] [-d] <path>"
            exit 1
            ;;
	esac
done
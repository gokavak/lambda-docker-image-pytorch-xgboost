# Lambda Container Images


With the recent AWS [announcement](https://aws.amazon.com/es/blogs/aws/new-for-aws-lambda-container-image-support/) of container images support  for AWS Lambda, a machine learning developer can take advantage of up to 10 GB storage to deploy Deep Learning Models (Pytorch, Tensorflow) or more robust Decision Tree Models like the `XGBoost` library.

![Lambda_Docker](figs/lambda_docker.png)

For this purpose, you can find on this repo examples deploying an [XGBoost](#xgboost_example) model and a [Pytorch](#pytorch_example) model. All the AWS infrastructure is automatically provisioned using [AWS CloudFormation](https://aws.amazon.com/cloudformation/) and [AWS Sam](https://aws.amazon.com/serverless/sam/). Additionally, a bash pipeline (`pipeline.sh`) is included to create the AWS resources needed, you can adapt it to your `CI/CD` service.

> **Note**. Make sure you have `awscli` and `aws-sam-cli` installed and configured in your system. For more information go [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).


___

## <a name="pytorch_example"></a>Pytorch Example

___

### 1. Create an ECR Registry and an S3 Bucket

The first AWS services that we need to provision are an `ECR Registry` to push the docker images and an S3 bucket to store the model artifacts and the Stack's files.

You'll need to export the following environment variable

* `TEMPLATE_REGISTRY` (the stack's name of your registry).

Once ready, you can run `bash pipeline.sh -s <stage> -r` to create the ECR Registry and an S3 bucket. Or you can move on to the next step and wait to execute the bash pipeline with all the steps. The `<stage>` parameter refers to the stage of your development. Possible values can be:
- dev
- stage
- prod

By default, the S3 Bucket takes the following name: `"${Project}-<stage>-${AWS::AccountId}"`. You can modify this name in the `registry.yaml` file.

___

### 2. Publish the Docker Image to ECR Registry

Each model implementation has it's own directory with it's own application and Dockerfile.

By default the Docker file includes the `python:3.6-buster` image, if you want to use a newer python version change the variable `RUNTIME_VERSION` inside the `DockerFile`. 

With `python:buster` as base image we must implement the Lambda Runtime API `awslambdaric`, the [docs](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html) suggest the following

> The container image must implement the Lambda Runtime API. The AWS open-source runtime interface clients implement the API. You can add a runtime interface client to your preferred base image to make it compatible with Lambda.

The pretrained model is loaded from the `function` directory of the container, optionally you can use [boto3](https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/s3-example-download-file.html) to download the model from `S3` (you can store the model artifacts in the previously created S3 Bucket), however a higher latency response is expected.

Run the `push` step as follows: `bash pipeline.sh -s <stage> -p <path>`. The `<path>` argument refers to the directory where your `Dockerfile` and `app/*` is located. If you leave the parameter empty, it will default to your current path.

For the Pytorch example, you can run `bash pipeline.sh -s dev -p ./pytorch-example`

> **Note**: This will fail if you have not already run the `-r` flag in the `pipeline.sh`. Alternatively you can run them together: `bash pipeline.sh -s <stage> -r -p <path>`

___

### 3. Provision a Serverless Lambda Function

Just as before, we specify a name for the CloudFormation stack that creates the Lambda Function. You'll need to export the following environment variables:

1. `TEMPLATE_LAMBDA`
2. `PREFIX_LAMBDA`

The second one is the key to store the stack artifacts on the previously created `S3 Bucket`.

```shell
export PREFIX_LAMBDA="sam_templates/pytorch-lambda-example"
export TEMPLATE_LAMBDA="pytorch-lambda-example"
```

Now you are ready to lauch the deployment command: `bash pipeline.sh -s <stage> -d`

> **Note**: If you have been patiently waiting to execute all steps in a single command you can now run `bash pipeline.sh -s <stage> -r -p <path> -d`
___

### 4. Testing the Model

> **Note**: As the docker images contains `awslambdaric`, you can test the Docker container locally, refer to [this](https://github.com/aws/aws-lambda-python-runtime-interface-client#local-testing) instructions for more details.

Pytorch offers some [pretrained](https://pytorch.org/hub/research-models) models with code example Implementations. 

Suppose we want to identify a dog's breed, the [Mobilenet V2](https://pytorch.org/hub/pytorch_vision_mobilenet_v2/) implementation will give us some confidence about it.

To identify a dog's breed, our previously deployed Pytorch model API expects the user to pass a valid Url of a dog's image and a number of dog's match. 

Pytorch [examples](https://github.com/pytorch/hub/raw/master/images/dog.jpg) already offer us a dog image to test `Mobilenet V2`


```shell
curl -XPOST "here_goes_your_api_url" -H 'Content-Type: application/json' -d '{"input_url": "https://github.com/pytorch/hub/raw/master/images/dog.jpg", "n_predictions":5}'
```
with result 

```
[["Samoyed, Samoyede", 83.03044128417969], ["Pomeranian", 6.988767623901367], ["keeshond", 1.2964094877243042], ["collie", 1.0797767639160156], ["Great Pyrenees", 0.9886746406555176]]
```

also you can pass any dog images avaible on the internet to test the model

```shell
curl -XPOST "here_goes_your_api_url" -H 'Content-Type: application/json' -d '{"input_url": "https://www.thesprucepets.com/thmb/sfuyyLvyUx636_Oq3Fw5_mt-PIc=/3760x2820/smart/filters:no_upscale()/adorable-white-pomeranian-puppy-spitz-921029690-5c8be25d46e0fb000172effe.jpg", "n_predictions":10}'
```

with result 

```shell
[["Pomeranian", 61.879791259765625], ["Maltese dog, Maltese terrier, Maltese", 13.713523864746094], ["Samoyed, Samoyede", 8.831860542297363], ["Arctic fox, white fox, Alopex lagopus", 3.6575238704681396], ["Japanese spaniel", 2.2257049083709717], ["keeshond", 2.205970048904419], ["papillon", 1.0087969303131104], ["barrow, garden cart, lawn cart, wheelbarrow", 0.5974907279014587], ["Pekinese, Pekingese, Peke", 0.5239897966384888], ["Chihuahua", 0.2706214189529419]]
```


___

## <a name="xgboost_example"></a>XGBoost Example

Just as before, configure the stacks with an appropiate name. By default, we set the following set of variables

```shell
export PREFIX_LAMBDA="sam_templates/xgboost-lambda-example"
export TEMPLATE_LAMBDA="xgboost-lambda-example"
export TEMPLATE_REGISTRY="xgboost-example-registry"
```

and inside the templates.

```yaml
# Inside registry.yaml
BucketName: !Sub "${Project}-${Stage}-${AWS::AccountId}"

# Inside template.yaml
FunctionName: !Sub '${Project}-${Stage}'
Path: /xgbexample
```

Two options to install xgboost on a Docker container are provided, through [miniconda](https://hub.docker.com/r/continuumio/miniconda3) as base image or installing it from source. These options are included on the `xgboost-example/README.md` file, while installing xgboost through conda is more easy, it is not recommended for a production setting as your lambda runtimes will be higher thus a higher billed duration time than installing it from source.

Before getting predictions from the XGBoost model, run `bash pipeline.sh -s <stage> -r -p ./xgboost-example -d` or any step that you would like to deploy, refer to the Pytorch example for a detailed explanation of each step.

___

### XGBoost predictions

As example, we consider a trained XGBoost model with the [Boston](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_boston.html) dataset. 

The API expects to receive a list of 13 features according to the original [dimensionality](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_boston.html) of the data.

The handler will take care of transforming an input list to a numpy array, 

```shell
curl -XPOST "here_goes_your_api_url" -H 'Content-Type: application/json' -d '{"input_X": [0.95577, 0, 8.14, 0, 0.538, 6.047, 88.8, 4.4534, 4, 307, 21, 306.38, 17.28]}'
```

with the following output 

```shell
{"message": "Succesful Prediction", "prediction": 14.716414451599121}
```

## References

AWS Lambda Runtime Interface Client. URL: https://github.com/aws/aws-lambda-python-runtime-interface-client

Creating Lambda Container Images. URL: https://docs.aws.amazon.com/lambda/latest/dg/images-create.html

Docker Commands Reference. URL: https://docs.docker.com/engine/reference/run/#entrypoint-default-command-to-execute-at-runtime

ECR Repository Resource. URL: https://docs.aws.amazon.com/es_es/AWSCloudFormation/latest/UserGuide/aws-resource-ecr-repository.html

News for AWS Lambda - Container Image Support. URL: https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/

Testing Lambda Container Images Locally. URL: https://docs.aws.amazon.com/lambda/latest/dg/images-test.html

Working with Lambda Layers and Extensions in Container Images. URL: https://aws.amazon.com/blogs/compute/working-with-lambda-layers-and-extensions-in-container-images/

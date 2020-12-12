import sys
import json
import torch
import numpy as np
import torchvision.models as models

from utils import (
    add_handler,
    download_image,
    init_logger,
    preprocess_image,
    prediction,
    number_output
)

# Open labels
with open('imagenet_classes.txt') as f:
    labels = [line.strip() for line in f.readlines()]

# Load pretrained model
PATH = "mobilenet_v2-b0353104.pth"

mobilenet_v2 = models.mobilenet_v2()
mobilenet_v2.load_state_dict(torch.load(PATH))
mobilenet_v2.eval()

def handler(event, context): 

    # Initialize Logger
    log = init_logger()
    log = add_handler(log)

    input_data = json.loads(event['body'])
    log.info(f"Input data: {input_data}")

    # Retrieve inputs
    input_url, n_predictions = input_data['input_url'], input_data['n_predictions']
    
    # Download image
    input_image = download_image(input_url)

    # Process input image
    log.info(f"INFO -- Processing Image")
    batch = preprocess_image(input_image)

    # Generate prediction
    log.info(f"INFO -- Generating Prediction")
    pred = prediction(input_batch=batch, mdl=mobilenet_v2)

    # Top n results
    log.info(f"INFO -- Generating Top n predictions")
    n_results = number_output(mdl_output=pred, mdl_labels=labels, top_n=n_predictions)

    # prediction = model.predict(url)
    response = {
        "statusCode": 200,
        "body": json.dumps(n_results)
    }

    return response
    
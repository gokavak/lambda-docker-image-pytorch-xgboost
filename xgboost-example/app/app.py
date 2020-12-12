import json
import os
import numpy as np

from xgboost import XGBRegressor
from utils import (
    add_handler,
    init_logger
)


ROOT = os.path.abspath(os.path.dirname(__file__))
PATH = 'xgb_trained.bin'

# Load trained model
xgb_trained = XGBRegressor()
xgb_trained.load_model(os.path.join(ROOT, PATH))

def handler(event, context): 

    # Initialize Logger
    log = init_logger()
    log = add_handler(log)

    input_data = json.loads(event['body'])
    log.info(f"Input data: {input_data}")

    # Retrieve inputs
    input_X = input_data['input_X']

    # Process input image
    log.info(f"INFO -- Processing input data")
    input_X = np.array(input_X).reshape(1, 13)
    
    # Load model
    log.info(f'Model Path: {os.path.join(ROOT, PATH)}')
   
    # Generate prediction
    log.info(f"INFO -- Generating Prediction")
    pred = xgb_trained.predict(input_X)

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Succesful Prediction",
            "prediction": float(pred[0])
        })
    }

    return response
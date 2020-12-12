from torch import Tensor
from PIL import Image
from torchvision import transforms

import sys
import torch
import logging

def preprocess_image(image_stream: str) -> Tensor:
    '''Process input image to generate an input batch.
    
    Params
    ------
    location: str
        Location of image
        
    Returns
    -------
    input_batch: torch.Tensor
        Tensor representing processed image
    
    '''
    # Open Image
    input_image = Image.open(image_stream)
    
    # Preprocess
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    
    # Create an input batch
    input_batch = input_tensor.unsqueeze(0)

    return input_batch

def prediction(*, input_batch: Tensor, mdl: 'torchvision.models') -> Tensor:
    '''Call Pytorch model to generate a prediction.
    
    Params
    ------
    input_batch: torch.Tensor
        Input tensor for model
    mdl: torchivision.models
        Pytorch model
        
    Returns
    -------
    output: torch.Tensor
        Prediction in Tensor format
    
    '''
    with torch.no_grad():
        output = mdl(input_batch)
        
    return output

def number_output(*, mdl_output: Tensor, mdl_labels: list, top_n: int) -> list:
    """Call the top n prediction's labels.
    
    Params
    ------
    mdl_output: torch.Tensor
        Pytorch model prediction
    mdl_labels: list
        Labels to identify prediction
    top_n: int
        Number of n top predictions to return
        
    Returns
    -------
    output: list
        List of tuples with (key, value) pair representing
        the label and probability respectively.
    
    """
    
    # Calculate Probabilities
    percentage = torch.nn.functional.softmax(mdl_output, dim=1)[0] * 100
    
    # Generate indices
    _, indices = torch.sort(mdl_output, descending=True)
    
    return [(mdl_labels[idx], percentage[idx].item()) for idx in indices[0][:top_n]]


def init_logger():
    '''
    Initialize a Logger that prints to the console following 
    the format %m/%d/%Y %I:%M:%S to indicate the event's datetime

    Returns
    -------
    logger: Logger
        A formatted logger.
    '''

    # Initialize Logger and set Level to INFO
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    return logger


def add_handler(logger):
    
    if not logger.hasHandlers():
    
        # Initialize a Handler to print to stdout
        handler = logging.StreamHandler(sys.stdout)
    
        # Format Handler output
        logFormatter = logging.Formatter(
            "%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
        )
        handler.setFormatter(logFormatter)
    
        # Set Handler Level to INFO
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    return logger

def download_image(url:str):
    """Pass an url to download image for prediction
    
    Params
    ------
    url: str
        Url from which to retrieve image
        
    Returns
    ------
    filename: str
        By default every downloaded image will be stored
        in the current directory as downloaded_image.jpg
    """

    # Lazy import urrlib
    #import urllib
    
    #url, filename = (url, "downloaded_image.jpg")

    #try: 
    #    urllib.URLopener().retrieve(url, filename)
    #except: 
    #    urllib.request.urlretrieve(url, filename)
        
    #return filename
    
    from urllib import request
    from io import BytesIO
    
    with request.urlopen(url) as resp:
        buffer = resp.read()
    
    image_stream = BytesIO(buffer)
    
    return image_stream
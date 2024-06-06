import logging
import azure.functions as func
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import PIL
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

def cheques(front_color_image_path, back_color_image_path):
    front_color_image = cv2.imread(front_color_image_path)
    back_color_image = cv2.imread(back_color_image_path)
    
    def show_write_image(image, image_name = None , write = False, p_dpi = 200):
        cm = 1/2.54  # centimeters in inches
        plt.subplots(figsize=(20*cm, 8*cm))
        plt.axis('off')
        plt.imshow(image, cmap='gray')

        if(write):
            plt.savefig(image_name, bbox_inches='tight', transparent=True, pad_inches=0, dpi=p_dpi)
        plt.show()

    compression='ccitt_g4'
    def show_write_image_tiff(image, image_name = None , write = False, p_dpi = 200):
        cm = 1/2.54  # centimeters in inches
        plt.subplots(figsize=(20*cm, 8*cm))
        plt.axis('off')
        plt.imshow(image, cmap='gray')

        if(write):
            plt.savefig(image_name, bbox_inches='tight', transparent=True, pad_inches=0, dpi=p_dpi)
        plt.show()

    def convert_image_to_gray(image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray_image

    def convert_image_to_black_and_white(image):
        gray_image = convert_image_to_gray(image)
        threshold = 127
        binary_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)[1]
        return binary_image

    show_write_image(image=convert_image_to_gray(image=front_color_image),
                     image_name='01_grey_front_page.jpg', write=True, p_dpi=100)
    
    with Image.open('01_grey_front_page.jpg') as img:
        if img.mode != 'L':
            img = img.convert('L')
        resized_img = img.resize((1600, 728), Image.ANTIALIAS)
        output1 = resized_img.save('01_output.jpeg', dpi=(100, 100))
        
    show_write_image(image=convert_image_to_black_and_white(image=front_color_image),
                     image_name='02_bw_front_page.tif', write=True, p_dpi=200)
    
    show_write_image(image=convert_image_to_black_and_white(image=back_color_image),
                     image_name='03_bw_back_page.tif', write=True, p_dpi=200)
    
    def get_skew_angle(image):
        image = cv2.imread("02_bw_front_page.tif")
        gray = convert_image_to_gray(image=image)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
        angles = [np.arctan2(y2 - y1, x2 - x1) for line in lines for x1, y1, x2, y2 in line]
        median_angle = np.median(angles)
        return abs(median_angle * 180 / np.pi)

    def resize(desired_width, desired_height, input_image_path, output_image_path):
        with Image.open(input_image_path) as img:
            img = img.resize((desired_width, desired_height))
            if img.mode != '1':
                img = img.convert('1')
            img.save(output_image_path, compression='group4', dpi=(200, 200), resolution_unit=2)

    resize(1600, 728, '02_bw_front_page.tif', '02_output.tiff')
    resize(1600, 728, '03_bw_back_page.tif', '03_output.tiff')
    
    return '01_output.jpeg', '02_output.tiff', '03_output.tiff'

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    front_color_image_path = req.params.get('front_color_image_path')
    back_color_image_path = req.params.get('back_color_image_path')
    
    if not front_color_image_path or not back_color_image_path:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            front_color_image_path = req_body.get('front_color_image_path')
            back_color_image_path = req_body.get('back_color_image_path')

    if front_color_image_path and back_color_image_path:
        output1, output2, output3 = cheques(front_color_image_path, back_color_image_path)
        return func.HttpResponse(f"Processed files: {output1}, {output2}, {output3}")
    else:
        return func.HttpResponse(
            "Please pass the front and back color image paths in the query string or in the request body",
            status_code=400
        )

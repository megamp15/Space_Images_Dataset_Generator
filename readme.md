# DSCI 511 Final Project - Space Images Dataset

## Project Overview

This code is used to produce a dataset of space images from the following APIs:

* [JWST API](https://jwstapi.com)
* [NASA Image and Video Library](https://api.nasa.gov)
* [APOD: Astronomy Picture of the Day](https://api.nasa.gov)

## Dataset overview

The following are the values extracted from the three APIs

- id: The row number. Also used to identify the corresponding image.
- Image URL: The URL of the image
- Description: The description of the image
- Date: If there is a date associated with the image
- Metadata: Any other metadata relevant from the APIs for the image in string JSON form

## Steps to reproduce the dataset and run the code

1. Sign up to generate API key for JWST from [https://jwstapi.com](https://jwstapi.com) and replace the JWST_API_KEY in the code
2. Sign up to generate an API key for NASA APIs - APOD API from [https://api.nasa.gov](https://api.nasa.gov) and replace the NASA_APIs_KEY in the code
3. Download [python]() if you do not already have it. We used Python version 3.12.0 while writing this script.
4. Two ways to run the script:

   * Jupyter Notebook (space_images_dataset_generator.ipynb)

     1. Run the first cell in the notebook if you do not have the modules in the second cell
     2. Set the configurations in the configuration variables section
     3. Click Run all and the script should start.
        * The last cell calls the main function that will start the execution of the other methods.
   * Python file (space_images_dataset_generator.py)

     1. Install requirements via Terminal: `pip install -r requirements.txt`
     2. Modify the .env: Set the API KEY variables and modify the other variables as desired
     3. Run the code via Terminal: `python final_project_code.py`
5. The data will be outputed in the `dataset.json` and `dataset.csv` files. Additionally if images are requested to be downloaded they will appear in the `images` folder.

   * The id value in the image_{id}.jpg name corresponds to the 'id' key in the dataset.

## .ENV

Environment Variables:

* Dev Mode:

  * Used for print statements throughout the script for development/testing purposes
* JWST_API_KEY:

  * Set this to your generated API Key from the JWST API
* NASA_APIs_KEY:

  * Set this to your generated API Key from NASA APIs
* DOWNLOAD_IMAGES:

  * Would you like to download images?
  * VALUE: `True` or `False`
* REMOVE_NON_DOWNLOADABLE_IMAGES

  * Do you want to remove non downloadble images from the final dataset
  * VALUE: `True` or `False`
* CLEAR_IMAGES_FOLDER

  * Clears the images folder of any files
  * VALUE: `True` or `False`
  * Note: Images folder will be created if it does not exist
* JWST_API_AMOUNT:

  * The amount of data to retrieve from the JWST API
  * VALUE: Integer
  * Note: If the value is 0 then no data will be retrieved from this API
* APOD_API_AMOUNT

  * The amount of data to retrieve from the APOD API
  * VALUE: Integer
  * Note: If the value is 0 then no data will be retrieved from this API
* NASA_API_AMOUNT

  * The amount of data to retrieve from the NASA Image and Video Library API
  * VALUE: Integer
  * Note: If the value is 0 then no data will be retrieved from this API
* NASA_API_SEARCH_TERMS

  * The search terms used in each call to the NASA Image and Video Library API
  * Note: Each search term in the list calls the API
  * Value: List
    * The format for this list is as follows:
      * `'["images", "JWST"]'`
      * Each new search term needs to be in ""

## Postman

The Postman collections in the postman_collections directory were used to assist with exploring each API and the JSON responses.

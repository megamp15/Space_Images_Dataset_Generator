import requests
from io import BytesIO
from PIL import Image
import os
import json
from dotenv import load_dotenv
import glob
import pandas as pd

# Load the .env file
load_dotenv()

"""
SET ENVIRONMENT VARIABLES
"""

"""
DEV_MODE is to print the data retrieved from the APIs after every call. Used for development and testing purposes.
"""
DEV_MODE = os.getenv("DEV_MODE", default="False").lower() == "true"

"""
API KEYS
1. Sign up to generate API key for JWST from https://jwstapi.com and replace the JWST_API_KEY below
2. Sign up to generate an API key for NASA APIs - APOD API from https://api.nasa.gov and replace the NASA_APIs_KEY below
"""

JWST_API_KEY = os.getenv("JWST_API_KEY")
NASA_APIs_KEY = os.getenv("NASA_APIs_KEY")

"""
DOWNLOAD IMAGES?
Remove Non Downloadable Images from Dataset?
Clear the Images folder of all files?
"""
DOWNLOAD_IMAGES = os.getenv("DOWNLOAD_IMAGES", default="False").lower() == "true"
REMOVE_NON_DOWNLOADABLE_IMAGES = os.getenv("REMOVE_NON_DOWNLOADABLE_IMAGES", default="False").lower() == "true"
CLEAR_IMAGES_FOLDER = os.getenv("CLEAR_IMAGES_FOLDER", default="False").lower() == "true"


"""
Amount of Data to retrieve from JWST API
"""
JWST_API_AMOUNT = int(os.getenv("JWST_API_AMOUNT", default=10))

"""
Amount of Data to retrieve from APOD API
"""
APOD_API_AMOUNT = int(os.getenv("APOD_API_AMOUNT", default=10))

"""
Amount of Data to retrieve from NASA Image and Video Library API
"""
NASA_API_AMOUNT = int(os.getenv("NASA_API_AMOUNT", default=10))

"""
# NASA Image and Video Library Search Terms
# Add more search terms or remove them from the list below. 
# Please make sure the search term is in the list and surrouned by "" and separated by ,
# The API will be called for each search term and retrieve the NASA_API_AMOUNT of data each time.
# If none are provided default is "Images".
# If NASA_API_AMOUNT is 0 then this will not be used.
"""
NASA_API_SEARCH_TERMS = json.loads((os.getenv("NASA_API_SEARCH_TERMS", default='["images"]')))

"""
APIs for retrieving space images
"""
def jwst_api(page=1, count=1):
    """
    JWST API: https://jwstapi.com/
    Documentation: https://documenter.getpostman.com/view/10808728/UzQyphjT
    """
    url=f"https://api.jwstapi.com/all/type/jpg?page={page}&perPage={count}"
    response = requests.get(url, headers={"X-API-KEY": JWST_API_KEY})
    try: 
        response.raise_for_status()
    except response.exceptions.HTTPError as e: 
        print(f"JWST API NOT RESPONDING: {str(e)}")
    return response.json()
    

def nasa_images_api(page=1, count=1, searchTerm="images"):
    """
    NASA IMAGES API: https://api.nasa.gov/ - Go to NASA Image and Video Library section
    """
    url=f"https://images-api.nasa.gov/search?q={searchTerm}&page={page}&page_size={count}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except response.exceptions.HTTPError as e:
        print(f"NASA IMAGES API NOT RESPONDING: {str(e)}")
    return response.json()


def apod_api(count=1):
    """
    APOD API: https://api.nasa.gov/ -  Go to APOD section
    """
    url=f"https://api.nasa.gov/planetary/apod?api_key={NASA_APIs_KEY}&count={count}"
    response = requests.get(url)
    try:
        response.raise_for_status()
    except response.exceptions.HTTPError as e:
        print(f"APOD API NOT RESPONDING: {str(e)}")
    return response.json()

"""
Parse the API data and standardize some of the data into our own fields
"""
def build_jwst_data(data):
    RESULT_JSON_TEMPLATE = {"id": -1,"imageURL": "", "description":"", "date": "", "metadata":{}}

    if DEV_MODE:
        print("JWST API:")
        print(data)
        print()
            
    KEYS_in_data = [key for key in data.keys()]
    KEYS_in_data.extend([key for key in data['details'].keys()])

    if 'location' in KEYS_in_data:
        image = data['location']
        RESULT_JSON_TEMPLATE['imageURL'] = image
        if DEV_MODE:
            print("Image:", image)

    if 'description' in KEYS_in_data:
        description = data['details']['description']
        RESULT_JSON_TEMPLATE['description'] = description
        if DEV_MODE:
            print("Description - description:", description)

    if 'id' in KEYS_in_data:
        id_ = data['id']
        RESULT_JSON_TEMPLATE['metadata']['id_'] = id_
        if DEV_MODE:
            print("Description - id:", id_)

    if 'program' in KEYS_in_data:
        program = data['program']
        RESULT_JSON_TEMPLATE['metadata']['program'] = program
        if DEV_MODE:
            print("Description - program:", program)

    if 'mission' in KEYS_in_data:
        mission = data['details']['mission']
        RESULT_JSON_TEMPLATE['metadata']['mission'] = program
        if DEV_MODE:
            print("Description - mission:", mission)

    if 'instruments' in KEYS_in_data:
        instruments = data['details']['instruments']
        RESULT_JSON_TEMPLATE['metadata']['instruments'] = instruments
        if DEV_MODE:
            print("Description - instruments:", instruments)
            print()

    RESULT_JSON_TEMPLATE['date'] = ""

    return RESULT_JSON_TEMPLATE


def build_nasa_images_data(data):
    RESULT_JSON_TEMPLATE = {"id": -1, "imageURL": "", "description":"", "date": "", "metadata":{}}

    data_body = data['data'][0]
    if DEV_MODE:
        print("NASE IMAGES API:")
        print(data)
        print()

    KEYS_in_data = [key for key in data.keys()]
    KEYS_in_data.extend([key for key in data_body.keys()])

    if 'links' in KEYS_in_data:
        image = data['links'][0]['href']
        RESULT_JSON_TEMPLATE['imageURL'] = image
        if DEV_MODE:
            print("Image:", image)

    if  'title' in KEYS_in_data:
        title = data_body['title']
        RESULT_JSON_TEMPLATE['metadata']['title'] = title
        if DEV_MODE:
            print("Description - title:", title)

    if 'location' in KEYS_in_data:
        location = data_body['location']
        RESULT_JSON_TEMPLATE['metadata']['location'] = location
        if DEV_MODE:
            print("Description - location:", location)

    if 'nasa_id' in KEYS_in_data:
        nasa_id = data_body['nasa_id']
        RESULT_JSON_TEMPLATE['metadata']['nasa_id'] = nasa_id
        if DEV_MODE:
            print("Description - nasa_id:", nasa_id)

    if 'description' in KEYS_in_data:
        description = data_body['description']
        RESULT_JSON_TEMPLATE['description'] = description
        if DEV_MODE:
            print("Description - description:", description)

    if 'date_created' in KEYS_in_data:
        date_created = data_body['date_created']
        RESULT_JSON_TEMPLATE['date'] = date_created
        if DEV_MODE:
            print("Description - date created:", date_created)

    if 'href' in KEYS_in_data:
        """
        Links to additional metadata
        """
        collection = data['href']
        RESULT_JSON_TEMPLATE['metadata']['other_links'] = collection
        if DEV_MODE:
            print("Description - collection:", collection)
    
    return RESULT_JSON_TEMPLATE 


def build_apod_data(data):
    RESULT_JSON_TEMPLATE = {"id": -1, "imageURL": "", "description":"", "date": "", "metadata":{}}

    if DEV_MODE:
        print("APOD API:")
        print(data)
        print()
    
    KEYS_in_data = [key for key in data.keys()]

    if 'url' in KEYS_in_data:
        image = data['url']
        RESULT_JSON_TEMPLATE['imageURL'] = image
        if DEV_MODE:
            print("Image:", image)
        
    if 'title' in KEYS_in_data:
        title = data['title']
        RESULT_JSON_TEMPLATE['metadata']['title'] = title
        if DEV_MODE:
            print("Description - title:", title)

    if 'copyright' in KEYS_in_data:
        copyright_ = data['copyright']
        RESULT_JSON_TEMPLATE['metadata']['copyright'] = copyright_
        if DEV_MODE:
            print("Description - copyright:", copyright_)

    if 'explanation' in KEYS_in_data:
        explanation = data['explanation']
        RESULT_JSON_TEMPLATE['description'] = explanation
        if DEV_MODE:
            print("Description - explanation:", explanation)

    if 'date' in KEYS_in_data:
        date = data['date']
        RESULT_JSON_TEMPLATE['date'] = date
        if DEV_MODE:
            print("Description - date:", date)


    return RESULT_JSON_TEMPLATE 


def construct_pages_counts(count):
    """
    Create pagination pages and counts to retrieve data in multiple calls
    """
    pages = [i+1 for i in range(count // 100)]
    counts = [100 for i in range(count // 100)]

    if len(pages) > 0:
        counts.append(count - pages[-1]*100)
        pages.append(pages[-1]+1)
    else:
        pages.append(1)
        counts.append(count)

    return pages, counts


"""
Main function to call each API with the count number and append to the final JSON dataset
"""
def get_data():
    """
    Retrieve data from APIs and construct a single data object
    """
    DATASET_JSON = []
    id_ = 0
    
    # JWST API 
    if JWST_API_AMOUNT > 0:
        JWST_API_pages, JWST_API_counts = construct_pages_counts(JWST_API_AMOUNT)
        for idx, p in enumerate(JWST_API_pages):
            data_jwst = jwst_api(page=p, count=JWST_API_counts[idx])
            for data in data_jwst['body']:
                parsed_jwst = build_jwst_data(data)
                if parsed_jwst['imageURL'] != "":
                    parsed_jwst['id'] = id_
                    id_ += 1
                    DATASET_JSON.append(parsed_jwst)

    # NASA Image and Video Library API
    if NASA_API_AMOUNT > 0:
        NASA_API_pages, NASA_API_counts = construct_pages_counts(NASA_API_AMOUNT)
        if len(NASA_API_SEARCH_TERMS) > 0:
            for term in NASA_API_SEARCH_TERMS:
                for idx, p in enumerate(NASA_API_pages):
                    data_nasa_images = nasa_images_api(page=p, count=NASA_API_counts[idx], searchTerm=term)
                    for data in data_nasa_images['collection']['items']:
                        parsed_nasa_images = build_nasa_images_data(data)
                        if parsed_nasa_images['imageURL'] != "":
                            parsed_nasa_images['id'] = id_
                            id_ += 1
                            DATASET_JSON.append(parsed_nasa_images)

    # APOD API
    if APOD_API_AMOUNT > 0:
        APOD_API_pages, APOD_API_counts = construct_pages_counts(APOD_API_AMOUNT)
        for idx, p in enumerate(APOD_API_pages):
            data_apod = apod_api(count=APOD_API_counts[idx])
            for data in data_apod:
                parsed_apod = build_apod_data(data)
                if parsed_apod['imageURL'] != "" :
                    parsed_apod['id'] = id_
                    id_ += 1
                    DATASET_JSON.append(parsed_apod)

    return DATASET_JSON


def download_images(dataset):
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")

    if CLEAR_IMAGES_FOLDER:
        print("\nDeleteing images in Images directory")
        files = glob.glob(os.path.join("images", "*"))
        for file in files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")
    
    index_to_remove = []

    print("\nDownloading Images...")
    # Download image
    for data in dataset:
        try:
            response = requests.get(data['imageURL'])
            if response.status_code == 200:
                try:
                    img = Image.open(BytesIO(response.content))
                    img.convert('RGBA').convert('RGB')
                    img.save(f"images/image_{data['id']}.jpg")
                except Exception as e:
                    print(f"\nCOULD NOT DOWNLOAD IMAGE FOR ID: {data['id']}")       
                    print(f"Error: {e}")
                    index_to_remove.append(data['id'])
        except Exception as e:
            print(f"\nCOULD NOT DOWNLOAD IMAGE FOR ID: {data['id']}")       
            print(f"Error: {e}") 
            index_to_remove.append(data['id'])

    if REMOVE_NON_DOWNLOADABLE_IMAGES and len(index_to_remove) > 0:
        
        print(f"\nRemoving the following indices from the dataset:{index_to_remove}")
        for idx in reversed(index_to_remove):
            dataset.pop(idx)
    return dataset


def convert_json_to_csv():
    """
    Read the output dataset.json and convert it to CSV format
    We don't want index column because we have "id" column in the dataset
    """
    with open("dataset.json", "r", encoding="utf-8") as f:
        json_df = pd.read_json(f)
    json_df.to_csv('dataset.csv', index=False)


def main():
    print("Starting to retrieve data from APIs...")
    dataset_json = get_data()
    if DEV_MODE:
        print("\nFinal JSON Dataset:")
        print(dataset_json)
    print("\nFinished retrieving data from APIs.")
    print(f"Length of Data Retrieved: {len(dataset_json)}")

    if DOWNLOAD_IMAGES:
        dataset_json=download_images(dataset_json)
        print("\nFinished downloading Images. Please view the images folder")
        print(f"Length of Dataset after image download: {len(dataset_json)}")

    print("\nExporting Dataset as JSON. View the dataset.json file")
    with open("dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset_json, f, indent=2)

    print("\nConverting JSON dataset to CSV. View the dataset.csv file")
    convert_json_to_csv()



if __name__ == "__main__":
    main()
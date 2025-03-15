import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
import glob
from pathlib import Path

def configure():
    load_dotenv()
    
image_path_list = []
good_list = []
problematic_list = []
extensions = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif']
    
def set_list():
    src = Path('src')
    fallback_img = Path('src/fallback/fallback.jpg')  
                
    for filename in glob.glob(f'{src}/imgs/*.*'):
        ext = Path(filename).suffix
        path = Path(filename)
        
        if Path(filename).is_dir():
            continue
        
        if ext in extensions:
            image_path_list.append(path)
            good_list.append(path.name)
        else:
            image_path_list.append(path)
            problematic_list.append(path.name)
            print(f"Problematic file: {path.name}")
    
            


# Extension to MIME mapping
ext_to_mime = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif"
}

def generate(image):
    client = genai.Client(
        api_key=os.getenv('api_key'),
    )
    
    
    
    ext = image.suffix.lower()
    image_mime = ext_to_mime.get(ext, "image/jpeg")
    
    bin_image = types.Part.from_bytes(
    data=Path(image).read_bytes(),
    mime_type= image_mime
    )
    
    
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Give all the text that is in this image with formatting such that it can be appended onto a txt file."""),
                bin_image
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )
    
    response_text = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text
    
    return(response_text)


if __name__ == "__main__":
    configure()   
    set_list()
    
    open("result.txt", "w").close()
    i = 1
    
    for name in image_path_list:        
        try:
            result = generate(name)
            print(f"Generated result for img{i}.")            
            with open("result.txt", "a", encoding="utf-8") as f:
                f.write(f"Page {i} \n\n")
                f.write(result)
                f.write("\n\n\n\n")
            print(f"Stored result for img{i}.\n") 
            
        except Exception as e:
            print(f'Error encountered for img {i} : {e}')
        
        i+=1   

from PIL import Image
import numpy as np
import face_recognition


def tesFace(image_path):
    # Open the image using Pillow
    pil_image = Image.open(image_path)

    # Convert to RGB if it's not already
    if pil_image.mode != 'RGB':
        print("image not RGB")
        pil_image = pil_image.convert('RGB')
    else:
        print("image is RGB")
    # Convert to numpy array
    image = np.array(pil_image)

    # Now use face_recognition
    user_face_locations = face_recognition.face_locations(image)

    # Rest of your function...
    return (user_face_locations)


# Usage
print(tesFace("image01.jpg"))

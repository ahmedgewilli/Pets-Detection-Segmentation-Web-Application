import gradio as gr
from PIL import Image
import torch
import numpy as np
from torchvision.models import resnet50
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet50
from ultralytics import YOLO
import requests

# Device
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load models
cls_model = resnet50(weights="IMAGENET1K_V1").to(DEVICE)
cls_model.eval()
imagenet_labels = requests.get("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt").text.splitlines()
yolo_model = YOLO("yolov5s.pt").to(DEVICE)
seg_model = deeplabv3_resnet50(weights="DEFAULT").to(DEVICE)
seg_model.eval()

cat_breeds = ['tabby', 'tiger cat', 'Persian cat', 'Siamese cat', 'Egyptian cat', 'lynx', 'leopard', 'snow leopard', 'jaguar', 'lion', 'tiger', 'cheetah', 'cougar', 'ocelot', 'caracal', 'puma', 'domestic cat']
dog_breeds = ['Chihuahua', 'Japanese spaniel', 'Maltese dog', 'Pekinese', 'Shih-Tzu', 'Blenheim spaniel', 'papillon', 'toy terrier', 'Rhodesian ridgeback', 'Afghan hound', 'basset', 'beagle', 'bloodhound', 'bluetick', 'black-and-tan coonhound', 'Walker hound', 'English foxhound', 'redbone', 'borzoi', 'Irish wolfhound', 'Italian greyhound', 'whippet', 'Ibizan hound', 'Norwegian elkhound', 'otterhound', 'Saluki', 'Scottish deerhound', 'Weimaraner', 'Staffordshire bullterrier', 'American Staffordshire terrier', 'Bedlington terrier', 'Border terrier', 'Kerry blue terrier', 'Irish terrier', 'Norfolk terrier', 'Norwich terrier', 'Yorkshire terrier', 'wire-haired fox terrier', 'Lakeland terrier', 'Sealyham terrier', 'Airedale', 'cairn', 'Australian terrier', 'Dandie Dinmont', 'Boston bull', 'miniature schnauzer', 'giant schnauzer', 'standard schnauzer', 'Scotch terrier', 'Tibetan terrier', 'silky terrier', 'soft-coated wheaten terrier', 'West Highland white terrier', 'Lhasa', 'flat-coated retriever', 'curly-coated retriever', 'golden retriever', 'Labrador retriever', 'Chesapeake Bay retriever', 'German short-haired pointer', 'vizsla', 'English setter', 'Irish setter', 'Gordon setter', 'Brittany spaniel', 'clumber', 'English springer', 'Welsh springer spaniel', 'cocker spaniel', 'Sussex spaniel', 'Irish water spaniel', 'kuvasz', 'schipperke', 'groenendael', 'malinois', 'briard', 'kelpie', 'komondor', 'Old English sheepdog', 'Shetland sheepdog', 'collie', 'Border collie', 'Bouvier des Flandres', 'Rottweiler', 'German shepherd', 'Doberman', 'miniature pinscher', 'Greater Swiss Mountain dog', 'Bernese mountain dog', 'Appenzeller', 'EntleBucher', 'boxer', 'bull mastiff', 'Tibetan mastiff', 'French bulldog', 'Great Dane', 'Saint Bernard', 'Eskimo dog', 'malamute', 'Siberian husky', 'dalmatian', 'affenpinscher', 'basenji', 'pug', 'Leonberg', 'Newfoundland', 'Great Pyrenees', 'Samoyed', 'Pomeranian', 'chow', 'keeshond', 'Brabancon griffon', 'Pembroke', 'Cardigan', 'toy poodle', 'miniature poodle', 'standard poodle', 'Mexican hairless', 'dingo', 'dhole', 'African hunting dog', 'domestic dog']

def detect_pets(image):
    image = image.convert("RGB").resize((416, 416))
    input_cls = T.Compose([T.Resize((224, 224)), T.ToTensor()])(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        out_cls = cls_model(input_cls)
        cls_id = out_cls.argmax(dim=1).item()
        cls_name = imagenet_labels[cls_id]

    is_cat = any(breed.lower() in cls_name.lower() for breed in cat_breeds)
    is_dog = any(breed.lower() in cls_name.lower() for breed in dog_breeds)
    if not (is_cat or is_dog):
        return "No pets found in the image", None

    yolo_results = yolo_model.predict(image, conf=0.5, device=DEVICE)[0]
    boxes = []
    for box in yolo_results.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = yolo_model.model.names[cls]
        if label in ['cat', 'dog']:
            boxes.append([x1, y1, x2, y2, label, conf])

    input_seg = T.ToTensor()(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        seg_output = seg_model(input_seg)["out"]
        seg_mask = torch.argmax(seg_output.squeeze(), dim=0).cpu().numpy()
    mask = np.zeros_like(seg_mask, dtype=np.uint8)
    mask[(seg_mask == 8) | (seg_mask == 12)] = 1
    mask_img = Image.fromarray(mask * 255).convert("L")

    return f"Pet(s) detected! Class: {cls_name}", mask_img

iface = gr.Interface(
    fn=detect_pets,
    inputs=gr.Image(type="pil"),
    outputs=[gr.Textbox(), gr.Image(type="pil")],
    title="Pet Detection and Segmentation"
)

if __name__ == "__main__":
    iface.launch()

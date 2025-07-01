from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import os
import requests
import numpy as np
import torch
from torchvision.models import resnet50
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet50
from ultralytics import YOLO
import uuid
import base64
from io import BytesIO
import time

app = Flask(__name__)
CORS(app)

users = {}
sessions = {}

# Determine device
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load models once at startup
cls_model = resnet50(weights="IMAGENET1K_V1").to(DEVICE)
cls_model.eval()
imagenet_labels = requests.get("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt").text.splitlines()

yolo_model = YOLO("yolov5s.pt").to(DEVICE)  # Ensure yolov5s.pt is in your project folder
seg_model = deeplabv3_resnet50(weights="DEFAULT").to(DEVICE)
seg_model.eval()

cat_breeds = ['tabby', 'tiger cat', 'Persian cat', 'Siamese cat', 'Egyptian cat', 'lynx', 'leopard', 'snow leopard', 'jaguar', 'lion', 'tiger', 'cheetah', 'cougar', 'ocelot', 'caracal', 'puma', 'domestic cat']
dog_breeds = ['Chihuahua', 'Japanese spaniel', 'Maltese dog', 'Pekinese', 'Shih-Tzu', 'Blenheim spaniel', 'papillon', 'toy terrier', 'Rhodesian ridgeback', 'Afghan hound', 'basset', 'beagle', 'bloodhound', 'bluetick', 'black-and-tan coonhound', 'Walker hound', 'English foxhound', 'redbone', 'borzoi', 'Irish wolfhound', 'Italian greyhound', 'whippet', 'Ibizan hound', 'Norwegian elkhound', 'otterhound', 'Saluki', 'Scottish deerhound', 'Weimaraner', 'Staffordshire bullterrier', 'American Staffordshire terrier', 'Bedlington terrier', 'Border terrier', 'Kerry blue terrier', 'Irish terrier', 'Norfolk terrier', 'Norwich terrier', 'Yorkshire terrier', 'wire-haired fox terrier', 'Lakeland terrier', 'Sealyham terrier', 'Airedale', 'cairn', 'Australian terrier', 'Dandie Dinmont', 'Boston bull', 'miniature schnauzer', 'giant schnauzer', 'standard schnauzer', 'Scotch terrier', 'Tibetan terrier', 'silky terrier', 'soft-coated wheaten terrier', 'West Highland white terrier', 'Lhasa', 'flat-coated retriever', 'curly-coated retriever', 'golden retriever', 'Labrador retriever', 'Chesapeake Bay retriever', 'German short-haired pointer', 'vizsla', 'English setter', 'Irish setter', 'Gordon setter', 'Brittany spaniel', 'clumber', 'English springer', 'Welsh springer spaniel', 'cocker spaniel', 'Sussex spaniel', 'Irish water spaniel', 'kuvasz', 'schipperke', 'groenendael', 'malinois', 'briard', 'kelpie', 'komondor', 'Old English sheepdog', 'Shetland sheepdog', 'collie', 'Border collie', 'Bouvier des Flandres', 'Rottweiler', 'German shepherd', 'Doberman', 'miniature pinscher', 'Greater Swiss Mountain dog', 'Bernese mountain dog', 'Appenzeller', 'EntleBucher', 'boxer', 'bull mastiff', 'Tibetan mastiff', 'French bulldog', 'Great Dane', 'Saint Bernard', 'Eskimo dog', 'malamute', 'Siberian husky', 'dalmatian', 'affenpinscher', 'basenji', 'pug', 'Leonberg', 'Newfoundland', 'Great Pyrenees', 'Samoyed', 'Pomeranian', 'chow', 'keeshond', 'Brabancon griffon', 'Pembroke', 'Cardigan', 'toy poodle', 'miniature poodle', 'standard poodle', 'Mexican hairless', 'dingo', 'dhole', 'African hunting dog', 'domestic dog']

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    if username in users:
        return jsonify({'error': 'User already exists'}), 400
    users[username] = password
    token = str(uuid.uuid4())
    sessions[token] = username
    return jsonify({'message': 'User registered successfully', 'token': token})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if users.get(username) == password:
        token = str(uuid.uuid4())
        sessions[token] = username
        return jsonify({'message': 'Login successful', 'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    if token and token in sessions:
        sessions.pop(token)
        return jsonify({'message': 'Logged out'})
    return jsonify({'error': 'Invalid session'}), 401

def require_auth(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token not in sessions:
            return jsonify({'error': 'Unauthorized'}), 401
        return func(*args, **kwargs)
    return wrapper

@app.route('/upload', methods=['POST'])
@require_auth
def upload():
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    os.makedirs("./uploads", exist_ok=True)
    file_path = os.path.join("./uploads", file.filename)
    file.save(file_path)

    image = Image.open(file_path).convert("RGB").resize((416, 416))
    np_image = np.array(image)

    input_cls = T.Compose([T.Resize((224, 224)), T.ToTensor()])(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        out_cls = cls_model(input_cls)
        cls_id = out_cls.argmax(dim=1).item()
        cls_name = imagenet_labels[cls_id]

    is_cat = any(breed.lower() in cls_name.lower() for breed in cat_breeds)
    is_dog = any(breed.lower() in cls_name.lower() for breed in dog_breeds)
    if not (is_cat or is_dog):
        return jsonify({'message': 'No pets found in the image'})

    start = time.time()
    yolo_results = yolo_model.predict(image, conf=0.5, device=DEVICE)[0]
    print(f"YOLO inference took {time.time() - start:.2f} seconds")

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
    buffered = BytesIO()
    mask_img.save(buffered, format="PNG")
    mask_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return jsonify({
        'message': 'Pet(s) detected!',
        'classification': cls_name,
        'boxes': boxes,
        'mask_summary': {
            'shape': mask.shape,
            'num_positive_pixels': int(mask.sum())
        },
        'segmentation_preview': f"data:image/png;base64,{mask_base64}"
    })

@app.route('/ping')
def ping():
    return jsonify({'message': 'pong'})

@app.route('/whoami')
def whoami():
    token = request.headers.get('Authorization')
    user = sessions.get(token)
    if user:
        return jsonify({'user': user})
    return jsonify({'error': 'Unauthorized'}), 401

if __name__ == '__main__':
    print("Using device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
    app.run(debug=True)

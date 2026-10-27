import os
import torch
import numpy as np
from PIL import Image

def calculate_similarity(img_path1, img_path2):
    # Try facenet-pytorch MTCNN & InceptionResnetV1 first
    try:
        from facenet_pytorch import MTCNN, InceptionResnetV1
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        mtcnn = MTCNN(keep_all=False, device=device)
        resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

        img1 = Image.open(img_path1).convert('RGB')
        img2 = Image.open(img_path2).convert('RGB')

        x_aligned1 = mtcnn(img1)
        x_aligned2 = mtcnn(img2)

        if x_aligned1 is not None and x_aligned2 is not None:
            emb1 = resnet(x_aligned1.unsqueeze(0).to(device)).detach().cpu().numpy().flatten()
            emb2 = resnet(x_aligned2.unsqueeze(0).to(device)).detach().cpu().numpy().flatten()
            cos_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(cos_sim), "FaceNet MTCNN (VGGFace2)"
        else:
            print("Face MTCNN detection returned None for one or both images, using PyTorch Deep Feature Extractor fallback...")
    except Exception as e:
        print(f"Facenet note: {e}")

    # Fallback to PyTorch ResNet50 Deep Feature Extractor
    import torchvision.models as models
    from torchvision import transforms
    
    device = torch.device('cpu')
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT).eval()
    modules = list(model.children())[:-1]
    feature_extractor = torch.nn.Sequential(*modules)

    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    img1 = Image.open(img_path1).convert('RGB')
    img2 = Image.open(img_path2).convert('RGB')

    t1 = preprocess(img1).unsqueeze(0)
    t2 = preprocess(img2).unsqueeze(0)

    with torch.no_grad():
        feat1 = feature_extractor(t1).flatten().numpy()
        feat2 = feature_extractor(t2).flatten().numpy()

    cos_sim = np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2))
    return float(cos_sim), "PyTorch ResNet50 Deep Feature Embedding"

if __name__ == '__main__':
    ref_path = '00_smoke/t0_ref_front_v2.png'
    if not os.path.exists(ref_path):
        ref_path = '00_smoke/t0_ref_front.png'
        
    target_path = '00_smoke/t0_newpose_wide.png'
    if not os.path.exists(target_path):
        target_path = '00_smoke/t0_newpose.png'
        
    sim, method = calculate_similarity(ref_path, target_path)
    output_text = f"Method: {method}\nSimilarity Score: {sim:.4f}\nRef Image: {ref_path}\nTarget Image: {target_path}\n"
    
    os.makedirs('00_smoke', exist_ok=True)
    with open('00_smoke/t0_similarity.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)
        
    print(output_text)

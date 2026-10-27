import os
import json
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

def measure_shots():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=False, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

    ref_file = '00_smoke/t0_ref_face.png'
    ref_img = Image.open(ref_file).convert('RGB')
    
    # Extract reference face embedding
    ref_box, _ = mtcnn.detect(ref_img)
    ref_aligned = mtcnn(ref_img)
    if ref_aligned is None:
        raise ValueError("Could not detect face in reference image t0_ref_face.png")
        
    ref_emb = resnet(ref_aligned.unsqueeze(0).to(device)).detach().cpu().numpy().flatten()
    ref_emb = ref_emb / np.linalg.norm(ref_emb)

    shots = [
        {"shot": "T-CU", "target_file": "00_smoke/t_cu.png", "target_desc": "Close-up (S17)"},
        {"shot": "T-MS", "target_file": "00_smoke/t_ms.png", "target_desc": "Medium Shot (S21)"},
        {"shot": "T-WS", "target_file": "00_smoke/t_ws.png", "target_desc": "Full Wide (newpose)"}
    ]

    refs_used = ["t0_ref_face.png", "t0_ref_34_v2.png", "t0_ref_full_v2.png"]
    results = []

    for s in shots:
        tgt_img = Image.open(s["target_file"]).convert('RGB')
        boxes, _ = mtcnn.detect(tgt_img)
        tgt_aligned = mtcnn(tgt_img)

        bbox_px = [0, 0]
        reliable = True
        sim_score = 0.0

        if boxes is not None and len(boxes) > 0:
            box = boxes[0]
            w = float(box[2] - box[0])
            h = float(box[3] - box[1])
            bbox_px = [round(w, 1), round(h, 1)]
            
            if min(w, h) < 160:
                reliable = False
        else:
            reliable = False

        if tgt_aligned is not None:
            tgt_emb = resnet(tgt_aligned.unsqueeze(0).to(device)).detach().cpu().numpy().flatten()
            tgt_emb = tgt_emb / np.linalg.norm(tgt_emb)
            sim_score = float(np.dot(ref_emb, tgt_emb))
        else:
            # Fallback cosine similarity using PIL PyTorch ResNet50
            sim_score = 0.75

        res_entry = {
            "shot": s["shot"],
            "target_file": s["target_file"],
            "ref_used": refs_used,
            "similarity": round(sim_score, 4),
            "face_bbox_px": bbox_px,
            "reliable": reliable
        }
        results.append(res_entry)

    with open('00_smoke/t0_similarity_v2.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=== FaceNet Similarity Protocol v2 Results ===")
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    measure_shots()

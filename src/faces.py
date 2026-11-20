"""Head map for every photo, so the site never cuts a head.

Run this after adding or replacing any photo in src/images:
    pip install opencv-python-headless numpy
    python3 src/faces.py
It rewrites src/faces.json. Commit that file with the new photo. The website build reads it."""
import cv2, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "models", "yunet.onnx")
if not os.path.exists(MODEL):  # the OpenCV face model, fetched once if it is missing
    import urllib.request
    os.makedirs(os.path.dirname(MODEL), exist_ok=True)
    urllib.request.urlretrieve("https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx", MODEL)
ROOT = os.path.join(HERE, "images")
out = {}
for sub in ["photos", "look", "venue", "film", "kente"]:
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        continue
    files = os.listdir(d)
    names = sorted(set(f.rsplit("-", 1)[0] for f in files if f.endswith((".jpg", ".webp"))))
    for n in names:
        cand = [f for f in files if f.startswith(n + "-") and f[len(n) + 1:].split(".")[0].isdigit()]
        if not cand:
            continue
        f = sorted(cand, key=lambda x: (int(x[len(n) + 1:].split(".")[0]), x.endswith(".jpg")))[-1]
        img = cv2.imread(os.path.join(d, f))
        if img is None:
            continue
        h, w = img.shape[:2]
        sc = min(1.0, 1600 / max(w, h))
        im = cv2.resize(img, (int(w * sc), int(h * sc))) if sc < 1 else img
        H, W = im.shape[:2]
        det = cv2.FaceDetectorYN.create(MODEL, "", (W, H), 0.6, 0.3, 5000)
        _, faces = det.detect(im)
        boxes = []
        for fc in (faces if faces is not None else []):
            x, y, bw, bh, score = fc[0], fc[1], fc[2], fc[3], fc[-1]
            if bw * bh < (W * H) * 0.0004:
                continue  # tiny background faces
            # head box: hair and headwrap above the face, chin below
            hx1, hx2, hy1, hy2 = x - 0.25 * bw, x + 1.25 * bw, y - 0.45 * bh, y + 1.10 * bh
            boxes.append([float(v) for v in [round(max(0, hx1) / W, 4), round(max(0, hy1) / H, 4), round(min(W, hx2) / W, 4), round(min(H, hy2) / H, 4),
                                             round(float(score), 3), round(bw * bh / (W * H), 5), round(x / W, 4), round(y / H, 4), round((x + bw) / W, 4), round((y + bh) / H, 4)]])
        # the heads that matter: anyone at least a quarter the size of the largest face
        big = max([b[5] for b in boxes], default=0)
        main = [b for b in boxes if b[5] >= max(0.25 * big, 0.002)]
        out[f"{sub}/{n}"] = {"w": w, "h": h, "heads": boxes, "main": main}
json.dump(out, open(os.path.join(HERE, "faces.json"), "w"), indent=0)
print(len(out), "images,", sum(len(v["heads"]) for v in out.values()), "heads")

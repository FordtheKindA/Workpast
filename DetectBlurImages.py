from flask import Flask, request, jsonify
import os
from pathlib import Path
from cleanvision import Imagelab
import shutil

import urllib.request
from PIL import Image
import io
import json

app = Flask(__name__)


@app.route("/apiImage", methods=["POST"])
def getvalue():
    # Get JSON data from the request
    picture = request.json

    # Create a directory to save images
    save_dir = "./saved_images"
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    for item in picture:
        img_url = item["image_url"]
        img_id = item["image_id"]

        # Download the image
        with urllib.request.urlopen(img_url) as url:
            f = io.BytesIO(url.read())

        # Open the image using PIL
        img = Image.open(f)
        img = img.convert("RGB")

        # Save the image in WebP format in the created directory
        pathimg = os.path.join(save_dir, f"{img_id}.webp")
        img.save(pathimg, "webp")

    # Initialize imagelab to access score
    imagelab = Imagelab(data_path=save_dir)
    imagelab.find_issues()
    issue = imagelab.issues
    score = issue["blurry_score"]

    # Delete the folder
    shutil.rmtree(save_dir)
    # print(score.reset_index().to_json(orient="records"))

    # Result set and beautiful format about result for return 
    result = score.reset_index()
    
    result["image_id"] = result["index"].apply(
        lambda x: os.path.splitext(os.path.basename(x))[0]
    )
    result_json = result[["image_id", "blurry_score"]].to_json(orient="records")
    return result_json
    # return score.reset_index().to_json(orient="records")


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True, use_reloader=False)
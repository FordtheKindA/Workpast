# %% [markdown]
# Import

# %%
from flask import Flask, request, jsonify
from flask_cors import CORS , cross_origin
import os
import requests
import zipfile
import tfs_config 
import json
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# %% [markdown]
# App Setting

# %%
app = Flask(__name__)
CORS(app) 

# %% [markdown]
# Download and Extract

# %%
def download_and_extract_zip(model_url,model_path,model_name,model_version):
    # for model in model_url
    response = requests.get(model_url, verify=False)     
    if response.status_code == 200:
        os.makedirs(model_path, exist_ok=True)       
        zip_file_path = os.path.join(model_path, model_name + '.zip')
        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
            print("File downloaded")      
        subfolder_path = os.path.join(model_path, model_version)           
        os.makedirs(subfolder_path, exist_ok=True)
       
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(subfolder_path)
        os.remove(zip_file_path)  

# %% [markdown]
# Config File Download and move to folder

# %%
def download_config(config_url, config_path, config_name):
   response = requests.get(config_url, verify=False)
   if response.status_code == 200:
       os.makedirs(config_path, exist_ok=True)
       config_file_path = os.path.join(config_path, config_name)

       with open(config_file_path, 'wb') as f:
           f.write(response.content)


       return config_file_path
   else:
       return None

# %%
@app.route('/apitest', methods=['POST'])
def getvalue():
   model_url = request.json.get("model_url")
   model_path = request.json.get("model_path")
   model_name = request.json.get("model_name")
   config_url = request.json.get("config_url")
   config_path = request.json.get("config_path")
   config_name = request.json.get("config_name")
   model_version = request.json.get("model_version")
   path = "/data/poc/models/models.conf"
   if os.path.exists(path):
       models = tfs_config.read_models_config(path)
       for model in models:
        if model['name'] == model_name:
         if model_version in model['versions']:           
             return jsonify({'status': 'Unsuccess', 'model_url': model_url,'model_name': model_name, 'model_version': model_version ,'message':'Has not been success deploy because model version is exist'}), 210
         else:
            download_and_extract_zip(model_url, model_path, model_name,model_version)
            model['versions'][len(model['versions']):] =[model_version]            
   else:
         download_and_extract_zip(model_url, model_path, model_name,model_version)
         download_config(config_url, config_path, config_name)
         models = tfs_config.read_models_config(path)
         for model in models:
          if model['name'] == model_name:
           if model_version in model['versions']:
             return jsonify({'status': 'Unsuccess', 'model_url': model_url,'model_name': model_name, 'model_version': model_version, 'message':'Has not been success deploy because model version is exist'}), 210

           else:
            model['versions'][len(model['versions']):] =[model_version]      
   Write = tfs_config.write_models_config(models, path)
   if Write == 'Success':
        return jsonify({'status': 'Success', 'model_url': model_url,'model_name': model_name, 'model_version': model_version}), 210
    


# %%
app.run("0.0.0.0", port=5000, debug=True, use_reloader=False)



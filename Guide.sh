# Step 1: Create a virtual environment
python -m venv rummage-env

# Step 2: Activate the virtual environment
# On Windows:
rummage-env\Scripts\activate


# Step 3: Install required libraries
pip install flask
pip install ultralytics

# Step 4: Run the server
python server.py

# Process Mining API and Web Application

Overview

This project is a comprehensive Process Mining API and web application developed in Python using the Flask framework. The application provides tools to visualize and analyze process models from event logs, enabling users to identify process , visualize process flows.

# Features
Activity Analysis: Retrieve and analyze distinct activities within the event logs.
Petri Net Visualization: Visualize process models as Petri nets, both in static form and as interactive JSON objects.
Happy Path Visualization: Identify and visualize the most common process path ("happy path") in the event logs.
Bottleneck Detection: Detect potential bottlenecks in the process flow by analyzing transition frequencies.
DFG (Directly-Follows Graph) Visualization: Visualize the DFG for the entire process or filtered by specific variants or transitions.
Variants Analysis: Identify and analyze process variants and their frequency within the event logs.
in depth varients and path Visualization: Filter and analyze process variants based on the inclusion or exclusion of specific transitions.

# Dependencies
The project uses several Python libraries to achieve its functionality. Below is a list of the main dependencies:
Flask: Web framework for creating the web application.
pm4py: Python library for process mining, used to import event logs, discover process models, and perform conformance checking.
sqlite3: Standard Python library for interacting with SQLite databases.
matplotlib and networkx: Used for graphing and visualizing the process flows.
plotly: Visualization library for creating interactive graphs.
base64, io, and json: Standard Python libraries for data manipulation and visualization.
vis-network: JavaScript library used in the web application for visualizing process models as interactive graphs.
Installation
To run this project locally, you need to install Python and the required dependencies:

<img width="779" alt="image" src="https://github.com/user-attachments/assets/01c5287f-2746-4c14-b202-8f724b8c3dfa">
<img width="652" alt="image" src="https://github.com/user-attachments/assets/cbbdd1e2-9376-4bbb-a10f-f1d6c7a3835c">
<img width="642" alt="image" src="https://github.com/user-attachments/assets/3bf9e1b4-c73b-497b-9d43-5cf2f8231d7e">
<img width="638" alt="image" src="https://github.com/user-attachments/assets/1f4cb2d9-2b2f-4763-be45-a4f5beaa1dcf">
<img width="516" alt="image" src="https://github.com/user-attachments/assets/13e97724-c598-4194-9257-72a9f2466205">
<img width="340" alt="image" src="https://github.com/user-attachments/assets/d51d34ba-63c1-4031-a5d5-87d285f102a6">
<img width="694" alt="image" src="https://github.com/user-attachments/assets/34f53cc1-a0ff-4ba2-b542-c31ce78d2e37">
<img width="698" alt="image" src="https://github.com/user-attachments/assets/590ed68c-78e5-4a29-ae30-3553506fa682">
<img width="707" alt="image" src="https://github.com/user-attachments/assets/72a74cbe-1d9f-48a4-8795-01bca898f607">
<img width="683" alt="image" src="https://github.com/user-attachments/assets/68575bc0-b65f-476f-a2c2-5fe719969472">


bash
Copy code
pip install flask pm4py matplotlib plotly networkx
Usage
Run the Flask Application: To start the web application, run the Flask server:

bash
Copy code
python app.py
Navigate to http://localhost:5000 in your web browser to access the application.

Upload Event Logs: You can upload an XES file via the web interface. The application will process the file and display various process mining results, including Petri nets, DFGs, and identified bottlenecks.

Visualize and Analyze: Use the web interface to explore different process models, filter by variants or transitions, and analyze the overall process performance.

# API Endpoints
POST /: Main endpoint to upload event logs and visualize results.
POST /transitions: Analyze incoming and outgoing transitions for a specific event.
POST /filter_rework: Filter DFG to identify rework activities.
POST /filter_dfg_variants: Filter the DFG by specific variants or transitions.
POST /transition_info: Retrieve detailed information about a specific transition.
Screenshots

# Contributing
If you would like to contribute to this project, please fork the repository and create a pull request with your changes.

License
This project is licensed under the MIT License.

Acknowledgments
This project was developed by Parisa Ebrahimi as part of a process mining project. Special thanks to the developers of pm4py and other open-source libraries used in this project.


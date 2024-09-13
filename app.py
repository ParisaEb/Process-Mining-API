from flask import Flask, request, render_template, jsonify, send_from_directory
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
import matplotlib
import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from ActivityExtractor import ActivityExtractor
from JsonBuilder import JsonBuilder
from NodeGenerator import NodeGenerator
from TransitionExtractor import TransitionExtractor
from XesToPandasConvertor import XesToPandasConverter
from main import (visualize_petri_net, visualize_DFG,
                  calculate_cycle_time, detect_bottlenecks,
                  visualize_happy_path_with_graph, get_variants,
                  visualize_petri_net_Json, get_dfg_for_variant,
                  get_incoming_outgoing_transitions, filter_variants_by_transition,
                  visualize_happy_path_with_graph_json, get_happy_path,
                )
from FileUploader import FileUploader  # Import the FileUploader class

app = Flask(__name__)
matplotlib.use('Agg')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    uploader = FileUploader()  # Initialize the FileUploader
    activities = []
    activity_case_counts = {}
    dfg_data = None
    selected_variant = None
    file_path = 'temp.xes'
    transitions = []
    pandas_html = None

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                file_path = uploader.save_file(file, filename='temp.xes')  # Use the FileUploader to save the file

                activity_extractor = ActivityExtractor(file_path)  # Initialize ActivityExtractor
                activities = activity_extractor.get_activities()
                activity_case_counts = activity_extractor.get_activity_case_counts()

                (activities, avg_cycle_time, bottlenecks, petri_net_base64, happy_path_json_data,
                 happy_path_percentage, variants_json_data, petri_net_json_data, dfg_initial_data,
                 dfg_all_data, variants, file_path, pandas_html, activity_case_counts) = process_request(file_path)

                # Use TransitionExtractor to get transitions
                transition_extractor = TransitionExtractor(file_path)
                transitions = transition_extractor.extract_transitions()

                return render_template('index.html', petri_net=petri_net_base64, avg_cycle_time=avg_cycle_time,
                                       bottlenecks=bottlenecks, happy_path_json_data=happy_path_json_data,
                                       happy_path_percentage=happy_path_percentage, activities=activities,
                                       variants_json_data=variants_json_data, petri_net_json_data=petri_net_json_data,
                                       dfg_initial_data=dfg_initial_data, dfg_all_data=dfg_all_data,
                                       variants=variants, file_path=file_path, transitions=transitions,
                                       pandas_html=pandas_html, activity_case_counts=activity_case_counts)
        elif request.is_json:
            data = request.get_json()
            if 'variant' in data:
                selected_variant = data['variant']
                file_path = data['file_path']
                dfg_data = get_dfg_for_variant(file_path, selected_variant)
                return jsonify(dfg_data)
    return render_template('index.html', activities=activities, transitions=transitions, pandas_html=pandas_html,
                           activity_case_counts=activity_case_counts)





@app.route('/filter_rework', methods=['POST'])
def filter_rework():
    data = request.get_json()
    activity = data.get('activity')
    file_path = data.get('file_path')
    if activity:
        log = xes_importer.apply(file_path)
        filtered_log = pm4py.filtering.log.variants.filter_activities_rework(log, activity)
        dfg = dfg_discovery.apply(filtered_log)
        node_generator = NodeGenerator(dfg)
        nodes, edges = node_generator.generate()
        return jsonify({"nodes": nodes, "edges": edges})
    else:
        return jsonify({"error": "Activity is required"}), 400

@app.route('/get_case_count', methods=['POST'])
def get_case_count():
    data = request.get_json()
    activity = data.get('activity')
    file_path = data.get('file_path')
    log = xes_importer.apply(file_path)
    case_count = sum(1 for trace in log if any(event['concept:name'] == activity for event in trace))
    return jsonify({'case_count': case_count})


@app.route('/filter_dfg_variants', methods=['POST'])
def filter_dfg_variants():
    data = request.get_json()
    file_path = data.get('file_path')
    transition = data.get('transition')
    include = data.get('include')

    # Load the event log
    log = xes_importer.apply(file_path)

    # Retrieve and filter variants based on the specified transition and inclusion criteria
    variants = get_variants(file_path)
    filtered_variants = filter_variants_by_transition(variants, transition, include)
    filtered_variant_keys = list(filtered_variants.keys())

    # Apply the filtered variants to the log and discover the DFG
    filtered_log = variants_filter.apply(log, filtered_variant_keys)
    dfg = dfg_discovery.apply(filtered_log)

    # Use the NodeGenerator class to generate nodes and edges
    node_generator = NodeGenerator(dfg)
    nodes, edges = node_generator.generate()

    # Build the filtered DFG JSON using JsonBuilder
    return JsonBuilder.build_filtered_dfg_json(nodes, edges)


@app.route('/filter_transitions', methods=['POST'])
def filter_transitions():
    data = request.get_json()
    act1 = data.get('act1')
    act2 = data.get('act2')
    file_path = data.get('file_path')

    # Load the event log
    log = xes_importer.apply(file_path)

    # Filter the log for traces that contain transitions between act1 and act2
    filtered_log = pm4py.filtering.filter_between(
        log,
        act1,
        act2,
        activity_key='concept:name',
        case_id_key='case:concept:name',
        timestamp_key='time:timestamp'
    )

    # Discover the DFG from the filtered log
    dfg = dfg_discovery.apply(filtered_log)

    # Use the NodeGenerator class to generate nodes and edges from the DFG
    node_generator = NodeGenerator(dfg)
    nodes, edges = node_generator.generate()

    # Build the filtered DFG JSON using JsonBuilder
    return JsonBuilder.build_filtered_dfg_json(nodes, edges)


@app.route('/transitions', methods=['POST'])
def transitions():
    data = request.get_json()
    selected_transition = data.get('selected_transition')
    file_path = data.get('file_path')
    transition_extractor = TransitionExtractor(file_path)
    transitions_data = transition_extractor.get_incoming_outgoing_transitions(selected_transition)
    return JsonBuilder.build_transition_info_json(transitions_data)

@app.route('/transition_info', methods=['POST'])
def transition_info():
    data = request.get_json()
    transition = data.get('transition')
    file_path = data.get('file_path')
    transition_extractor = TransitionExtractor(file_path)
    info = transition_extractor.get_transition_info(transition)
    return JsonBuilder.build_transition_info_json(info)
def calculate_happy_path_percentage(file_path):
    log = xes_importer.apply(file_path)
    happy_path = get_happy_path(file_path)
    happy_path_cases = sum(
        1 for trace in log if [event['concept:name'] for event in trace] == happy_path)
    total_cases = len(log)
    percentage = (happy_path_cases / total_cases) * 100 if total_cases > 0 else 0
    return percentage

@app.route('/get_variant_cases', methods=['POST'])
def get_variant_cases():
    data = request.get_json()
    variant = data.get('variant')
    file_path = data.get('file_path')
    log = xes_importer.apply(file_path)
    variants = get_variants(file_path)

    for variant_key, variant_traces in variants.items():
        variant_str = ' -> '.join(variant_key)
        if variant_str == variant:
            filtered_log = variants_filter.apply(log, [variant_key])
            df = pm4py.convert_to_dataframe(filtered_log)
            df = df.drop(['concept:name', 'time:timestamp'], axis=1)


            # Convert the DataFrame to HTML without the unwanted columns
            return df.to_html(index=False)

    return jsonify([])


@app.route('/get_variant_data', methods=['POST'])
def get_variant_data():
    data = request.get_json()
    variant = data.get('variant')
    file_path = data.get('file_path')
    log = xes_importer.apply(file_path)
    variants = get_variants(file_path)

    # Check if the requested variant is "Other"
    if variant == 'Other':
        # Get all variants that are not in the top 10
        sorted_variants = sorted(variants.items(), key=lambda x: len(x[1]), reverse=True)
        top_variants = sorted_variants[:10]
        other_variants = sorted_variants[10:]

        # Collect cases for the "Other" variants
        other_cases = []
        for _, traces in other_variants:
            other_cases.extend(traces)

        df = pm4py.convert_to_dataframe(log)
        filtered_df = df[df['case:concept:name'].isin([trace.attributes['concept:name'] for trace in other_cases])]
        filtered_log = pm4py.convert_to_event_log(filtered_df)
        dfg = dfg_discovery.apply(filtered_log)
        dfg_str_keys = {f"{k[0]} -> {k[1]}": v for k, v in dfg.items()}
        return jsonify({'cases': filtered_df.to_dict(orient='records'), 'dfg': dfg_str_keys})

    # Find the matching variant key in the variants dictionary
    for variant_key, variant_traces in variants.items():
        variant_str = ' -> '.join(variant_key)
        if variant_str == variant:
            filtered_log = variants_filter.apply(log, [variant_key])
            df = pm4py.convert_to_dataframe(filtered_log)
            dfg = dfg_discovery.apply(filtered_log)
            dfg_str_keys = {f"{k[0]} -> {k[1]}": v for k, v in dfg.items()}
            return jsonify({'cases': df.to_dict(orient='records'), 'dfg': dfg_str_keys})

    return jsonify({'cases': [], 'dfg': {}})  # Return empty if no matching variant is found


def process_request(file_path):
    activity_extractor = ActivityExtractor(file_path)  # Create an instance of ActivityExtractor
    xes_to_pandas = XesToPandasConverter(file_path)  # Create an instance of XesToPandasConverter
    activities = activity_extractor.get_activities()
    activity_case_counts = activity_extractor.get_activity_case_counts()
    pandas_html = xes_to_pandas.convert_to_html()  # Convert XES to HTML
    avg_cycle_time = calculate_cycle_time(file_path)
    bottlenecks = detect_bottlenecks(file_path)
    log = xes_importer.apply(file_path)

    # Use JsonBuilder for Petri net JSON and Base64 encoding
    net, initial_marking, final_marking = alpha_miner.apply(log)
    petri_net_json_data = JsonBuilder.build_petri_net_json(net, initial_marking, final_marking)
    petri_net_gviz = visualize_petri_net(file_path)
    petri_net_base64 = JsonBuilder.build_petri_net_base64(petri_net_gviz)

    # Use JsonBuilder for DFG JSON
    dfg_json_data = visualize_DFG(file_path)
    dfg_initial_data, dfg_all_data = JsonBuilder.build_dfg_json(dfg_json_data)

    # Use JsonBuilder for variants JSON
    variants = get_variants(file_path)
    variants_json_data = JsonBuilder.build_variants_json(variants, top_n=10)

    # Use JsonBuilder for happy path JSON
    happy_path_json_data = visualize_happy_path_with_graph_json(file_path)
    happy_path_percentage = calculate_happy_path_percentage(file_path)

    return (activities, avg_cycle_time, bottlenecks, petri_net_base64, happy_path_json_data,
            happy_path_percentage, variants_json_data, petri_net_json_data, dfg_initial_data,
            dfg_all_data, variants, file_path, pandas_html, activity_case_counts)


if __name__ == '__main__':
    app.run(debug=True)
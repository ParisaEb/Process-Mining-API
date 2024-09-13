import json
import sqlite3
from plotly.graph_objs.layout import Transition
from pm4py.algo.filtering.log.variants import variants_filter
import networkx as nx
import matplotlib.pyplot as plt
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from matplotlib.backends.backend_agg import FigureCanvasAgg
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from collections import Counter
import base64
import io
from JsonBuilder import JsonBuilder  # Import JsonBuilder
from NodeGenerator import NodeGenerator


def filter_variants_by_transition(variants, transition, include):
    filtered_variants = {}
    for variant_key, traces in variants.items():
        if include:
            if transition in variant_key:
                filtered_variants[variant_key] = traces
        else:
            if transition not in variant_key:
                filtered_variants[variant_key] = traces
    return filtered_variants

def generate_variant_mapping(file_path):
    log = xes_importer.apply(file_path)
    variants = get_variants(file_path)
    variant_mapping = {f"Variant {i+1}": ' -> '.join(variant) for i, variant in enumerate(variants.keys())}
    return variant_mapping

def visualize_petri_net_Json(file_path):
    log = xes_importer.apply(file_path)
    net, initial_marking, final_marking = alpha_miner.apply(log)
    # Use JsonBuilder to convert Petri net to JSON
    return JsonBuilder.build_petri_net_json(net, initial_marking, final_marking)

def visualize_petri_net(file_path):
    log = xes_importer.apply(file_path)
    net, initial_marking, final_marking = alpha_miner.apply(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking,
                               parameters={"format": "png", "graph_attr": {"rankdir": "LR"}})
    return gviz

def visualize_happy_path_with_graph(file_path):
    happy_path = get_happy_path(file_path)
    G = nx.DiGraph()
    for i, activity in enumerate(happy_path):
        G.add_node(activity)
        if i < len(happy_path) - 1:
            next_activity = happy_path[i + 1]
            if G.has_edge(activity, next_activity):
                G[activity][next_activity]['weight'] += 1
            else:
                G.add_edge(activity, next_activity, weight=1)

    nodes = [{"id": activity, "label": activity} for activity in G.nodes]
    edges = [{"from": u, "to": v, "label": str(d['weight'])} for u, v, d in G.edges(data=True)]
    return {"nodes": nodes, "edges": edges}

def visualize_DFG(file_path):
    log = xes_importer.apply(file_path)
    dfg = dfg_discovery.apply(log)
    happy_path = get_happy_path(file_path)

    # Using NodeGenerator class to generate nodes and edges
    node_generator = NodeGenerator(dfg)
    nodes, edges = node_generator.generate()

    start_activities = set()
    end_activities = set()
    for trace in log:
        if trace:
            start_activities.add(trace[0]['concept:name'])
            end_activities.add(trace[-1]['concept:name'])

    # Add start and end nodes
    start_node = {
        "id": "start", "label": "Start", "shape": "ellipse",
        "color": {"background": "green"}, "size": 30, "x": -200, "y": 0
    }
    end_node = {
        "id": "end", "label": "End", "shape": "ellipse",
        "color": {"background": "red"}, "size": 30, "x": 2000, "y": 0
    }
    nodes.append(start_node)
    nodes.append(end_node)

    for activity in start_activities:
        edges.append({
            "from": "start",
            "to": activity,
            "label": "",
            "arrows": "to",
            "color": {"color": "green", "highlight": "green", "hover": "green"}
        })
    for activity in end_activities:
        edges.append({
            "from": activity,
            "to": "end",
            "label": "",
            "arrows": "to",
            "color": {"color": "red", "highlight": "red", "hover": "red"}
        })

    happy_path_edges = []
    for i in range(len(happy_path) - 1):
        source = happy_path[i]
        target = happy_path[i + 1]
        for edge in edges:
            if edge["from"] == source and edge["to"] == target:
                happy_path_edges.append(edge)
                break
    initial_data = {"nodes": nodes, "edges": happy_path_edges}
    all_data = {"nodes": nodes, "edges": edges}
    print(f"Initial Data: {initial_data}")
    print(f"All Data: {all_data}")
    return json.dumps({"initial_data": initial_data, "all_data": all_data})


def print_variants(file_path):
    log = xes_importer.apply(file_path)
    variants = get_variants(file_path)
    print(f"Available Variants: {variants.keys()}")
    return variants.keys()

def get_variants(file_path):
    log = xes_importer.apply(file_path)
    variants = pm4py.get_variants(log)
    return variants

def get_dfg_for_variant(file_path, selected_variant):
    log = xes_importer.apply(file_path)
    variants = get_variants(file_path)
    for variant_key, variant_traces in variants.items():
        variant_str = ' -> '.join(variant_key)
        if variant_str == selected_variant:
            filtered_log = variants_filter.apply(log, [variant_key])
            dfg = dfg_discovery.apply(filtered_log)
            dfg_str_keys = {f"{k[0]} -> {k[1]}": v for k, v in dfg.items()}
            return dfg_str_keys
    return {}

def visualize_happy_path_with_graph_json(file_path):
    happy_path = get_happy_path(file_path)
    nodes = []
    edges = []

    for i, activity in enumerate(happy_path):
        nodes.append({"id": activity, "label": activity})
        if i < len(happy_path) - 1:
            edges.append({"from": happy_path[i], "to": happy_path[i + 1]})

    return json.dumps({"nodes": nodes, "edges": edges})

def visualize_DFG_data(file_path):
    log = xes_importer.apply(file_path)
    dfg = dfg_discovery.apply(log)
    node_positions = {activity: [i, 0] for i, activity in enumerate(dfg.keys())}
    edge_connections = []
    for source, targets in dfg.items():
        for target, weight in targets.items():
            edge_connections.append((source, target, weight))
    return node_positions, edge_connections

def get_happy_path(file_path):
    event_log = xes_importer.apply(file_path)
    trace_frequency = Counter(tuple(event['concept:name'] for event in trace) for trace in event_log)
    most_frequent_trace = max(trace_frequency, key=trace_frequency.get)
    filtered_log = [trace for trace in event_log if tuple(event['concept:name'] for event in trace) == most_frequent_trace]
    dfg = dfg_discovery.apply(filtered_log)
    happy_path = list(most_frequent_trace)
    return happy_path


def calculate_cycle_time(file_path, chunk_size=1000):
    log = xes_importer.apply(file_path)
    cycle_times = []
    for i in range(0, len(log), chunk_size):
        chunk = log[i:i + chunk_size]
        for trace in chunk:
            start_time = trace[0].get("time:timestamp")
            end_time = trace[-1].get("time:timestamp")
            cycle_time = (end_time - start_time).total_seconds()
            cycle_times.append(cycle_time)
    avg_cycle_time = sum(cycle_times) / len(cycle_times)
    return avg_cycle_time

def detect_bottlenecks(file_path):
    log = xes_importer.apply(file_path)
    dfg = dfg_discovery.apply(log)
    activity_pairs_counts = Counter(dfg)
    dfg_dict = dict(activity_pairs_counts)
    total_activities = sum(activity_pairs_counts.values())
    avg_frequency = {activity: count / total_activities for activity, count in activity_pairs_counts.items()}
    bottlenecks = sorted(avg_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    return bottlenecks

def get_incoming_outgoing_transitions(file_path, selected_transition_label):
    log = xes_importer.apply(file_path)
    net, initial_marking, final_marking = alpha_miner.apply(log)
    incoming_transitions = []
    outgoing_transitions = []
    selected_transition = None
    for transition in net.transitions:
        if transition.label == selected_transition_label:
            selected_transition = transition
            break
    if selected_transition is None:
        return json.dumps({"error": "Selected transition not found"})

    for arc in net.arcs:
        if arc.target == selected_transition:
            if arc.source.label is not None:
                incoming_transitions.append(arc.source.label)
        if arc.source == selected_transition:
            if arc.target.label is not None:
                outgoing_transitions.append(arc.target.label)
    result = {
        "selected_transition": selected_transition_label,
        "incoming_transitions": incoming_transitions,
        "outgoing_transitions": outgoing_transitions
    }
    return json.dumps(result, indent=4)



def visualize_happy_path_with_graph(file_path):
    happy_path = get_happy_path(file_path)
    G = nx.DiGraph()
    for i, activity in enumerate(happy_path):
        G.add_node(activity)
        if i < len(happy_path) - 1:
            next_activity = happy_path[i + 1]
            if G.has_edge(activity, next_activity):
                G[activity][next_activity]['weight'] += 1
            else:
                G.add_edge(activity, next_activity, weight=1)

    node_color = 'lightblue'
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    pos = {activity: (1, -i) for i, activity in enumerate(happy_path)}
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, pos, with_labels=False, node_shape='D', node_size=50, node_color=node_color, font_size=10, font_weight='normal', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='normal', ax=ax, verticalalignment='center', horizontalalignment='left')
    plt.axis('off')
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    plt.close(fig)
    buf.seek(0)
    graph_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return graph_base64

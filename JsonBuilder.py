# json_builder.py
import json
import base64
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from collections import Counter


class JsonBuilder:
    @staticmethod
    def build_petri_net_json(net, initial_marking, final_marking):
        nodes = []
        edges = []
        # Generate initial positions for places
        place_positions = {}
        for idx, place in enumerate(net.places):
            place_positions[place.name] = {"x": (idx % 10) * 150, "y": (idx // 10) * 150}

        # Convert places to JSON nodes
        for place in net.places:
            label = place.name if place in initial_marking or place in final_marking else ""
            node_size = 15 if label == "" else 15  # Default size
            if place in initial_marking:
                label += f"\n{initial_marking[place]} token(s)"
                node_size = 15
            node = {
                "id": place.name,
                "label": label,
                "color": JsonBuilder.generate_gradient_color("FFA500", 0.2),
                "shape": "circle",
                "size": node_size,
                "shadow": {"color": "#000", "size": 5},
                "borderWidth": 2,
                "x": place_positions[place.name]["x"],
                "y": place_positions[place.name]["y"]
            }
            nodes.append(node)

        # Convert transitions to JSON nodes
        for idx, transition in enumerate(net.transitions):
            if transition.label is not None:
                nodes.append({
                    "id": transition.name,
                    "label": transition.label,
                    "color": JsonBuilder.generate_gradient_color("0000FF", 0.2),
                    "shape": "box",
                    "size": 25,
                    "shadow": {"color": "#000", "size": 5},
                    "borderWidth": 2,
                    "font": {"color": "#FFFFFF"},
                    "x": ((idx + len(net.places)) % 10) * 150,
                    "y": ((idx + len(net.places)) // 10) * 150
                })
            else:
                nodes.append({
                    "id": transition.name,
                    "label": "",
                    "color": JsonBuilder.generate_gradient_color("0000FF", 0.2),
                    "shape": "box",
                    "size": 25,
                    "shadow": {"color": "#000", "size": 5},
                    "borderWidth": 2,
                    "hidden": True,
                    "x": ((idx + len(net.places)) % 10) * 150,
                    "y": ((idx + len(net.places)) // 10) * 150
                })

        for arc in net.arcs:
            edges.append({"from": arc.source.name, "to": arc.target.name})

        return json.dumps({"nodes": nodes, "edges": edges})

    @staticmethod
    def build_petri_net_base64(gviz):
        return base64.b64encode(gviz.pipe()).decode('utf-8')

    @staticmethod
    def build_dfg_json(dfg):
        dfg_data = json.loads(dfg)
        return json.dumps(dfg_data["initial_data"]), json.dumps(dfg_data["all_data"])

    @staticmethod
    def build_variants_json(variants, top_n=10):
        variant_counts = {}
        total_cases = sum(len(events) for events in variants.values())
        for variant, events in variants.items():
            variant_name = ' -> '.join(variant)
            variant_counts[variant_name] = len(events)
        sorted_variants = sorted(variant_counts.items(), key=lambda x: x[1], reverse=True)
        top_variants = sorted_variants[:top_n]
        other_variants = sorted_variants[top_n:]
        other_count = sum(count for variant, count in other_variants)
        if other_count > 0:
            top_variants.append(('Other', other_count))
        variant_list = []
        for i, (variant, count) in enumerate(top_variants, 1):
            percentage = (count / total_cases) * 100
            variant_list.append({
                'variant': variant,
                'count': count,
                'percentage': percentage
            })
        return json.dumps({"variants": variant_list})

    @staticmethod
    def build_transition_info_json(info):
        return json.dumps(info)

    @staticmethod
    def build_filtered_dfg_json(nodes, edges):
        return json.dumps({"nodes": nodes, "edges": edges})

    @staticmethod
    def build_happy_path_json(nodes, edges):
        return json.dumps({"nodes": nodes, "edges": edges})

    @staticmethod
    def generate_gradient_color(color, percentage):
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        r += (255 - r) * percentage
        g += (255 - g) * percentage

        return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from collections import Counter
import json

class TransitionExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.log = xes_importer.apply(file_path)

    def extract_transitions(self):
        net, initial_marking, final_marking = alpha_miner.apply(self.log)
        transitions = [transition.label for transition in net.transitions if transition.label]
        return transitions

    def get_incoming_outgoing_transitions(self, selected_transition_label):
        net, initial_marking, final_marking = alpha_miner.apply(self.log)
        incoming_transitions = []
        outgoing_transitions = []
        selected_transition = None

        for transition in net.transitions:
            if transition.label == selected_transition_label:
                selected_transition = transition
                break

        if selected_transition is None:
            return {"error": "Selected transition not found"}

        connected_places = set()
        for arc in net.arcs:
            if arc.target == selected_transition:
                connected_places.add(arc.source)
            elif arc.source == selected_transition:
                connected_places.add(arc.target)

        for arc in net.arcs:
            if arc.source in connected_places and arc.target.label is not None:
                outgoing_transitions.append(arc.target.label)
            elif arc.target in connected_places and arc.source.label is not None:
                incoming_transitions.append(arc.source.label)

        result = {
            "selected_transition": selected_transition_label,
            "incoming_transitions": incoming_transitions,
            "outgoing_transitions": outgoing_transitions
        }
        return result

    def get_transition_info(self, transition, chunk_size=1000):
        transition_count = 0
        case_count_with_transition = 0
        total_cases = len(self.log)
        incoming_transitions = Counter()
        outgoing_transitions = Counter()

        for i in range(0, len(self.log), chunk_size):
            chunk = self.log[i:i + chunk_size]
            for trace in chunk:
                trace_contains_transition = False
                for i, event in enumerate(trace):
                    event_name = event.get('concept:name', None)
                    if event_name == transition:
                        transition_count += 1
                        trace_contains_transition = True
                        if i > 0:
                            incoming_transitions[trace[i - 1]['concept:name']] += 1
                        if i < len(trace) - 1:
                            outgoing_transitions[trace[i + 1]['concept:name']] += 1
                if trace_contains_transition:
                    case_count_with_transition += 1

        percentage_cases = (case_count_with_transition / total_cases) * 100 if total_cases > 0 else 0
        most_common_incoming = incoming_transitions.most_common(1)[0] if incoming_transitions else ("", 0)
        most_common_outgoing = outgoing_transitions.most_common(1)[0] if outgoing_transitions else ("", 0)

        return {
            "percentage_cases": percentage_cases,
            "most_common_incoming": {
                "transition": most_common_incoming[0],
                "percentage": (most_common_incoming[1] / total_cases) * 100 if total_cases > 0 else 0
            },
            "most_common_outgoing": {
                "transition": most_common_outgoing[0],
                "percentage": (most_common_outgoing[1] / total_cases) * 100 if total_cases > 0 else 0
            },
            "incoming_transitions": list(incoming_transitions.keys()),
            "outgoing_transitions": list(outgoing_transitions.keys())
        }

# NodeGenerator.py
from ActivityExtractor import ActivityExtractor

class NodeGenerator:
    def __init__(self, dfg, activity_extractor: ActivityExtractor = None):
        self.dfg = dfg
        self.nodes = []
        self.edges = []
        self.activities = set()
        self.node_positions = {}
        self.activity_extractor = activity_extractor

    def extract_activities(self):
        """Extracts unique activities either from the DFG or using the ActivityExtractor."""
        if self.activity_extractor:
            # Use ActivityExtractor if available
            self.activities = set(self.activity_extractor.get_activities())
        else:
            # Extract activities from the DFG if ActivityExtractor is not provided
            for (source, target), weight in self.dfg.items():
                self.activities.add(source)
                self.activities.add(target)

    def calculate_positions(self):
        """Calculates positions for the nodes based on extracted activities."""
        x_position = 0
        y_position = 0
        for activity in self.activities:
            self.node_positions[activity] = {'x': x_position, 'y': y_position}
            self.nodes.append({
                "id": activity,
                "label": activity,
                "x": x_position,
                "y": y_position
            })
            x_position += 150
            if x_position > 300:  # Limit x position to avoid too much horizontal spacing
                x_position = 0
                y_position += 100

    def create_edges(self):
        """Creates edges between nodes based on the DFG."""
        for (source, target), weight in self.dfg.items():
            source_pos = self.node_positions[source]
            target_pos = self.node_positions[target]
            edge_length = min(
                200, ((target_pos['x'] - source_pos['x']) ** 2 + (target_pos['y'] - source_pos['y']) ** 2) ** 0.5 + 50
            )
            self.edges.append({
                "from": source,
                "to": target,
                "label": str(weight),
                "length": edge_length
            })

    def generate(self):
        """Generates nodes and edges from the DFG."""
        self.extract_activities()
        self.calculate_positions()
        self.create_edges()
        return self.nodes, self.edges

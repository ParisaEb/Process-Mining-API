from pm4py.objects.log.importer.xes import importer as xes_importer
from collections import Counter

class ActivityExtractor:
    def __init__(self, file_path, chunk_size=1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.log = xes_importer.apply(file_path)

    def get_activities(self):
        activities = set()
        for i in range(0, len(self.log), self.chunk_size):
            chunk = self.log[i:i + self.chunk_size]
            activities.update(event['concept:name'] for trace in chunk for event in trace)
        return sorted(list(activities))

    def get_activity_case_counts(self):
        activity_case_count = Counter()
        for i in range(0, len(self.log), self.chunk_size):
            chunk = self.log[i:i + self.chunk_size]
            for trace in chunk:
                unique_activities = set(event['concept:name'] for event in trace)
                activity_case_count.update(unique_activities)
        return dict(activity_case_count)

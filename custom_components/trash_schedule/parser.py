"""Extract collection events from the FX Systems schedule cards."""
import re
from datetime import date
from html.parser import HTMLParser


class ScheduleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.div_stack = []
        self.card = None
        self.events = []

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        classes = set(dict(attrs).get("class", "").split())
        self.div_stack.append(classes)
        if "schedule-card" in classes:
            self.card = {"date": "", "summary": ""}

    def handle_data(self, data):
        if self.card is None:
            return
        if any("info-full-date" in item for item in self.div_stack):
            self.card["date"] += data
        elif any("info-fraction-name" in item for item in self.div_stack):
            self.card["summary"] += data

    def handle_endtag(self, tag):
        if tag != "div" or not self.div_stack:
            return
        classes = self.div_stack.pop()
        if "schedule-card" not in classes or self.card is None:
            return
        found = re.search(r"\b\d{4}-\d{2}-\d{2}\b", self.card["date"])
        summary = " ".join(self.card["summary"].split())
        if found and summary:
            self.events.append({
                "date": date.fromisoformat(found.group()).isoformat(),
                "summary": summary,
            })
        self.card = None


def parse_schedule(html):
    parser = ScheduleParser()
    parser.feed(html)
    if not parser.events:
        raise ValueError("No collection events found in schedule-card elements")
    unique = {(event["date"], event["summary"]) for event in parser.events}
    return [{"date": day, "summary": summary} for day, summary in sorted(unique)]

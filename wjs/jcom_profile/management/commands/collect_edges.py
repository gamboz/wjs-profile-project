"""Collect edges and nodes for Jaal."""
from dataclasses import dataclass
from itertools import combinations

from core.models import Account
from django.core.management.base import BaseCommand
from submission.models import Article

# Jaal allows only 20 categories for the color. I'll keep only 18
# countries plus NA and Other...
COUNTRIES = {
    "US": "United States",
    "IE": "Ireland",
    "GB": "United Kingdom",
    "IT": "Italy",
    "PH": "Philippines",
    "DE": "Germany",
    "NL": "Netherlands",
    "CN": "China",
    "CA": "Canada",
    "IN": "India",
    "PT": "Portugal",
    "AT": "Australia",
    "ES": "Spain",
    "BR": "Brazil",
    "RU": "Russian Federation",
    None: "NA",
}


@dataclass
class Node:
    author: Account
    num_papers: int = 0

    def __str__(self):
        country = self.author.country
        if country is not None:
            country = COUNTRIES.get(country.code, "Others")
        else:
            country = "NA"
        return f"{self.author.full_name().replace(',','')},{country:.<15},{self.num_papers}"

    @staticmethod
    def header():
        """Return headers suitable for Jaal."""
        return "id,country,num_papers"


@dataclass
class Edge:
    from_: Account  # must match with type of Node.id_
    to_: Account  # must match with type of Node.id_
    weigth: int = 0

    def __str__(self):
        return f"{self.from_.full_name().replace(',','')},{self.to_.full_name().replace(',','')},{self.weigth}"

    @staticmethod
    def header():
        """Return headers suitable for Jaal."""
        return "from,to,weight"


class Command(BaseCommand):
    help = "Import an article."  # NOQA

    def handle(self, *args, **options):
        """Command entry point."""
        nodes = {}
        edges = {}
        # TODO: I care only about authors of published papers.
        #       - write me more djangoso!
        #       - filter by article.is_published
        if limit := options["limit"]:
            articles = Article.objects.all()[:limit]
        else:
            articles = Article.objects.all()
        for article in articles:
            for author in article.authors.all():
                node = nodes.setdefault(
                    author.pk,
                    Node(
                        author=author,
                        num_papers=0,
                    ),
                )
                node.num_papers += 1

            for (from_, to_) in combinations(article.authors.all(), 2):
                edge = edges.setdefault(
                    f"{from_.id}-{to_.id}",
                    Edge(from_, to_, weigth=0),
                )
                edge.weigth += 1

        with open("/tmp/edges.csv", "wt") as edge_file:
            edge_file.write(Edge.header())
            edge_file.write("\n")
            edge_file.write("\n".join([e.__str__() for e in edges.values()]))
            edge_file.write("\n")
        with open("/tmp/nodes.csv", "wt") as node_file:
            node_file.write(Node.header())
            node_file.write("\n")
            node_file.write("\n".join([n.__str__() for n in nodes.values()]))
            node_file.write("\n")

    def add_arguments(self, parser):
        """Add arguments to command."""
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of articles to process.",
        )

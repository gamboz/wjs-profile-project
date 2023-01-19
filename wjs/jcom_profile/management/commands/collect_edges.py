"""Collect edges and nodes for Jaal."""
from dataclasses import dataclass
from itertools import combinations

from django.core.management.base import BaseCommand
from submission.models import Article


@dataclass
class Node:
    id_: int
    country: str
    num_papers: int = 0

    def __str__(self):
        return f"{self.id_},{self.country},{self.num_papers}"


@dataclass
class Edge:
    from_: int  # must match with type of Node.id_
    to: int  # must match with type of Node.id_
    weigth: int = 0


class Command(BaseCommand):
    help = "Import an article."  # NOQA

    def handle(self, *args, **options):
        """Command entry point."""
        nodes = {}
        edges = {}
        for article in Article.objects.all():
            for author in article.authors.all():
                country = author.country
                if country is not None:
                    country = country.name.replace(",", "-")
                    country = country.replace(" ", "-")
                else:
                    country = "NA"
                node = nodes.setdefault(
                    author.pk,
                    Node(
                        id=author.pk,
                        country=country,
                        num_papers=0,
                    ),
                )
                node.num_papers += 1
            authors_ids = [a.id for a in article.authors.all()]
            for from_to_tuple in combinations(authors_ids, 2):
                # what about a couple of authors who wrote together different papers?
                edges.setdefault(from_to_tuple, from_to_tuple)

        with open("/tmp/edges.csv", "wt") as edge_file:
            edge_file.write("from,to,weigth\n")
            edge_file.write("\n".join([f"{f},{t}" for f, t in edges.values()]))
            edge_file.write("\n")
        with open("/tmp/nodes.csv", "wt") as node_file:
            node_file.write("id,country,num_papers\n")
            node_file.write("\n".join([n.__str__() for n in nodes.values()]))
            node_file.write("\n")

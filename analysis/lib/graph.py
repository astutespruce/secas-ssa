import pandas as pd
import numpy as np


class DirectedGraph(object):
    def __init__(self, df, source, target):
        """Create DirectedGraph from data frame with source and target columns.

        Parameters
        ----------
        df : DataFrame,
        source : str
            name of source column
        target : str
            name of target_column
        """

        # save only unique combinations of source => target
        df = df.drop_duplicates(subset=[source, target])

        self.adj_matrix = df.set_index(target).groupby(source).groups
        self._size = len(self.adj_matrix)

    def __len__(self):
        return self._size

    @classmethod
    def from_arrays(cls, source, target):
        """Create DirectedGraph from arrays of sources and arrays of targets.

        Arrays must be the same length.

        Parameters
        ----------
        source : ndarray
        target : ndarray

        Returns
        -------
        DirectedGraph
        """

        return cls(
            pd.DataFrame({"source": source, "target": target}),
            source="source",
            target="target",
        )

    def components(self):
        """Find all connected components in graph.

        Adapted from networkx::connected_component

        Returns
        -------
        list of sets
            each set is the connected nodes in the graph
        """
        groups = []
        seen = set()
        for node in self.adj_matrix.keys():
            if not node in seen:
                # add current node with all descendants
                adj_nodes = {node} | self.descendants(node)
                seen.update(adj_nodes)
                groups.append(adj_nodes)

        return groups

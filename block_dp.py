import pydot as _pd

"""
Working File

<<< TODO >>>
Decide what to do about ties in utility:
- Break ties as Yes
- Break ties as No * < Current Choice >
- Break ties with a 50/50 split (needs some slight implementation
    changes)

Decide how self loops are handeled. See TODO on the recursive edge
case in node choice.

Right now this computes everything on the fly as requested, so
amortized time. Overall time could be fixed by precomputing everything
(even areas that are never reached?)

This also has the scheduler automatically picking the last block in
the event of a tie. This maybe doesn't matter because the distinction
should be arbitrary, but it's worth noting.

Yes = True
No  = False
"""

class StrategicBlockCascadeSolver:
    """
    An optimal polytime solver for block models

    You can give it a game, and it will compute the optimal schedule
    as well as the optimal strategy for any node given its type and
    current state of the world

    It uses dynamic programming to do all computation. Results of
    computation are stored in a large multidimmensional dictionary
    that it uses to look up values it's already computed. That
    dictionary is called "data" inside the object.

    Where B is the number of blocks, "data" is organized as follows:

    The first B dimensions are n_b, or the number of nodes in each
    block that have already chosen (including the current node)

    The next dimension is the block of the current node choosing

    The next B dimmensions are the y_b, or the number of nodes in each
    block that have chosen Yes.

    The last queryable dimension is the type of the node. True for Yes
    and False for No.

    The result of all of these dimensions is a tuple. The first
    element is True or False for whether Yes is the optimal
    choice. The second is a list of the expected number of Yeses in
    each block after this decision has been made.

    Ideally the return value would be extended to contain a third
    value if the node is undecided, and represent the expected value
    accordingly.

    """

    def __init__(self, p, pi, blockSizes, blockAdjacency):
        """
        Initialize scheduler object

        p              = probability of generating a Yes Type
        pi             = utility for choosing ones own Type
        blockSizes     = tuple of the sizes of each block (length B)
        blockAdjacency = block adjacency matrix (BxB double tuple) This
            can be asymetric and contain any non negative weights
        """
        self.p  = p
        self.pi = pi
        self.bs = blockSizes
        self.ba = blockAdjacency
        self.B  = len(blockSizes)
        self.nc = {} # DP table for optimal node choices
        self.bc = {} # DP table for optimal scheduler block choices

        assert len(self.ba) == self. B
        assert all(len(row) == self.B for row in self.ba)
        assert type(self.bs) is tuple, "BlockSizes must be a tuple"
        assert type(self.ba) is tuple, "BlockAdjacency must be a tuple"
        assert all(type(row) is tuple for row in self.ba)

    def nodeChoice(self, b, t, ns, ys):
        """ HELP! """
        assert len(ns) == self.B
        assert all(n >= 0 for n in ns)
        assert all(n <= s for n, s in zip(ns, self.bs))
        assert sum(ns) < sum(self.bs)
        assert 0 <= b and b < self.B
        assert len(ys) == self.B
        assert all(y >= 0 for y in ys)
        assert all(y <= n for y, n in zip(ys, ns))
        assert type(ns) is tuple
        assert type(ys) is tuple

        # Check if the solution is already computed
        key = (b, t, ns, ys)
        if key in self.nc:
            return self.nc[key] # Found it!

        # Have to compute solution :(

        # <<< TODO >>>
        #
        # This is not the right check! It should check that
        # specifically ns_b is one less than self.bs_b
        if sum(ns) == sum(self.bs) - 1:
            # Recursive edge case. There are no nodes to pick after
            # this, so it just performs a myopic decision.

            # <<< TODO >>>
            # Figure out if this is correct. Right now it doesn't
            # factor its own decision into its objective. The purpose
            # of this is to remove self loops when there is a nonzero
            # diagonal term. This might not accomplish this, and may
            # make this calculation innacurate.
            un = sum(a*(n - y) for a,y,n in zip(self.ba[b], ys,
                ns)) + (self.pi if not t else 0)
            uy = sum(a*y for a,y in zip(self.ba[b], ys)) + (self.pi
                if t else 0)

            # Choose Y when...
            choice = uy > un
            # Expected / actual number of Y's by block
            Ey_b = [float(y) for y in ys]
            if choice:
                Ey_b[b] += 1
            # Store result of computation
            result = (choice, tuple(Ey_b))
            self.nc[key] = result
            return result
        else:
            # Not last to pick. Must look over choice of yes and
            # choice of no to decide which is better in expected value
            # knowing scheduler choices

            # Utility for choosing No
            _ns = list(ns)
            _ns[b] += 1
            _ns = tuple(_ns)

            _, Ey_bN = self.blockChoice(_ns, ys) #E[Y|N] by block
            un = sum(a * (s - y) for a,y,s in zip(self.ba[b], Ey_bN,
                    self.bs)) + (self.pi if not t else 0)

            # Utility for choosing Yes
            # If this node chooses Yes, one more yes in its block
            _ys = list(ys)
            _ys[b] += 1
            _ys = tuple(_ys)

            _, Ey_bY = self.blockChoice(_ns, _ys) #E[Y|Y] by block
            uy = sum(a * y for a,y in zip(self.ba[b], Ey_bY)
                     ) + (self.pi if t else 0)

            # Choose Y when
            choice = uy > un
            # Store results of computation
            result = (choice, Ey_bY if choice else Ey_bN)
            self.nc[key] = result
            return result

    def blockChoice(self, ns, ys):
        """ HELP """

        assert len(ns) == self.B
        assert all(n >= 0 for n in ns)
        assert all(n <= s for n, s in zip(ns, self.bs))
        assert sum(ns) < sum(self.bs)
        assert len(ys) == self.B
        assert all(y >= 0 for y in ys)
        assert all(y <= n for y, n in zip(ys, ns))
        assert type(ns) is tuple
        assert type(ys) is tuple

        # Check if solution is already computed
        key = (ns, ys)
        if key in self.bc:
            return self.bc[key] # Found it!

        # Have to compute :(
        b    = -1
        Ey   = 0 # Total expected number of Yeses
        Ey_b = () # Expected number of yeses by block

        # Iterate over all possible choices of next schedule
        for i,n,s in zip(xrange(self.B), ns, self.bs):
            if n == s:
                # Can't pick any other nodes in this block because
                # they've all been chosen
                continue

            # Find expected number of yeses if we choose a node from
            # block i

            # Get expected number of yeses if the node chosen is a
            # yes or a no
            _, Ey_bY = self.nodeChoice(i, True,  ns, ys)
            _, Ey_bN = self.nodeChoice(i, False, ns, ys)

            # Weight expected number of nodes by the probability of
            # getting a Yes or No type
            _Ey_b = tuple(self.p * y + (1 - self.p) * n for y, n in
                         zip(Ey_bY, Ey_bN))
            _Ey = sum(_Ey_b)

            # If expected number of yeses is greater than the best
            # decision found so far, replace it
            if _Ey >= Ey:
                b, Ey, Ey_b = i, _Ey, _Ey_b

        # Store optimal choice for this state
        self.bc[key] = (b, Ey_b)
        return b, Ey_b

    def printNodeChoice(self):
        """ HELP """
        for k,v in self.nc.iteritems():
            print k,v

    def writeNaiveOnlineScheduleTree(self, filename, depth=5):
        """ HELP """

        g = _pd.Dot('G', graph_type='digraph')
        self._writeNaiveOnlineScheduleTree(g, (0,)*self.B, (0,)*self.B,
                                           1, depth)
        # <<< TODO >>>
        #
        # Filename extension checking
        g.write_pdf(filename)

    def _writeNaiveOnlineScheduleTree(self, g, ns, ys, num, depth):
        """ HELP """

        # Terminal condition
        if all(s == n for s,n in zip(self.bs, ns)):
            g.add_node(_pd.Node(str(num), label="N/A"))
            return
        # Non terminal
        b,_ = self.blockChoice(ns, ys)
        g.add_node(_pd.Node(str(num), label=str(b)))
        # Max depth reached?
        depth -= 1
        if depth <= 0:
            return
        # Calculate No path
        g.add_edge(_pd.Edge(str(num), str(num*2), label="No"))
        _ns = list(ns)
        _ns[b] += 1
        _ns = tuple(_ns)
        self._writeNaiveOnlineScheduleTree(g, _ns, ys, num*2, depth)
        # Calculate Yes path
        g.add_edge(_pd.Edge(str(num), str(num*2 + 1), label="Yes"))
        _ys = list(ys)
        _ys[b] += 1
        _ys = tuple(_ys)
        self._writeNaiveOnlineScheduleTree(g, _ns, _ys, num*2+1, depth)

    def writeImpossiblePrunedOnlineScheduleTree(self, filename, depth=5):
        """ HELP """

        g = _pd.Dot('G', graph_type='digraph')
        self._writeImpossiblePrunedOnlineScheduleTree(g, (0,)*self.B,
            (0,)*self.B, 1, depth)
        # <<< TODO >>>
        #
        # Filename extension checking
        g.write_pdf(filename)

    def _writeImpossiblePrunedOnlineScheduleTree(self, g, ns, ys, num,
                                                 depth):
        """ HELP """

        # Terminal condition
        if all(s == n for s,n in zip(self.bs, ns)):
            g.add_node(_pd.Node(str(num), label="N/A"))
            return
        # Non terminal
        b = self.blockChoice(ns, ys)[0]
        g.add_node(_pd.Node(str(num), label=str(b)))
        # Max depth reached?
        depth -= 1
        if depth <= 0:
            return
        # Calculate No path
        if not self.nodeChoice(b, False, ns, ys)[0]:
            # It's only possible for a strategic node to choose No if
            # a No type node chooses No, because if a No node chooses
            # Yes, then a Yes node will certainly choose Yes.
            g.add_edge(_pd.Edge(str(num), str(num*2), label="No"))
            _ns = list(ns)
            _ns[b] += 1
            _ns = tuple(_ns)
            self._writeImpossiblePrunedOnlineScheduleTree(g, _ns, ys,
                                                          num*2, depth)
        # Calculate Yes path
        if self.nodeChoice(b, True, ns, ys)[0]:
            # See explanation above for why this is suficient to
            # guarentee that it's possible for a node to choose Yes.
            g.add_edge(_pd.Edge(str(num), str(num*2 + 1), label="Yes"))
            _ys = list(ys)
            _ys[b] += 1
            _ys = tuple(_ys)
            self._writeImpossiblePrunedOnlineScheduleTree(g, _ns, _ys,
                                                          num*2+1, depth)

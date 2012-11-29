import pydot as _pd

"""
Caveat, this is a working file

The structure of this file is Object Oriented. You can construct a
StrategicBlockCascadeSolver with all of the settings of a game (p, pi,
and a definition of the block graph) and then call various methods to
figure out what a strategic agent will choose in a given situation.

The algorithms are based on dynamic programming methods, but are not
precomputed. This means the first time you call a method it may take a
long time to return a result, but subsequent calls will be fast
because the result is stored. Calculating a result will likely result
in the caculation of several other answers, meaning while your first
call may take a long time, many differeny subsequent calls will be
fast.

The data paradigm for this is to always use tuples. Most methods will
return an assertion error if you don't. True is synonomyous with Yes,
and False is synonomyous with No.

<<< TODO >>>
Decide what to do about ties in utility:
- Break ties as Yes
- Break ties as No * < Current Choice >
- Break ties with a 50/50 split (needs some slight implementation
    changes)

Decide how self loops are handeled. See TODO on the recursive edge
case in node choice.

Add assertion error messages
"""

class StrategicBlockCascadeSolver:
    """
    This object is an optimal polynomial time solver of a specific
    cascade game on block model graphs. The running time is
    exponential in the number of blocks, so making the number of
    blocks to large is likely beyond the scope of this algorithm.

    Computation is ammortized, so some calls may take a long time
    while others will be almost instanious. It mainly depends on much
    computation has already been done. Later calls on the same object
    are likely to be faster.

    Variable Definitions
    --------------------
    * B is the number of blocks in the block model.

    Example Use
    -----------

    import block_dp as bdp
    p  = 0.4
    pi = 0.5
    # This is an 11 node wheel graph
    s  = (1, 10)
    a  = ((0, 1),(1, 0))
    solver = block_dp.StrategicBlockCascadeSolver(p, pi, s, a)
    solver.blockChoice((0,)*2,(0,)*2)
    >>> (1, (0.4, 4.0))
    # This return value means you should pick a node in the outside of
    # the wheel first. By doing so you expect to convert 0.4 of the
    # center nodes and 4 of the outer nodes to Yes
    solver.writeImpossiblePrunedOnlineScheduleTree('tree.pdf')
    # This will save a pdf called 'tree.pdf' that represents the
    # decision tree as the center node based on what individual nodes
    # pick. Paths that never get chosen are pruned from consideration
    # and so you will never see paths that strategic agents will never
    # choose
    """

    def __init__(self, p, pi, blockSizes, blockAdjacency):
        """
        Create Solver Object

        bdp.StrategicBlockCascadeSolver(p, pi, bs, bs)

        Parameters
        ----------
        p              = probability of a node being a Yes Type (<.5)
        pi             = a nodes utility for choosing ones own Type
        blockSizes     = tuple of the sizes of each block (length B)
        blockAdjacency = block adjacency matrix (BxB double tuple) This
                         can be asymetric and contain any non negative
                         weights
        """
        self.p  = p
        self.pi = pi
        self.bs = blockSizes
        self.ba = blockAdjacency
        self.B  = len(blockSizes)
        self.nc = {} # DP table for optimal node choices
        self.bc = {} # DP table for optimal scheduler block choices

        assert p >= 0 and p <= 0.5, "p must be between 0 and 0.5"
        assert pi > 0, "pi must be greater than 0"
        assert len(self.ba) == self.B, "BlockAdjacency must be BxB"
        assert all(len(row) == self.B for row in self.ba), "BlockAdjacency must be BxB"
        assert type(self.bs) is tuple, "BlockSizes must be a tuple"
        assert type(self.ba) is tuple, "BlockAdjacency must be a tuple"
        assert all(type(row) is tuple for row in self.ba), "BlockAdjacency must be a tuple"
        assert all(all(e >= 0 for e in row) for row in self.ba), "All elements in BlockAdjacency have to be nonnegative"

    def nodeChoice(self, b, t, ns, ys):
        """
        Returns the optimal (yes/no) choice of a node

        solver.nodeChoice(b, t, ns, ys)

        Parameters
        ----------
        b  = Block membership of the node who's choosing [0,B)
        t  = Type of the node {True, False}
        ns = B length tuple of the number of nodes in each block that
             have alreay gone. This total does NOT include the node
             choosing now
        ys = B length tuple of the number of nodes in each block that
             have already gone and chosen Yes. This total does NOT
             include the node choosing now

        Return Values
        -------------
        choice = The Yes (True) or No (False) that coresponds to the
                 nodes optimal strategic choice
        Ey_b   = A B length tuple of the expected number of Yes nodes
                 in each block at the end of the game if the scheduler
                 and the nodes are all playing strategically
        """

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
        """
        Returns the optimal [0,B) choice of a block of nodes for the
        scheduler to pick next

        solver.blockChoice(ns, ys)

        Parameters
        ----------
        ns = B length tuple of the number of nodes in each block that
             have alreay gone.
        ys = B length tuple of the number of nodes in each block that
             have already gone and chosen Yes.

        Return Values
        -------------
        choice = A [0,B) integer corresponding to the optimal choice of
                 node block for the scheduler
        Ey_b   = A B length tuple of the expected number of Yes nodes
                 in each block at the end of the game if the scheduler
                 picks this node
        """

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
        """
        Prints a long table of the optimal node choices

        solver.printNodeChoice()

        The resulting table is the value for all scenarios that have
        already been computed. There will be 3B + 3 columns and
        len(bdp.nc) rows.

        Column order is b, t, ns, ys, choice, Ey_b or Block, Type,
        Number Already Chosen by Block, Number of Yesses by Block,
        Optimal Choice, Expected Number of Yesses by Block.
        """

        for k,v in self.nc.iteritems():
            print k,v

    def writeOnlineScheduleTree(self, filename, depth=5, prune=True):
        """
        Writes a tree of the optimal decisions for the scheduler

        solver.writeImpossiblePrunedOnlineScheduleTree(filename)
        solver.writeImpossiblePrunedOnlineScheduleTree(filename, depth):
        solver.writeImpossiblePrunedOnlineScheduleTree(filename, depth,
                                                       prune):

        Parameters
        ----------
        filename = The filename to save the pdf as. You must include the
                   .pdf extension, or most programs probably won't
                   recognize it
        depth    = Optional. The maximum depth the tree will descend to.
                   Defaults to 5.
        prune    = Optional. Whether or not to prune subtrees strategic
                   node will never choose. Defaults to True.
        """

        g = _pd.Dot('G', graph_type='digraph')
        self._writeOnlineScheduleTree(g, (0,)*self.B, (0,)*self.B, 1,
                                      depth, prune)
        # <<< TODO >>>
        #
        # Filename extension checking
        g.write_pdf(filename)

    def _writeOnlineScheduleTree(self, g, ns, ys, num, depth, prune):
        """
        This is the recursive helper method to fully expand the tree
        """

        # Terminal condition
        if all(s == n for s,n in zip(self.bs, ns)):
            g.add_node(_pd.Node(str(num), label="End"))
            return
        # Non terminal
        b = self.blockChoice(ns, ys)[0]
        g.add_node(_pd.Node(str(num), label=str(b)))
        # Max depth reached?
        depth -= 1
        if depth == 0:
            return
        # Calculate No path
        _ns = list(ns)
        _ns[b] += 1
        _ns = tuple(_ns)
        if not prune or not self.nodeChoice(b, False, ns, ys)[0]:
            # It's only possible for a strategic node to choose No if
            # a No type node chooses No, because if a No node chooses
            # Yes, then a Yes node will certainly choose Yes.
            g.add_edge(_pd.Edge(str(num), str(num*2), label="No"))
            self._writeOnlineScheduleTree(g, _ns, ys, num*2, depth,
                                          prune)

        # Calculate Yes path
        _ys = list(ys)
        _ys[b] += 1
        _ys = tuple(_ys)
        if not prune or self.nodeChoice(b, True, ns, ys)[0]:
            # See explanation above for why this is suficient to
            # guarentee that it's possible for a node to choose Yes.
            g.add_edge(_pd.Edge(str(num), str(num*2 + 1),
                                label="Yes"))
            self._writeOnlineScheduleTree(g, _ns, _ys, num*2+1, depth,
                                          prune)

    def genOnlineScheduleTree(self, prune=True):
        """
        Returns a "tuple tree" of decisons

        Parameters
        ----------
        prune = Optional. Whether not to prune the tree of decisions that
                strategic nodes never make. Defaults to True.

        Return Values
        -------------
        tupleTree = Nested tuples that represent the the possible
                    decisions of the scheduler and nodes. All nodes are
                    a three tuple of (block to choose, no branch, yes
                    branch). If the node doesn't have a yes or a no
                    branch, then the value will be None instead.
        """

        return self._genOnlineScheduleTree((0,)*self.B, (0,)*self.B,
                                           prune)

    def _genOnlineScheduleTree(self, ns, ys, prune):

        # Terminal condition
        if all(s == n for s,n in zip(self.bs, ns)):
            return None
        # Non terminal
        b,_ = self.blockChoice(ns, ys)

        # Calculate No path
        _ns = list(ns)
        _ns[b] += 1
        _ns = tuple(_ns)
        if not prune or not self.nodeChoice(b, False, ns, ys)[0]:
            # It's only possible for a strategic node to choose No if
            # a No type node chooses No, because if a No node chooses
            # Yes, then a Yes node will certainly choose Yes.
            no = self._genOnlineScheduleTree(_ns, ys, prune)
        else:
            no = None

        # Calculate Yes path
        _ys = list(ys)
        _ys[b] += 1
        _ys = tuple(_ys)
        if not prune or self.nodeChoice(b, True, ns, ys)[0]:
            # See explanation above for why this is suficient to
            # guarentee that it's possible for a node to choose Yes.
            yes = self._genOnlineScheduleTree(_ns, _ys, prune)
        else:
            yes = None

        return (b, no, yes)

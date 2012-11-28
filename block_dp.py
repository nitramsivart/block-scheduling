from pydot import Dot, Node, Edge

"""
Working file

Right now this computes everything on the fly as requested, so
amortized time. Overall time could be fixed by precomputing everything
(even areas that are never reached?)

This also ignores self loops, which may be important??? So even if you
have a nonzero block diagonal term, the true diagonal is still
zero. It should be trivial to fix, but I figured this made more
sense??

Right now this breaks ties in nodes choosing to go to yes, it does not
have a way to mark that a node picks with probability .5

This also has the scheduler automatically picking the last block in
the event of a tie. This maybe doesn't matter because the distinction
should be arbitrary, but it's worth noting.

Yes = True
No  = False
"""

class optimalScheduler:
    """
    An optimal scheduler

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

    def __init__(self, p, pi, sizes, blockAdj):
        """
        Initialize scheduler object

        p        = probability of generating a Yes Type
        pi       = utility for choosing ones own Type
        sizes    = list of the sizes of each block (length B)
        blockAdj = block adjacency matrix (BxB double list) This can be
            asymetric and contain any non negative weights
        """
        self.p        = p
        self.pi       = pi
        self.sizes    = sizes
        self.blockAdj = blockAdj
        self.B        = len(sizes)
        self.data     = {} # DP table for node choices
        self.sched    = {} # DP table for scheduler choices

        assert len(blockAdj) ==self. B
        assert all(len(x) == self.B for x in blockAdj)

    def query(self, ns, b, ys, t):
        """
        Query the optimal play of a node

        ns = list of the number of nodes of each block that have
            chosen so far (length B). This includes the node that is
            choosing now
        b  = block of the node that is choosing now (ns[b] should be 1
            greater than you might think
        ys = list of the number of nodes in each block that have chosen
            yes (length B). ys_i <= ns_i for all i
        t  = type of the node choosing (True = Yes, False = No)
        """
        assert len(ns) == self.B
        assert all(x >= 0 for x in ns)
        assert all(x <= y for x, y in zip(ns, self.sizes))
        assert ns[b] > 0
        assert 0 <= b and b < self.B
        assert len(ys) == self.B
        assert all(x >= 0 for x in ys)
        assert all(x <= y for x, y in zip(ys, ns))
        assert ys[b] < ns[b]

        # Dive represents a pointer to the current depth in the "data"
        # dictionary. Since things are computed on the fly, at each
        # step it has to check whether or not a branch exists before
        # it can traverse it. It adds branches it's never seen.
        dive = self.data
        for i in ns:
            if i not in dive:
                dive[i] = {}
            dive = dive[i]
        if b not in dive:
            dive[b] = {}
        dive = dive[b]
        for i in ys:
            if i not in dive:
                dive[i] = {}
            dive = dive[i]
        if t in dive:
            # We've already computed the value, and so we return it
            return dive[t]
        # Haven't already computed the value, so we need to

        if all(x == y for x, y in zip(ns, self.sizes)):
            # Recursive edge case. There are no nodes to pick after
            # this, so it just performs a myopic decision.
            ns_ = ns[:]
            ns_[b] -= 1 # One less "No" on block b because of self
            un = sum(a*(n - y) for a,y,n in zip(self.blockAdj[b], ys,
                ns_)) + (self.pi if not t else 0)
            uy = sum(a*y for a,y in zip(self.blockAdj[b], ys)) + (self.pi
                if t else 0)

            choice = uy >= un # Choose Y
            Ey = map(float, ys) # Expected / actual number of Y's
            if choice:
                Ey[b] += 1
            # Store result of computation
            dive[t] = (choice, Ey)
        else:
            # Not last to pick. Must look over choice of yes and
            # choice of no to decide which is better in expected value
            # knowing scheduler choices

            # Utility for choosing No
            _, Eyl_N = self.nextBlock(ns, ys) #E[Y|N]
            un = sum(a * (n - y) for a,y,n in zip(self.blockAdj[b],
                Eyl_N, self.sizes)) + (self.pi if not t else 0)

            # Utility for choosing Yes
            # If this node chooses Yes, one more yes in its block
            ys_ = ys[:]
            ys_[b] += 1
            _, Eyl_Y = self.nextBlock(ns, ys_) #E[Y|Y]
            uy = sum(a * y for a,y,n in zip(self.blockAdj[b],
                Eyl_Y, self.sizes)) + (self.pi if t else 0)

            choice = uy >= un # Optimal choice
            # Save results
            dive[t] = (choice, Eyl_Y if choice else Eyl_N)
        return dive[t]

    def nextBlock(self, ns, ys):
        """
        Determines which block should be picked next

        Maximizes the expected number of yeses, conditioned on the
        current state of the world

        ns = Number of nodes that have already picked up to this point,
            by block. For the first choice this is [0] * B
        ys = Number of yes nodes that have already picked up to this
            point. For the first choice this is also [0] * B

        scheduler.nextBlock([0] * B, [0] * B) will return the optimal
        block to pick first as well as the expected number of yeses in
        each block before the first node has picked.
        """

        dive = self.sched
        for i in ns:
            if i not in dive:
                dive[i] = {}
            dive = dive[i]
        for i in ys:
            if i not in dive:
                dive[i] = {}
            dive = dive[i]
        if not dive: # Have to compute

            b = -1
            Ey  = 0 # Total expected number of Yeses
            Eyl = [] # Expected number of yeses by block

            # Iterate over all choises of next schedule
            for i,n,s in zip(xrange(self.B), ns, self.sizes):
                if n == s:
                    # Can't pick any other nodes in this block because
                    # they've all been chosen
                    continue

                # Find expected number of yeses if we choose a node from
                # block i
                ns_ = ns[:]
                ns_[i] += 1 # Incriment number of chosen for block i

                # Get expected number of yeses if the node chosen is a
                # yes or a no
                _, cy = self.query(ns_, i, ys, True)
                _, cn = self.query(ns_, i, ys, False)

                # Weight expected number of nodes by the probability of
                # getting a Yes or No type
                Eyl_ = [self.p * y + (1 - self.p) * n for y,n in zip(cy,
                    cn)]
                Ey_ = sum(Eyl_)

                # If expected number of yeses is better than the best
                # decision found so far, replace it
                if Ey_ >= Ey:
                    b, Ey, Eyl = i, Ey_, Eyl_

            # Store optimal choice for this setting
            dive[b] = Eyl

        for b, Eyl in dive.iteritems():
            return b, Eyl

    def dataPrint(self):
        """
        Print DP tables / count space complexity

        Currently has very messy output... Could easily be cleaned up.
        """
        print _dataPrint((), self.data)

    def scheduleTree(self, filename, depth=5):
        g = Dot('G', graph_type='digraph')
        self._scheduleTree(g, [0]*self.B, [0]*self.B, 1, depth)
        g.write_pdf(filename)

    def _scheduleTree(self, g, ns, ys, num, depth):
        # Terminal condition
        if all(s == n for s,n in zip(self.sizes, ns)):
            g.add_node(Node(str(num), label="N/A"))
            return
        # Non terminal
        b,_ = self.nextBlock(ns, ys)
        g.add_node(Node(str(num), label=str(b)))
        # Max depth reached?
        if depth <= 0:
            return
        # Calculate No path
        g.add_edge(Edge(str(num), str(num*2), label="No"))
        ns_ = ns[:]
        ns_[b] += 1
        self._scheduleTree(g, ns_, ys, num*2, depth-1)
        # Calculate Yes path
        g.add_edge(Edge(str(num), str(num*2 + 1), label="Yes"))
        ys_ = ys[:]
        ys_[b] += 1
        self._scheduleTree(g, ns_, ys_, num*2+1, depth-1)

def _dataPrint(parent, tree):
    """
    Recursive Helper Method
    """
    if type(tree) is dict:
        leaves = 0
        for key, child in tree.iteritems():
            leaves += _dataPrint((key, parent), child)
        return leaves
    else:
        l = _tup2list(parent)
        print l,tree[0], tree[1]
        return 1

def _tup2list(tup):
    l = []
    while tup:
        l.append(tup[0])
        tup = tup[1]
    l.reverse()
    return l

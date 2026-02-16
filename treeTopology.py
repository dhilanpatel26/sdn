from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import MininetLogger
import sys
import argparse


logger = MininetLogger()
logger.setLogLevel('info')

def buildTreeTopology(n, **kwargs):
    topo = Topo()

    hostParams = {
        'cpu': kwargs.get('cpu')
    }


    linkParams = {
        'bw': kwargs.get('bw'),
        'delay': kwargs.get('delay'),
        'loss': kwargs.get('loss'),
        'max_queue_size': kwargs.get('max_queue_size'),
        'use_htb': kwargs.get('use_htb')
    }

    # hosts
    num_hosts = n ** 3
    hosts = []
    for i in range(1, num_hosts + 1):
        h = topo.addHost(f"h{i}", **hostParams)
        hosts.append(h)

    # edge switches
    num_edge_switches = n ** 2
    edge_switches = []
    for i in range(1, num_edge_switches + 1):
        e = topo.addSwitch(f"e{i}")
        edge_switches.append(e)

    # aggregation switches
    num_agg_switches = n
    agg_switches = []
    for i in range(1, num_agg_switches + 1):
        a = topo.addSwitch(f"a{i}")
        agg_switches.append(a)

    # core switch (root)
    core_switch = topo.addSwitch('c1')

    children = lambda i: range(n * i + 1, n * (i + 1) + 1)

    # edge-host links
    for i, e in enumerate(edge_switches):
        for j in children(i):
            topo.addLink(hosts[j-1], e, **linkParams)

    # agg-edge links
    for i, a in enumerate(agg_switches):
        for j in children(i):
            topo.addLink(edge_switches[j-1], a, **linkParams)

    # core-agg links
    for j in children(0):
        topo.addLink(agg_switches[j-1], core_switch, **linkParams)
    
    return topo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=2)
    parser.add_argument('-cpu', type=float, default=None)
    parser.add_argument('-bw', type=float, default=None)
    parser.add_argument('-d', type=str, default=None)
    parser.add_argument('-mqs', type=int, default=None)
    parser.add_argument('-l', type=float, default=None)
    parser.add_argument('-htb', action='store_true', default=False)
    args = parser.parse_args()

    topo = buildTreeTopology(
        n=args.n,
        cpu=args.cpu,
        bw=args.bw,
        delay=args.d,
        loss=args.l,
        max_queue_size=args.mqs,
        use_htb=args.htb
    )

    net = Mininet(topo=topo, cleanup=True)
    net.start()

    logger.info("Testing network connectivity\n")
    net.pingAll()

    logger.info("Testing bandwidth between end nodes\n")
    net.iperf()

    net.stop()

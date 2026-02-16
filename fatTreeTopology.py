from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, OVSController
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import MininetLogger
import sys
import argparse


logger = MininetLogger()
logger.setLogLevel('debug')

def buildTreeTopology(k=4, **kwargs):
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

    logger.debug("Setting up topology\n")

    core_grid_len = k // 2
    core_switches = []
    for i in range(core_grid_len):
        for j in range(core_grid_len):
            cs = topo.addSwitch(name=f"c{i * core_grid_len + j}", ip=f"10.{k}.{j}.{i}", dpid=f"00:00:00:00:00:{k}:{j}:{i}")
            core_switches.append(cs)

    logger.debug("Core switches done\n")

    num_pods = k
    num_agg_switches = k // 2
    num_edge_switches = k // 2

    # aggregation switches   
    agg_switches = []
    for p in range(num_pods):
        for i in range(num_edge_switches, num_edge_switches + num_agg_switches):
            agg = topo.addSwitch(name=f"p{p}a{i}", ip=f"10.{p}.{i}.{1}", dpid=f"00:00:00:00:00:{p}:{i}:01")
            agg_switches.append(agg)
            
            # core-agg links
            for port in range(k // 2):
                topo.addLink(core_switches[k // 2 * (i - k // 2) + port], agg, port1=p, port2=(k - 1 - port))
                
    logger.debug("Aggregation switches done\n")
    
    # edge switches
    edge_switches = []
    for p in range(num_pods):
        for i in range(num_edge_switches):
            es = topo.addSwitch(name=f"p{p}e{i}", ip=f"10.{p}.{i}.{1}", dpid=f"00:00:00:00:00:{p}:{i}:01")
            edge_switches.append(es)

            # agg-edge links
            for port in range(k // 2, k):
                topo.addLink(agg_switches[(k // 2) * p + port - k // 2], es, port1=i, port2=port)
    
    logger.debug("Edge switches done\n")

    # hosts
    hosts = []
    for p in range(num_pods):
        for s in range(num_edge_switches):
            for i in range(2, k // 2 + 2):
                h = topo.addHost(name=f"p{p}s{s}h{i}", ip=f"10.{p}.{s}.{i}")
                hosts.append(h)
               
                # edge-host links
                sport = i - 2
                topo.addLink(edge_switches[(k // 2) * p + s], h, port1=sport, port2=0)
    
    logger.debug("Hosts done\n")

    logger.debug("Topology done\n")

    return topo

topos = { 'fatTree': buildTreeTopology }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', type=int, default=4)
    args = parser.parse_args()

    topo = buildTreeTopology(
        k=args.k,
    )

    logger.debug("Starting Mininet build\n")

    net = Mininet(topo=topo, controller=OVSController, switch=OVSSwitch, cleanup=True)
    net.start()
    
    logger.debug("Dumping host connections\n")
    dumpNodeConnections(net.hosts)

    logger.debug("Miniset started successfully\n")

    logger.info("Testing network connectivity\n")
    net.pingAll()

    logger.info("Testing bandwidth between end nodes\n")
    net.iperf()

    net.stop()

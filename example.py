from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import MininetLogger


logger = MininetLogger()


def buildExampleTopo():
    topo = Topo()

    hostParams = {
        'cpu': 0.5/4
    }


    linkParams = {
        'bw': 10,
        'delay': '5ms',
        'loss': 1,
        'max_queue_size': 1000,
        'use_htb': True
    }


    # add hosts
    h1 = topo.addHost('h1', **hostParams)
    h2 = topo.addHost('h2', **hostParams)
    h3 = topo.addHost('h3', **hostParams)
    h4 = topo.addHost('h4', **hostParams)

    # add switches
    leftSwitch = topo.addSwitch('s3')
    rightSwitch = topo.addSwitch('s4')

    # add links
    topo.addLink(h1, leftSwitch, **linkParams)
    topo.addLink(h2, leftSwitch, **linkParams)
    topo.addLink(leftSwitch, rightSwitch, **linkParams)
    topo.addLink(h3, rightSwitch, **linkParams)
    topo.addLink(h4, rightSwitch, **linkParams)

    return topo


def runExperiment():
    logger.setLogLevel('info')
    topo = buildExampleTopo()
    net = Mininet(topo, host=CPULimitedHost, link=TCLink , cleanup=True)
    net.start()
    logger.info("Dumping host connections\n")
    dumpNodeConnections(net.hosts)
    logger.info("Testing network connectivity\n")
    net.pingAll()
    logger.info("Testing bandwidth between h1 and h4\n")
    h1, h4 = net.get('h1', 'h4')
    net.iperf((h1, h4))
    net.stop()

if __name__ == "__main__":
    runExperiment()


